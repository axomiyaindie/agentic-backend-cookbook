# ─────────────────────────────────────────────────────────────
# Multi-stage Dockerfile for a FastAPI lesson.
#
# Copy this file into any lesson folder and change ONE line
# (the port at the bottom) to deploy that lesson.
#
#   docker build -t my-app .
#   docker run -p 8000:8000 --env-file .env my-app
#
# Why multi-stage: the build stage installs pip + gcc to compile
# wheels. The runtime stage gets only the installed packages —
# no compiler, no build cache, no source of compromise.
# ─────────────────────────────────────────────────────────────


# ─── Stage 1: build ────────────────────────────────────────
# Install everything needed to build the Python dependencies.
# This stage produces a wheel cache and a virtualenv.
FROM python:3.12-slim AS builder

WORKDIR /build

# Build tools: gcc and libpq-dev are needed by some Python
# packages (psycopg, asyncpg). They are NOT needed at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a self-contained virtualenv we can
# copy into the runtime stage.
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# ─── Stage 2: runtime ──────────────────────────────────────
# Minimal image. No compilers, no pip cache, no build tools.
FROM python:3.12-slim AS runtime

# Create a non-root user. If the app is compromised, the
# attacker cannot escalate to the host.
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy the virtualenv from the build stage.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code. This is the only thing that changes
# between lessons, so it comes last — Docker caches every layer
# above it.
COPY main.py ./
# If the lesson has static files, uncomment:
# COPY client.html ./

# Environment defaults. Override at runtime with --env-file .env
# or -e KEY=value. Never commit real secrets.
ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

# Healthcheck: the orchestrator uses this to know the app is
# ready, not just started. Adjust the path if your lesson has
# no /docs endpoint.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; \
        urllib.request.urlopen('http://127.0.0.1:8000/docs').read() \
        or sys.exit(1)" || exit 1

# CHANGE THIS LINE for each lesson: the module path to the app.
# For main.py in the same folder:  main:app
# For a different port:            --port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]