# hng14-stage2-devops

A job processing system made up of three services — a frontend, an API, and a worker — orchestrated with Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) v24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2.20+ (included with Docker Desktop)
- Git

Verify your installation:

```bash
docker --version
docker compose version
```

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/AmosSpark/hng14-stage2-devops.git
cd hng14-stage2-devops
```

**2. Create your environment file**

```bash
cp .env.example .env
```

Open `.env` and set a strong value for `REDIS_PASSWORD`. All other defaults work out of the box.

**3. Build and start the stack**

```bash
docker compose up --build -d
```

**4. Verify all services are healthy**

```bash
docker compose ps
```

All four services (`redis`, `api`, `worker`, `frontend`) should show `healthy` before the frontend becomes reachable.

## Accessing the App

Once all services are healthy, open your browser at:

```
http://localhost:3000
```

## What a Successful Startup Looks Like

Running `docker compose ps` should show:

```
NAME                STATUS
project-redis-1     Up X seconds (healthy)
project-api-1       Up X seconds (healthy)
project-worker-1    Up X seconds (healthy)
project-frontend-1  Up X seconds (healthy)
```

> **Note:** The worker has no HTTP server — its health check verifies Redis connectivity directly.

You can also check service logs:

```bash
docker compose logs -f
```

Expected log output per service:

- **redis** — `Ready to accept connections`
- **api** — `Application startup complete`
- **worker** — `Processing job ...` / `Done: ...` as jobs are picked up
- **frontend** — `Frontend running on port 3000`

To submit a job, click **Submit New Job** on the dashboard. The job will move through `queued → processing → completed` and update in real time.

## API Endpoints

All endpoints return `Content-Type: application/json` and HTTP `200`.

| Endpoint         | Method | Response                                                          |
| ---------------- | ------ | ----------------------------------------------------------------- |
| `/health`        | GET    | `{"status": "healthy"}`                                           |
| `/jobs`          | POST   | `{"job_id": "<uuid>"}`                                            |
| `/jobs/{job_id}` | GET    | `{"job_id": "<uuid>", "status": "queued\|processing\|completed"}` |

## CI/CD Pipeline

The pipeline runs on GitHub Actions on every push:

`lint → test → build → security scan → integration test`

- **Lint** — flake8 (Python), eslint (JavaScript), hadolint (Dockerfiles)
- **Test** — pytest with Redis mocked, coverage report uploaded as artifact
- **Build** — all three images built, tagged with git SHA and latest, pushed to local registry
- **Security** — Trivy scans all images, fails on CRITICAL findings
- **Integration** — full stack brought up, job submitted and polled until completed

## Bug Fixes

All bugs found in the original source code are documented in [FIXES.md](./FIXES.md).

## Stopping the Stack

```bash
docker compose down
```

To also remove volumes:

```bash
docker compose down -v
```
