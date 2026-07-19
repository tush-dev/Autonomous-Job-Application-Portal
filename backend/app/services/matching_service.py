import uuid
import json
import re
import structlog
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, delete
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job, Company, SavedJob
from app.models.application import JobApplication
from app.models.matching import JobMatch, CareerInsight, LearningPath
from app.schemas.matching import (
    JobWithMatchResponse, JobMatchResponse, CareerInsightResponse,
    LearningPathResponse, DashboardResponse,
)
from app.core.ai.gateway import get_gateway
from app.core.config import settings
from sqlalchemy import case

logger = structlog.get_logger()

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "angularjs": "angular",
    "angular.js": "angular",
    "nodejs": "node",
    "node.js": "node",
    "cplusplus": "c++",
    "csharp": "c#",
    "golang": "go",
    "python3": "python",
    "python 3": "python",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "k8s": "kubernetes",
    "k8": "kubernetes",
    "tf": "tensorflow",
    "pt": "pytorch",
    "pg": "postgresql",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "elastic": "elasticsearch",
    "es": "elasticsearch",
    "rb": "ruby",
    "rubyonrails": "rails",
    "ruby on rails": "rails",
    "vue3": "vue",
    "vue 3": "vue",
    "react18": "react",
    "react 18": "react",
    "node18": "node",
    "node 18": "node",
    "typescriptreact": "react",
    "javascripttypescript": "typescript",
    "restapi": "api",
    "rest api": "api",
    "graphql": "graphql",
    "cicd": "ci/cd",
    "ci cd": "ci/cd",
    "machinelearning": "machine learning",
    "machine learning": "machine learning",
    "datascience": "data science",
    "data science": "data science",
    "deeplearning": "deep learning",
    "deep learning": "deep learning",
    "naturallanguageprocessing": "nlp",
    "natural language processing": "nlp",
    "computervision": "computer vision",
    "computer vision": "computer vision",
}


def normalize_skill(skill: str) -> str:
    s = skill.lower().strip()
    s = re.sub(r'[\s\-_]+', ' ', s)
    if s in SKILL_ALIASES:
        return SKILL_ALIASES[s]
    for alias, canonical in SKILL_ALIASES.items():
        if s.replace(" ", "").replace(".", "") == alias.replace(" ", "").replace(".", ""):
            return canonical
    return s


def extract_skills_from_text(text: str) -> set:
    text_lower = text.lower()
    skills_found = set()
    common_tech = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "react", "angular", "vue", "node", "django", "flask", "fastapi",
        "spring", "rails", "ruby", "php", "swift", "kotlin",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "jenkins",
        "machine learning", "ml", "ai", "data science", "tensorflow", "pytorch",
        "html", "css", "graphql", "rest", "api", "git",
        "linux", "bash", "typescript", "nodejs", "vuejs", "angularjs",
    ]
    for tech in common_tech:
        pattern = r'\b' + re.escape(tech) + r'\b'
        if re.search(pattern, text_lower):
            skills_found.add(tech)
    return skills_found


class MatchingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def score_jobs_for_resume(
        self, user_id: uuid.UUID, resume_id: uuid.UUID, job_ids: Optional[list[uuid.UUID]] = None
    ) -> int:
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        resume = result.scalar_one_or_none()
        if not resume or not resume.parsed_data:
            return 0

        query = select(Job).where(Job.is_active == True)
        if job_ids:
            query = query.where(Job.id.in_(job_ids))
        query = query.options(selectinload(Job.company))

        jobs_result = await self.db.execute(query)
        jobs = jobs_result.scalars().all()

        if not jobs:
            return 0

        existing_result = await self.db.execute(
            select(JobMatch.job_id).where(
                JobMatch.resume_id == resume_id,
                JobMatch.user_id == user_id,
            )
        )
        existing_job_ids = set(existing_result.scalars().all())

        parsed = resume.parsed_data
        resume_skills = set(s.lower() for s in parsed.get("skills", []))
        resume_title = parsed.get("name", "")
        resume_summary = parsed.get("summary", "")

        scored = 0
        for job in jobs:
            if job.id in existing_job_ids:
                continue

            match = await self._score_single_job(resume_skills, parsed, resume_summary, job, resume_id, user_id)
            if match:
                self.db.add(match)
                scored += 1

        if scored:
            await self.db.flush()

        logger.info("scored_jobs", resume_id=str(resume_id), scored=scored, total_jobs=len(jobs))
        return scored

    async def _score_single_job(
        self, resume_skills: set, parsed: dict, resume_summary: str, job: Job,
        resume_id: uuid.UUID, user_id: uuid.UUID,
    ) -> Optional[JobMatch]:
        job_title_lower = (job.title or "").lower()
        job_desc_lower = (job.description or "").lower()

        explicit_job_skills = set(normalize_skill(s) for s in (job.skills_required or []))
        normalized_resume_skills = set(normalize_skill(s) for s in resume_skills)

        skills_in_title = set()
        for skill in normalized_resume_skills:
            sl = skill.lower()
            if len(sl) > 1:
                pattern = r'\b' + re.escape(sl) + r'\b'
                if re.search(pattern, job_title_lower):
                    skills_in_title.add(skill)

        desc_skills_found = extract_skills_from_text(job.description or "")
        normalized_desc_skills = set(normalize_skill(s) for s in desc_skills_found)

        all_matched_set = set()
        all_matched_set.update(explicit_job_skills & normalized_resume_skills)
        all_matched_set.update(skills_in_title)
        all_matched_set.update(normalized_desc_skills & normalized_resume_skills)

        explicit_overlap = len(explicit_job_skills & normalized_resume_skills)
        explicit_score = (explicit_overlap / max(len(explicit_job_skills), 1)) * 100 if explicit_job_skills else 0

        desc_match_count = len(normalized_desc_skills & normalized_resume_skills)
        desc_score = min(100, desc_match_count * 15)

        title_boost = 10 if skills_in_title else 0
        title_has_tech = self._title_matches_relevance(job_title_lower)

        base_match = (
            explicit_score * 0.40 +
            desc_score * 0.40 +
            title_boost * 0.10 +
            title_has_tech * 0.10
        )

        # Skills alone are not enough: career stage and work eligibility are
        # decisive for whether a listing is realistically applyable.
        experience_entries = parsed.get("experience", []) or []
        education_entries = parsed.get("education", []) or []
        is_early_career = len(experience_entries) <= 2 or any(
            "2026" in str(entry.get("date", "")) for entry in education_entries
        )

        seniority_penalty = 0.0
        if is_early_career:
            senior_terms = {
                "principal": 48, "staff": 43, "director": 48,
                "head": 45, "manager": 38, "architect": 38,
                "senior": 32, "sr.": 32, "lead": 28,
            }
            seniority_penalty = max(
                (penalty for term, penalty in senior_terms.items() if re.search(rf"\b{re.escape(term)}\b", job_title_lower)),
                default=0,
            )

        entry_terms = ("intern", "junior", "graduate", "new grad", "entry level", "fresher", "associate", "engineer i", "engineer 1", "l1", "l2")
        entry_boost = 14.0 if is_early_career and any(term in job_title_lower for term in entry_terms) else 0.0

        location_lower = (job.location or "").lower()
        india_terms = ("india", "bengaluru", "bangalore", "delhi", "gurgaon", "gurugram", "noida", "pune", "hyderabad", "mumbai")
        restricted_terms = ("remote - us", "remote (u.s", "united states", "us-perm", "remote, us", "canada only", "remote - emea", "remote - na")
        foreign_markers = (
            "canada", "spain", "germany", "france", "ireland", "australia",
            "united kingdom", "uk", "singapore", "israel", "netherlands",
            "poland", "portugal", "romania", "mexico", "brazil", "japan",
            "new zealand", "south africa", "sweden", "norway", "denmark",
        )
        remote_value = str(getattr(job.remote, "value", job.remote)).lower() if job.remote else ""
        source_value = str(getattr(job.source, "value", job.source)).lower() if job.source else ""
        global_remote_markers = ("anywhere", "worldwide", "global remote", "any office or remote")
        is_global_remote = (
            (remote_value == "remote" and source_value != "arbeitnow")
            or any(term in location_lower for term in global_remote_markers)
        ) and not any(term in location_lower for term in restricted_terms)
        location_eligible = (
            any(term in location_lower for term in india_terms)
            or is_global_remote
        ) and not (
            any(term in location_lower for term in foreign_markers)
            and not any(term in location_lower for term in india_terms)
        )
        if any(term in location_lower for term in india_terms):
            location_adjustment = 14.0
        elif any(term in location_lower for term in restricted_terms) or location_lower in {"us", "usa", "emea", "na"}:
            location_adjustment = -24.0
            location_eligible = False
        elif not location_eligible:
            location_adjustment = -20.0
        elif job.remote and str(getattr(job.remote, "value", job.remote)).lower() == "remote":
            location_adjustment = 7.0
        elif "remote" in location_lower and not any(country in location_lower for country in ("us", "united states", "canada", "europe", "emea")):
            location_adjustment = 6.0
        else:
            location_adjustment = 0.0

        target_terms = ("ai", "machine learning", "ml", "software", "full stack", "fullstack", "backend", "frontend", "data engineer", "python", "react")
        role_boost = 8.0 if any(term in job_title_lower for term in target_terms) else -8.0

        match_pct = round(base_match + entry_boost + location_adjustment + role_boost - seniority_penalty, 1)
        match_pct = max(5, min(100, match_pct))

        skills_matched = sorted(all_matched_set, key=lambda s: (
            s in explicit_job_skills & normalized_resume_skills,
            s in skills_in_title,
            s in normalized_desc_skills & normalized_resume_skills,
        ), reverse=True)[:15]

        if explicit_job_skills:
            missing_skills = sorted(explicit_job_skills - normalized_resume_skills)[:15]
        else:
            missing_skills = []

        ats = self._compute_ats(match_pct, skills_matched, missing_skills)
        interview_pct = self._compute_interview_prob(match_pct, len(skills_matched), len(missing_skills))
        reasoning = self._generate_reasoning(match_pct, skills_matched, missing_skills, job)

        return JobMatch(
            resume_id=resume_id,
            job_id=job.id,
            user_id=user_id,
            match_score=match_pct,
            skills_matched=skills_matched,
            missing_skills=missing_skills,
            ats_compatibility=ats,
            interview_probability=interview_pct,
            salary_fit=self._compute_salary_fit(job),
            experience_fit=self._compute_experience_fit(parsed, job),
            location_fit=self._compute_location_fit(parsed, job),
            growth_potential=min(100.0, match_pct + 12.0),
            learning_difficulty=self._compute_learning_difficulty(missing_skills),
            reasoning=reasoning,
            is_recommended=match_pct >= 42.0 and seniority_penalty == 0 and location_eligible,
        )

    def _title_matches_relevance(self, title: str) -> float:
        keywords = {
            "software engineer", "developer", "frontend", "backend", "full stack",
            "fullstack", "data scientist", "data engineer", "machine learning",
            "ml engineer", "ai engineer", "devops", "sre", "cloud engineer",
            "python", "javascript", "typescript", "react", "node",
            "product manager", "engineering manager", "tech lead",
        }
        for kw in keywords:
            if kw in title:
                return 80.0
        tech_indicators = {"engineer", "developer", "analyst", "scientist", "architect", "specialist"}
        for ti in tech_indicators:
            if ti in title:
                return 50.0
        return 20.0

    def _compute_ats(self, match_pct: float, matched: list, missing: list) -> float:
        base = match_pct
        penalty = len(missing) * 3
        return max(0, min(100, base - penalty))

    def _compute_interview_prob(self, match_pct: float, matched_count: int, missing_count: int) -> float:
        base = match_pct * 0.8
        bonus = matched_count * 1.5
        penalty = missing_count * 2
        return max(0, min(100, base + bonus - penalty))

    def _compute_salary_fit(self, job: Job) -> float:
        if job.salary_min and job.salary_max:
            avg = (job.salary_min + job.salary_max) / 2
            if avg >= 80000:
                return 90.0
            elif avg >= 50000:
                return 70.0
            return 50.0
        return 60.0

    def _compute_experience_fit(self, parsed: dict, job: Job) -> float:
        exp_entries = parsed.get("experience", [])
        years = len(exp_entries) * 1.5
        if years >= 5:
            return 90.0
        elif years >= 3:
            return 75.0
        elif years >= 1:
            return 60.0
        return 40.0

    def _compute_location_fit(self, parsed: dict, job: Job) -> float:
        preferred = parsed.get("preferred_locations", [])
        if not preferred or not job.location:
            return 70.0
        for p in preferred:
            if p.lower() in job.location.lower():
                return 95.0
        return 50.0

    def _compute_learning_difficulty(self, missing_skills: list) -> str:
        if not missing_skills:
            return "easy"
        hard_keywords = {"kubernetes", "tensorflow", "pytorch", "rust", "golang", "aws", "gcp", "azure"}
        hard = sum(1 for s in missing_skills if s.lower() in hard_keywords)
        if hard >= 2:
            return "hard"
        elif hard >= 1:
            return "medium"
        return "easy"

    def _generate_reasoning(self, match_pct: float, matched: list, missing: list, job: Job) -> str:
        parts = []
        if matched:
            matched_str = ", ".join(matched[:4])
            parts.append(f"Your {matched_str} experience aligns with this role.")
        if missing:
            missing_str = ", ".join(missing[:3])
            parts.append(f"Learning {missing_str} could increase your match from {match_pct:.0f}% to {min(100, match_pct + 15):.0f}%.")
        if match_pct >= 80:
            parts.append("Strong alignment.")
        elif match_pct >= 65:
            parts.append("Good potential with some skill gaps.")
        elif match_pct >= 45:
            parts.append("Some relevant skills found. Consider developing missing areas.")
        else:
            parts.append("Limited skill overlap with this role.")
        if not matched and not missing:
            parts.append("Your resume skills are present in the job description suggesting relevance.")
        return " ".join(parts)

    async def get_recommended_jobs(
        self, user_id: uuid.UUID, resume_id: uuid.UUID, limit: int = 10
    ) -> list[JobWithMatchResponse]:
        result = await self.db.execute(
            select(JobMatch)
            .join(Job, Job.id == JobMatch.job_id)
            .where(
                JobMatch.user_id == user_id,
                JobMatch.resume_id == resume_id,
                JobMatch.is_recommended == True,
                Job.is_active == True,
                Job.application_url.is_not(None),
                Job.application_url != "",
            )
            .order_by(desc(JobMatch.match_score))
            .limit(limit)
        )
        matches = result.scalars().all()

        saved_ids = await self._get_saved_ids(user_id)
        applied_ids = await self._get_applied_ids(user_id)

        response = []
        for m in matches:
            job_result = await self.db.execute(
                select(Job).options(selectinload(Job.company)).where(Job.id == m.job_id)
            )
            job = job_result.scalar_one_or_none()
            if not job:
                continue
            response.append(self._job_to_response(job, m, saved_ids, applied_ids))
        return response

    async def get_recent_jobs(
        self, user_id: uuid.UUID, limit: int = 10
    ) -> list[JobWithMatchResponse]:
        result = await self.db.execute(
            select(Job)
            .options(selectinload(Job.company))
            .where(Job.is_active == True)
            .order_by(desc(Job.created_at))
            .limit(limit)
        )
        jobs = result.scalars().all()

        saved_ids = await self._get_saved_ids(user_id)
        applied_ids = await self._get_applied_ids(user_id)

        return [self._job_to_response(j, None, saved_ids, applied_ids) for j in jobs]

    async def generate_career_insights(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> CareerInsightResponse:
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        resume = result.scalar_one_or_none()
        if not resume or not resume.parsed_data:
            raise NotFoundException("Resume not found or not parsed")

        parsed = resume.parsed_data
        skills = parsed.get("skills", [])
        exp = parsed.get("experience", [])
        edu = parsed.get("education", [])
        certs = parsed.get("certifications", [])
        projs = parsed.get("projects", [])

        skill_count = len(skills)
        exp_count = len(exp)
        edu_count = len(edu)
        cert_count = len(certs)
        has_summary = bool(parsed.get("summary", "").strip())

        total_score = skill_count * 5 + exp_count * 8 + edu_count * 6 + cert_count * 4
        if has_summary:
            total_score += 10
        health = min(100, total_score / 2)

        ats_score = min(100, skill_count * 3 + exp_count * 5 + (10 if has_summary else 0) + 20)
        completeness = min(100, (skill_count / 10) * 25 + (exp_count / 3) * 25 + (edu_count / 2) * 20 + (cert_count / 2) * 15 + (15 if has_summary else 0))

        all_text = " ".join(skills + [parsed.get("summary", "")]).lower()
        tech_keywords = {"python", "react", "typescript", "docker", "aws", "sql", "kubernetes"}
        tech_found = [s for s in skills if s.lower() in tech_keywords]
        technical_strength = min(100, len(tech_found) * 15 + exp_count * 5)

        leadership_score = 40.0 + exp_count * 10
        project_quality = min(100, len(projs) * 15 + exp_count * 5)

        weak_bullets = []
        for e in exp:
            for h in e.get("highlights", []):
                if len(h) < 30:
                    weak_bullets.append(h)
        missing_metrics = []
        for e in exp:
            for h in e.get("highlights", []):
                if "%" not in h and not any(c.isdigit() for c in h):
                    if len(h) > 20:
                        missing_metrics.append(h)

        career_level = "Senior" if exp_count >= 3 else "Mid-Level" if exp_count >= 1 else "Entry"
        industry = self._detect_industry(skills)

        insight = CareerInsight(
            user_id=user_id,
            resume_health_score=health,
            ats_score=ats_score,
            technical_strength=technical_strength,
            communication_score=min(100, health * 0.8),
            leadership_score=min(100, leadership_score),
            project_quality=min(100, project_quality),
            skill_coverage=min(100, skill_count * 8),
            completeness=completeness,
            readability=min(100, 70 + (10 if has_summary else 0)),
            industry_alignment=industry,
            career_level=career_level,
            suggested_skills=self._suggest_skills(skills),
            weak_bullet_points=weak_bullets[:10],
            missing_metrics=missing_metrics[:10],
            weak_action_verbs=["led", "managed"] if exp_count > 0 else [],
            formatting_suggestions=["Add quantifiable metrics", "Use stronger action verbs", "Include a professional summary"] if not has_summary else [],
            insights={
                "skill_count": skill_count,
                "experience_count": exp_count,
                "education_count": edu_count,
                "certification_count": cert_count,
                "has_summary": has_summary,
                "career_level": career_level,
                "industry": industry,
            },
        )
        existing = await self.db.execute(
            select(CareerInsight).where(CareerInsight.user_id == user_id)
        )
        old = existing.scalar_one_or_none()
        if old:
            await self.db.delete(old)
            # Flush the deletion before inserting the replacement because the
            # table has a unique constraint on user_id.
            await self.db.flush()
        self.db.add(insight)
        await self.db.flush()

        return CareerInsightResponse(
            resume_health_score=health,
            ats_score=ats_score,
            technical_strength=technical_strength,
            communication_score=min(100, health * 0.8),
            leadership_score=min(100, leadership_score),
            project_quality=min(100, project_quality),
            skill_coverage=min(100, skill_count * 8),
            completeness=completeness,
            readability=min(100, 70 + (10 if has_summary else 0)),
            industry_alignment=industry,
            career_level=career_level,
            suggested_skills=self._suggest_skills(skills),
            weak_bullet_points=weak_bullets[:10],
            missing_metrics=missing_metrics[:10],
            weak_action_verbs=["led", "managed"] if exp_count > 0 else [],
            formatting_suggestions=["Add quantifiable metrics", "Use stronger action verbs", "Include a professional summary"] if not has_summary else [],
            insights={
                "skill_count": skill_count,
                "experience_count": exp_count,
                "education_count": edu_count,
                "certification_count": cert_count,
                "career_level": career_level,
                "industry": industry,
            },
        )

    def _detect_industry(self, skills: list) -> str:
        s_lower = [s.lower() for s in skills]
        if any(k in s_lower for k in ["python", "react", "typescript", "javascript", "java", "go", "rust"]):
            return "Software Engineering"
        if any(k in s_lower for k in ["tensorflow", "pytorch", "machine learning", "deep learning"]):
            return "Machine Learning / AI"
        if any(k in s_lower for k in ["aws", "gcp", "azure", "kubernetes", "docker", "terraform"]):
            return "DevOps / Cloud Infrastructure"
        if any(k in s_lower for k in ["sql", "tableau", "power bi", "data analysis"]):
            return "Data / Analytics"
        if any(k in s_lower for k in ["product", "strategy", "agile", "roadmap"]):
            return "Product Management"
        return "Technology"

    def _suggest_skills(self, existing_skills: list) -> list:
        s_lower = [s.lower() for s in existing_skills]
        suggestions = []
        if "python" not in s_lower:
            suggestions.append("Python")
        if "typescript" not in s_lower and "javascript" not in s_lower:
            suggestions.append("TypeScript")
        if "docker" not in s_lower:
            suggestions.append("Docker")
        if "aws" not in s_lower:
            suggestions.append("AWS")
        if "sql" not in s_lower:
            suggestions.append("SQL")
        if "react" not in s_lower:
            suggestions.append("React")
        if "kubernetes" not in s_lower:
            suggestions.append("Kubernetes")
        if "git" not in s_lower:
            suggestions.append("Git")
        if "ci/cd" not in s_lower:
            suggestions.append("CI/CD")
        if "api" not in s_lower:
            suggestions.append("REST APIs")
        return suggestions[:8]

    async def get_dashboard(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> DashboardResponse:
        insights_result = await self.db.execute(
            select(CareerInsight).where(CareerInsight.user_id == user_id)
        )
        insight = insights_result.scalar_one_or_none()
        insight_resp = CareerInsightResponse.model_validate(insight) if insight else None

        recommended = await self.get_recommended_jobs(user_id, resume_id, 6)
        recent = await self.get_recent_jobs(user_id, 4)

        from app.models.interview import InterviewSchedule
        interviews_result = await self.db.execute(
            select(InterviewSchedule)
            .where(
                InterviewSchedule.user_id == user_id,
                InterviewSchedule.status == "SCHEDULED",
            )
            .order_by(desc(InterviewSchedule.scheduled_at))
            .limit(5)
        )
        interviews = []
        for iv in interviews_result.scalars().all():
            interviews.append({
                "id": str(iv.id),
                "interview_type": iv.interview_type,
                "scheduled_at": iv.scheduled_at.isoformat() if iv.scheduled_at else None,
                "status": iv.status,
            })

        learning_result = await self.db.execute(
            select(LearningPath).where(LearningPath.user_id == user_id).limit(5)
        )
        learning = [LearningPathResponse.model_validate(l) for l in learning_result.scalars().all()]

        from app.models.application import JobApplication
        stats_result = await self.db.execute(
            select(
                func.count(JobApplication.id).label("total"),
                func.sum(case((JobApplication.status == "APPLIED", 1), else_=0)).label("applied"),
                func.sum(case((JobApplication.status == "INTERVIEW", 1), else_=0)).label("interview"),
                func.sum(case((JobApplication.status == "OFFER", 1), else_=0)).label("offer"),
                func.sum(case((JobApplication.status == "REJECTED", 1), else_=0)).label("rejected"),
            ).where(JobApplication.user_id == user_id)
        )
        row = stats_result.one()
        app_stats = {
            "total": row.total or 0,
            "applied": row.applied or 0,
            "interview": row.interview or 0,
            "offer": row.offer or 0,
            "rejected": row.rejected or 0,
        }

        return DashboardResponse(
            resume_health=insight_resp,
            recommended_jobs=recommended,
            recent_jobs=recent,
            upcoming_interviews=interviews,
            application_stats=app_stats,
            learning_path=learning,
            career_insights=insight_resp,
        )

    async def _get_saved_ids(self, user_id: uuid.UUID) -> set:
        result = await self.db.execute(
            select(SavedJob.job_id).where(SavedJob.user_id == user_id)
        )
        return {str(row[0]) for row in result}

    async def _get_applied_ids(self, user_id: uuid.UUID) -> set:
        result = await self.db.execute(
            select(JobApplication.job_id).where(JobApplication.user_id == user_id)
        )
        return {str(row[0]) for row in result}

    def _job_to_response(self, job: Job, match: Optional[JobMatch], saved_ids: set, applied_ids: set) -> JobWithMatchResponse:
        company = None
        if job.company:
            company = {"id": str(job.company.id), "name": job.company.name, "logo_url": job.company.logo_url}

        match_resp = None
        if match:
            match_resp = JobMatchResponse(
                id=str(match.id),
                job_id=str(match.job_id),
                match_score=match.match_score,
                skills_matched=match.skills_matched or [],
                missing_skills=match.missing_skills or [],
                ats_compatibility=match.ats_compatibility,
                interview_probability=match.interview_probability,
                salary_fit=match.salary_fit,
                experience_fit=match.experience_fit,
                location_fit=match.location_fit,
                growth_potential=match.growth_potential,
                learning_difficulty=match.learning_difficulty,
                reasoning=match.reasoning,
                is_recommended=match.is_recommended,
            )

        return JobWithMatchResponse(
            id=str(job.id),
            title=job.title,
            company=company,
            location=job.location,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            remote=job.remote.value if hasattr(job.remote, 'value') else str(job.remote),
            application_url=job.application_url,
            source=job.source.value if hasattr(job.source, 'value') else str(job.source),
            employment_type=job.employment_type,
            posted_at=job.created_at,
            match=match_resp,
            is_saved=str(job.id) in saved_ids,
            has_applied=str(job.id) in applied_ids,
        )
