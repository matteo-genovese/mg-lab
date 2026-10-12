# Roadmap

All work below is planned. OCI ARM, K3s, and centralized logging are not deployed.

| Priority | Improvement | Completion criterion |
| --- | --- | --- |
| First | Exercise administrative access boundaries | Confirm intended access through a controlled review |
| First | Exercise Portainer operations and Beszel telemetry | Demonstrate management operations and telemetry for each documented host, building on the four-endpoint Up dashboard observation |
| First | Test alert delivery | Observe a controlled notification at its intended destination |
| First | Define backup coverage and exercise capture | Demonstrate that required data is included in a successful snapshot |
| First | Perform an isolated recovery exercise | Restore required data and verify application behavior |
| Next | Measure OCI micro VM headroom | Use CPU/memory trends to make a capacity decision |
| Explore | Evaluate mg-prod-02 on OCI ARM | Assess compatibility, capacity, cost, and rollback |
| Explore | Experiment with K3s and IONOS | Demonstrate operational benefit relative to Compose |
| Explore | Evaluate mg-logs-01 centralized logging | Demonstrate useful queries within an access and storage budget |

A future cluster needs its own resilience design and validation before any HA claim. See the [planned architecture](../diagrams/rendered/future-architecture.svg).
