# Deploy

Everything else in this cookbook runs on `localhost`. This lesson is
about getting it off your laptop and onto the internet.

## The one idea to take away

Deployment is **not** a single step. It's a chain of concerns, and
getting any one wrong means your app is down:

1. **Container** — package the app so it runs the same on every machine
2. **Config** — secrets and settings, not hardcoded, not committed
3. **Database** — a real database, not SQLite-on-a-temp-disk
4. **Reverse proxy** — terminate HTTPS, route requests, serve static files
5. **Process supervision** — restart the app when it crashes
6. **Logs** — you can't debug what you can't see
7. **Backups** — the database dies, and you need it back

This lesson focuses on the **first three** (container, config, database)
because they're the parts that need files in your repo. The rest are
provider-specific and vary by cloud.

## The Dockerfile — package once, run anywhere

The lesson's `Dockerfile` builds a minimal image that runs **one**
FastAPI app. It's written so you can copy it into any lesson folder and
change one line (the port) to deploy that lesson.

Three principles:

**1. Multi-stage build.** Build dependencies (pip, gcc) don't belong in
the final image. The build stage installs them, the runtime stage gets
only the installed packages.

**2. Non-root user.** The container runs as `appuser`, not `root`. If the
app is compromised, the attacker can't escalate to the host.

**3. Healthcheck.** The orchestrator (Docker, Kubernetes, Cloud Run) uses
this to know when the app is actually ready, not just started.

## The docker-compose.yml — local dev with the full stack

A single command brings up:

- the FastAPI app
- Postgres (for the database lessons)
- Redis (for the caching lesson)

`docker compose up` and everything works. `docker compose down` and it's
all gone. That's the "it works on my machine" problem solved.

## Config — never hardcode, never commit

Every lesson in this cookbook reads secrets from environment variables:

```python
SECRET = os.environ.get("WEBHOOK_SECRET", "dev-secret")
```

The `dev-secret` fallback is fine for local dev. In production, the env
var is set by the platform (Cloud Run, Railway, Fly.io, Railway) and the
fallback is never used.

**The three rules:**

1. **Never commit `.env`** — it's in `.gitignore`.
2. **Never log secrets** — log `"api_key set"`, not the key.
3. **Fail loudly in production if a required env var is missing** — better
   a crash than a silently broken webhook verifier.

## The database — SQLite is not production

Every lesson in this cookbook uses SQLite because it's zero-setup. In
production:

- **SQLite on a single server** is actually fine for small apps — but it
  doesn't scale across processes, and backup is manual.
- **Postgres** is the default for anything real. Managed Postgres from
  any cloud provider is a good choice.
- **The migration path from SQLite to Postgres** is mostly one line
  (change the connection string) for the database lessons here, because
  they use parameterised queries that work on both.

## What this lesson does not cover

- **Kubernetes.** Overkill for the scale these examples target. When
  you need it, you'll know.
- **CI/CD pipelines.** GitHub Actions can build and push the Docker
  image; that's a separate lesson.
- **CDN / static files.** The lesson serves nothing static; if your app
  does, put it behind Cloudflare or a similar CDN.
- **Domain and DNS.** Set up when you have a provider.
- **Monitoring and alerting.** `13-observability/` covers logs; metrics
  and alerts are the next layer.

## Where this fits in real code

- **Dockerfile** — every cloud provider accepts a container. Learn it
  once, use it everywhere.
- **docker-compose** — local development, integration tests, small
  self-hosted deployments.
- **Fly.io / Railway / Render** — deploy a Dockerfile with one command.
- **Cloud Run / App Runner / Container Apps** — serverless containers,
  scale to zero, pay per request.
- **VPS + Dokploy / Coolify** — self-hosted PaaS on a $5/mo box. Good
  for learning the whole stack.

## Lesson

`01-docker/` contains:

- `Dockerfile` — copy-paste template for any lesson
- `docker-compose.yml` — the local full-stack setup
- `.dockerignore` — what not to send to the build context

None of them run a "lesson" per se — they deploy one. The exercise is to
run one of the existing lessons (RBAC, transactions, idempotency) inside
the container.

---

## In another language?

Docker is language-agnostic. The Dockerfile changes per language, but the
principles (multi-stage, non-root, healthcheck) are the same:

| Language | Base image | Install step |
|---|---|---|
| Python | `python:3.12-slim` | `pip install -r requirements.txt` |
| Node | `node:20-alpine` | `npm ci --omit=dev` |
| Go | `golang:1.22-alpine` (build) → `scratch` (run) | `go build` |
| Rust | `rust:1.79-slim` (build) → `debian:bookworm-slim` (run) | `cargo build --release` |
| Java | `maven:3.9-eclipse-temurin-21` (build) → `eclipse-temurin:21-jre` (run) | `mvn package` |
| PHP | `php:8.3-fpm-alpine` | `composer install --no-dev` |
| Ruby | `ruby:3.3-slim` | `bundle install --without development` |
| C# | `mcr.microsoft.com/dotnet/sdk:8.0` (build) → `aspnet:8.0` (run) | `dotnet publish -c Release` |

The multi-stage pattern is what makes each of them small. A naive Go
image is 900 MB; the multi-stage version is 10 MB.