# 001 · Split production from control plane

Status: **Accepted**

## Context

Production runs on the public VPS; management and monitoring run on separate AMD micro VMs. Home remains a local-services node.

## Decision

Keep production application duties separate from control-plane duties.

## Consequences

A single production VPS still has no failover. Provider and OS diversity adds troubleshooting cost.

## Alternative considered

Co-locating control services on production would simplify the estate but couple their failure to the production host.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
