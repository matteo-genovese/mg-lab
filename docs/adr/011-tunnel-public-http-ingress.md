# 011 · Move public HTTP ingress behind an outbound tunnel, one vhost at a time

Status: **Accepted** · Decision date: **2026-11-01** · Implementation date: **2026-11-01**

## Context

**Observed, 2026-10-18:** the production host publishes the proxy on all interfaces for HTTP and HTTPS, and publishes a second HTTPS listener for the customer-domain origin leg, protected by the CDN's Authenticated Origin Pulls ([ADR 007](007-authenticated-origin-leg.md)). Administrative names behind the proxy are reachable only by tailnet sources; the proxy administration port and the agent port are bound to the overlay.

**Inferred, 2026-11-01:** a published listener is the one surface that a patch shortage cannot narrow. The October 2026 remote use-after-free in the IPv4 TCP handshake, CVE-2026-98432, is the instance: while distribution kernels lag, an operator whose host publishes no reachable listener can remove the exposure by closing a port, and an operator who must keep the listener open can only wait for the vendor. Blocking after accept ([ADR 009](009-proxy-edge-blocking.md)) does not help here, because the flaw is reached before any application-level decision.

## Decision

**Accepted, 2026-11-01:** for public HTTP and HTTPS vhosts, replace inbound listeners with an outbound-only tunnel to the CDN edge, so that the origin publishes no HTTP port. Keep the customer-domain origin leg on its current direct, certificate-authenticated listener: the CDN reaches it with an SNI that differs from the request host, and a tunnel would change that contract.

Migrate one public vhost first. Accept the change only if, measured from an external egress, the vhost answers with a valid certificate, the origin no longer answers on its published HTTP ports, and the proxy log still records the real client address. Roll back by restoring the DNS record that points at the origin; the proxy configuration remains valid in both states.

## Implementation, 2026-11-01

**Observed:** ten public hostnames across three zones answer through one named tunnel with four connections; every one of them was measured from an external egress with the expected status code, and the proxy log records the real client addresses rather than a loopback source. The migration ran in two batches after a single pilot hostname, because the acceptance criteria were met on the pilot within minutes.

**Observed:** the tunnel reaches the proxy over loopback with the public hostname as SNI. The proxy rejects an unknown SNI with a handshake failure rather than serving a default vhost; the tunnel therefore states the origin name explicitly for each hostname. Without it the pilot returned an edge error for roughly twenty-five seconds.

**Observed:** the HTTP listener was closed on 2026-11-01 by binding it to loopback. The precondition was the certificate migration: five certificates, each a wildcard plus its apex, renewed by DNS validation only. No vhost was left on HTTP-01, so no renewal needed the public HTTP listener. Before this change the same listener was the last reason to keep the port open.

**Observed:** the HTTPS listener stays published, and it is the only one that still has to. It serves the customer-domain origin leg; the CDN reaches that leg on the published port by design.

**Observed:** a second HTTPS listener, published by an application container outside the proxy stack, accepts connections and answers no protocol on them, from the public side and from loopback. It is a leftover of an earlier TLS configuration in that stack. Removal is pending because the stack is defined in the container panel's own store, not in a file on the host.

**Observed, and the migration's main surprise:** the proxy omits the TLS server block for a vhost whose certificate does not cover that vhost's own name exactly. A wildcard certificate does not cover its apex, so a hostname served by a wildcard-only certificate silently loses its HTTPS block at the next configuration regeneration, and keeps answering only because the running configuration predates it. Two production names were in that state. Certificates are therefore issued as wildcard **plus** apex, and every regenerated vhost is checked for its TLS block before the change is considered done.

**Observed:** administrative names stay on their access-list path and are not tunnelled. Traffic arriving through the tunnel reaches the proxy from loopback, so a source-based allow list would deny it; the same reason keeps the overlay-only administration binding as is.

## Consequences and accepted limits

**Inferred, 2026-11-01:** the origin leaves the public DNS and the listening surface shrinks to the origin leg. The costs are a hard availability dependency on the CDN edge, TLS termination at the CDN so the edge reads plaintext, one more component whose failure is invisible to the host's own monitoring, and a migration that is per-vhost, not atomic. Source-based decisions keep working only if the client-address header is trusted, which the 2026-10-18 correction already assumes. The host does not become free of public listeners: the origin leg stays public by design.

**Observed:** the tunnel connector is one more process with its own update cycle, and a failure in it looks like an edge error, not like a host failure. Availability is therefore inferred from the public endpoints, which are monitored, rather than from the host.

## Alternatives considered

**Inferred, 2026-11-01:**

- Keep the direct edge: no new dependency and no change in TLS visibility, but the listening surface cannot be closed when a patch is unavailable.
- Tunnel every listener, including the origin leg and the administrative names: closes the surface completely, breaks the SNI contract of the customer-domain leg, and replaces overlay identity with CDN access policy for administration.
- Tunnel the whole host behind one hostname: fewer DNS records, but it removes per-vhost routing from the proxy and discards an existing, tested configuration.

## Evidence boundary

**Observed, 2026-10-18:** listener bindings, access-list classes and the authenticated origin leg are owner-supplied observations recorded in the private inventory. **Observed, 2026-11-01:** the kernel advisory and the distribution fix status are public; the running kernel of each documented host, the tunnel inventory, the certificate set and the post-change port scan are recorded in the private inventory and validation log. **Verified, 2026-11-01:** all migrated hostnames answer with a valid certificate from an external egress, the HTTP listener no longer answers from outside, and every remaining certificate completes a simulated renewal.
