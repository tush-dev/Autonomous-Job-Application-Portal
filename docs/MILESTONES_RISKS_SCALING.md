# Milestones, Risks & Scaling Strategy

## 1. Milestones

### Milestone 1: Planning & Architecture (Week 1)
**Deliverables:**
- PRD finalized
- Architecture Document (with diagrams)
- Database Schema (ERD)
- API Contracts (OpenAPI)
- Folder Structure created
- Monorepo initialized (frontend + backend)
- Docker Compose for local development
- CI/CD pipeline (basic lint + typecheck)

**Acceptance Criteria:**
- All docs reviewed and approved
- Docker Compose starts all services
- `make dev` runs frontend + backend
- CI passes on PR

**Risks:** Scope creep in planning; lock scope after Milestone 1.

---

### Milestone 2: Authentication System (Week 2)
**Deliverables:**
- Backend: User model, auth endpoints (signup, login, logout, refresh)
- Backend: JWT generation (RS256) + refresh token rotation
- Backend: Google OAuth integration
- Backend: Forgot password + reset password flow
- Backend: Email verification flow
- Backend: MFA setup + verification (TOTP)
- Backend: RBAC middleware
- Backend: Rate limiting on auth endpoints
- Backend: Audit logging for auth events
- Frontend: Login page, Signup page, Google OAuth button
- Frontend: Forgot password page, Reset password page
- Frontend: MFA setup flow
- Frontend: Auth context/provider, protected routes
- Tests: Unit + integration for all auth flows

**Acceptance Criteria:**
- User can sign up, verify email, login, logout
- Google OAuth works end-to-end
- Password reset flow works (email + token)
- MFA can be enabled/disabled and required on login
- Refresh token rotation works
- Rate limiting blocks after 5 failed attempts
- Admin role enforced on admin endpoints
- Test coverage >85% for auth

**Risks:** OAuth callback URL configuration; email deliverability.

---

### Milestone 3: Database Foundation (Week 3)
**Deliverables:**
- All SQLAlchemy models (see database schema)
- Alembic migrations (initial + seed)
- PostgreSQL with pgvector setup
- Database indexing strategy
- Row-level security policies
- Connection pooling (PgBouncer)
- Partitioning setup for log tables
- Database backup configuration

**Acceptance Criteria:**
- All tables created with correct schema
- Migrations forward/backward work
- Indexes created in production mode
- Vector similarity search works with pgvector
- RLS policies enforce user isolation
- Connection pooling configured

---

### Milestone 4: Resume Parsing (Week 4)
**Deliverables:**
- Backend: File upload endpoint with validation
- Backend: PDF/DOCX parsing (PyMuPDF + python-docx)
- Backend: AI-powered structured extraction (OpenAI)
- Backend: Confidence scoring per field
- Backend: Versioning system
- Backend: S3 storage integration
- Background worker: Async parsing
- Frontend: Resume upload component (drag & drop)
- Frontend: Resume list view
- Frontend: Resume detail view (parsed data)
- Frontend: Edit parsed data inline
- Tests: PDF/DOCX fixtures, extraction accuracy tests

**Acceptance Criteria:**
- PDF and DOCX both parse correctly
- Extracted fields: skills, experience, education, projects, achievements
- Confidence scores displayed per field
- User can edit parsed data
- Version history preserved
- >90% extraction accuracy on test resumes

**Risks:** Variable PDF formats; image-based PDFs require OCR.

---

### Milestone 5: AI Resume Understanding (Week 5)
**Deliverables:**
- Backend: Resume Agent (LangGraph)
- Backend: Skill graph generation (nodes + edges)
- Backend: Career level estimation
- Backend: Industry detection
- Backend: Missing skills identification
- Backend: Strengths/weaknesses analysis
- Backend: Experience summary generation
- Backend: Embedding generation + storage in pgvector
- Frontend: Skill graph visualization (D3.js / vis-network)
- Frontend: Analysis view (strengths, weaknesses, gaps)
- Frontend: Career level badge
- Tests: Agent output validation, hallucination detection

**Acceptance Criteria:**
- Skill graph correctly infers related skills
- Career level matches human evaluation >80%
- Missing skills are relevant to user's target roles
- No hallucinated experience in output
- Embeddings are stored and searchable

**Risks:** AI hallucination; high token costs for long resumes.

---

