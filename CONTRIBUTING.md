# Contributing

Thanks for wanting to add a recipe. This cookbook is small on purpose —
every file teaches one idea, and the format is what keeps it readable.

## The recipe format

Every lesson folder must contain:

1. **A `README.md`** with these sections, in this order:
   - `## What you'll learn` — 2–4 bullets, concrete
   - `## How to run` — exact commands, copy-pasteable
   - `## What to look at` — which files to open first, and why
   - `## In another language?` — a short table mapping the concept to Go,
     Rust, PHP, Ruby, Java, C#

2. **A runnable example** — one or two files, not five. If it needs more
   than two files to demonstrate the concept, the concept is too big.

3. **An exercise at the bottom of the code** — a comment block that asks
   the reader to change one thing and observe the result.

## Rules

- **One idea per lesson.** If the README needs "and also…", split it.
- **No frameworks beyond what's needed.** FastAPI, Express, plain
  `net/http` — fine. A meta-framework that hides the concept — not fine.
- **No dependencies you can't explain in one sentence.** If a package
  exists only to save 10 lines, don't add it.
- **Never commit secrets.** No API keys, no `.env` files, no tokens in
  examples. If a lesson needs credentials, use environment variables and
  document them in the README.
- **Code must run.** A PR that adds a lesson without showing the expected
  output in the README will be asked to add one.
- **Two languages, not ten.** The examples are TypeScript and Python
  because those are the easiest to skim. If you want to add a lesson
  in another language, put it in a *separate* subfolder (e.g.
  `01-api-design/01-http-go/`) — don't translate in place.

## Adding a new section

New top-level folders (`06-…`, `07-…`) are welcome if they fit the theme:
**the backend behind AI applications.** Good candidates:

- Rate limiting and backpressure
- Background jobs and queues
- File uploads and storage
- WebSockets and streaming
- Observability (logs, metrics, traces)

Bad candidates for this repo: frontend-only topics, cloud-specific
deployment walkthroughs, framework comparisons.

## Pull request checklist

Before opening a PR, confirm:

- [ ] The lesson runs locally with the exact commands in its README
- [ ] The README has all four required sections
- [ ] The example has an exercise at the bottom
- [ ] No secrets, no `.env`, no API keys committed
- [ ] `git status` is clean after your test run (add lockfiles if generated)
- [ ] One commit per file, or one commit per lesson — no "fix typo" noise

## Reporting problems

If a lesson doesn't run on your machine, open an issue with:
- Your OS and language/runtime versions
- The exact command you ran
- The full error output
- What you expected to happen

The lesson isn't "working" just because it worked on the author's machine.

## License

By contributing, you agree your work is released under the MIT license
(see `LICENSE`).