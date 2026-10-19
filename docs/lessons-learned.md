# Lessons learned

1. **Keep failure signals outside the managed VM.** Separate monitoring retains a useful boundary when management fails. Shared cloud placement and micro VM resources still limit independence.
2. **Use central status as an operational signal.** Portainer's dashboard showed all four documented environments Up. That status is useful without proving every network path; Beszel telemetry deserves its own integration exercise.
3. **Design collection, capture, and recovery separately.** Backrest and data collection provide the mechanism. Define coverage and exercise an isolated restore to demonstrate usable recovery.
4. **Simple orchestration has a ceiling.** Compose reduces operational complexity, but one production host remains a single point of failure. A planned K3s experiment must justify its maintenance cost and address data recovery separately.
5. **Validate access boundaries deliberately.** Tailscale provides private administration connectivity; its presence alone does not guarantee Internet isolation.
6. **Exercise the alert path.** Configured notifications do not establish delivery. A controlled test should demonstrate that a useful signal reaches its destination.
   **Observed, 2026-10-19:** Console thresholds now use measured background noise, with a separate rule for a persistent source; see [ADR 010](adr/010-thresholds-from-a-measured-baseline.md).
7. **Attribute the client before counting or blocking sources.** When the proxy is behind a CDN, its access log records the CDN address rather than the client address until it reads the header carrying the real client address. Until then, every source count and every source-based block is silently wrong. Logging continues, so the system can appear to work while attributing traffic to the wrong source. This is an owner-supplied lesson, not an independently verified configuration change.

These lessons guide the [roadmap](roadmap.md). Observation provenance and the distinction between current design and plans are in the [scope](scope.md).