### Milestone 6: Job Search Engine (Weeks 6-7)
**Deliverables:**
- Backend: Crawler framework (base class, factory)
- Backend: Greenhouse API crawler
- Backend: Lever API crawler
- Backend: Wellfound crawler
- Backend: RemoteOK crawler
- Backend: YC Jobs crawler
- Backend: RSS feed crawler
- Backend: Job deduplication engine
- Backend: Job normalization (unified schema)
- Backend: Redis caching for search results
- Backend: Search + filter API endpoint
- Background worker: Scheduled crawling
- Frontend: Job search page with filters
- Frontend: Job card component
- Frontend: Job detail view
- Frontend: Save/unsave job
- Frontend: Infinite scroll pagination
- Tests: Crawler tests with mock responses

**Acceptance Criteria:**
- Each crawler returns normalized jobs
- Deduplication reduces duplicate results by >90%
- Search returns results in <500ms (cached)
- Filters work correctly (location, salary, remote, keywords)
- Jobs are refreshed within 1 hour of posting
- Rate limits respected for each source

**Risks:** LinkedIn API restrictions; source API changes; legal compliance.

---

### Milestone 7: Intelligent Matching Engine (Week 8)
**Deliverables:**
- Backend: Matching service (skills, experience, education, location, salary)
- Backend: Embedding-based semantic matching
- Backend: Match score calculation (0-100)
- Backend: Explainable match reasons
- Backend: Missing skills identification per job
- Backend: Interview chance estimation
- Backend: Risk level assessment
- Backend: Match caching
- Frontend: Match score badge (color-coded)
- Frontend: Match breakdown view
- Frontend: Missing skills list per job
- Tests: Match accuracy validation against labeled dataset

**Acceptance Criteria:**
- Match scores correlate with user feedback >85%
- Explanations are human-readable and accurate
- Missing skills are relevant to each specific job
- Caching improves repeat search speed by 10x
- Edge cases handled (empty resume, short JD, etc.)

**Risks:** Subjectivity of "good match"; calibration of scoring weights.

---

### Milestone 8: Resume Tailoring & Cover Letters (Week 9)
**Deliverables:**
- Backend: Resume Optimizer Agent
- Backend: ATS-optimized resume generation
- Backend: Keyword optimization (truthful only)
- Backend: PDF generation from tailored resume
- Backend: ATS score calculation
- Backend: Cover Letter Agent
- Backend: Cover letter generation (3 tones)
- Backend: Anti-cliché filter
- Backend: Cover letter versioning
- Frontend: Tailored resume preview
- Frontend: Cover letter editor + preview
- Frontend: Tone selector
- Frontend: Download as PDF
- Tests: ATS score validation; cliché detection accuracy

**Acceptance Criteria:**
- Generated resumes are ATS-friendly (clean layout, standard sections)
- No hallucinated experience — only user's actual data
- Cover letters sound human (no detectable AI patterns)
- Keywords match job description without stuffing
- PDF output is properly formatted
- User can edit both before finalizing

**Risks:** ATS systems vary widely; PDF formatting inconsistencies.

---

### Milestone 9: Application Automation (Weeks 10-11)
**Deliverables:**
- Backend: Application Agent
- Backend: Form auto-fill (Playwright-based)
- Backend: Resume upload automation
- Backend: Cover letter upload/attachment
- Backend: Screening question answering (with pre-configured answers)
- Backend: Approval gate system (always ask / trusted / auto)
- Backend: Idempotency protection (no double-submit)
- Backend: Retry logic (3 attempts, exponential backoff)
- Backend: Application status tracking
- Backend: Webhook for external status updates
- Frontend: Application flow (draft → review → submit)
- Frontend: Approval gate UI
- Frontend: Application detail view (with timeline)
- Frontend: Pre-configured answers management
- Tests: Mock form submissions; Playwright test suite

**Acceptance Criteria:**
- Form auto-fill works for Greenhouse, Lever, Workday (top 3)
- Resume and cover letter uploaded correctly
- Approval gate respected (blocks when required)
- Idempotency prevents duplicate submissions
- Failed submissions retried and logged
- Application timeline accurately recorded

**Risks:** CAPTCHA blocks; form structure changes; legal liability.

---

### Milestone 10: Dashboard & Analytics (Week 12)
**Deliverables:**
- Backend: Dashboard statistics API
- Backend: Application analytics (rate, trends, sources)
- Frontend: Pipeline view (saved → applied → screening → interview → offer)
- Frontend: Analytics charts (recharts)
- Frontend: Timeline view per application
- Frontend: Statistics cards (total, interview rate, offer rate)
- Frontend: Applications list with filters
- Frontend: Empty states, loading states, error states
- Tests: Dashboard component tests

