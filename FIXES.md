# FIXES

### Fix 1
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** Redis host hardcoded as `localhost` — fails in Docker network where Redis runs as a named service
- **Fix:** Changed to use `os.environ["REDIS_HOST"]` with no fallback — since all services communicate over a named internal network, `localhost` is never valid and a fallback would silently mask a misconfiguration

### Fix 2
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** Redis connection does not use a password, but `REDIS_PASSWORD` is defined in `.env` — unauthenticated connection will be rejected if Redis requires a password
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to the `redis.Redis(...)` call

### Fix 3
- **File:** `api/main.py`
- **Line:** 13
- **Problem:** Job pushed to queue key `"job"` (singular), but worker pops from `"jobs"` (plural) — jobs are never picked up by the worker
- **Fix:** Changed `r.lpush("job", job_id)` to `r.lpush("jobs", job_id)`

### Fix 4
- **File:** `worker/worker.py`
- **Line:** 6
- **Problem:** Redis host hardcoded as `localhost` — fails in Docker network
- **Fix:** Changed to use `os.environ["REDIS_HOST"]` with no fallback — same reasoning as Fix 1

### Fix 5
- **File:** `worker/worker.py`
- **Line:** 6
- **Problem:** Redis connection does not use a password — same issue as Fix 2, unauthenticated connection rejected when Redis requires auth
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to the `redis.Redis(...)` call

### Fix 6
- **File:** `worker/worker.py`
- **Line:** 14–18
- **Problem:** `signal` module is imported but no signal handlers are registered — the worker cannot be stopped gracefully (e.g. `SIGTERM` from Docker) and will be killed hard, potentially mid-job
- **Fix:** Added `SIGTERM`/`SIGINT` handlers that set a shutdown flag so the loop exits cleanly after finishing the current job

### Fix 7
- **File:** `worker/worker.py`
- **Line:** 14–18
- **Problem:** Bare `while True` loop has no exception handling — any Redis error or unexpected exception crashes the entire worker process permanently
- **Fix:** Wrapped the loop body in a `try/except` block to log errors and continue

### Fix 8
- **File:** `frontend/app.js`
- **Line:** 6
- **Problem:** API URL hardcoded as `http://localhost:8000` — fails in Docker where the API runs as a named service on an internal network
- **Fix:** Changed to use `process.env.API_URL` with no fallback — since the API always runs as a named service on an internal network, a `localhost` fallback would silently mask a missing environment variable

### Fix 9
- **File:** `api/main.py`
- **Line:** 10
- **Problem:** Redis port was hardcoded as the integer `6379` — not configurable via environment and would silently ignore any non-default Redis port
- **Fix:** Changed to `int(os.environ["REDIS_PORT"])` — explicit, required, and cast to int since `os.environ` always returns strings

### Fix 10
- **File:** `worker/worker.py`
- **Line:** 6
- **Problem:** Same hardcoded Redis port issue as Fix 9
- **Fix:** Changed to `int(os.environ["REDIS_PORT"])`

### Fix 11
- **File:** `api/main.py`
- **Line:** 23–24
- **Problem:** `get_job` returned `{"error": "not found"}` with HTTP 200 when a job doesn't exist — callers have no way to distinguish a missing job from a successful response without inspecting the body
- **Fix:** Changed to `raise HTTPException(status_code=404, detail="Job not found")` so the correct HTTP semantics are used

### Fix 12
- **File:** `worker/worker.py`
- **Line:** 17
- **Problem:** `process_job` jumped straight from `queued` to `completed` with no intermediate state — the frontend would never show a `processing` status, making it impossible to distinguish a job that hasn't started from one actively being worked on
- **Fix:** Added `r.hset(f"job:{job_id}", "status", "processing")` before the sleep

### Fix 13
- **File:** `frontend/app.js`
- **Line:** 7–10
- **Problem:** If `API_URL` env var is missing the app would start silently and every request would fail with a cryptic error — no indication of the root cause
- **Fix:** Added a startup guard that logs a clear error and calls `process.exit(1)` if `API_URL` is not set

### Fix 14
- **File:** `frontend/app.js`
- **Line:** 29–30
- **Problem:** Error handlers always returned HTTP 500 with `"something went wrong"` regardless of the upstream status — a 404 from the API (job not found) would reach the client as a 500 with a generic message, masking the real error
- **Fix:** Proxied the upstream status code with `err.response?.status || 500` and mapped 404 specifically to `"job not found"` for a meaningful client response

### Fix 15
- **File:** `api/.env`
- **Line:** 1–2
- **Problem:** Real secret (`REDIS_PASSWORD=supersecretpassword123`) committed directly to the repository — this is a critical security violation; secrets must never be in version control
- **Fix:** Deleted `api/.env`, created a root-level `.env.example` with placeholder values, and updated `.gitignore` with `.env*` / `!.env.example` to catch all `.env` variants while keeping `.env.example` tracked
