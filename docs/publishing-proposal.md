# Publishing proposal

Current state: the repository is public on GitHub. Owner approval for publication was recorded on 2026-10-18, after the safety gate and the full-history scan passed on the exact candidate.

The repository can stand alone on GitHub with the README and relative SVG links. A later MkDocs Material site could provide ADR navigation, search, and theme-aware figures, hosted through GitHub Pages after review.

The steps completed before publication: the rendered diagrams were approved, every candidate file was reviewed against the facts allowlist, the safety and deterministic rendering checks passed, and the commit history was scanned separately. Decide the public repository identity and publishing permissions only at that point.

No site configuration, GitHub Actions workflow, remote, deployment, or publishing integration is included. A future workflow would itself be a publication candidate and must pass the same review. This proposal creates no deployment commitment.
