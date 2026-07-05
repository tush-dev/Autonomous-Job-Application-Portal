# Edge Cases & Error Handling

## 1. Authentication Edge Cases

| Scenario | Handling |
|----------|----------|
| User signs up with existing email | Return 409 Conflict; prompt login or password reset |
| User logs in with wrong password >5 times | Temp lockout (15 min); email notification |
| JWT expired mid-session | Auto-refresh via interceptor; if refresh fails, redirect to login |
| Google OAuth email conflicts with existing email | Link accounts; send verification email |
| User tries to access admin endpoints | Return 403 Forbidden |
| MFA secret lost | Recovery codes; admin override with verification |
| Email verification token expired | Allow resend within 24h window |
| Concurrent refresh token usage | Revoke all refresh tokens for user; force re-login |
| User deletes account with active applications | Soft delete; mark applications as orphaned |

## 2. Resume Edge Cases

| Scenario | Handling |
|----------|----------|
| Uploaded file >10MB | Reject with 413; clear error message |
| Uploaded file is not PDF/DOCX | Reject with 415; list accepted formats |
| Corrupted PDF/DOCX | Return parsing error; suggest re-upload |
| Image-based PDF (scanned) | OCR fallback (Tesseract); warn about lower accuracy |
| Resume with no extractable text | Return parsing failed; suggest text-based resume |
| Resume in non-English language | Detect language; offer translation or native parsing |
| Resume with missing sections | Handle gracefully; set empty arrays for missing sections |
| Multiple resumes uploaded | Allow versioning; mark one as active |
| Resume parsing takes >60s | Background task; notify via WebSocket when done |
| Resume PDF contains malware | ClamAV scan; quarantine; notify admin |

## 3. Job Search Edge Cases

| Scenario | Handling |
|----------|----------|
| No jobs found matching criteria | Return empty array; suggest broadening filters |
| Job source API is down | Circuit breaker; fall back to cached results; log error |
| Job source returns rate-limited | Respect rate limits; exponential backoff; queue |
| Duplicate job from multiple sources | Deduplicate by normalized title + company + location |
| Job posting is expired | Mark as inactive; update status on next crawl |
| Job URL is broken | Attempt Wayback Machine fallback; skip if unreachable |
| Company removed from source | Soft delete; notify users who saved/bookmarked |
| User searches without resume uploaded | Allow search; suggest uploading resume for matching |
| Salary range ambiguous (e.g., "DOE") | Parse common patterns; default to null; note confidence |

## 4. Matching Engine Edge Cases

| Scenario | Handling |
|----------|----------|
| Resume has no skills listed | Fall back to experience titles and education; low confidence |
| Job description is too short (<50 words) | Match primarily on title and company; medium confidence |
| User has multiple career tracks | Cluster skills; match against each cluster |
| Salary range formats differ | Normalize to min/max/currency; handle "Competitive" |
| Location mismatch (remote vs onsite) | Apply location preference weight; partial score |
| User prefers remote but job is hybrid | Score based on policy; flag as partial match |
| Experience years don't match exactly | Apply tolerance (±1 year); score proportionally |
| No exact skill matches exist | Use semantic similarity via embeddings |

## 5. Cover Letter Edge Cases

| Scenario | Handling |
|----------|----------|
| Generated cover letter exceeds 500 words | Summarize; flag for user review |
| Cover letter contains AI clichés | Post-processing filter; regenerate if detected |
| User's resume has minimal content | Generate shorter letter; note limitations |
| Non-English job description | Generate cover letter in match language |
| User custom instructions are empty | Use default tone and style |
| Generated content hallucinates experience | Validation against resume data; reject & regenerate |

## 6. Application Submission Edge Cases

| Scenario | Handling |
|----------|----------|
| Application form has unexpected fields | Log unknown fields; submit with known fields; partial success |
| Resume upload field has size/type restrictions | Check before submission; convert if needed |
| CAPTCHA on application form | Flag for manual intervention; notify user |
| Application requires login | Attempt auto-login with user credentials; 2FA breaks |
| Application submitted but server says timeout | Check via status endpoint; don't double-submit |
| Network failure during submission | Retry 3x with exponential backoff; mark as failed |
| Multiple rapid submissions (anti-spam) | Rate limit; flag for review |
| Job posting removed during application | Return 410 Gone; update status |
| File format not accepted by ATS (e.g., DOCX rejected) | Convert to PDF before upload |
| Application requires video/portfolio | Skip; flag as partial submission |

## 7. AI Agent Edge Cases

| Scenario | Handling |
|----------|----------|
| AI provider API is down | Fail over to secondary provider; log incident |
| AI response is empty or nonsensical | Retry with different prompt; max 3 attempts |
| Token limit exceeded for long resume/chats | Truncate input with smart chunking; inform user |
| AI hallucinates facts | Cross-reference with structured resume data; reject |
| Prompt injection attempt detected | Sanitize input; escape special chars; log security event |
| Rate limit on AI API | Queue requests; exponential backoff; notify on delay |
| Streaming connection drops | Client reconnects; server resends from last checkpoint |
| User asks about non-career topics | Gently redirect; log off-topic queries |

## 8. Notification Edge Cases

| Scenario | Handling |
|----------|----------|
| Email delivery fails | Retry 3x; fall back to in-app notification |
| User has too many unread notifications | Batch display; oldest first; paginated |
| Push notification permission denied | Fall back to email only |
| Calendar integration fails | Log error; notify user to re-authenticate |
| Timezone confusion for reminders | Always store UTC; convert on display |

## 9. Security Edge Cases

| Scenario | Handling |
|----------|----------|
| XSS attempt in job search query | Input sanitization; encode output |
| SQL injection via search filters | Parameterized queries; ORM prevents injection |
| JWT stolen from localStorage | Use httpOnly cookies is too complex; implement refresh rotation |
| CSRF via API calls | Double-submit cookie pattern; CSRF token in header |
| File upload with malicious content | Validate MIME type; scan with ClamAV; strip metadata |
| Brute force on login | Rate limiting + progressive delay + CAPTCHA after 3 failures |
| Session fixation | Regenerate session on login |
| Path traversal in file download | Validate path; use UUID-based storage keys |

## 10. Performance Edge Cases

| Scenario | Handling |
|----------|----------|
| User uploads 50-page resume | Summarize before AI processing; handle page limit |
| Search returns 10,000+ results | Paginate; limit to top 100 by default |
| 1000 users trigger AI simultaneously | Queue-based processing; max concurrent AI workers |
| Redis goes down | Fall back to PostgreSQL (slower); alert ops team |
| Database connection pool exhausted | Queue requests; return 503 with retry header |
| Very long job descriptions (>10K chars) | Truncate for AI processing; full text for matching |

## 11. Data Consistency Edge Cases

| Scenario | Handling |
|----------|----------|
| User deletes resume attached to application | Keep application reference; mark resume as deleted |
| Job removed after application submitted | Keep application; mark job as removed |
| Concurrent application status updates | Optimistic locking with version field |
| User updates preferences mid-search | Invalidate related caches; flag as stale |
| Orphaned records from failed transactions | Transaction rollback; periodic cleanup jobs |

## 12. Concurrency Edge Cases

| Scenario | Handling |
|----------|----------|
| Double-click on "Apply" | Debounce on frontend; idempotency key on backend |
| Same job applied by same user twice | Idempotency check; return existing application |
| Two crawlers fetch same job simultaneously | Upsert with unique constraint (source + source_job_id) |
| WebSocket reconnection storm | Jittered reconnection delay (2s + random 0-3s) |
| Celery task executes twice (at-least-once) | Idempotent task design; check before processing |
