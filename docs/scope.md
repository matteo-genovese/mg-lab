# Architecture scope and provenance

This portfolio documents four hosts: mg-home-01 (home mini PC), mg-prod-01 (production VPS), and mg-mgmt-01 / mg-mon-01 (management and monitoring micro VMs). Home, the public VPS and the cloud nodes are three placement contexts.

Documentation is current to **2026-10-19**. Container counts are not published here: a dated figure would be stale within days and carries no architectural information. Containers are not Portainer endpoints.

The supplied source observations were taken on **2026-10-11 at 21:16/21:17 UTC**, or **23:16/23:17 CEST** that same day. They establish software placement and configuration, including Portainer Server and Beszel Hub on management, Uptime Kuma on monitoring, Pi-hole at home, and Backrest on production. Compose, Tailscale, separate Caddy ingress, personal services, and the backup staging/dump design also use owner-supplied architectural context; they are not fresh health measurements.

The owner provided a Portainer dashboard screenshot showing all **four documented environments Up**. Its date was not independently verified, and the authenticated dashboard was not independently accessed live. This supports the observed dashboard status; it does not validate every network path, a measured SLA, or recovery. Beszel is shown as a logical telemetry relationship rather than a fully validated integration.

## Decisions supplied on 2026-10-18

The owner reports one self-hosted observability console for metrics, logs, and alert rules on the home node, lightweight collection agents on every node, and an independent synthetic witness on a separate host. The owner also reports edge detection feeding central events and proxy-based blocking without host root privileges. The [console decision](adr/008-single-observability-console.md) and [blocking decision](adr/009-proxy-edge-blocking.md) record alternatives, constraints, and accepted limits. These statements extend the earlier observations; no private configuration or live host was consulted. Collection completeness, capacity, failure behavior, delivery, source attribution, and blocking remain independently unverified.

**Observed, 2026-10-19:** The owner reports that alert thresholds in the self-hosted observability console built on Grafana, Loki and Prometheus no longer use default values: they were chosen by measuring normal network noise. A second rule targets a single persistent source rather than traffic spread across sources. The [baseline decision](adr/010-thresholds-from-a-measured-baseline.md) records the method; operational measurements remain in the private repository. The owner also reports one successful notification delivery test. These are supplied observations, not independently exercised results. **Unverified, 2026-10-19:** The measurement covers only one 24-hour window.

## Reading the architecture

Diagram edges express labeled architectural relationships. Provider grouping describes placement, not enforced isolation. Production has one host and no HA claim. An administration overlay alone does not guarantee Internet isolation. Kuma notification configuration is not evidence of delivery. Backrest and data collection are mechanisms, not proof of tested recovery.

The [roadmap](roadmap.md) sets improvement goals for telemetry, access boundaries, alert delivery, backup coverage, and recovery exercises. ARM cloud capacity and K3s remain planned. Centralized logging is now reported as implemented in the home observability console; validation remains planned.

This local editorial review uses only supplied public facts and existing portfolio sources. Private operational details and raw source material are excluded under the [redaction policy](redaction-policy.md).
