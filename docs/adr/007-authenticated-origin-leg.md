# 007 · Authenticate the origin leg that serves customer domains

Status: **Accepted**

## Context

One workload on the production host serves its customers' own domains. A CDN's service for customer
domains terminates those customer certificates and connects to the origin carrying a server name that
differs from the request host, because the tenant is resolved from that host. The origin therefore
answers for names it does not declare, and its endpoint is reachable by any client, not only by the
CDN.

## Decision

Serve this leg from its own TLS terminator, kept out of the shared proxy, and require the CDN's client
certificate at the origin so that only the CDN can complete a handshake there. Keep the endpoint
public: reaching it is the CDN's job, and the shared proxy cannot serve this traffic at all.

## Consequences

A client without the certificate is refused at the handshake, whichever name it presents. The leg is
fail-closed: withdrawing the CDN's origin-pull setting, or rotating its certificate, stops every
customer domain, and recovery is one configuration file plus a restart. The requirement lives in
deployment-local configuration rather than in the application image, so a clone without it behaves as
before. Trust stays one-directional: the CDN does not verify the origin certificate in this mode.

## Alternative considered

Leaving the endpoint open relies on it being unannounced, and restricting it by source address ranges
still leaves the origin trusting any client that knows the address, while adding a list to maintain.
Terminating this leg through the shared proxy fails rather than degrades: the proxy rejects the
server-name and host mismatch that this traffic is built on.

## Evidence boundary

See the [shared evidence scope](../scope.md). Planned verification is not a completed result.
