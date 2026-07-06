from typing import Optional
import structlog

from app.agents.base import BaseAgent
from app.core.ai import gateway
from app.integrations.jsearch import search_jobs

logger = structlog.get_logger()


class ResumeAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        resume_text = context.get("resume_text", "")
        job_description = context.get("job_description")
        self.logger.info("analyzing_resume")

        if not resume_text:
            return {"error": "No resume text provided"}

        result = await gateway.analyze_resume(resume_text, job_description)
        return {
            "type": "resume_analysis",
            **result,
        }


class JobSearchAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        query = context.get("query", "")
        location = context.get("location")
        self.logger.info("searching_jobs", query=query, location=location)

        if not query:
            return {"error": "No search query provided", "jobs": [], "total": 0}

        jobs = await search_jobs(query, location)
        return {
            "type": "job_search",
            "jobs": jobs,
            "total": len(jobs),
        }


class ResumeOptimizerAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        resume_text = context.get("resume_text", "")
        job_description = context.get("job_description", "")
        target_role = context.get("target_role", "")
        self.logger.info("optimizing_resume", target_role=target_role)

        if not resume_text or not job_description:
            return {"error": "Resume text and job description required", "content": {}, "ats_score": 0}

        prompt = f"""Tailor this resume for maximum ATS compatibility against the job description below.

Rules:
- ONLY use information present in the original resume. NEVER fabricate experience.
- Incorporate keywords from the job description naturally.
- Maintain standard ATS-friendly section headers.
- Keep formatting clean (no graphics, tables, columns).

Resume:
{resume_text}

{'Target Role: ' + target_role if target_role else ''}

Job Description:
{job_description}

Return ONLY valid JSON with keys: summary, experience (list of rewritten bullets), skills (reordered), ats_score (0-100), keywords_added (list)."""
        response = await gateway.generate(
            prompt,
            system_prompt="You are an ATS optimization expert.",
            temperature=0.3,
        )
        import json
        cleaned = response.content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        try:
            parsed = json.loads(cleaned.strip())
        except (json.JSONDecodeError, Exception):
            parsed = {"content": {}, "ats_score": 0}
        return {
            "type": "resume_optimized",
            **parsed,
        }


class CoverLetterAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        resume_text = context.get("resume_text", "")
        job_title = context.get("job_title", "")
        company_name = context.get("company_name", "")
        job_description = context.get("job_description", "")
        tone = context.get("tone", "professional")
        self.logger.info("generating_cover_letter", job_title=job_title, company=company_name)

        content = await gateway.generate_cover_letter(
            resume_text, job_title, company_name, job_description, tone
        )
        return {
            "type": "cover_letter",
            "content": content,
            "tone": tone,
        }


class ApplicationAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        job_id = context.get("job_id")
        resume_id = context.get("resume_id")
        cover_letter = context.get("cover_letter")
        user_id = context.get("user_id")
        approval_required = context.get("approval_required", True)
        notes = context.get("notes")
        db = context.get("db")
        self.logger.info("processing_application", job_id=job_id)

        if not job_id or not resume_id:
            return {"error": "job_id and resume_id required", "type": "application", "status": "failed"}

        if not user_id or not db:
            return {"error": "user_id and db required for application submission", "type": "application", "status": "failed"}

        from app.services.application_service import ApplicationService

        service = ApplicationService(db)
        try:
            app_result = await service.create_application(
                user_id=user_id,
                job_id=job_id,
                resume_id=resume_id,
                approval_required=approval_required,
                notes=notes,
            )
            return {
                "type": "application",
                "status": "created",
                "result": {
                    "application_id": app_result.id,
                    "job_id": job_id,
                    "resume_id": resume_id,
                },
            }
        except Exception as e:
            self.logger.error("application_creation_failed", error=str(e))
            return {"error": str(e), "type": "application", "status": "failed"}


class ReminderAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        self.logger.info("checking_reminders")
        user_id = context.get("user_id")
        db = context.get("db")

        if not user_id or not db:
            return {"type": "reminder", "reminders": []}

        from datetime import datetime, timedelta, timezone
        from sqlalchemy import select
        from app.models.interview import InterviewSchedule

        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)
        result = await db.execute(
            select(InterviewSchedule).where(
                InterviewSchedule.user_id == user_id,
                InterviewSchedule.scheduled_at >= now,
                InterviewSchedule.scheduled_at <= tomorrow,
                InterviewSchedule.reminder_sent == False,
            )
        )
        upcoming = result.scalars().all()
        reminders = []
        for iv in upcoming:
            reminders.append({
                "id": str(iv.id),
                "type": "interview_reminder",
                "title": f"Upcoming interview at {iv.scheduled_at.strftime('%H:%M on %b %d')}",
                "application_id": str(iv.application_id),
                "scheduled_at": iv.scheduled_at.isoformat(),
            })
        return {
            "type": "reminder",
            "reminders": reminders,
        }


class CareerAdvisorAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        resume_text = context.get("resume_text", "")
        preferences = context.get("preferences")
        question = context.get("question")
        self.logger.info("providing_career_advice")

        if question:
            prompt = f"""The user asks: {question}

{'Resume context: ' + resume_text[:1000] if resume_text else 'No resume provided.'}
{'Preferences: ' + preferences if preferences else ''}

Provide practical, actionable career advice."""
            response = await gateway.generate(
                prompt,
                system_prompt="You are a supportive career coach AI. Be encouraging but honest. Suggest specific next steps.",
            )
            return {
                "type": "career_advice",
                "response": response.content,
            }

        result = await gateway.suggest_career_path(resume_text, preferences)
        return {
            "type": "career_advice",
            **result,
        }
