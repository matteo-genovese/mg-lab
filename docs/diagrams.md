# Diagram guide

Seven native D2 sources in `diagrams/src` produce nine SVGs and one hero PNG in `diagrams/rendered`. The overview and network retain dark variants with the same labels and geometry. Their wide compositions separate direct public production ingress, the logical administration plane, and provider/home placement; local DNS appears only between home users and the home host in the network view. Historical separate Caddy ingress context remains in the README and scope, outside these diagrams. No external assets or icon packages are used.

| Source | Purpose |
| --- | --- |
| infrastructure-overview | Four hosts grouped by provider/home; direct public production ingress and logical administration overlay |
| network-topology | Public application path, private administration peers, local DNS; no access-policy observations |
| management-architecture | Four Docker environments Up in the owner dashboard observation; logical Beszel telemetry |
| monitoring-alerting | HTTP/ping relationships and configured notification association; no delivery claim |
| services-workloads | Generic software groups by host, with owner-supplied design context marked separately |
| future-architecture | Dashed amber planned capacity, K3s experiment, and logging |
| backup-dataflow | Conceptual collection, snapshot mechanism, and planned recovery validation; no schedules or destinations |

## Visual system and semantics

Navy text and slate provider/host containers establish the baseline. Teal denotes logical administration, purple management, deep green with white text monitoring, and amber plans or validation goals. In the overview and network views, public application arrows are solid blue and end at production; administrative peer links are dashed teal with no arrowheads. Their D2 direction constrains layout only. Other views retain their existing palettes. Other solid slate arrows describe check or conceptual data relationships. Dashed amber arrows indicate planned work or validation goals. The overview, network, backup, management, and monitoring views carry legends for the colors and line styles they use.

An arrow expresses the labeled relationship, not verified packet direction or connectivity. Tailscale is a separate logical peer overlay. It is not an application gateway. Provider grouping describes placement rather than enforced isolation. The workload view groups software for readability; boxes are not a claim of one deployed stack. Observation provenance and owner-supplied design context are defined in the [scope](scope.md). The management view records four endpoints Up in the owner's dashboard. Its Portainer connector describes private management over Tailscale, not an independent test of every path; the Beszel connector describes a logical telemetry relationship because full integration has not been validated.

## Install locally

Install the official **D2 v0.9.0** release for your platform from [the upstream release](https://github.com/terrastruct/d2/releases/tag/v0.9.0), and verify its version. ELK is included in this D2 distribution. Install `rsvg-convert` from your OS package manager (typically the librsvg tools package), plus Python 3 and Make. No browser or network access is used by rendering.

```sh
d2 --version
rsvg-convert --version
make diagrams D2=/path/to/d2
make check-diagrams D2=/path/to/d2
make lint D2=/path/to/d2
make security
make check-history
```

`D2` defaults to `d2` on PATH. The build rejects other D2 versions rather than silently changing rendering. The render script explicitly selects ELK, fixed themes, padding, stable salts, and version omission. Dark sources are temporary palette transforms. A sans-serif fallback is added to SVG font-family rules for librsvg, which does not use embedded webfonts; browsers retain the bundled D2 font first. The PNG is rasterized from the light SVG at width 1600, preserving aspect ratio.

`check-diagrams` renders every SVG and the PNG to a fresh temporary directory, compares file inventory and bytes to the checked-in candidates, and deletes the temporary directory. It does not depend on commits or Git history. XML parsing checks SVG root, viewBox dimensions, nonempty text labels, and size; `lint` invokes D2 validation on all seven sources. rsvg-convert version differences may affect PNG bytes: use the same version when reviewing a render change.

`make security` also runs 29 regression tests covering address/credential patterns, metadata, category false positives, changed unapproved labels, prohibited paths (including hidden directories in ZIP/no-Git trees and caches), symlinks, and per-committed-tree review manifests in isolated temporary repositories.

Changing a diagram requires inspecting the output, rerunning all checks, and explicitly reviewing the updated content hashes under the public redaction policy. Byte equality verifies reproducibility, not topology truth or visual quality.

## Visual review

Review all nine SVGs at a 900-pixel width, including both dark variants, and inspect the hero PNG. Check readable labels, connector endpoints, crossings, and legend consistency. The public arrow must terminate at the production host box; no operational addresses, destinations, access-policy details, or backup timing may enter the assets.

Inspect the final renders at that width as a separate review step after source editing, including the hero PNG and both dark variants. This local asset review does not prove live topology or constitute external approval. The public-review manifest records the exact reviewed bytes after content inspection.
