# Interview Preparation Notes

## 1. Architecture Decisions: Why?

### Why React + Next.js?
- **SSR/SSG/ISR:** Public pages (landing, blog) need SEO; dashboard needs CSR. Next.js provides both with zero config.
- **App Router:** Nested layouts, loading states, error boundaries are first-class primitives.
- **React Server Components:** Reduce client-side JavaScript; improved performance, especially on slower devices.
- **BFF Pattern:** API routes in Next.js handle auth token exchange, CSRF token generation — keeping secrets on the server.
- **Ecosystem:** TailwindCSS + Shadcn UI + TypeScript = best DX for building polished UIs quickly.

**Tradeoff:** Server-rendering increases complexity vs. pure SPA (Vite + React). Worth it for SEO and performance.

### Why FastAPI?
- **Async native:** Critical for streaming AI responses, handling concurrent WebSocket connections, and async database operations.
- **Performance:** FastAPI benchmarks at ~50,000 req/s (vs ~10,000 for Django, ~15,000 for Flask) — 5x faster.
- **Automatic OpenAPI:** Pydantic schemas auto-generate API docs — saves weeks of documentation work.
- **Type safety:** Pydantic provides runtime validation + IDE autocompletion — catches bugs at dev time.
- **Python ecosystem:** LangChain, LangGraph, OpenAI SDK, all AI/ML libraries are Python-first.

**Tradeoff:** Smaller community than Django but growing fast; less "batteries included" — need to build admin panel separately.

### Why PostgreSQL?
- **Liquidity:** Most mature open-source relational DB; host anywhere (AWS RDS, Supabase, Neon, Railway).
- **pgvector:** Vector similarity search without a separate infrastructure — saves complexity and cost at launch.
- **JSONB:** Store semi-structured resume data while maintaining the ability to query it.
- **Full-text search:** Built-in `tsvector` for job description search — no need for Elasticsearch at launch.
- **ACID compliance:** Critical for application status tracking and financial data.
- **Tooling:** Alembic for migrations, pg_stat_statements for monitoring.

**Tradeoff:** Vertical scaling limit; horizontal scaling requires read replicas/federation beyond 10M users. For this use case, vertical scaling + caching handles up to 1M users.

### Why Redis?
1. **Cache:** Job search results (30min TTL) — reduces database load by 80%.
2. **Rate Limiting:** Sliding window counter — fast and memory-efficient.
3. **Task Queue:** Celery + Redis for background processing (resume parsing, crawling, AI).
4. **Session Store:** Token blacklist for logout + refresh token tracking.
5. **Pub/Sub:** Real-time notifications across API instances.

**Tradeoff:** Data loss risk (RDB/AOF persistence mitigates this). For purely ephemeral data, this is acceptable. For critical data, we write-through to PostgreSQL.

### Why Vector DB (pgvector)?
- **Semantic search:** Match job descriptions to resumes based on meaning, not just keywords.
- **Skill similarity:** Find related skills (e.g., "React" → "Next.js" → "Vue.js").
- **Context retrieval for RAG:** Store job descriptions, company info, and previous applications for AI context.

**Why pgvector over Qdrant/Pinecone?**
- Zero additional infrastructure at launch
- ACID-compliant vector storage alongside relational data
- Single SQL query can filter (location, salary) + vector search
- Migrate to dedicated vector DB only when needed (>10M vectors)

### Why LangGraph?
- **State graphs:** Agents can have state (memory, context) across multiple turns — essential for complex workflows.
- **Human-in-the-loop:** Built-in checkpointing for approval gates — pause, review, resume.
- **Tool calling:** Agents can call APIs (search jobs, generate resumes, submit applications) as tools.
- **Streaming:** LangGraph supports streaming token-by-token responses to the frontend.
- **Observability:** LangSmith integration for debugging agent behavior.

**Why not build custom?** LangGraph solves the hard problems of agent orchestration (state management, loops, error recovery). Custom solutions tend to become unmaintainable spaghetti after 5+ agent types.

### Why JWT + OAuth?
- **Stateless:** No server-side session store — enables horizontal scaling with zero configuration.
- **RS256 signing:** Asymmetric keys — services verify with public key, only the auth service has the private key.
- **OAuth 2.0:** Google login reduces friction — 60%+ of users prefer social login.
- **Refresh tokens:** Balance security (short-lived access tokens) with UX (long-lived sessions).

**Why not session-based auth?** Sessions require sticky sessions or a shared session store (Redis), increasing infrastructure complexity. JWT works out of the box with any number of stateless API servers.

### Why Docker + Docker Compose?
- **Consistency:** Every developer gets the exact same environment (PostgreSQL 16, Redis 7, Python 3.12).
- **CI/CD parity:** Same images used in development, CI, and production.
- **Multi-service orchestration:** API + workers + Redis + PostgreSQL + Celery all start with `docker compose up`.
- **Horizontal scaling:** `docker compose up --scale api=5` for load testing.

## 2. Database Relationships

```
User 1:N Resume         — User has multiple resume versions
User 1:N Application    — User submits many applications
User 1:N SavedJob       — User saves jobs for later
User 1:N Notification   — User receives notifications
User 1:N Interview      — User has interviews
User 1:N ActivityLog    — User generates activity
User 1:M AIRequest      — User triggers AI calls
User 1:1 UserSettings   — User has one config
User 1:1 UserPreferences — User has one preference set

Resume 1:N ResumeVersion  — Version history
Resume 1:1 SkillGraph     — AI analysis result
Resume 1:N GeneratedResume — Tailored copies

Company 1:N Job  — Company posts many jobs

Job 1:N Application    — Many users apply
Job 1:N SavedJob       — Many users save

Application 1:N Timeline    — Status history
Application 1:1 CoverLetter — One per application
Application 1:N GeneratedResume — Multiple tailored versions
Application 0:N Interview   — Multiple interview rounds

AIRequest 0:N Feedback  — User feedback on AI output
```

