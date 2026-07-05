# Deployment Guide

## 1. Prerequisites

### Required Tools
- Docker & Docker Compose v2.24+
- Node.js 20+ (local development)
- Python 3.12+ (local development)
- Poetry (Python package manager)

### Required Accounts
- Vercel (frontend hosting)
- Railway.app or Fly.io (backend hosting)
- Neon.tech or Supabase (PostgreSQL)
- Upstash or Redis Cloud (Redis)
- AWS S3 or Cloudflare R2 (File storage)
- OpenAI API key
- Google Cloud Console (OAuth credentials)

## 2. Environment Variables

```bash
# ============ APP ============
APP_NAME=JobAgent
APP_ENV=production
APP_SECRET_KEY=<generate: openssl rand -hex 32>
DEBUG=false

# ============ DATABASE ============
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/jobagent
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# ============ REDIS ============
REDIS_URL=redis://:password@host:6379/0
REDIS_CACHE_TTL=1800

# ============ JWT ============
JWT_PRIVATE_KEY=<base64-encoded PEM>
JWT_PUBLIC_KEY=<base64-encoded PEM>
JWT_ACCESS_TOKEN_EXPIRE=900
JWT_REFRESH_TOKEN_EXPIRE=604800

# ============ OAUTH ============
GOOGLE_CLIENT_ID=<from Google Cloud Console>
GOOGLE_CLIENT_SECRET=<from Google Cloud Console>
GOOGLE_REDIRECT_URI=https://api.jobagent.ai/api/v1/auth/google/callback

# ============ AI ============
OPENAI_API_KEY=sk-...
OPENAI_ORGANIZATION=org-...
ANTHROPIC_API_KEY=sk-ant-...
AI_DEFAULT_MODEL=gpt-4o
AI_FALLBACK_MODEL=gpt-4o-mini

# ============ STORAGE ============
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
S3_BUCKET=jobagent-uploads
S3_REGION=us-east-1

# ============ EMAIL ============
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<SendGrid API key>
EMAIL_FROM=noreply@jobagent.ai

# ============ MONITORING ============
SENTRY_DSN=https://...
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# ============ CORS ============
CORS_ORIGINS=https://app.jobagent.ai,https://admin.jobagent.ai
```

## 3. Local Development

```bash
# Clone and setup
git clone https://github.com/yourusername/autonomous-job-agent.git
cd autonomous-job-agent

# Copy environment
cp .env.example .env

# Start all services
docker compose up -d

# Or for development (hot reload):
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run migrations
docker compose exec api alembic upgrade head

# Seed sample data
docker compose exec api python scripts/seed_db.py

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090

# Run tests
docker compose exec api pytest
docker compose exec frontend npm run test
```

## 4. Docker Compose Configuration

```yaml
# docker-compose.yml (development)
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports: ['8000:8000']
    env_file: .env
    depends_on: [postgres, redis]
    volumes: ['./backend:/app']  # Hot reload
  
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A app.workers.celery_app worker -l info
    env_file: .env
    depends_on: [postgres, redis]
  
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports: ['3000:3000']
    volumes: ['./frontend:/app']
  
  postgres:
    image: pgvector/pgvector:pg16
    ports: ['5432:5432']
    environment:
      POSTGRES_DB: jobagent
      POSTGRES_USER: jobagent
      POSTGRES_PASSWORD: jobagent_dev
    volumes: ['pgdata:/var/lib/postgresql/data']
  
  redis:
    image: redis:7-alpine
    ports: ['6379:6379']
    command: redis-server --requirepass redis_dev
  
  prometheus:
    image: prom/prometheus
    ports: ['9090:9090']
    volumes: ['./docker/prometheus.yml:/etc/prometheus/prometheus.yml']
  
  grafana:
    image: grafana/grafana
    ports: ['3001:3000']
    depends_on: [prometheus]

volumes:
  pgdata:
```

## 5. Production Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod \
  --env NEXT_PUBLIC_API_URL=https://api.jobagent.ai \
  --env NEXT_PUBLIC_GOOGLE_CLIENT_ID=<id>
```

**Configuration:**
- Framework preset: Next.js
- Build command: `npm run build`
- Output directory: `.next`
- Node version: 20.x

### Backend (Railway/Fly.io)

```bash
# Railway deploy
railway login
railway up

# Or Fly.io
fly launch
fly deploy
```

**Dockerfile (production):**

```dockerfile
FROM python:3.12-slim AS builder
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/
USER app

EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 6. Health Checks

```python
# Endpoint: GET /health
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": { "status": "healthy", "latency_ms": 5 },
    "redis": { "status": "healthy", "latency_ms": 2 },
    "ai_provider": { "status": "healthy", "latency_ms": 150 },
    "s3": { "status": "healthy", "latency_ms": 20 },
    "queue": { "status": "healthy", "queue_depth": 15 }
  },
  "uptime_seconds": 3600
}
```

## 7. Monitoring & Alerts

### Prometheus Metrics
- `http_requests_total` — Request count by method, path, status
- `http_request_duration_seconds` — Latency histogram
- `ai_requests_total` — AI call count by agent, model, status
- `ai_tokens_total` — Token usage by model
- `ai_cost_cents_total` — Cost tracking
- `redis_cache_hit_ratio` — Cache effectiveness
- `celery_queue_depth` — Background task queue depth
- `database_connections_active` — Connection pool usage
- `application_submissions_total` — Submission rate

### Grafana Dashboards
1. **API Performance:** Latency, error rate, request rate
2. **AI Usage:** Token consumption, cost, model distribution, cache hit rate
3. **Business Metrics:** Applications submitted, match scores, user growth
4. **Infrastructure:** CPU, memory, disk, network

### Alert Rules
- Error rate >5% (5 min window) → PagerDuty
- AI API latency >10s (5 min window) → Slack
- Redis cache hit rate <60% → Email
- Database connection pool >80% → PagerDuty
- Failed application submissions >10/min → Slack

## 8. Backup & Disaster Recovery

### Database Backups
- Automatic daily snapshots (RDS automated backups, 7-day retention)
- Point-in-time recovery (last 35 days)
- Manual backup before major deployments

### Recovery Procedures
```
1. Identify incident severity (S1/S2/S3/S4)
2. For S1 (complete outage):
   a. Restore latest DB snapshot
   b. Redeploy last known-good version
   c. Verify health checks pass
   d. Monitor for 1 hour post-recovery
3. For data corruption:
   a. Use point-in-time recovery to moment before corruption
   b. Validate data integrity
   c. Replay event log for missed events
```
