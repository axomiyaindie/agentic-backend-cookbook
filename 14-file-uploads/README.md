# File uploads

**File uploads** are how a client sends a binary file (image, PDF, video)
to the server. Every AI app eventually needs them — a chat app that
accepts images, a document summarizer that accepts PDFs, an audio
transcriber that accepts voice notes.

## The one idea to take away

**Do not read the whole file into memory.**

The naive way to handle an upload:

```python
content = await file.read()     # loads the ENTIRE file into RAM
```

works fine for a 5 KB text file. It is catastrophic for a 500 MB video:
500 MB of RAM per upload, and if 10 users upload at once, 5 GB of RAM,
and the server crashes.

The right way is to **stream** the file in chunks:

```python
while chunk := await file.read(1024 * 1024):   # 1 MB at a time
    write_to_storage(chunk)
```

That uses 1 MB of RAM per upload regardless of file size. 10 simultaneous
uploads of any size still use 10 MB.

**Same result. 500× less memory. One line of code different.**

## Why this matters more for AI backends

AI workloads are memory-hungry by default — the model itself may use
gigabytes. Adding file buffering on top means the server dies faster.

Real AI upload patterns:

| App | Upload | Why buffering hurts |
|---|---|---|
| Image chat | Photos, 2–10 MB | 10 users → 100 MB buffered |
| PDF summarizer | Documents, 5–50 MB | 1 PDF can be 50 MB in RAM |
| Audio transcription | Voice notes, 10–100 MB | 100 MB audio + model memory = OOM |
| Video analysis | Videos, 100 MB–2 GB | Buffering = instant crash |

For the first three, buffering *sometimes* works. For the fourth, it
never works. Streaming is the only option that scales.

## The three ways to handle an upload

| Approach | Memory | Speed | When to use |
|---|---|---|---|
| **Read whole file into RAM** | File size | Fast | Files under ~10 MB, low concurrency |
| **Stream to disk** | Chunk size | Slower (disk I/O) | Medium files, single-server apps |
| **Stream to object storage** | Chunk size | Slower (network I/O) | Production, S3/GCS/R2 |

Most production AI apps use the third. The second is what this lesson
demonstrates, because it runs locally without any cloud account. The
pattern is identical — only the destination changes.

## What you should validate on every upload

Even before the bytes hit storage:

1. **Size limit.** Reject files over N MB *before* reading them. FastAPI's
   `UploadFile` exposes `file.size` and the raw header `Content-Length`,
   but neither is trustworthy — the client controls it. The real defense
   is to abort the read after N bytes.
2. **Content type.** Check the `Content-Type` header — but also sniff
   the actual bytes. A file named `photo.jpg` can contain a PDF or a
   shell script.
3. **File extension.** Cheap first filter. Not sufficient on its own.
4. **Filename.** Never use the client-supplied filename directly in a
   filesystem path. Path traversal (`../../etc/passwd`) is real.

This lesson demonstrates size limit and extension check, and explains
why each is incomplete on its own.

## Lesson

`01-fastapi-upload/` — a FastAPI server with two endpoints:
- `POST /upload/buffered` — reads the whole file into memory (the
  anti-pattern, for comparison)
- `POST /upload/streamed` — writes in 1 MB chunks (the correct pattern)

Both store the file to `./uploads/`. Both return the same response. The
only difference is memory.

The README walks you through uploading a 50 MB test file and watching
`Get-Process python` memory to see the difference.

## Where this fits in real code

- **Local disk** — fine for small apps, single server. Doesn't scale
  past one machine.
- **S3 / GCS / R2** — production default. The server streams the upload
  straight to the bucket; the file never touches local disk.
- **Presigned URLs** — the best pattern: the client uploads directly to
  S3, the server never sees the file at all. The server just issues a
  short-lived signed URL. This lesson doesn't cover it (it needs AWS),
  but it's worth knowing about.
- **Virus scanning** — uploads are untrusted input. Production scans
  before serving. ClamAV is the common open-source choice.

## What this lesson does not cover

- **Presigned URLs.** The best pattern needs cloud setup. Mentioned above.
- **Chunked resumable uploads.** For huge files (videos), even a single
  request is too long. Resumable protocols (tus, S3 multipart) fix this.
- **Virus scanning.** Production-critical, but needs ClamAV running.
- **CDN delivery.** After upload, the file is served from a CDN, not from
  your Python server.
- **Image processing.** Thumbnails, resizing, EXIF stripping. Pillow does
  this; it's its own lesson.

Each of those is worth its own lesson eventually. The mechanism in this
lesson — stream, don't buffer — is the foundation all of them build on.

---

## In another language?

Streaming uploads is universal. Every language has a way to read a request
body in chunks:

| Language | Chunked read |
|---|---|
| Python | `await file.read(size)` in a loop |
| Go | `io.Copy(dst, r.Body)` (already streams by default) |
| Rust | `tokio::io::copy(&mut body, &mut dest).await` |
| Node | `req.pipe(fs.createWriteStream(path))` |
| PHP | `fopen('php://input', 'r')` + `fread` in a loop |
| Ruby | `request.body.each { |chunk| out.write(chunk) }` |
| Java | `InputStream in = request.getInputStream(); in.read(buf)` |
| C# | `await request.Body.CopyToAsync(fileStream)` |

**Go and Rust are already streaming by default** — `io.Copy` and
`tokio::io::copy` do the right thing. Node and Python require you to
explicitly avoid `await file.read()` / `await req.body()`, because
those helpers buffer.

The lesson is the same in every language: **don't hold the whole file
in memory**. If you understand why, you can do it correctly anywhere.