**Acceptance Criteria:**
- Pipeline view shows correct status distribution
- Charts render correctly with real data
- Timeline shows chronological events
- Statistics match raw data
- Filters work correctly
- Responsive design across devices

---

### Milestone 11: Notifications & Reminders (Week 13)
**Deliverables:**
- Backend: Notification service (in-app, email)
- Backend: Interview reminder system
- Backend: Email templates
- Backend: Calendar integration (Google Calendar API)
- Backend: Notification preferences
- Backend: Push notification support (Web Push API)
- Frontend: Notification bell with badge
- Frontend: Notification dropdown/panel
- Frontend: Notification settings page
- Frontend: Interview schedule view
- Frontend: Calendar sync UI
- Tests: Notification delivery tests

**Acceptance Criteria:**
- In-app notifications appear in real-time
- Email notifications delivered within 2 minutes
- Interview reminders sent at configured intervals
- Calendar integration creates events
- User can control notification preferences

---

### Milestone 12: Admin Panel (Week 14)
**Deliverables:**
- Backend: Admin API endpoints
- Backend: Admin-specific analytics
- Backend: AI usage tracking dashboard
- Frontend: Admin layout (sidebar + header)
- Frontend: User management table (search, filter, disable)
- Frontend: Job management table
- Frontend: Analytics dashboard (charts, metrics)
- Frontend: System logs viewer
- Frontend: Audit log viewer
- Frontend: AI usage dashboard (tokens, cost, latency)
- Tests: Admin endpoint authorization tests

**Acceptance Criteria:**
- Admin can view all users and disable accounts
- Admin can view all jobs and remove listings
- Analytics show real-time metrics
- Audit logs are searchable and filterable
- AI usage tracked per user and aggregated
- Non-admin users blocked from admin routes

---

### Milestone 13: Caching & Performance (Week 15)
**Deliverables:**
- Redis caching layer for all frequent queries
- CDN caching for static assets
- API response time optimization (profile + optimize)
- Database query optimization (explain analyze)
- N+1 query elimination
- Connection pooling optimization
- Pagination optimization
- Lazy loading for frontend routes
- Image optimization (next/image)
- Bundle size optimization (code splitting)
- Performance benchmarks established

**Acceptance Criteria:**
- p95 API response <200ms (non-AI)
- Redis cache hit rate >80%
- Lighthouse score >90
- Largest Contentful Paint (LCP) <1.5s
- First Input Delay (FID) <100ms
- Cumulative Layout Shift (CLS) <0.1

---

### Milestone 14: Security Hardening (Week 16)
**Deliverables:**
- Penetration test findings addressed
- Input validation audit
- Rate limiting audit and tuning
- Security headers audit
- Dependency vulnerability scan (pass with 0 critical)
- Secrets management audit
- Audit logging completeness check
- Prompt injection test suite
- XSS/CSRF/SQLi test suite
- Security documentation updated

**Acceptance Criteria:**
- OWASP Top 10 vulnerabilities addressed
- No critical/high vulnerabilities in dependencies
- All endpoints have appropriate rate limiting
- Prompt injection resistant (tested with known attack patterns)
- Audit logs capture all required events
- Security documentation complete

---

### Milestone 15: Testing (Week 17)
**Deliverables:**
- Unit tests: 80%+ coverage (backend + frontend)
- Integration tests: All API endpoints
- E2E tests: Critical user flows (Playwright)
  - Signup → resume upload → job search → save job → apply
  - Login → dashboard → view applications
  - Admin → manage users → view analytics
- Load tests: 1000 concurrent users (k6)
- AI accuracy tests: Hallucination rate <2%
- Accessibility tests: WCAG 2.1 AA
- Security tests: OWASP ZAP

**Acceptance Criteria:**
- Backend coverage >80%
- Frontend coverage >70%
- E2E tests pass on CI
- Load test: p95 <500ms at 1000 concurrent users
- AI hallucination rate <2%
- No WCAG AA violations
- OWASP ZAP reports medium+ issues addressed

---

### Milestone 16: Deployment & DevOps (Week 18)
**Deliverables:**
- Production Dockerfile for backend
- Production Dockerfile for frontend
- Docker Compose production configuration
- CI/CD pipeline (GitHub Actions)
  - Frontend: build → test → deploy to Vercel
  - Backend: build → test → deploy to Railway/Fly.io
  - Workers: build → deploy