## 3. Scaling to 10 Million Users

### Database
- **Sharding:** Partition users by ID hash across PostgreSQL instances (8-16 shards).
- **Read replicas:** 3-5 read replicas per shard for dashboard queries.
- **Global distribution:** Regional PostgreSQL clusters (US, EU, APAC) with cross-region replication.
- **CQRS pattern:** Separate read models for dashboards (materialized views updated via event stream).

### API
- **Microservices:** Split monolith into domain services: Auth, Resume, Job, Application, AI, Notification.
- **API Gateway:** Single entry point (Kong/APISIX) with rate limiting, auth, routing.
- **Auto-scaling:** Kubernetes HPA based on CPU/memory/request rate.
- **gRPC for internal communication:** 10x faster than HTTP/REST for service-to-service calls.

### AI
- **Dedicated inference:** GPU-backed inference servers (vLLM/TGI) for self-hosting open-source models.
- **Batch processing:** Group non-time-sensitive AI calls into batches for cost efficiency.
- **Caching layer:** Multi-level cache (in-memory → Redis → PostgreSQL) for common AI responses.
- **Fallback models:** Cheaper models for simple tasks (classification, extraction) vs. expensive models for generation.

### Caching
- **CDN:** Edge caching for static assets and some API responses.
- **Redis Cluster:** 32+ shards for distributed caching.
- **Write-through cache:** Invalidate related caches on data mutation.
- **Cache warming:** Pre-fill common searches on schedule.

### Queue
- **Dedicated queue per worker type:** AI jobs, crawling, notifications, resume parsing.
- **Priority queues:** Application submissions get priority over analytics.

## 4. AI Call Optimization

| Strategy | Savings | Complexity |
|----------|---------|------------|
| Semantic caching (exact + similar queries) | 40-60% | Medium |
| Tiered model selection (GPT-4o for complex, GPT-4o-mini for simple) | 70-80% | Low |
| Token budgeting per user (cap monthly token usage) | Prevents runaway costs | Low |
| Prompt compression (extract only relevant context) | 30-50% | Medium |
| Batch similar AI requests | 20-30% | High |
| Cache common patterns (resume summaries, skill graphs) | 50-70% | Medium |
| Use structured outputs (JSON mode) — fewer retries | 10-20% | Low |

## 5. Preventing Prompt Injection

1. **Input sanitization:** Strip known injection patterns (`ignore all previous instructions`, `---`, `|im_start|`)
2. **System prompt hardening:** Embed instructions that cannot be overridden by user input
3. **Output validation:** Cross-reference AI output with source data (resume) to detect hallucinations
4. **Input/output separation:** Clearly delimit user input from system context
5. **Principle of least privilege:** AI only has access to data relevant to the current task
6. **Rate limiting:** Prevent automated injection attempts
7. **Logging:** All prompt injections flagged and logged for security review
8. **Red team testing:** Regular penetration testing with known prompt injection patterns

## 6. Bottlenecks & Their Solutions

| Bottleneck | Solution |
|------------|----------|
| AI API latency | Streaming responses; parallel independent AI calls; caching |
| Database writes (concurrent applications) | Write queue; batch inserts; connection pooling |
| Resume PDF parsing I/O | Async processing; background worker; S3 pre-signed URLs |
| Job crawling (blocking I/O) | Async HTTP clients (httpx); concurrent crawling; queue-based |
| Vector similarity search at scale | IVFFlat indexes; partitioning; migrate to Qdrant at >10M vectors |
| File storage (resumes, generations) | S3 with CDN; pre-signed URLs instead of proxy downloads |
| WebSocket connections (notifications) | Dedicated WebSocket server; horizontal scaling with Redis Pub/Sub |

## 7. Migration to Microservices

**When:** Current monolith exceeds 50 API endpoints, 20 database tables, or team grows to 5+ developers.

**Strategy:**
1. **Strangler Fig pattern:** Gradually extract services, one domain at a time.
2. **Extract Auth first:** Most independent domain, highest security requirements.
3. **Shared database → Database per service:** Migration over several sprints.
4. **Event-driven communication:** RabbitMQ/Kafka for async events; REST/gRPC for sync.
5. **API Gateway:** Kong/APISIX for routing, auth, rate limiting.
6. **Service mesh:** mTLS, observability, traffic management (Istio/Linkerd).

**Services to extract (in order):**
1. Auth Service (JWT, OAuth, MFA)
2. Notification Service (email, push, in-app)
3. AI Service (LLM calls, agent orchestration)
4. Job Service (crawling, search, matching)
5. Resume Service (parsing, generation)
6. Application Service (submission, tracking)

## 8. Future Improvements

- **Voice-based resume input:** Whisper API for dictating resume details
- **Interview practice:** AI mock interviews with speech recognition
- **Salary negotiation coach:** AI agent trained on compensation data
- **Network-based referrals:** Find alumni/connections at target companies
- **Chrome extension:** One-click save from any job board
- **Mobile app:** React Native for iOS/Android
- **Team plans:** Companies can manage team members' applications
- **Affiliate/referral program:** Revenue sharing with users who get hired
- **Market analytics:** Salary trends, hiring demand, skill trends
- **ATS provider partnerships:** Direct API integrations with Workday, Taleo, BambooHR
