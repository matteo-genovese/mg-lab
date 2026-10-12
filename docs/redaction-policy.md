# Public allowlist and redaction policy

Infrastructure evidence comes exclusively from the supplied explicit public allowlist and the supplied observations and owner dashboard report identified in the [shared evidence scope](scope.md). Newer restrictive corrections take precedence over earlier wording. Private audits, host configurations, SSH, environment files, and private repositories must never be consulted or copied to populate this repository. The approved public host/software inventory and its caveats are documented in the README and scope page. Anything else must be omitted or explicitly planned/unverified.

## Human review before the mechanical gate

Review every sentence and diagram label against the explicit source. Generic application labels are mandatory; do not add customer/internal organization names, private application identities, operational URLs, address literals, provider identifiers, credential values, firewall/listener/security-list observations, precise backup schedules or ordering diagnosis, backup destinations, Hub system-row totals, or raw configuration. Do not replace missing evidence with a plausible claim. Future nodes remain clearly Planned.

`docs/public-review.json` is the reviewed candidate inventory: SHA-256 hashes bind the review to exact file bytes, including scripts, sources, rendered assets, and dotfiles. Changes and new files fail closed until reviewed. The manifest cannot hash itself; it is scanned for forbidden content and requires human review too. Do not regenerate it automatically from a render target. Hash approval is a deliberate content review, never a substitute for one.

## Mechanical checks

`make security` enumerates all public working-tree candidates, including ignored exports and any future workflow, and unions tracked paths. The presence of a prohibited directory is rejected before opening it, even if empty, nested, untracked, or ignored, in both working trees and ZIP/no-Git trees. Protected local tool/credential directories and environment directories are never traversed. Only the candidate root's validated `.git` directory or worktree pointer is treated as repository metadata; nested `.git` paths are prohibited. Developer caches `__pycache__` and `.venv` have their entry names inspected for prohibited directories, but their file contents are excluded and their symlinks are never followed; protected symlink paths are refused. Tracked cache paths remain prohibited. Candidate symlinks and unapproved binary formats are refused. The initial repository forbids workflow files because publication has not been approved.

The scanner blocks numeric address literals, provider identifiers, private/SSH URLs and local paths, credential assignment/key/token patterns, non-allowlisted host labels, operational URLs, external SVG references, SVG metadata/comments/scripts, and unapproved PNG metadata chunks. XML namespace identifiers and official D2 documentation links are narrowly exempted. Documentation can discuss secret categories without including their values; mentioning an environment-file category is not credential content.

Unknown internal names cannot reliably be recognized by regex, and private name lists must not be imported. The exact-content manifest blocks any newly introduced organization/application label until explicit review; a reviewer must then check labels against the source. Never claim this scanner alone proves semantic accuracy or detects every secret format.

`make check-history` separately scans every commit reachable from all local refs and HEAD, every referenced tree, and all commit messages. Each historical tree must contain its own valid `docs/public-review.json`, approving that tree's exact file bytes and complete inventory. Thus reviewed README, documentation, ADR, and diagram revisions can evolve together with their manifest. The current working manifest cannot approve an older revision. Static content and path rules still apply even to hash-approved historical files; deleting a credential does not cleanse history. Missing/malformed manifests, unsafe paths, invalid hashes, missing or extra files, symlinks, and unknown content fail closed.

History checking requires Git, a repository whose top-level directory is the candidate root (including a worktree with a `.git` pointer file), and at least one commit. Missing Git, ZIP/no-Git candidates, empty history, and shallow history return nonzero with an explicit "not checked" message. No commits exist initially. A ZIP can pass `make security` using its current manifest, but cannot attest history. Before eventual publication, include any otherwise unreachable history in a deliberate review too; this helper covers reachable refs and HEAD, not reflogs or dangling objects. Git replacement objects cannot override the scan. No remote access or rewriting is performed.

## Safe update procedure

1. Change only public documentation from explicitly approved facts.
2. Render and inspect all changed diagrams; run lint and deterministic comparison.
3. Review the complete candidate inventory, prose, labels, SVG structure, and PNG metadata.
4. Manually update only hashes for explicitly reviewed additions/changes in the manifest using Python's `hashlib.sha256` or `sha256sum`; remove inventory entries only for reviewed deletions. Review the manifest itself, including its metadata, paths, and complete inventory. Neither scan generates hashes or approves content.
5. Run `make security` on the exact candidate before committing. In an authorized repository, commit the reviewed files and their matching manifest together in every revision; review the commit message too. Do not commit first and attempt to bless it afterward with a newer manifest.
6. After committing, run `make check-history`. For a first commit, the pre-commit history check intentionally reports "not checked"; the post-commit check must pass. Publication still requires preview approval.

For future CI, require both `make security` and `make check-history` using a complete Git checkout with all refs intended for publication and no shallow history. Run the trusted scanner and review manifest changes as content approvals; a hash proves byte equality, not the legitimacy of the reviewer or the facts. This is a recommendation only; workflow files remain prohibited here.

Gitignore reduces accidental collection but is not the security boundary. The scanner deliberately sees ignored public candidates such as exports and refuses them.
