# Publishing proposal - not enabled

Current state: the repository is hosted in a **private** GitHub repository for owner review; this document covers a later public publication.

The repository can stand alone on GitHub with the README and relative SVG links. A later MkDocs Material site could provide ADR navigation, search, and theme-aware figures, hosted through GitHub Pages after review.

Before publishing: approve the rendered diagrams, review every candidate file against the facts allowlist, run the safety and deterministic rendering checks, and scan any commit history separately. Decide the public repository identity and publishing permissions only at that point.

No site configuration, GitHub Actions workflow, remote, deployment, or publishing integration is included. A future workflow would itself be a publication candidate and must pass the same review. This proposal creates no deployment commitment.
