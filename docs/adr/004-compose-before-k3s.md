# 004 · Keep Compose; evaluate K3s experimentally

Status: **Accepted baseline; experiment planned**

## Context

Production uses Docker Compose. There is no production K3s deployment.

## Decision

Retain Compose for simple operation; evaluate a planned K3s experiment on the public VPS and planned ARM cloud capacity separately.

## Consequences

Single-host scheduling and failure remain limits. Cluster complexity must earn its maintenance cost through demonstrated benefits.

## Alternative considered

Adopting a cluster now would add orchestration duties without evidence of an operating resilience design.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
