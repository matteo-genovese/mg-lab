# 003 · Separate monitoring from management

Status: **Accepted**

## Context

Portainer and Beszel share the management VM; Kuma runs on another cloud VM.

## Decision

Keep availability checks on a separate monitoring VM.

## Consequences

Management VM failure need not remove monitoring. Both nodes still share a cloud location and limited micro VM capacity. Configured notifications do not establish delivery; a controlled alert exercise is planned.

## Alternative considered

Co-location uses fewer resources but couples signal collection to management failure.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
