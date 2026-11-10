# Webhooks

A **webhook** is an HTTP request that a third-party service sends *to you*
when something happens. It's the inverse of an API call: instead of you
polling them, they push to you.

## The one idea to take away

A webhook is **untrusted inbound HTTP**. Anyone can POST to your endpoint.
The only thing that proves the request came from the service you expect is
a **signature** — an HMAC over the raw body, computed with a shared secret.

If you don't verify the signature, you've built a free "charge $1000 to
anyone's card" endpoint that the whole internet can call. **Every webhook
receiver must verify the signature before doing anything.**

## How signature verification works

Most providers (Stripe, GitHub, Slack, Square) use the same pattern:

1. You and the provider share a **secret** (set when you configure the
   webhook in their dashboard).
2. On every delivery, the provider computes
   `HMAC-SHA256(secret, raw_body)` and puts the result in a header
   (`Stripe-Signature`, `X-Hub-Signature-256`, `X-Slack-Signature`, etc.).
3. You compute the same HMAC on the raw request body and compare.

```text
Provider:  signature = HMAC-SHA256(secret, raw_body)
You:       expected  = HMAC-SHA256(secret, raw_body)
           if signature != expected: reject (401)
```

**The raw body matters.** If your framework parses the JSON first and then
you re-serialize it to compute the HMAC, the bytes will differ (whitespace,
key order) and the signature won't match. You must capture the raw bytes
**before** any parsing.

FastAPI gives you `await request.body()` for exactly this.

## The three things every webhook receiver must do

1. **Verify the signature.** Reject anything that doesn't match.
2. **Be idempotent.** Providers retry. The same event will arrive more
   than once. Use the provider's event ID as the idempotency key (this is
   exactly the pattern from `16-idempotency/`).
3. **Respond fast.** Return 200 within ~5 seconds. Do the actual work in
   a background job (`11-background-jobs/`). If you're slow, the provider
   assumes failure and retries — which you then have to dedupe.

**The rule:** `webhook receiver = verify → enqueue → return 200`. The
handler should be ~20 lines and finish in milliseconds.

## Lesson

`01-fastapi-webhook/` — a FastAPI receiver that:
- Computes and verifies an HMAC signature over the raw body
- Uses the event ID as an idempotency key
- Stores the event and returns 200

The README includes a sender script so you can generate valid (and
deliberately invalid) requests locally.

## Where this fits in real code

- **Stripe** — `charge.succeeded`, `invoice.paid`, `customer.created`.
  The backbone of most payment integrations.
- **GitHub** — `push`, `pull_request`, `issues`. Used by CI, bots, and
  notification systems.
- **Slack** — slash commands and interactive components are HTTP POSTs
  with an HMAC signature.
- **OpenAI** — batch completion webhooks (newer).
- **Any SaaS** — "notify us when X happens" is the universal webhook.

## What this lesson does not cover

- **Signature timestamp checks.** Stripe includes a timestamp in the
  signed payload so old requests can't be replayed. Real receivers should
  reject signatures older than 5 minutes.
- **Multiple secrets (rotation).** When you rotate a secret, the receiver
  must accept both old and new during the rollover. Production systems
  check both.
- **Replay prevention beyond idempotency.** Idempotency keys stop
  duplicate processing, but they don't stop an attacker who captured a
  valid request and replays it. The timestamp check handles that.
- **Retry / timeout behavior.** Providers retry with exponential backoff
  and give up after N hours. Your receiver has to be idempotent for
  exactly this reason — covered in `16-idempotency/`.

The mechanism here — HMAC + raw body + idempotency key — is the seed of
all of them.

---

## In another language?

HMAC verification is universal. The header name and the signing string
change per provider, but the pattern is identical:

| Language | HMAC library | Header to expect (Stripe) |
|---|---|---|
| Python | `hmac` + `hashlib` (stdlib) | `Stripe-Signature` |
| Go | `crypto/hmac` + `crypto/sha256` | same |
| Rust | `hmac` crate | same |
| Node | `crypto.createHmac` | same |
| PHP | `hash_hmac` | same |
| Ruby | `OpenSSL::HMAC` | same |
| Java | `javax.crypto.Mac` | same |
| C# | `System.Security.Cryptography.HMACSHA256` | same |

Every one of them is: `HMAC-SHA256(secret, raw_body)`, compare to header,
reject on mismatch. If you understand why the raw body matters, you can
verify any provider's signature in any language.