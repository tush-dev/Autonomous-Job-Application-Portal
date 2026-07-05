# API Design

## 1. Base URL

- **Development:** `http://localhost:8000/api/v1`
- **Production:** `https://api.jobagent.ai/api/v1`

## 2. Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
X-CSRF-Token: <csrf_token>  (for state-changing requests)
```

### Standard Response Envelope

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-07-05T12:00:00Z"
  }
}
```

### Error Response

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-07-05T12:00:00Z"
  }
}
```

## 3. Endpoints

### 3.1 Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/login` | Login with email/password | No |
| POST | `/auth/google` | Google OAuth login | No |
| POST | `/auth/refresh` | Refresh access token | No |
| POST | `/auth/logout` | Logout & revoke refresh token | Yes |
| POST | `/auth/forgot-password` | Send password reset email | No |
| POST | `/auth/reset-password` | Reset password with token | No |
| POST | `/auth/verify-email` | Verify email with token | No |
| POST | `/auth/resend-verification` | Resend verification email | No |
| POST | `/auth/mfa/setup` | Setup MFA (returns QR code) | Yes |
| POST | `/auth/mfa/verify` | Verify & enable MFA | Yes |
| POST | `/auth/mfa/disable` | Disable MFA | Yes |
| GET  | `/auth/me` | Get current user profile | Yes |
| PATCH | `/auth/me` | Update current user profile | Yes |

#### POST `/auth/signup`

```json
// Request
{
  "email": "user@example.com",
  "password": "SecureP@ss1",
  "full_name": "John Doe"
}

// Response 201
{
  "success": true,
  "data": {
    "user": { "id": "uuid", "email": "...", "full_name": "...", "role": "user" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 900
  }
}
```

#### POST `/auth/login`

```json
// Request
{
  "email": "user@example.com",
  "password": "SecureP@ss1"
}

// Response 200
{
  "success": true,
  "data": {
    "user": { "id": "uuid", "email": "...", "full_name": "...", "role": "user" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 900,
    "mfa_required": false
  }
}
```

### 3.2 Resume Management

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/resumes/upload` | Upload resume file | Yes |
| GET  | `/resumes` | List user's resumes | Yes |
| GET  | `/resumes/{id}` | Get resume details | Yes |
| DELETE | `/resumes/{id}` | Delete resume | Yes |
| GET  | `/resumes/{id}/versions` | List resume versions | Yes |
| GET  | `/resumes/{id}/versions/{version}` | Get specific version | Yes |
| GET  | `/resumes/{id}/skills` | Get skill graph | Yes |
| GET  | `/resumes/{id}/analysis` | Get full AI analysis | Yes |

#### POST `/resumes/upload`

```
Request: multipart/form-data
  file: <binary> (PDF/DOCX, max 10MB)

Response 201
{
  "success": true,
  "data": {
    "id": "uuid",
    "file_name": "resume.pdf",
    "file_size": 245760,
    "file_type": "pdf",
    "parsing_status": "processing",
    "created_at": "2026-07-05T12:00:00Z"
  }
}
```

#### GET `/resumes/{id}/analysis`

```json
// Response 200
{
  "success": true,
  "data": {
    "skills": [
      { "name": "Python", "category": "language", "proficiency": "expert", "years": 5 },
      { "name": "React", "category": "framework", "proficiency": "advanced", "years": 3 }
    ],
    "career_level": "senior",
    "industry": "technology",
    "missing_skills": ["Kubernetes", "GraphQL"],
    "strengths": ["Full-stack development", "System design"],
    "weaknesses": ["No management experience"],
    "summary": "Senior full-stack engineer with 5+ years...",
    "experience_summary": "...",
    "recommended_roles": ["Senior Software Engineer", "Tech Lead"],
    "skill_graph": { "nodes": [...], "edges": [...] }
  }
}
```

### 3.3 Job Search

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/jobs/search` | Search & match jobs | Yes |
| GET  | `/jobs/{id}` | Get job details | Yes |
| POST | `/jobs/{id}/save` | Save job for later | Yes |
| DELETE | `/jobs/{id}/save` | Unsave job | Yes |
| GET  | `/jobs/saved` | List saved jobs | Yes |

#### POST `/jobs/search`

```json
// Request
{
  "query": "software engineer",
  "location": "San Francisco",
  "remote": "hybrid",
  "salary_min": 100000,
  "salary_max": 200000,
  "page": 1,
  "page_size": 20,
  "sources": ["greenhouse", "lever", "wellfound"],
  "exclude_applied": true
}

// Response 200
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "uuid",
        "company": { "id": "uuid", "name": "Google", "logo_url": "..." },
        "title": "Senior Software Engineer",
        "location": "Mountain View, CA",
        "remote": "hybrid",
        "salary_min": 150000,
        "salary_max": 250000,
        "salary_currency": "USD",
        "match_score": 87,
        "match_reasons": [
          "Skills match: Python, React, Go (85%)",
          "Experience level matches (5+ years)",
          "Remote preference aligns"
        ],
        "missing_skills": ["Kubernetes"],
        "estimated_interview_chance": "high",
        "posted_at": "2026-07-01T00:00:00Z",
        "is_saved": false,
        "has_applied": false
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 145,
      "total_pages": 8
    }
  }
}
```

