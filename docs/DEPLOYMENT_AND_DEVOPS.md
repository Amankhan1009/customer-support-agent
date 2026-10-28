# Deployment & DevOps Guide

---

## 1. Multi-Platform Docker Architecture

The application is fully containerized into two decoupled services:
1. **API Backend**: `Dockerfile` (FastAPI service exposing port 8000).
2. **Frontend UI**: `Dockerfile.frontend` (Streamlit service exposing port 8501).

Both images are published to Docker Hub as multi-platform images supporting:
- `linux/amd64` (standard Intel/AMD cloud servers like Render, AWS EC2, GCP Compute Engine).
- `linux/arm64` (Apple Silicon M-series Macs and ARM-based cloud instances like AWS Graviton).

### Published Images:
- **API**: `amankhan1009/customer-support-agent-api:latest`
- **Frontend**: `amankhan1009/customer-support-agent-frontend:latest`

---

## 2. GitHub Actions Automated CI/CD Pipeline (`.github/workflows/ci.yml`)

The repository includes a continuous integration and continuous deployment pipeline triggered on every push or pull request to the `main` branch.

```mermaid
flowchart LR
    Push["git push origin main"] --> TestJob["Job 1: Automated Pytest Suite<br/>(62 unit & regression tests)"]
    TestJob --> BuildJob["Job 2: Multi-Platform Docker Build<br/>(Buildx + QEMU)"]
    BuildJob --> PushHub["Push to Docker Hub<br/>(amd64 + arm64 images)"]
    PushHub --> RenderDeploy["Render Auto-Deploy Webhook<br/>(Roll out live containers)"]
```

### Pipeline Steps:
1. **Testing**: Sets up Python 3.11/3.12, installs all dependencies from `requirements.txt`, and executes `pytest tests/`. If any test fails, the build halts immediately.
2. **QEMU Emulation**: Installs `docker/setup-qemu-action@v3` to support cross-compilation between AMD64 and ARM64.
3. **Docker Buildx**: Initializes `docker/setup-buildx-action@v3` for concurrent multi-architecture building.
4. **Docker Hub Authentication**: Logs into Docker Hub using encrypted repository secrets (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`).
5. **Build & Push**: Builds and pushes both `customer-support-agent-api` and `customer-support-agent-frontend` tagged with both git commit SHA and `latest`.

---

## 3. Local Multi-Container Deployment via Docker Compose

To run the complete stack locally using Docker Compose:

```bash
docker compose up --build
```

### `docker-compose.yml` Configuration:
```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CHECKPOINTER_BACKEND=sqlite
      - DATABASE_PATH=support_checkpoints.db
      - GROQ_API_KEY=${GROQ_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-local-secret-key}
    volumes:
      - ./data:/app/data

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
```

---

## 4. Cloud Deployment on Render & Neon PostgreSQL

### 4.1 Production Managed Database (Neon Serverless PostgreSQL)
In production, persistence runs on a managed PostgreSQL cluster provided by Neon:
1. Provision a Neon PostgreSQL database.
2. Retrieve the pooled connection string:
   ```text
   postgresql://username:password@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Set backend environment variables on Render:
   - `CHECKPOINTER_BACKEND=postgres`
   - `DATABASE_URL=postgresql://username:password@ep-xyz-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require`

### 4.2 Handling Render Free-Tier Cold Starts
Render free-tier web services automatically spin down into a sleeping state after 15 minutes of inactivity. The first inbound request takes 30–50 seconds while the container initializes.

To provide an optimal user experience:
1. **Frontend Health Probe**: The Streamlit frontend issues a non-blocking 2.5-second health check to `/health` on startup. If the backend is sleeping, it displays a status badge: `🔴 Server Sleeping`.
2. **"⚡ Wake Up Backend" Button**:
   - The user can click the button to trigger a 65-second keepalive request to `/health`.
   - An active spinner informs the user: *"Waking up backend on Render... Free tier instances take ~30–50s to start."*
3. **Synchronized UI Re-render**:
   - Upon receiving HTTP 200, the session status updates to `🟢 Backend Online`.
   - The frontend immediately executes `st.rerun()`, simultaneously updating the status indicator in both the sidebar and the main login view.

---

## 5. Production Environment Variables Reference

| Variable | Default | Required in Production | Description |
| :--- | :--- | :--- | :--- |
| `CHECKPOINTER_BACKEND` | `sqlite` | **Yes** (`postgres`) | Selects between `sqlite` or `postgres` persistence backend. |
| `DATABASE_URL` | `""` | **Yes** (if postgres) | Connection string for PostgreSQL / Neon database. |
| `DATABASE_PATH` | `support_checkpoints.db` | No | Filepath for local SQLite database. |
| `GROQ_API_KEY` | `""` | **Yes** | Groq API key for Llama-3.3-70B intent classification. |
| `JWT_SECRET_KEY` | `insecure-default...` | **Yes** | Secret cryptographic key for signing JWT tokens. |
| `JWT_ALGORITHM` | `HS256` | No | Cryptographic algorithm for JWT signatures. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | No | Lifespan of JWT access tokens in minutes. |
| `API_URL` | `http://127.0.0.1:8000` | **Yes** (frontend) | URL pointing from Streamlit frontend to the FastAPI backend. |
| `LOG_LEVEL` | `INFO` | No | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
