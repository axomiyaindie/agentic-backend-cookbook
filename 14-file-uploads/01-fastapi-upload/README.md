# FastAPI upload

Two endpoints that do the same thing — store an uploaded file — but use
different amounts of memory.

## What you'll learn
- How `UploadFile` exposes the incoming bytes
- The difference between `await file.read()` (buffers) and `await file.read(N)` (streams)
- How to measure the memory difference with `Get-Process` (Windows) or `ps` (macOS/Linux)
- Why size and extension checks are necessary but not sufficient

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8014
```

Using port 8014 so it doesn't collide with the SSE lesson on 8012 or
observability on 8013. Both can run at once.

## What to look at
- `main.py` — the two endpoints are deliberately parallel. Read
  `/upload/buffered` first, then `/upload/streamed`. The only difference
  is inside the `while` loop.
- `_validate_upload()` — the size and extension checks. Note the comment
  about why these are not enough on their own.

## Walkthrough — prove it works

**Step 1: Make a 50 MB test file**

Windows PowerShell:
```powershell
$bytes = New-Object byte[] (50 * 1024 * 1024)
[System.Random]::new().NextBytes($bytes)
[System.IO.File]::WriteAllBytes("$env:TEMP\test-50mb.bin", $bytes)
```

That creates a 50 MB random binary file. It's not a valid image or PDF,
so the upload will need to bypass the extension check — or you can
rename it to `.pdf` if you prefer. For the memory comparison, the content
doesn't matter.

macOS/Linux:
```bash
head -c 50M /dev/urandom > /tmp/test-50mb.bin
```

**Step 2: Start the server**

```powershell
cd D:\agentic-backend-cookbook\14-file-uploads\01-fastapi-upload
uvicorn main:app --reload --port 8014
```

**Step 3: Watch memory while uploading (buffered — the bad way)**

Open a **second** PowerShell:

```powershell
# Note the server's PID
Get-NetTCPConnection -LocalPort 8014 -State Listen | Select-Object OwningProcess
```

Then upload the 50 MB file:

```powershell
curl.exe -X POST -F "file=@$env:TEMP\test-50mb.bin" http://127.0.0.1:8014/upload/buffered
```

While it runs, check the server's memory:

```powershell
Get-Process -Id <server-pid> | Select-Object Id, WorkingSet64
```

**You should see WorkingSet64 jump by ~50 MB during the request.** The
whole file was held in memory.

**Step 4: Upload the same file to `/upload/streamed`**

```powershell
curl.exe -X POST -F "file=@$env:TEMP\test-50mb.bin" http://127.0.0.1:8014/upload/streamed
```

Watch memory again. **It should stay near the baseline** — memory only
goes up by the chunk size (~1 MB), not the file size (50 MB).

The two responses are identical:
```json
{"status": "saved", "bytes": 52428800, "filename": "test-50mb.bin", "method": "buffered"}
{"status": "saved", "bytes": 52428800, "filename": "test-50mb.bin", "method": "streamed"}
```

**Same output. Different memory. That's the whole lesson.**

**Step 5: Prove the difference is real**

Try a bigger file. Generate a 500 MB file (or skip if disk space is tight):

```powershell
$bytes = New-Object byte[] (500 * 1024 * 1024)
[System.Random]::new().NextBytes($bytes)
[System.IO.File]::WriteAllBytes("$env:TEMP\test-500mb.bin", $bytes)
```

Upload to `/upload/buffered`. Watch memory hit ~500 MB. On a small
machine, the server might crash. Upload to `/upload/streamed`. Memory
stays flat.

**That's why streaming exists.** Not because it's faster — it's often
slower because it does more small I/O operations. Because it uses less
memory, which means it survives.

## The trade-off: speed vs memory

Streaming isn't free:

| | Buffered | Streamed |
|---|---|---|
| Peak memory | ~file size | ~chunk size |
| Total time | Slightly faster | Slightly slower |
| Survives 10 concurrent uploads of 500 MB | No | Yes |
| Survives one upload of 2 GB | No | Yes |

The 1 MB chunk size in `main.py` is a tuning knob. Smaller chunks use
less memory but do more I/O operations. 1 MB is a reasonable default;
it's what most file-copying tools use.

## What the validation does (and doesn't) catch

The `_validate_upload()` function in `main.py` checks:

- **File size** — against `MAX_BYTES` (default 10 MB for this lesson).
  Rejects early. But the size check trusts the `Content-Length` header,
  which the client controls — so the real check is the `while` loop that
  aborts after `MAX_BYTES`.
- **File extension** — from the filename. Cheap filter. But an attacker
  can rename `evil.exe` to `photo.jpg` and the extension check passes.

What it does **not** catch, but production should:

- **Sniffing actual content** — read the first few bytes and check for
  magic numbers. `image/jpeg` starts with `FF D8 FF`. If it doesn't, the
  file isn't a JPEG no matter what the extension says.
- **Path traversal in filename** — never use the raw client filename in
  a filesystem path. `../../etc/passwd` would overwrite a system file.
  The lesson strips the path to just the base name; production should
  also generate a random name and store the original as metadata.
- **Virus scanning** — uploaded files are untrusted input.

Each of these is a lesson on its own. This one shows the streaming
pattern, which is the hardest to retrofit later.

## Why this pattern is hard to retrofit

Adding streaming to an existing codebase is painful because:

1. **Database writes** — you probably wrote `content = await file.read()`
   then stored `content` in a `BLOB` column. To stream, you'd rewrite
   the DB layer.
2. **Image processing** — you probably did `Image.open(file)` (in-memory)
   then resized. To stream, you'd need `Image.open(file.file)` (the
   underlying file object) and rework the resize.
3. **APIs that expect `bytes`** — many third-party SDKs take `bytes`
   arguments. You can't stream into them without buffering.

So the cost of doing it wrong is paid later, when you discover the
production server can't handle the traffic. Getting it right from the
start costs almost nothing.

---

## In another language?

The comparison is the same everywhere — the question is whether your
framework gives you chunks or the whole body:

| Language | Buffered (bad) | Streamed (good) |
|---|---|---|
| Python | `await file.read()` | `while chunk := await file.read(N): ...` |
| Go | `io.ReadAll(r.Body)` | `io.Copy(dst, r.Body)` |
| Rust | `body.collect().await` | `tokio::io::copy(&mut body, &mut dst).await` |
| Node | `await req.arrayBuffer()` | `req.pipe(createWriteStream(...))` |
| PHP | `file_get_contents('php://input')` | `while (!feof($in)) fread($in, N)` |
| Ruby | `request.body.read` | `request.body.each { \|chunk\| out.write(chunk) }` |
| Java | `in.readAllBytes()` | `in.transferTo(out)` or a `byte[] buf` loop |
| C# | `await reader.ReadToEndAsync()` | `await request.Body.CopyToAsync(fileStream)` |

**Go and Rust are the easiest** — `io.Copy` and `tokio::io::copy` are
the default streaming helpers. **Python and Node are the trickiest**
because their frameworks give you a buffering helper (`await file.read()`,
`await req.arrayBuffer()`) that looks like the obvious thing to call.
The lesson is: recognize that helper as the trap, and use the chunked
form instead.