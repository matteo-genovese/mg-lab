# 006 · Document backup evidence before recovery claims

Status: **Accepted documentation; verification planned**

## Context

Backrest runs on production. The backup design collects node data and selected logical database dumps into a production staging tree before snapshot capture. The mechanism does not establish tested recovery.

## Decision

Document collection, snapshot capture, and restore as separate stages. Require coverage evidence and an isolated end-to-end recovery test before claiming recoverability. Keep operational details private.

## Consequences

Define required coverage, demonstrate successful capture, and perform an isolated recovery exercise. These are improvement goals rather than completed recovery results.

## Alternative considered

Treating successful collection as proof of restoration would skip a necessary validation stage.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