### 3.4 Cover Letters

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/cover-letters/generate` | Generate cover letter | Yes |
| GET  | `/cover-letters/{id}` | Get cover letter | Yes |
| PATCH | `/cover-letters/{id}` | Edit cover letter | Yes |

#### POST `/cover-letters/generate`

```json
// Request
{
  "application_id": "uuid",
  "tone": "professional",
  "custom_instructions": "Mention my experience with distributed systems"
}

// Response 201
{
  "success": true,
  "data": {
    "id": "uuid",
    "content": "Dear Hiring Manager,\n\n...",
    "tone": "professional",
    "word_count": 312,
    "created_at": "2026-07-05T12:00:00Z"
  }
}
```

### 3.5 Resume Tailoring

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/resumes/tailor` | Generate tailored resume | Yes |
| GET  | `/resumes/tailored/{id}` | Get tailored resume | Yes |
| POST | `/resumes/tailored/{id}/download` | Get download URL | Yes |

#### POST `/resumes/tailor`

```json
// Request
{
  "resume_id": "uuid",
  "job_id": "uuid",
  "format": "ats_friendly"
}

// Response 201
{
  "success": true,
  "data": {
    "id": "uuid",
    "content": { ... },
    "ats_score": 92,
    "version": 1,
    "created_at": "2026-07-05T12:00:00Z"
  }
}
```

### 3.6 Applications

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET  | `/applications` | List user's applications | Yes |
| GET  | `/applications/{id}` | Get application details | Yes |
| POST | `/applications` | Create application draft | Yes |
| POST | `/applications/{id}/submit` | Submit application | Yes |
| POST | `/applications/{id}/retry` | Retry failed submission | Yes |
| DELETE | `/applications/{id}` | Delete draft application | Yes |
| GET  | `/applications/{id}/timeline` | Get application timeline | Yes |
| GET  | `/applications/stats` | Get application statistics | Yes |

#### POST `/applications`

```json
// Request
{
  "job_id": "uuid",
  "resume_id": "uuid",
  "approval_required": true,
  "notes": "Apply with tailored resume"
}

// Response 201
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "draft",
    "job": { ... },
    "approval_required": true,
    "created_at": "2026-07-05T12:00:00Z"
  }
}
```

#### POST `/applications/{id}/submit`

```json
// Request
{
  "cover_letter_id": "uuid",
  "generated_resume_id": "uuid",
  "additional_answers": {
    "How did you hear about us?": "LinkedIn",
    "Current salary": "Confidential"
  }
}

// Response 200
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "applied",
    "applied_at": "2026-07-05T12:00:00Z",
    "submission_result": {
      "success": true,
      "source_application_id": "gh_12345"
    }
  }
}
```

### 3.7 Interview Schedules

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET  | `/interviews` | List user's interviews | Yes |
| POST | `/interviews` | Create interview record | Yes |
| PATCH | `/interviews/{id}` | Update interview | Yes |

### 3.8 Notifications

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET  | `/notifications` | List user's notifications | Yes |
| PATCH | `/notifications/{id}/read` | Mark as read | Yes |
| POST | `/notifications/read-all` | Mark all as read | Yes |
| POST | `/notifications/settings` | Update notification settings | Yes |
| GET  | `/notifications/settings` | Get notification settings | Yes |

### 3.9 AI Agent

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/ai/chat` | Chat with AI career coach | Yes |
| POST | `/ai/analyze` | Analyze resume/job match | Yes |
| POST | `/ai/suggest` | Get career suggestions | Yes |
| POST | `/ai/roadmap` | Generate career roadmap | Yes |

#### POST `/ai/chat` (Streaming)

```
Request: Server-Sent Events (SSE)

Response:
data: {"type": "token", "content": "Based on your"}
data: {"type": "token", "content": " profile, I recommend..."}
data: {"type": "done", "content": null}
data: {"type": "error", "content": "Rate limit exceeded"}
```

### 3.10 Admin

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET  | `/admin/users` | List all users | Admin |
| PATCH | `/admin/users/{id}` | Update user (disable, role) | Admin |
| GET  | `/admin/jobs` | List all jobs | Admin |
| DELETE | `/admin/jobs/{id}` | Remove job listing | Admin |
| GET  | `/admin/analytics` | Get system analytics | Admin |
| GET  | `/admin/logs` | Get system logs | Admin |
| GET  | `/admin/audit-logs` | Get audit logs | Admin |
| GET  | `/admin/ai-usage` | Get AI usage statistics | Admin |

## 4. Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1688563200
Retry-After: 45
```

## 5. Pagination

All list endpoints support:
- `page` (default: 1)
- `page_size` (default: 20, max: 100)
- `sort_by` (field name)
- `sort_order` (asc/desc)

Response metadata includes pagination info.

## 6. WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `application.status_changed` | Server → Client | Application status update |
| `resume.parsing_completed` | Server → Client | Resume parsing done |
| `job.match_found` | Server → Client | New high-match job found |
| `notification.new` | Server → Client | New notification |

## 7. Webhook Events (Outgoing)

| Event | Description | Payload |
|-------|-------------|---------|
| `application.submitted` | Application was submitted | `{application_id, job_id, status}` |
| `application.status_changed` | Status changed | `{application_id, old_status, new_status}` |
| `interview.scheduled` | Interview was scheduled | `{interview_id, user_id, scheduled_at}` |
