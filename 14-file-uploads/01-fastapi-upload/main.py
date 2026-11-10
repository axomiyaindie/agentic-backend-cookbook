# ─────────────────────────────────────────────────────────────
# Lesson: buffered vs streamed file uploads
#
# Two endpoints, same result, different memory:
#   POST /upload/buffered  -> await file.read()      (whole file in RAM)
#   POST /upload/streamed  -> while chunk := read(N) (chunk at a time)
#
# Both write the file to ./uploads/ and return the same JSON.
# Only the memory profile is different.
# ─────────────────────────────────────────────────────────────

import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="File upload lesson")

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_BYTES = 10 * 1024 * 1024          # 10 MB — small, so testing is fast
CHUNK_SIZE = 1024 * 1024              # 1 MB per chunk
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".txt", ".bin", ".webp"}


# ── Validation ──────────────────────────────────────────────
# What we CAN do cheaply: check extension and declared size.
# What we CAN'T do cheaply: verify the actual bytes match the
# extension. A file named photo.jpg can contain a PDF or a shell
# script. Production should sniff magic bytes, scan with ClamAV,
# and store under a random name — not the client's filename.
def _validate_upload(file: UploadFile):
    if not file.filename:
        raise HTTPException(400, "missing filename")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"extension {ext!r} not allowed")
    # `file.size` reflects the Content-Length header, which the
    # client controls. It's a cheap first filter, not a guarantee.
    if file.size is not None and file.size > MAX_BYTES:
        raise HTTPException(413, f"file too large (max {MAX_BYTES} bytes)")


# Safe filename: strip any directory components the client sent.
# `../../etc/passwd` becomes `passwd`. Production should also
# generate a random name and keep the original as metadata.
def _safe_name(filename: str) -> str:
    return Path(filename).name


# ── The buffered endpoint ───────────────────────────────────
# Everything in one allocation. Simple, and wrong at scale.
@app.post("/upload/buffered")
async def upload_buffered(file: UploadFile = File(...)):
    _validate_upload(file)

    content = await file.read()       # <-- whole file into RAM
    if len(content) > MAX_BYTES:
        raise HTTPException(413, f"file too large (max {MAX_BYTES} bytes)")

    dest = UPLOAD_DIR / _safe_name(file.filename)
    dest.write_bytes(content)

    return {
        "status": "saved",
        "bytes": len(content),
        "filename": dest.name,
        "method": "buffered",
    }


# ── The streamed endpoint ───────────────────────────────────
# Read a chunk, write a chunk, forget the chunk. Memory stays
# near CHUNK_SIZE no matter how big the file is.
@app.post("/upload/streamed")
async def upload_streamed(file: UploadFile = File(...)):
    _validate_upload(file)

    dest = UPLOAD_DIR / _safe_name(file.filename)
    total = 0

    with dest.open("wb") as out:
        while True:
            chunk = await file.read(CHUNK_SIZE)   # <-- 1 MB at a time
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                # Abort mid-stream if the client lied about size.
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, f"file too large (max {MAX_BYTES} bytes)")
            out.write(chunk)

    return {
        "status": "saved",
        "bytes": total,
        "filename": dest.name,
        "method": "streamed",
    }


# ── Debug helpers ───────────────────────────────────────────
@app.get("/uploads")
def list_uploads():
    return [
        {"name": p.name, "size": p.stat().st_size}
        for p in sorted(UPLOAD_DIR.iterdir())
        if p.is_file()
    ]


@app.delete("/uploads/{name}")
def delete_upload(name: str):
    path = UPLOAD_DIR / _safe_name(name)
    if not path.is_file():
        raise HTTPException(404, "no such file")
    path.unlink()
    return {"deleted": path.name}


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Make a 50 MB test file (see the README for the command).
#   2. Start the server and record its PID:
#        Get-NetTCPConnection -LocalPort 8014 -State Listen
#   3. Upload to /upload/buffered. Watch memory:
#        Get-Process -Id <pid> | Select-Object WorkingSet64
#      It jumps by ~file size (50 MB).
#   4. Upload to /upload/streamed. Memory stays flat (~1 MB rise).
#   5. Both endpoints returned 200, and the file on disk is
#      identical. Only the memory profile is different.
#
#   Try it with a bigger file to see the difference clearly.
#   On a small machine, /upload/buffered with 500 MB will
#   actually crash the server — that's the lesson.
# ─────────────────────────────────────────────────────────────