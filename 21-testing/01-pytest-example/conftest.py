# ─────────────────────────────────────────────────────────────
# Pytest configuration for this folder.
#
# The idempotency lesson lives at ../../16-idempotency/.
# We add it to sys.path so tests can `import main` from there.
#
# We also delete its SQLite file before each test session so the
# tests start from a known state. Real projects use a dedicated
# test database; this cookbook uses SQLite so this is the
# simplest correct thing.
# ─────────────────────────────────────────────────────────────

import sys
from pathlib import Path

# Path to the idempotency lesson
LESSON_DIR = (Path(__file__).parent.parent.parent / "16-idempotency" / "01-fastapi-idempotency").resolve()

# Add it to sys.path so `import main` finds its main.py
sys.path.insert(0, str(LESSON_DIR))

# Remove the lesson's database file so tests always start clean.
# (The lesson's _init_db() will recreate it on import.)
for name in ("idempotency.db", "idempotency.db-journal"):
    p = LESSON_DIR / name
    if p.exists():
        p.unlink()