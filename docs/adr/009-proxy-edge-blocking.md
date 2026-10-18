# 009 · Block at the edge without host root privileges

Status: **Accepted** · Decision date: **2026-10-18**

## Context

Hostile traffic reaching the proxy should be blocked by source. The operational user on the public host has no root privileges. Obtaining those privileges indirectly is explicitly outside the design; this is a deliberate constraint, not a missing dependency.

## Decision

Detection produces events in a central service. An enforcement component writes a block list into the proxy configuration, tests the resulting configuration, and reloads the proxy only if the test passes.

Before enabling any blocking, allowlist the CDN network. Otherwise, a scan against a host exposing the edge can cause the CDN to be banned, taking all sites down. Correct client-source attribution is also required; see the [lesson on CDN access logs](../lessons-learned.md).

## Consequences and accepted limits

- Blocking happens after the connection has been accepted. It limits application processing and access-log load, but does not protect against bandwidth saturation.
- The block list remains a file that can be inspected and emptied by hand. That manual rollback must remain available; applying the cleared configuration follows the same test-before-reload rule.
- A failed configuration test must prevent the reload. This gate is part of the design, not evidence that failure behavior has been tested.
- CDN allowlisting prevents an accidental shared-source ban; it does not replace correct client-source attribution.

## Evidence boundary

The privilege constraint and implementation are owner-supplied context dated 2026-10-18. No independent live test of detection, blocking, rejected configuration, reload, manual rollback, CDN allowlist coverage, or client-source attribution was performed. See the [shared evidence scope](../scope.md).
