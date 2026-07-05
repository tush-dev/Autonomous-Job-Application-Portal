# Folder Structure

```
autonomous-job-agent/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # CI pipeline (lint, typecheck, test)
│   │   ├── cd-frontend.yml            # Deploy frontend to Vercel
│   │   ├── cd-backend.yml             # Deploy backend to Railway/Fly.io
│   │   └── docker-build.yml           # Build & push Docker images
│   └── CODEOWNERS                     # PR review ownership
│
├── frontend/                          # Next.js Application
│   ├── .env.example
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── components.json                # Shadcn UI config
│   │
│   ├── public/
│   │   ├── fonts/
│   │   ├── images/
│   │   └── manifest.json
│   │
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing page
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   ├── not-found.tsx
│   │   │
│   │   ├── (auth)/                    # Auth group
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   ├── forgot-password/page.tsx
│   │   │   └── reset-password/page.tsx
│   │   │
│   │   ├── (dashboard)/               # Protected dashboard group
│   │   │   ├── layout.tsx             # Dashboard layout (sidebar + header)
│   │   │   ├── page.tsx               # Dashboard home / overview
│   │   │   ├── applications/
│   │   │   │   ├── page.tsx           # Applications list
│   │   │   │   ├── [id]/page.tsx      # Application detail
│   │   │   │   └── new/page.tsx       # New application
│   │   │   ├── jobs/
│   │   │   │   ├── page.tsx           # Job search
│   │   │   │   └── saved/page.tsx     # Saved jobs
│   │   │   ├── resumes/
│   │   │   │   ├── page.tsx           # Resume list
│   │   │   │   ├── [id]/page.tsx      # Resume detail
│   │   │   │   └── upload/page.tsx    # Upload resume
│   │   │   ├── cover-letters/
│   │   │   │   └── page.tsx           # Cover letters
│   │   │   ├── interviews/
│   │   │   │   └── page.tsx           # Interview schedule
│   │   │   ├── coach/
│   │   │   │   └── page.tsx           # AI career coach
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx           # Personal analytics
│   │   │   └── settings/
│   │   │       ├── page.tsx           # General settings
│   │   │       ├── notifications/
│   │   │       └── security/
│   │   │
│   │   ├── admin/                     # Admin panel
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               # Admin dashboard
│   │   │   ├── users/page.tsx
│   │   │   ├── jobs/page.tsx
│   │   │   ├── analytics/page.tsx
│   │   │   ├── logs/page.tsx
│   │   │   └── ai-usage/page.tsx
│   │   │
│   │   └── api/                       # Next.js API routes (BFF)
│   │       ├── auth/
│   │       │   └── [...nextauth]/route.ts
│   │       └── webhooks/
│   │           └── clerk/route.ts
│   │
│   ├── components/                    # Reusable components
│   │   ├── ui/                        # Shadcn UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── avatar.tsx
│   │   │   ├── skeleton.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── tooltip.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                    # Layout components
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   ├── main-nav.tsx
│   │   │   └── mobile-nav.tsx
│   │   │
│   │   ├── auth/                      # Auth components
│   │   │   ├── login-form.tsx
│   │   │   ├── signup-form.tsx
│   │   │   ├── google-login-button.tsx
│   │   │   └── mfa-setup.tsx
│   │   │
│   │   ├── dashboard/                 # Dashboard components
│   │   │   ├── stats-card.tsx
│   │   │   ├── applications-chart.tsx
│   │   │   ├── status-pipeline.tsx
│   │   │   └── recent-activity.tsx
│   │   │
│   │   ├── jobs/                      # Job components
│   │   │   ├── job-card.tsx
│   │   │   ├── job-detail.tsx
│   │   │   ├── job-search-filters.tsx
│   │   │   ├── match-score-badge.tsx
│   │   │   └── saved-jobs-list.tsx
│   │   │
│   │   ├── resumes/                   # Resume components
│   │   │   ├── resume-upload.tsx
│   │   │   ├── resume-card.tsx
│   │   │   ├── resume-viewer.tsx
│   │   │   ├── skill-graph.tsx
│   │   │   └── resume-analysis.tsx
│   │   │
│   │   ├── applications/              # Application components
│   │   │   ├── application-card.tsx
│   │   │   ├── application-timeline.tsx
│   │   │   ├── application-status-badge.tsx
│   │   │   └── application-form.tsx
│   │   │
│   │   ├── cover-letters/             # Cover letter components
│   │   │   ├── cover-letter-preview.tsx
│   │   │   ├── cover-letter-editor.tsx
│   │   │   └── tone-selector.tsx
│   │   │
│   │   ├── coach/                     # AI coach components
│   │   │   ├── chat-interface.tsx
│   │   │   ├── suggestion-card.tsx
│   │   │   └── roadmap-view.tsx
│   │   │
│   │   ├── notifications/             # Notification components
│   │   │   ├── notification-bell.tsx
│   │   │   ├── notification-list.tsx
│   │   │   └── notification-toast.tsx
│   │   │
│   │   └── shared/                    # Shared components
│   │       ├── loading-skeleton.tsx
│   │       ├── error-boundary.tsx
│   │       ├── empty-state.tsx
│   │       ├── confirm-dialog.tsx
│   │       ├── search-input.tsx
│   │       ├── pagination.tsx
│   │       ├── theme-toggle.tsx
│   │       ├── keyboard-shortcuts.tsx
│   │       └── providers.tsx
│   │
│   ├── hooks/                         # Custom React hooks
│   │   ├── use-auth.ts
│   │   ├── use-resumes.ts
│   │   ├── use-jobs.ts
│   │   ├── use-applications.ts
│   │   ├── use-notifications.ts
│   │   ├── use-interviews.ts
│   │   ├── use-debounce.ts
│   │   ├── use-local-storage.ts
│   │   └── use-media-query.ts
│   │
│   ├── lib/                           # Utility functions
│   │   ├── api-client.ts              # Axios/fetch wrapper
│   │   ├── auth.ts                    # Auth helpers
│   │   ├── constants.ts
│   │   ├── utils.ts                   # cn() etc.
│   │   └── validators.ts
│   │
│   ├── store/                         # State management
│   │   ├── auth-store.ts
│   │   ├── app-store.ts
│   │   └── notification-store.ts
│   │
│   ├── types/                         # TypeScript types
│   │   ├── api.ts                     # API response types
│   │   ├── user.ts
│   │   ├── resume.ts
│   │   ├── job.ts
│   │   ├── application.ts
│   │   ├── notification.ts
│   │   └── common.ts
│   │
│   └── __tests__/                     # Frontend tests
│       ├── components/
│       ├── hooks/
│       └── pages/
│
├── backend/                           # FastAPI Application
│   ├── .env.example
│   ├── pyproject.toml
│   ├── poetry.lock (or requirements.txt)
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── env.py
│   │   ├── alembic.ini
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   │
│   │   ├── core/                      # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Settings (pydantic-settings)
│   │   │   ├── security.py            # JWT, hashing, MFA
│   │   │   ├── database.py            # SQLAlchemy engine & session
│   │   │   ├── redis.py               # Redis client
│   │   │   ├── s3.py                  # S3 storage client
│   │   │   ├── rate_limiter.py        # Rate limiting logic
│   │   │   ├── logging.py             # Logging configuration
│   │   │   ├── telemetry.py           # OpenTelemetry setup
│   │   │   └── exceptions.py          # Custom exceptions
│   │   │
│   │   ├── models/                    # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Declarative base
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   ├── company.py
│   │   │   ├── application.py
│   │   │   ├── cover_letter.py
│   │   │   ├── interview.py
│   │   │   ├── notification.py
│   │   │   └── misc.py                # Activity logs, AI requests, etc.
│   │   │
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   ├── application.py
│   │   │   ├── cover_letter.py
│   │   │   ├── notification.py
│   │   │   ├── interview.py
│   │   │   ├── ai.py
│   │   │   ├── admin.py
│   │   │   └── common.py              # Pagination, response envelope
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                # Dependency injection
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py          # Main v1 router
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── resumes.py
│   │   │   │   ├── jobs.py
│   │   │   │   ├── applications.py
│   │   │   │   ├── cover_letters.py
│   │   │   │   ├── interviews.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── admin.py
│   │   │   │   └── webhooks.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/                  # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── resume_service.py
│   │   │   ├── resume_parser.py        # PDF/DOCX parsing
│   │   │   ├── job_service.py
│   │   │   ├── job_search_service.py
│   │   │   ├── matching_service.py
│   │   │   ├── tailoring_service.py
│   │   │   ├── cover_letter_service.py
│   │   │   ├── application_service.py
│   │   │   ├── application_submitter.py # Auto-submit logic
│   │   │   ├── interview_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── ai_service.py           # AI provider abstraction
│   │   │   ├── admin_service.py
│   │   │   └── cache_service.py
│   │   │
│   │   ├── agents/                    # AI Agent definitions
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base agent class
│   │   │   ├── orchestrator.py        # Master orchestrator
│   │   │   ├── resume_agent.py
│   │   │   ├── job_search_agent.py
│   │   │   ├── resume_optimizer_agent.py
│   │   │   ├── cover_letter_agent.py
│   │   │   ├── application_agent.py
│   │   │   ├── reminder_agent.py
│   │   │   ├── career_advisor_agent.py
│   │   │   └── tools.py               # Agent tools
│   │   │
│   │   ├── crawlers/                  # Job source crawlers
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base crawler
│   │   │   ├── greenhouse.py
│   │   │   ├── lever.py
│   │   │   ├── wellfound.py
│   │   │   ├── remoteok.py
│   │   │   ├── yc_jobs.py
│   │   │   ├── linkedin.py            # API-based only
│   │   │   ├── rss_feed.py
│   │   │   └── factory.py             # Crawler factory
│   │   │
│   │   ├── workers/                   # Background task workers (Celery)
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   ├── resume_tasks.py
│   │   │   ├── job_search_tasks.py
│   │   │   ├── ai_tasks.py
│   │   │   └── notification_tasks.py
│   │   │
│   │   ├── middleware/                # FastAPI middleware
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   ├── csrf.py
│   │   │   ├── rate_limit.py
│   │   │   ├── request_id.py
│   │   │   ├── logging.py
│   │   │   └── security_headers.py
│   │   │
│   │   └── utils/                     # Utility modules
│   │       ├── __init__.py
│   │       ├── file_validator.py
│   │       ├── pdf_generator.py
│   │       ├── token_bucket.py
│   │       ├── prompt_templates.py
│   │       └── helpers.py
│   │
│   ├── tests/                         # Backend tests
│   │   ├── conftest.py
│   │   ├── factories.py               # Test factories
│   │   ├── test_auth/
│   │   ├── test_resumes/
│   │   ├── test_jobs/
│   │   ├── test_applications/
│   │   ├── test_cover_letters/
│   │   ├── test_agents/
│   │   ├── test_crawlers/
│   │   └── test_api/
│   │
│   └── scripts/                       # Utility scripts
│       ├── seed_db.py
│       ├── create_admin.py
│       └── migrate.sh
│
├── docs/                              # Documentation
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── database/SCHEMA.md
│   ├── api/END_POINTS.md
│   ├── FOLDER_STRUCTURE.md
│   ├── SECURITY.md
│   ├── EDGE_CASES.md
│   ├── MILESTONES.md
│   ├── RISKS_SCALING.md
│   ├── DEPLOYMENT.md
│   ├── TESTING.md
│   ├── INTERVIEW_PREP.md
│   └── images/
│       ├── architecture.png
│       └── erd.png
│
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   ├── Dockerfile.worker
│   ├── nginx.conf
│   ├── prometheus.yml
│   └── grafana/
│       └── dashboards/
│
├── docker-compose.yml                 # Local development
├── docker-compose.prod.yml            # Production
├── .env.example                       # Environment variables template
├── .pre-commit-config.yaml
├── .editorconfig
├── .gitignore
├── .dockerignore
├── README.md
├── LICENSE
└── Makefile                           # Common commands
```
