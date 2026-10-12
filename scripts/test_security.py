#!/usr/bin/env python3
"""Exercise rejection paths without fixtures containing real sensitive facts."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import security

class PublicGateTests(unittest.TestCase):
    def test_address_literals_and_identifiers(self):
        for text in ('.'.join(['192', '0', '2', '1']), ':'.join(['2001', 'db8', '', '1']),
                     'ocid' + '1.instance.example', 'mg-unlisted-' + '99'):
            with self.subTest(category=text.split('.')[0]):
                self.assertTrue(security.content_check('example.md', text.encode()))

    def test_credentials_and_private_urls(self):
        cases = ['password' + '=ExampleCredentialValue', 'ssh' + '://example',
                 'https' + '://example.internal', 'https' + '://user:ExampleValue@example',
                 '-----BEGIN ' + 'PRIVATE KEY-----', '/home' + '/example/private']
        for text in cases:
            self.assertTrue(security.content_check('example.md', text.encode()))

    def test_category_discussion_is_safe(self):
        text = b'No IP literals, OCIDs, SSH URLs, .env content, credential values, or backup destinations.'
        self.assertEqual([], security.content_check('policy.md', text))

    def test_svg_and_png_metadata(self):
        self.assertTrue(security.content_check('figure.svg', b'<svg><metadata>creator</metadata></svg>'))
        self.assertTrue(security.content_check('figure.svg', b'<svg><image href="external"/></svg>'))
        self.assertTrue(security.content_check('figure.png', b'not a PNG'))
        # A text chunk is rejected without needing any real identifying content.
        chunk = (0).to_bytes(4, 'big') + b'tEXt' + bytes(4)
        self.assertTrue(security.png_check(b'\x89PNG\r\n\x1a\n' + chunk))

    def test_changed_unknown_label_fails_exact_content_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'docs').mkdir()
            candidate = root / 'README.md'
            candidate.write_text('Generic application groups\n')
            manifest = {'files': {'README.md': hashlib.sha256(candidate.read_bytes()).hexdigest()}}
            (root / security.MANIFEST).write_text(json.dumps(manifest))
            with patch.object(security, 'ROOT', root), \
                 patch('sys.argv', ['security.py']), contextlib.redirect_stdout(io.StringIO()):
                security.main()
                candidate.write_text('Invented organization or application label\n')
                with self.assertRaises(SystemExit):
                    security.main()

    def test_forbidden_paths_and_symlinks(self):
        for path in ('.env', 'exports/data.txt', '.github/workflows/publish.yml', '.aws/config'):
            self.assertTrue(security.unsafe_path(path))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'link').symlink_to('missing')
            with patch.object(security, 'ROOT', root):
                with self.assertRaises(ValueError):
                    security.candidates()

class RepositoryGateTests(unittest.TestCase):
    """Real Git plumbing; all writes and commits stay in isolated temp repos."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='security-regression-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = dict({k: v for k, v in os.environ.items()
                         if not k.startswith('GIT_')}, GIT_CONFIG_NOSYSTEM='1',
                        GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_AUTHOR_NAME='Temporary Test',
                        GIT_AUTHOR_EMAIL='test@example.invalid',
                        GIT_COMMITTER_NAME='Temporary Test',
                        GIT_COMMITTER_EMAIL='test@example.invalid')
        self.write('README.md', 'Public documentation\n')
        self.approve()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root,
                                       env=self.env, stderr=subprocess.PIPE)

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def approve(self):
        files = {p.relative_to(self.root).as_posix():
                 hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob('*')
                 if p.is_file() and '.git' not in p.parts
                 and p.relative_to(self.root).as_posix() != security.MANIFEST}
        self.write(security.MANIFEST, json.dumps({'files': files}))

    def commit(self, message='Reviewed public revision'):
        self.git('add', '--all')
        self.git('commit', '-m', message)

    def initialize(self):
        self.git('init', '-q')
        self.commit()

    def run_gate(self, history=True):
        output = io.StringIO()
        with patch.object(security, 'ROOT', self.root), \
             patch('sys.argv', ['security.py'] + (['--history'] if history else [])), \
             patch.dict(os.environ, self.env, clear=True), \
             contextlib.redirect_stdout(output):
            try:
                security.main()
            except SystemExit as exc:
                return exc.code, output.getvalue()
        return 0, output.getvalue()

    def assert_gate(self, passed, history=True, diagnostic=None):
        code, output = self.run_gate(history)
        self.assertEqual(code == 0, passed, output)
        if diagnostic:
            self.assertIn(diagnostic, output)

    def test_reviewed_initial_readme_and_new_adr_commits(self):
        self.initialize()
        self.assert_gate(True)
        self.write('README.md', 'Revised public documentation\n')
        self.approve()
        self.commit()
        self.assert_gate(True)
        self.write('docs/adr/007-example.md', 'Reviewed architectural decision\n')
        self.approve()
        self.commit()
        self.assert_gate(True)

    def test_deleted_credential_still_fails(self):
        self.initialize()
        self.write('README.md', 'Second reviewed revision\n')
        self.approve()
        self.commit()
        self.write('docs/adr/007-example.md', 'Reviewed decision\n')
        self.approve()
        self.commit()
        self.write('example.txt', 'password' + '=' + 'FAKE_SENTINEL_' + 'VALUE')
        self.approve()
        self.commit()
        (self.root / 'example.txt').unlink()
        self.approve()
        self.commit()
        self.assert_gate(True, history=False)
        self.assert_gate(False, diagnostic='credential assignment')

    def test_current_manifest_cannot_bless_unapproved_history(self):
        self.initialize()
        self.write('README.md', 'Unreviewed historical revision\n')
        self.commit()
        self.approve()  # Deliberately malicious current working manifest.
        self.assert_gate(False)

    def test_zip_tree_passes_but_history_is_not_checked(self):
        self.assert_gate(True, history=False)
        self.assert_gate(False, diagnostic='not checked')

    def test_zip_empty_inventory_cannot_hide_aws_directory(self):
        (self.root / 'README.md').unlink()
        self.write(security.MANIFEST, json.dumps({'files': {}}))
        self.write('.aws/config', 'Benign regression fixture\n')
        self.assert_gate(False, history=False, diagnostic='.aws: prohibited candidate path')

    def test_zip_protected_directories_are_rejected_without_opening(self):
        for directory in ('.aws', '.ssh', '.codex', '.agents',
                          'nested/.aws', 'nested/deeper/.ssh', '.env',
                          'nested/.env.local', 'exports', 'nested/private',
                          'nested/.git', '__pycache__/.aws', '.venv/nested/.ssh'):
            with self.subTest(directory=directory):
                protected = self.root / directory
                protected.mkdir(parents=True)
                payload = protected / 'config'
                payload.write_text('Benign regression fixture\n')
                original_iterdir = Path.iterdir
                original_read = Path.read_bytes

                def guarded_iterdir(path):
                    if path == protected:
                        self.fail('Protected directory was opened')
                    return original_iterdir(path)

                def guarded_read(path):
                    if path == payload:
                        self.fail('Protected content was read')
                    return original_read(path)

                try:
                    with patch.object(Path, 'iterdir', guarded_iterdir), \
                         patch.object(Path, 'read_bytes', guarded_read):
                        self.assert_gate(False, history=False,
                                         diagnostic='prohibited candidate path')
                finally:
                    payload.unlink()
                    protected.rmdir()

    def test_empty_protected_directory_is_rejected(self):
        (self.root / '.aws').mkdir()
        self.assert_gate(False, history=False, diagnostic='prohibited candidate path')

    def test_ignored_untracked_protected_directories_are_rejected(self):
        self.write('.gitignore', '.aws/\n.ssh/\n.codex/\n.agents/\n.env*/\n')
        self.approve()
        self.initialize()
        for directory in ('.aws', '.ssh', '.codex', '.agents', 'nested/.aws',
                          'nested/.env.local'):
            with self.subTest(directory=directory):
                self.write(directory + '/config', 'Benign regression fixture\n')
                self.assertEqual(b'', self.git('ls-files', '--', directory))
                self.assertTrue(self.git('check-ignore', directory + '/config'))
                self.assert_gate(False, history=False,
                                 diagnostic='prohibited candidate path')
                (self.root / directory / 'config').unlink()
                (self.root / directory).rmdir()

    def test_developer_caches_are_excluded_but_tracked_cache_paths_fail(self):
        self.write('__pycache__/module.pyc', 'Benign cache fixture\n')
        self.write('.venv/lib/module.py', 'Benign cache fixture\n')
        (self.root / '.venv/python').symlink_to('missing-cache-interpreter')
        original_read = Path.read_bytes

        def guarded_read(path):
            if any(part in {'__pycache__', '.venv'} for part in path.parts):
                self.fail('Cache content was read')
            return original_read(path)

        with patch.object(Path, 'read_bytes', guarded_read):
            self.assert_gate(True, history=False)
        self.git('init', '-q')
        self.assert_gate(True, history=False)
        self.git('add', '__pycache__/module.pyc')
        self.assert_gate(False, history=False, diagnostic='prohibited candidate path')

    def test_empty_repository_history_is_not_checked(self):
        self.git('init', '-q')
        self.assert_gate(False, diagnostic='not checked')

    def test_missing_git_history_is_not_checked(self):
        self.initialize()
        self.env['PATH'] = str(self.root / 'no-executables')
        self.assert_gate(False, diagnostic='not checked')

    def test_invalid_historical_manifests(self):
        invalid = [None, '{', json.dumps({'files': []}),
                   json.dumps({'files': {'../escape.md': 'a' * 64}}),
                   json.dumps({'files': {'README.md': 'invalid'}}),
                   json.dumps({'files': {'README.md': hashlib.sha256(
                       (self.root / 'README.md').read_bytes()).hexdigest(),
                                         'missing.md': 'b' * 64}}),
                   '{"files": {}, "files": {}}',
                   json.dumps({'files': {security.MANIFEST: 'a' * 64}})]
        self.initialize()
        initial = self.git('rev-parse', 'HEAD').decode().strip()
        for manifest in invalid:
            with self.subTest(manifest=manifest):
                # Each bad commit remains reachable even after a valid repair.
                self.git('reset', '--hard', initial)
                if manifest is None:
                    (self.root / security.MANIFEST).unlink()
                else:
                    self.write(security.MANIFEST, manifest)
                self.commit()
                self.approve()
                self.commit()
                self.assert_gate(False)

    def test_worktree_git_file(self):
        self.initialize()
        with tempfile.TemporaryDirectory(prefix='security-worktree-') as temp:
            worktree = Path(temp) / 'candidate'
            self.git('worktree', 'add', '--detach', str(worktree))
            original = self.root
            try:
                self.root = worktree
                self.assertTrue((worktree / '.git').is_file())
                self.assert_gate(True)
                self.assert_gate(True, history=False)
            finally:
                self.root = original

    def test_tree_ref_is_scanned(self):
        self.initialize()
        initial = self.git('rev-parse', 'HEAD').decode().strip()
        self.write('notes.md', 'api_' + 'key=' + 'FAKE_SENTINEL_' + 'TREE')
        self.approve()
        self.commit()
        tree = self.git('rev-parse', 'HEAD^{tree}').decode().strip()
        self.git('update-ref', 'refs/tags/review-tree', tree)
        self.git('reset', '--hard', initial)
        self.assert_gate(False, diagnostic='credential assignment')

    def test_repository_top_level_must_match_root(self):
        self.initialize()
        nested = self.root / 'nested'
        nested.mkdir()
        (nested / '.git').write_text('gitdir: ../.git\n')
        original = self.root
        try:
            self.root = nested
            self.env['GIT_WORK_TREE'] = str(original)
            self.assert_gate(False, diagnostic='top-level must equal candidate root')
        finally:
            self.root = original
            self.env.pop('GIT_WORK_TREE', None)

    def test_manifest_symlink_is_rejected_before_reading(self):
        self.write('target.txt', 'Not a review manifest\n')
        (self.root / security.MANIFEST).unlink()
        (self.root / security.MANIFEST).symlink_to('../target.txt')
        self.assert_gate(False, history=False, diagnostic='Symlink candidate refused')

    def test_history_does_not_read_current_manifest(self):
        self.initialize()
        (self.root / security.MANIFEST).unlink()
        self.assert_gate(True)
        self.write(security.MANIFEST, '{')
        self.assert_gate(True)
        self.assert_gate(False, history=False, diagnostic='Malformed review manifest')

    def test_working_tree_unknown_and_missing_files_fail(self):
        self.write('unknown.md', 'Public but unreviewed content\n')
        self.assert_gate(False, history=False, diagnostic='absent from review')
        self.approve()
        (self.root / 'unknown.md').unlink()
        self.assert_gate(False, history=False, diagnostic='approved file missing')

    def test_side_ref_and_commit_message_are_scanned(self):
        self.initialize()
        initial = self.git('rev-parse', 'HEAD').decode().strip()
        self.write('notes.md', 'Reviewed public note\n')
        self.approve()
        self.commit('password' + '=' + 'FAKE_SENTINEL_' + 'MESSAGE')
        self.git('branch', 'retained-review')
        self.git('reset', '--hard', initial)
        self.assert_gate(False, diagnostic='Commit message: credential assignment')

    def test_prohibited_tracked_path_is_not_read(self):
        self.initialize()
        self.write('.aws/config', 'Fake protected local content\n')
        self.commit()
        (self.root / '.aws/config').unlink()
        self.assert_gate(False, history=False, diagnostic='prohibited candidate path')
        self.assert_gate(False, diagnostic='prohibited historical path/type')

    def test_symlink_svg_and_credential_remain_rejected(self):
        self.initialize()
        (self.root / 'link').symlink_to('README.md')
        self.assert_gate(False, history=False, diagnostic='Symlink candidate refused')
        self.commit()
        self.assert_gate(False, diagnostic='prohibited historical path/type')
        (self.root / 'link').unlink()
        self.write('figure.svg', '<svg><image href="external"/></svg>')
        self.approve()
        self.assert_gate(False, history=False, diagnostic='Forbidden SVG')
        self.write('figure.svg', '<svg/>')
        self.write('notes.md', 'api_' + 'key=' + 'FAKE_SENTINEL_' + 'VALUE')
        self.approve()
        self.assert_gate(False, history=False, diagnostic='credential assignment')

if __name__ == '__main__':
    unittest.main()
