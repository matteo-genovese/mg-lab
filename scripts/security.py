#!/usr/bin/env python3
"""Fail-closed public candidate gate. No host access or private fact discovery."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'docs/public-review.json'
LOCAL_ONLY = {'.git', '.aws', '.agents', '.codex', '.ssh', '__pycache__', '.venv'}
LOCAL_CACHES = {'__pycache__', '.venv'}
HOSTS = {'mg-home-01', 'mg-prod-01', 'mg-mgmt-01', 'mg-mon-01',
         'mg-prod-02', 'mg-logs-01'}
# Patterns name categories without embedding example secrets or private names.
RULES = {
    'OCI identifier': r'\bocid[0-9]+\.[A-Za-z0-9_.-]+',
    'SSH/private URI': r'(?i)(?:ssh|sftp|scp)://|git' + r'@[^\s]+|https?://(?:localhost|[^/\s]+\.(?:internal|local|lan))\b',
    'private path': r'/(?:home|root|Users)/[^\s<>"\']+|mg-infrastructure-' + 'private|oci-mg-' + 'nodes',
    'private key': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    'credential assignment': r'(?i)\b(?:password|passwd|api[_-]?key|access[_-]?token|secret[_-]?key|bot[_-]?token)\s*[:=]\s*["\']?[A-Za-z0-9_+/=-]{8,}',
    'cloud key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\bgh[pousr]_[A-Za-z0-9]{20,}',
    'notification token': r'\b[0-9]{6,}:[A-Za-z0-9_-]{25,}\b',
    'authenticated URI': r'\b[a-z]+://[^\s/]+:[^\s/]+@',
}

def unsafe_path(path):
    p = Path(path)
    return (not path or p.is_absolute() or '\\' in path
            or any(x in {'', '.', '..'} for x in path.split('/'))
            or any(x in LOCAL_ONLY or x in {'private', 'secrets', 'exports', 'backups', 'audit'} for x in p.parts)
            or any(x.startswith('.env') for x in p.parts)
            or p.suffix.lower() in {'.env', '.pem', '.key', '.dump', '.sql', '.tfstate', '.tfvars'}
            or path.startswith('.github/workflows/'))

def png_check(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        return ['Invalid PNG']
    pos, chunks, errors = 8, [], []
    while pos < len(data):
        if pos + 12 > len(data):
            return ['Truncated PNG']
        size = struct.unpack('>I', data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        if kind not in {b'IHDR', b'IDAT', b'IEND', b'bKGD', b'sRGB', b'gAMA', b'cHRM', b'pHYs'}:
            errors.append('Unapproved PNG metadata/chunk')
        chunks.append(kind)
        pos += size + 12
    if pos != len(data) or not chunks or chunks[-1] != b'IEND':
        errors.append('Malformed PNG or trailing payload')
    return errors

def content_check(path, data):
    if path.endswith('.png'):
        return png_check(data)
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return ['Unapproved binary format']
    errors = []
    for name, pattern in RULES.items():
        if re.search(pattern, text):
            errors.append(name)
    for candidate in re.findall(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])', text):
        # Block even invalid numeric dotted quads: no public address literals.
        errors.append('Numeric IP literal')
    for candidate in re.findall(r'(?<![\w])(?:[0-9A-Fa-f]{0,4}:){2,}[0-9A-Fa-f:.]*', text):
        try:
            ipaddress.IPv6Address(candidate)
            errors.append('Numeric IP literal')
        except ValueError:
            pass
    unknown = set(re.findall(r'\bmg-[a-z]+-\d+\b', text)) - HOSTS
    if unknown:
        errors.append('Host label outside allowlist')
    # There are no operational URLs in this portfolio. XML namespace identifiers
    # and official tool/license references are the only URI exceptions.
    for url in re.findall(r'https?://[^\s<>"\')]+', text):
        if not any(url.startswith(prefix) for prefix in
                   ('http://www.w3.org/', 'https://www.w3.org/',
                    'https://github.com/terrastruct/d2', 'https://d2lang.com/',
                    'https://mit-license.org/')):
            errors.append('URL outside public documentation allowlist')
    if path.endswith('.svg'):
        try:
            doc = ET.fromstring(data)
            for elem in doc.iter():
                tag = elem.tag.rsplit('}', 1)[-1]
                if tag in {'metadata', 'image', 'script', 'foreignObject'}:
                    errors.append('Forbidden SVG metadata / embedded object')
                for key, value in elem.attrib.items():
                    if key.rsplit('}', 1)[-1] in {'href', 'src'} and not value.startswith('#'):
                        errors.append('External SVG reference')
                    if key.lower().startswith('on'):
                        errors.append('SVG event handler')
            if '<!--' in text:
                errors.append('SVG comment metadata')
        except ET.ParseError:
            errors.append('Invalid SVG XML')
    return sorted(set(errors))

def git(*args):
    env = dict(os.environ, GIT_NO_REPLACE_OBJECTS='1')
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env,
                                   stderr=subprocess.PIPE)

def repository_required():
    if not (ROOT / '.git').exists():
        raise ValueError('History not checked: Git repository required')
    try:
        top = Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve()
        if top != ROOT.resolve():
            raise ValueError('History not checked: Git top-level must equal candidate root')
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError('History not checked: Git unavailable or invalid repository') from exc


def load_review(data):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate manifest key')
            result[key] = value
        return result

    try:
        review = json.loads(data, object_pairs_hook=unique_object)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError('Malformed review manifest') from exc
    if not isinstance(review, dict) or not isinstance(review.get('files'), dict):
        raise ValueError('Manifest files must be an object')
    approved = review['files']
    for path, digest in approved.items():
        if unsafe_path(path) or path == MANIFEST:
            raise ValueError('Manifest contains unsafe path or self approval')
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError('Manifest contains invalid SHA-256 hash')
    return approved


def scan_history():
    repository_required()
    try:
        if git('rev-parse', '--is-shallow-repository').strip() != b'false':
            raise ValueError('History not checked: shallow repository is incomplete')
        commits = git('rev-list', '--all').decode().splitlines()
        # Detached HEAD need not be named by a ref.
        try:
            head = git('rev-parse', '--verify', 'HEAD^{commit}').decode().strip()
        except subprocess.CalledProcessError:
            head = None
        if head:
            commits = sorted(set(commits) | set(git('rev-list', head).decode().splitlines()))
        if not commits:
            raise ValueError('History not checked: no commits exist')
        failures, scanned = [], 0
        trees = set()
        for commit in commits:
            message = git('show', '-s', '--format=%B', commit)
            failures.extend('Commit message: ' + e for e in content_check('commit-message.txt', message))
            trees.add(git('rev-parse', commit + '^{tree}').decode().strip())
        # Include refs pointing directly to trees; non-tree/blob refs fail closed.
        for ref in git('for-each-ref', '--format=%(objectname)').decode().splitlines():
            try:
                trees.add(git('rev-parse', ref + '^{tree}').decode().strip())
            except subprocess.CalledProcessError:
                failures.append('Ref has no reviewable tree')
        for tree in sorted(trees):
            entries = {}
            for record in git('ls-tree', '-r', '-z', tree).split(b'\0'):
                if not record:
                    continue
                meta, raw_path = record.split(b'\t', 1)
                path = raw_path.decode()
                mode, kind, oid = meta.decode().split()
                entries[path] = (mode, kind, oid)
            manifest = entries.get(MANIFEST)
            if manifest is None or (manifest[0] not in {'100644', '100755'} or manifest[1] != 'blob'):
                failures.append(tree + ': missing or unsafe historical manifest')
                approved = {}
            else:
                try:
                    approved = load_review(git('cat-file', 'blob', manifest[2]))
                except ValueError as exc:
                    failures.append(tree + ': ' + str(exc))
                    approved = {}
            failures.extend(tree + ': ' + path + ': approved file missing'
                            for path in set(approved) - set(entries))
            for path, (mode, kind, oid) in entries.items():
                if unsafe_path(path) or mode not in {'100644', '100755'} or kind != 'blob':
                    failures.append(path + ': prohibited historical path/type')
                    continue
                data = git('cat-file', 'blob', oid)
                scanned += 1
                failures.extend(path + ': ' + e for e in content_check(path, data))
                if path != MANIFEST and approved.get(path) != hashlib.sha256(data).hexdigest():
                    failures.append(tree + ': ' + path + ': absent from historical review or content changed')
        return failures, scanned
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        raise ValueError('History not checked: Git history could not be read completely') from exc


def candidates():
    # Enumerate public candidates without opening protected local directories.
    repository = (ROOT / '.git').exists()
    if repository:
        repository_required()
    found = set()
    def visit(folder, cache=False):
        for p in folder.iterdir():
            rel = p.relative_to(ROOT).as_posix()
            # Cache contents are not candidates, but their directory names must
            # not conceal protected paths. Never follow cache symlinks.
            policy_path = '/'.join(x for x in Path(rel).parts if x not in LOCAL_CACHES)
            if p.is_symlink():
                if cache and not unsafe_path(policy_path):
                    continue
                raise ValueError('Symlink candidate refused: ' + rel)
            if repository and rel == '.git':
                continue
            if p.is_dir():
                if policy_path and unsafe_path(policy_path):
                    raise ValueError(rel + ': prohibited candidate path')
                visit(p, cache or p.name in LOCAL_CACHES)
            elif not cache:
                found.add(rel)
    visit(ROOT)
    # Tracked protected paths are rejected by name, never read.
    if repository:
        found.update(x.decode() for x in git('ls-files', '-z').split(b'\0') if x)
    return found

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    failures, scanned = [], 0
    if args.history:
        failures, scanned = scan_history()
    else:
        paths = candidates()
        approved = load_review((ROOT / MANIFEST).read_bytes())
        for path in sorted(paths):
            if unsafe_path(path):
                failures.append(path + ': prohibited candidate path')
                continue
            p = ROOT / path
            if not p.is_file() or p.is_symlink():
                failures.append(path + ': missing or unsafe file type')
                continue
            data = p.read_bytes()
            scanned += 1
            failures.extend(path + ': ' + e for e in content_check(path, data))
            if path != MANIFEST and approved.get(path) != hashlib.sha256(data).hexdigest():
                failures.append(path + ': absent from review or content changed')
        failures.extend(path + ': approved file missing' for path in set(approved) - paths)
    if failures:
        print('\n'.join(sorted(set(failures))))
        sys.exit(1)
    print(f'Public gate passed: {scanned} files/blobs scanned, exact reviewed content required.')

def main():
    try:
        run()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc) if isinstance(exc, ValueError) else 'Public gate not checked: candidate or Git read failed')
        sys.exit(1)


if __name__ == '__main__':
    main()
