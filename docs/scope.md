# Architecture scope and provenance

This portfolio documents four hosts: mg-home-01 (home mini PC, Rome), mg-prod-01 (IONOS production VPS), and mg-mgmt-01 / mg-mon-01 (OCI Milan management and monitoring micro VMs). Home, IONOS, and OCI Milan are three placement contexts; no exact city is assigned to IONOS.

Documentation is current to **2026-10-12**. Container counts are not published here: a dated figure would be stale within days and carries no architectural information. Containers are not Portainer endpoints.

The supplied source observations were taken on **2026-10-11 at 21:16/21:17 UTC**, or **23:16/23:17 CEST** that same day. They establish software placement and configuration, including Portainer Server and Beszel Hub on management, Uptime Kuma on monitoring, Pi-hole at home, and Backrest on production. Compose, Tailscale, separate Caddy ingress, personal services, and the backup staging/dump design also use owner-supplied architectural context; they are not fresh health measurements.

The owner provided a Portainer dashboard screenshot showing all **four documented environments Up**. Its date was not independently verified, and the authenticated dashboard was not independently accessed live. This supports the observed dashboard status; it does not validate every network path, a measured SLA, or recovery. Beszel is shown as a logical telemetry relationship rather than a fully validated integration.

## Reading the architecture

Diagram edges express labeled architectural relationships. Provider grouping describes placement, not enforced isolation. Production has one host and no HA claim. An administration overlay alone does not guarantee Internet isolation. Kuma notification configuration is not evidence of delivery. Backrest and data collection are mechanisms, not proof of tested recovery.

The [roadmap](roadmap.md) sets improvement goals for telemetry, access boundaries, alert delivery, backup coverage, and recovery exercises. OCI ARM capacity, K3s, and centralized logging are planned, not deployed.

This local editorial review uses only supplied public facts and existing portfolio sources. Private operational details and raw source material are excluded under the [redaction policy](redaction-policy.md).
