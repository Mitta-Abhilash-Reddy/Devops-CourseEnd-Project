# Image Comparison and Justification

## Comparison table (measured locally, Docker 29.4, `--no-cache` builds)

| Metric | `library-tracker:full` (python:3.12) | `library-tracker:slim` (python:3.12-slim) |
|---|---|---|
| Dockerfile | `Dockerfile.full` | `Dockerfile` |
| Base image size | 1.62 GB | 180 MB |
| Final image size | **1.61 GB** | **187 MB** (about 8.6x smaller) |
| Build time (cold cache, base already pulled) | 16 s | 10 s |
| Layers (`docker history`) | 23 | 20 |
| Added by our lines | about 7 MB (pip packages + app) | about 7 MB (same) |

## Which Dockerfile lines cause the differences

- **`FROM python:3.12` vs `FROM python:3.12-slim`** is the only line that differs and it causes essentially all of the gap. The full image is built on Debian `buildpack-deps`, so it carries gcc, make, git, Subversion/Mercurial, `-dev` headers, ImageMagick libs and so on (hundreds of MB of layers, mostly the extra buildpack-deps layers behind the 3 additional layers). The slim image has only Python and the minimal Debian runtime.
- **`RUN pip install --no-cache-dir -r requirements.txt`** adds the same ~7 MB (Flask, Werkzeug, Jinja2, gunicorn) to both. `--no-cache-dir` avoids storing the wheel cache in the layer.
- **`COPY requirements.txt` before `COPY app.py`** is a cache-ordering choice, not a size one: dependency layer is reused when only code changes. Both files share it.
- **`RUN useradd ... USER appuser`** adds a tiny layer and runs as non-root (same in both).
- Build time differs because the full base is about 9x larger to pull, extract and snapshot. The pip step itself took similar time in both. (Base images were pre-pulled for the timing, so a first-time pull would widen the gap.)
- Layer count differs because the full base image has more layers of its own; our own layers are identical.

## Justification: production choice = `python:3.12-slim` (1 page)

I would deploy the **slim** image for the Library Book Tracker.

1. **Size and speed.** 187 MB vs 1.61 GB. Pulls, CI pushes, autoscaling and rollbacks are about 8x faster and use less registry and disk cost. For a college deployment on modest hardware this matters.
2. **Smaller attack surface.** Fewer packages means fewer CVEs to scan, patch and be exposed to. The full image ships compilers, git and dev headers that a running Flask app never uses, and an attacker who gains a shell could use them. Security scanners (Trivy, Docker Scout) report far fewer findings on slim images.
3. **No need for the extras.** The app's dependencies (Flask, gunicorn) are pure Python wheels, so no C compiler is required. SQLite is built into Python. Nothing in the app needs the full toolchain.
4. **Production hygiene.** The image runs gunicorn (not Flask's dev server) as a non-root user, with data kept on a volume (`/data`).
5. **Counter-arguments and answers.**
   - *Slim uses glibc (Debian) not musl,* so it avoids the compatibility pitfalls of Alpine while still being small. That is why I did not choose Alpine.
   - *If a future dependency needs compiling (e.g. a C-extension package), slim can break.* Answer: use a multi-stage build (build wheels in the full image, copy into slim) rather than shipping the full image. The full image remains useful as a development or build stage only.
   - *Debugging tools are missing in slim.* Answer: use `docker exec`/ephemeral debug containers; production images should not carry debug tools.
6. **Trade-off accepted.** Slightly less convenience when adding native dependencies, in exchange for big gains in size, security and delivery speed.

**Decision:** production uses `python:3.12-slim`; the full image is kept only for reference in this comparison.
