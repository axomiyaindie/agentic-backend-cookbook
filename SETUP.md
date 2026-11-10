# Setup

How to get any lesson in this repo running on your machine.

## Clone the repo

```bash
git clone https://github.com/axomiyaindie/agentic-backend-cookbook.git
cd agentic-backend-cookbook
```

That's the only clone step. No submodules, no LFS, no extra repos.

## Prerequisites

| Tool | Version | Used by |
|---|---|---|
| Python | 3.11+ | Most lessons (FastAPI) |
| Node.js | 18+ | `01-api-design/`, `02-mcp-connectors/` |
| Docker | any recent | `20-deploy/` (optional) |

Everything else installs per lesson.

## Running any lesson

Each lesson folder has a `README.md` with a **`## How to run`** section. The pattern is always the same:

```bash
cd <lesson-folder>
pip install -r requirements.txt    # or: npm install
uvicorn main:app --reload --port <PORT>
```

The **port** is different for every lesson so you can run several at once. The ports:

| Section | Port |
|---|---|
| 03-rbac-admin | 8000 |
| 06-caching | 8006 |
| 07-rate-limiting | 8007 |
| 12-streaming | 8012 |
| 13-observability | 8013 |
| 14-file-uploads | 8014 |
| 15-transactions | 8015 |
| 16-idempotency | 8016 |
| 17-websockets | 8017 |
| 18-webhooks | 8018 |
| 19-search | 8019 |
| 10-reference/fastapi-types-example.py | any (e.g. 8020) |

If a port is busy (another lesson, or a leftover process), kill everything first:

```bash
# Windows PowerShell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# macOS / Linux
pkill -f uvicorn
```

Then use `--port <different-number>` for the new lesson.

## Lessons that need no Python

Two lessons run with just Node.js:

```bash
# 01-api-design
cd 01-api-design/01-http-typescript
npx tsx example.ts

# 02-mcp-connectors
cd 02-mcp-connectors/01-minimal-mcp-server
npm install
npx tsx server.ts
```

And two lessons need no dependencies at all:

```bash
# 09-agent-harness
cd 09-agent-harness/01-minimal-harness
python main.py

# 11-background-jobs
cd 11-background-jobs/01-minimal-queue
python main.py
```

(SQLite is built into Python — no install needed.)

## Lessons that need a live database

`04-databases/` has four engines. Each needs a running instance:

| Engine | How to get it |
|---|---|
| Postgres | `docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16` |
| MySQL | `docker run -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8` |
| MongoDB | `docker run -p 27017:27017 mongo:7` |
| DynamoDB | `docker run -p 8000:8000 amazon/dynamodb-local`, then set `DYNAMODB_ENDPOINT=http://localhost:8000` |

Or use `20-deploy/01-docker/docker-compose.yml` — it starts Postgres (with pgvector) and Redis together.

`19-search/` uses SQLite only — no external database needed.

## Testing one lesson

`21-testing/` shows what a test file looks like for the idempotency lesson:

```bash
cd 21-testing/01-pytest-example
pip install -r requirements.txt
pytest -v
```

Should show **4 passed in <1s**.

## Windows notes

- **Use PowerShell or `cmd.exe`.** Git Bash works but has different quoting rules.
- **`curl.exe`, not `curl`.** PowerShell aliases `curl` to `Invoke-WebRequest`, which hides streaming and mangles quotes. Use `curl.exe` for real curl.
- **`Invoke-RestMethod` for JSON bodies.** PowerShell strips quotes from strings passed to native executables, so `curl.exe` with a JSON body fails. `Invoke-RestMethod` works:

  ```powershell
  Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8016/charge `
    -ContentType "application/json" `
    -Headers @{"Idempotency-Key"="key-1"} `
    -Body '{"amount":50,"user":"alice"}'
  ```

- **`cd` to the repo root before any `git` command.** Git paths are relative to your current directory. If you see `fatal: not a git repository` or `pathspec did not match any files`, you're in a subfolder.

## What to do if a lesson fails

1. Re-read the lesson's README — the walkthrough shows exact commands and expected output.
2. Check the port table above — you may be hitting a different lesson's server.
3. Check the Python or Node version — `python --version` should be 3.11+; `node --version` should be 18+.
4. If it still fails, open an issue with:
   - OS and version
   - Python/Node version
   - The exact command you ran
   - The full error output

The lesson's README is the source of truth. If it doesn't work as written, that's a bug — [open an issue](https://github.com/axomiyaindie/agentic-backend-cookbook/issues).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the recipe format every lesson follows.
```

**Save, close.**

---

## FILE 3 of 3 — append to `CONTRIBUTING.md`

The contributing guide already exists and is correct. Just add one section at the end that points at `SETUP.md`:

**Open it:**
```powershell
code CONTRIBUTING.md
```

**Scroll to the bottom.** Find the last line:
```
MIT — see `LICENSE`.
```

**Add after it:**

```

## Local setup

See [`SETUP.md`](SETUP.md) for clone instructions, per-lesson ports, and Windows notes. Every lesson README has its own `## How to run` section that overrides anything here if there's a conflict.
```

**Save, close.**

---

## Commit all three

```powershell
cd D:\agentic-backend-cookbook
git add README.md SETUP.md CONTRIBUTING.md
git commit -m "Restructure README as navigation index; move setup to SETUP.md"
git push
```

---

## What changed and why

| Before | After |
|---|---|
| README had ~450 lines with per-lesson walkthroughs | README has ~280 lines, **pure navigation** — every file linked, no duplicated content |
| No setup file; clone/install info scattered in lesson READMEs | `SETUP.md` is the single place for "how do I run this" — ports table, Windows notes, database setup |
| CONTRIBUTING didn't mention setup | One-line pointer to `SETUP.md` |
| Root README duplicated lesson content that could go stale | Single source of truth: each lesson's README |

The rule you stated — "README should just link to each folder/project; setup goes in SETUP.md; contribute goes in CONTRIBUTING.md" — is now the structure.
