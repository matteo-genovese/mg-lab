# 010 · Choose alert thresholds from a measured baseline

Status: **Accepted** · Decision date: **2026-10-19**

## Context

**Inferred, 2026-10-19:** A public address attracts automated scanning as routine background traffic. Its noise baseline is not zero and will not become zero. A threshold below that baseline repeatedly alerts on ordinary traffic. The predictable response is to silence the alert, losing the useful signal as well.

## Decision

**Observed, 2026-10-19:** The owner reports replacing default console thresholds with thresholds chosen by measuring the same event source each rule queries. Count events in windows matching the rule's duration, then place the threshold above the ninetieth percentile and below the observed maximum. Traffic spread across sources does not warrant frequent alerts. A different event, one persistent source, warrants a rare alert and has a separate rule. This replaces the initial-threshold limit recorded in [ADR 008](008-single-observability-console.md).

## Consequences and accepted limits

**Inferred, 2026-10-19:** This method keeps alerts few and readable. The cost is remeasurement when traffic changes. Calibration from a short sample is an estimate, not a certainty.

## Alternatives considered

**Inferred, 2026-10-19:** The alternatives have these costs:

- Keep default thresholds: the alert gets lost in background noise.
- Alert on every event: nobody reads the alerts.
- Raise no alerts: a real attack loses its signal too.

## Evidence boundary

**Observed, 2026-10-19:** The method and separate rule are owner-supplied observations. Operational measurements remain in the private repository; no private source or live host was consulted. See the [shared evidence scope](../scope.md). **Unverified, 2026-10-19:** The measurement covers only one 24-hour window; its representativeness and subsequent alert behavior have not been independently verified.