- Health check endpoints
- Environment validation script
- Database backup automation
- Monitoring setup (Prometheus + Grafana)
- Logging pipeline (OpenTelemetry → Loki/ELK)
- Error tracking (Sentry)
- Uptime monitoring
- Incident response runbook
- SSL certificate management (Let's Encrypt)

**Acceptance Criteria:**
- Production deployment fully automated
- Rolling updates with zero downtime
- Health checks pass for all services
- Monitoring dashboards show key metrics
- Alerts configured for critical events
- Rollback procedure documented and tested

---

### Milestone 17: Documentation & Launch (Week 19)
**Deliverables:**
- README (comprehensive)
- Architecture diagram (Mermaid + rendered)
- ER diagram (Mermaid + rendered)
- API documentation (OpenAPI/Swagger)
- Environment setup guide
- Deployment guide
- Scaling guide
- Troubleshooting guide
- Interview preparation notes
- Release notes v1.0
- Demo video / walkthrough
- User onboarding flow finalized

**Acceptance Criteria:**
- All documentation reviewed and accurate
- New developer can set up project in <30 min
- API docs are complete with examples
- Deployment guide covers staging + production
- Scaling guide covers up to 1M users
- Interview notes ready for portfolio presentation

---

## 2. Risks & Mitigations

| ID | Risk | Probability | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | AI provider API changes/deprecation | Medium | High | Multi-provider abstraction; fallback models |
| R2 | LinkedIn blocks scraping | High | Medium | Use official API only; respect robots.txt |
| R3 | ATS systems reject auto-submissions | Medium | High | Manual approval gates; CAPTCHA detection |
| R4 | User data privacy regulations (GDPR) | Medium | High | Privacy-by-design; data deletion flows; consent management |
| R5 | AI hallucination causes resume lies | Low | Critical | Validation layer cross-referencing source data |
| R6 | High AI costs at scale | High | Medium | Caching; tiered models; token budgeting per user |
| R7 | Job source API rate limits | High | Medium | Respectful crawling; backoff; queue-based |
| R8 | Form structure changes break automation | High | Medium | Retry logic; manual fallback; logging |
| R9 | Legal liability from auto-applications | Medium | High | User consent; approval gates; terms of service |
| R10 | Database performance degradation | Medium | High | Indexing; read replicas; partitioning; monitoring |

## 3. Scaling Strategy

### Phase 1: Launch (Up to 1,000 users)
- Single FastAPI instance (2 vCPU, 4GB RAM)
- PostgreSQL on managed instance (db.t3.medium)
- Redis on managed instance (cache.t3.micro)
- Background workers on same instance
- **Monthly cost:** ~$100-200

### Phase 2: Growth (Up to 10,000 users)
- FastAPI scaled to 3 instances behind load balancer
- PostgreSQL with read replica (db.r6g.large)
- Redis cluster (2 shards)
- Separate worker pool (2 instances)
- CDN for static assets
- **Monthly cost:** ~$500-1000

### Phase 3: Scale (Up to 100,000 users)
- FastAPI: 10+ instances, auto-scaling
- PostgreSQL: Multi-AZ, 2 read replicas, connection pooling
- Redis: 6 shard cluster
- Workers: 5+ instances, auto-scaling
- Dedicated Qdrant for vector search
- Database sharding (user_id hash)
- **Monthly cost:** ~$3000-5000

### Phase 4: Enterprise (1M+ users)
- Microservices decomposition (auth, resume, jobs, applications, AI)
- Kubernetes orchestration
- Global PostgreSQL (Aurora/Spanner)
- Global Redis (ElastiCache Global Datastore)
- Dedicated AI inference infrastructure
- Multi-region deployment
- **Monthly cost:** ~$15,000-30,000+

### Key Scaling Decisions:
1. **Stateless API** (JWT auth) — enables horizontal scaling immediately
2. **Async everywhere** — FastAPI async, async SQLAlchemy, async Redis
3. **Background workers** — Celery separates heavy tasks from API
4. **Caching first** — Redis before database for frequently accessed data
5. **Read replicas** — Analytics/queries offloaded from primary DB
6. **Connection pooling** — PgBouncer prevents connection exhaustion
7. **CDN** — Static assets never hit origin servers
8. **Database indexes** — Carefully designed for query patterns
9. **Partitioning** — Log tables partitioned to prevent bloat
10. **Feature flags** — Gradual rollout of new features
