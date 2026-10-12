# 002 · Use an administration overlay

Status: **Accepted**

## Context

Administration crosses home and provider boundaries; public applications still need production ingress.

## Decision

Use Tailscale for administration and control-plane traffic rather than publishing private dashboards.

## Consequences

Overlay identity, policy, and availability become dependencies. Public application ingress goes directly to production. The overlay alone does not guarantee Internet isolation. A controlled access-boundary review is an improvement goal.

## Alternative considered

Publishing private dashboards would enlarge the public access surface. Operational access rules are intentionally omitted.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
