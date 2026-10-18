# 008 · One observability console, with an independent witness

Status: **Accepted** · Decision date: **2026-10-18**

## Context

Four machines span a public VPS, two cloud nodes, and a home node. Previously, a synthetic availability monitor and a per-node metrics panel could show availability and resources, but not what happened or who was making requests. Container logs were not collected centrally.

## Alternatives considered

- An all-in-one monitoring platform with an agent, server, and relational database covers thresholds and triggers well, but reads logs rather than providing the needed log search. Its memory requirement is disproportionate for the smallest node.
- A real-time agent-based monitor offers strong metrics and interface support, but weak log capabilities, the missing use case.
- An external managed service sends data outside the self-hosted estate and adds recurring cost for an objective the existing hardware can cover.

## Decision

Use one self-hosted observability console for metrics, searchable logs, and alert rules, with lightweight collection agents on every node. Place the heavy components on the home node, the only node with sufficient memory and disk capacity. Keep the independent synthetic witness on a separate host: the component that raises the failure signal must live outside what it watches.

The console's rules and the independent witness each have a logical notification path. Configured paths do not establish successful delivery.

## Consequences and accepted limits

- The console's access name depends on the host acting as the proxy. If that host fails, direct address access remains available, but access by name does not.
- A failure of the console itself is detected only by the out-of-band witness, with a delay. No measured detection time is claimed.
- This is not a security correlation system; operators search the logs manually.
- Alert thresholds retain their initial values and have not been tuned against a baseline.
- Centralizing the heavy components makes home-node availability a dependency for the console.

## Evidence boundary

The placement, implementation, alternatives, and accepted limits above are owner-supplied context dated 2026-10-18, not an independent live audit. Resource sufficiency, collection completeness, direct access during a proxy failure, witness detection, and notification delivery have not been independently exercised. See the [shared evidence scope](../scope.md).
