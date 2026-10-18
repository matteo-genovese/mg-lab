# Roadmap

All work below is planned validation or exploration. The owner reports a deployed observability console with centralized logs as of 2026-10-18; ARM cloud capacity and K3s remain planned.

| Priority | Improvement | Completion criterion |
| --- | --- | --- |
| First | Exercise administrative access boundaries | Confirm intended access through a controlled review |
| First | Exercise Portainer operations and Beszel telemetry | Demonstrate management operations and telemetry for each documented host, building on the four-endpoint Up dashboard observation |
| First | Test alert delivery | Observe a controlled notification at its intended destination |
| First | Define backup coverage and exercise capture | Demonstrate that required data is included in a successful snapshot |
| First | Perform an isolated recovery exercise | Restore required data and verify application behavior |
| Next | Measure cloud micro VM headroom | Use CPU/memory trends to make a capacity decision |
| Explore | Evaluate mg-prod-02 on ARM cloud capacity | Assess compatibility, capacity, cost, and rollback |
| Explore | Experiment with K3s on the public VPS | Demonstrate operational benefit relative to Compose |
| First | Validate console collection and tune alert thresholds | Demonstrate useful log queries and collection from every node; tune initial thresholds against a baseline |
| First | Exercise independent witness and console access fallback | Observe a console failure signal, measure its delay, and test direct access during a proxy failure |
| First | Validate proxy blocking and rollback | Confirm CDN allowlisting and client attribution, rejection of invalid configuration, and manual block-list clearing |

A future cluster needs its own resilience design and validation before any HA claim. See the [planned architecture](../diagrams/rendered/future-architecture.svg).
