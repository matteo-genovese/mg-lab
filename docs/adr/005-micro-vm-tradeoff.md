# 005 · Bound the micro VM role

Status: **Accepted**

## Context

Management and monitoring each use small AMD micro VMs.

## Decision

Use these nodes for bounded control-plane roles. Treat CPU and memory headroom as a constraint.

## Consequences

No SLA or HA follows from the provider split. Capacity measurement should precede additional services; ARM expansion remains planned.

## Alternative considered

A larger consolidated host increases capacity but combines failure domains; expansion needs a separate measured decision.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
