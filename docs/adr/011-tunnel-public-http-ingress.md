# 011 · Move public HTTP ingress behind an outbound tunnel, one vhost at a time

Status: **Proposed** · Decision date: **2026-11-01**

## Context

**Observed, 2026-10-18:** the production host publishes the proxy on all interfaces for HTTP and HTTPS, and publishes a second HTTPS listener for the customer-domain origin leg, protected by the CDN's Authenticated Origin Pulls ([ADR 007](007-authenticated-origin-leg.md)). Administrative names behind the proxy are reachable only by tailnet sources; the proxy administration port and the agent port are bound to the overlay.

**Inferred, 2026-11-01:** a published listener is the one surface that a patch shortage cannot narrow. The October 2026 remote use-after-free in the IPv4 TCP handshake, CVE-2026-98432, is the instance: while distribution kernels lag, an operator whose host publishes no reachable listener can remove the exposure by closing a port, and an operator who must keep the listener open can only wait for the vendor. Blocking after accept ([ADR 009](009-proxy-edge-blocking.md)) does not help here, because the flaw is reached before any application-level decision.

## Decision

**Proposed, 2026-11-01:** for public HTTP and HTTPS vhosts, replace inbound listeners with an outbound-only tunnel to the CDN edge, so that the origin publishes no HTTP port. Keep the customer-domain origin leg on its current direct, certificate-authenticated listener: the CDN reaches it with an SNI that differs from the request host, and a tunnel would change that contract.

Migrate one public vhost first. Accept the change only if, measured from an external egress, the vhost answers with a valid certificate, the origin no longer answers on its published HTTP ports, and the proxy log still records the real client address. Roll back by restoring the DNS record that points at the origin; the proxy configuration remains valid in both states.

## Consequences and accepted limits

**Inferred, 2026-11-01:** the origin leaves the public DNS and the listening surface shrinks to the origin leg. The costs are a hard availability dependency on the CDN edge, TLS termination at the CDN so the edge reads plaintext, one more component whose failure is invisible to the host's own monitoring, and a migration that is per-vhost, not atomic. Source-based decisions keep working only if the client-address header is trusted, which the 2026-10-18 correction already assumes. The host does not become free of public listeners: the origin leg stays public by design.

## Alternatives considered

**Inferred, 2026-11-01:**

- Keep the direct edge: no new dependency and no change in TLS visibility, but the listening surface cannot be closed when a patch is unavailable.
- Tunnel every listener, including the origin leg and the administrative names: closes the surface completely, breaks the SNI contract of the customer-domain leg, and replaces overlay identity with CDN access policy for administration.
- Tunnel the whole host behind one hostname: fewer DNS records, but it removes per-vhost routing from the proxy and discards an existing, tested configuration.

## Evidence boundary

**Observed, 2026-10-18:** listener bindings, access-list classes and the authenticated origin leg are owner-supplied observations recorded in the private inventory. **Observed, 2026-11-01:** the kernel advisory and the distribution fix status are public; the running kernel of each documented host is recorded in the private inventory. **Unverified, 2026-11-01:** no vhost has been migrated, no tunnel behavior has been measured, and the acceptance criteria above have not been exercised.
