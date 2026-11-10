# Rate limiting

**Rate limiting** = controlling how many requests a client can make in a
given time window.

## The one idea to take away

Rate limiting is a **defense**, not an optimization.

Caching makes things faster. Rate limiting makes things *survive*. It
answers the question: "what stops one client from using up all the
capacity?"

## Why it matters

- **Abuse prevention** — stops scraping, brute-force login attempts, and
  spam.
- **Fairness** — one noisy client shouldn't starve everyone else.
- **Cost control** — if your backend calls a paid AI model, an unlimited
  endpoint is an unlimited bill.
- **Stability** — protects downstream services from a traffic spike.

## The three common algorithms

| Algorithm | How it works | Trade-off |
|---|---|---|
| **Fixed window** | N requests per calendar minute/hour | Simple, but allows a burst at the boundary (30 requests at :59, 30 at :00 = 60 in 2 seconds) |
| **Sliding window** | N requests per rolling window | Smoother, slightly more state to track |
| **Token bucket** | Bucket refills at a steady rate; each request takes one token | Allows controlled bursts; the most common production choice |

For a first lesson, fixed window is enough to understand the concept.
Production systems usually use token bucket or sliding window.

## What you actually return

When a client is over the limit, return **HTTP 429 Too Many Requests**
and include headers so the client knows when to retry:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000030
```

Without these headers, the client can only guess. With them, the client
can back off intelligently.

## Keying — who is the "client"?

Rate limits apply to a **key**. The choice of key determines what the
limit actually protects:

| Key | Protects | Weakness |
|---|---|---|
| **IP address** | Anonymous endpoints (login, signup) | NAT means one user behind a shared IP affects others |
| **User ID** | Authenticated APIs | Requires auth first |
| **API key** | Third-party integrations | Each key gets its own quota |
| **Endpoint + IP** | Fine-grained per-resource limits | More state to track |

Most production systems layer these: a per-IP limit on `/login`, a
per-user limit on `/api/*`, and a global limit on outbound model calls.

## Lesson

`01-fastapi-rate-limit/` — a single-file FastAPI app with a custom
in-memory rate limiter. No third-party library needed, so you can see
the mechanism instead of just calling `@limiter.limit("5/minute")`.

## Where this fits in real code

- **nginx / Caddy** — reverse-proxy rate limiting at the edge
- **Cloudflare / Fastly** — provider-level DDoS + rate limiting
- **API gateways** (Kong, Traefik, AWS API Gateway) — centralized policies
- **Application level** (this lesson) — per-user, per-tenant, per-endpoint rules

Real systems usually combine several layers. This lesson shows the
application-level one because that's the layer you write.

---

## In another language?

Rate limiting is universal. Every language has a way to count requests
per key in a time window:

| Language | Common library / pattern |
|---|---|
| Go | `golang.org/x/time/rate` (token bucket) |
| Rust | `governor` crate |
| PHP | `symfony/rate-limiter` |
| Ruby | `rack-attack` |
| Java | Bucket4j, Resilience4j |
| C# | `AspNetCore.RateLimiter` (built-in since .NET 7) |

The mechanism is always: store a counter per key, check it on each
request, reject when the counter exceeds the limit. Redis is the usual
shared store when you have multiple server processes.
```