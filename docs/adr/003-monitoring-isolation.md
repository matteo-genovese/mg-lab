# 003 · Separate monitoring from management

Status: **Accepted**

## Context

Portainer runs on the management VM; Kuma and the Beszel hub run on another cloud VM.

**Corrected 2026-11-09:** the Beszel hub no longer shares the management VM. It was moved to the monitoring VM, so the two concerns this decision separates are now split by host as well as by purpose. The original wording described the state until that date.

## Decision

Keep availability checks on a separate monitoring VM.

## Consequences

Management VM failure need not remove monitoring. Both nodes still share a cloud location and limited micro VM capacity. Configured notifications do not establish delivery; a controlled alert exercise is planned.

## Alternative considered

Co-location uses fewer resources but couples signal collection to management failure.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
