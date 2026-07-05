"""Seed the database with sample data for development."""
import asyncio
import uuid
from datetime import datetime, timezone, timedelta

from app.core.database import async_session_factory, engine
from app.models.base import Base
from app.models.user import User, UserSettings, UserPreferences, UserRole
from app.models.job import Company, Job, JobSource, RemoteType
from app.core.security import get_password_hash


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        admin = User(
            id=uuid.uuid4(),
            email="admin@jobagent.ai",
            password_hash=get_password_hash("AdminP@ss123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_verified=True,
        )
        session.add(admin)
        session.add(UserSettings(user_id=admin.id))

        demo = User(
            id=uuid.uuid4(),
            email="demo@jobagent.ai",
            password_hash=get_password_hash("DemoP@ss123"),
            full_name="Demo User",
            role=UserRole.USER,
            is_verified=True,
        )
        session.add(demo)
        session.add(UserSettings(user_id=demo.id))
        session.add(
            UserPreferences(
                user_id=demo.id,
                preferred_locations=["San Francisco", "Remote"],
                preferred_remote="remote",
                salary_min=120000,
                salary_max=200000,
                preferred_industries=["technology"],
                keywords=["python", "react", "aws"],
            )
        )

        google = Company(
            id=uuid.uuid4(),
            name="Google",
            website="https://google.com",
            logo_url="https://logo.clearbit.com/google.com",
            description="Search and AI technology company",
            industry="Technology",
            size="10000+",
            headquarters="Mountain View, CA",
            careers_page_url="https://careers.google.com",
        )
        session.add(google)

        companies_data = [
            ("Stripe", "Fintech", "https://stripe.com"),
            ("Notion", "Productivity", "https://notion.so"),
            ("Linear", "Project Management", "https://linear.app"),
            ("Vercel", "Cloud Platform", "https://vercel.com"),
            ("Anthropic", "AI Safety", "https://anthropic.com"),
            ("OpenAI", "AI Research", "https://openai.com"),
        ]

        companies = {"Google": google}
        for name, industry, website in companies_data:
            company = Company(
                id=uuid.uuid4(),
                name=name,
                website=website,
                logo_url=f"https://logo.clearbit.com/{website.replace('https://', '')}",
                industry=industry,
            )
            session.add(company)
            companies[name] = company

        jobs_data = [
            ("Google", "Senior Software Engineer", "Build and scale distributed systems for search and AI products.", "Mountain View, CA", "hybrid", 180000, 350000, ["Python", "Go", "Distributed Systems", "ML"], "senior"),
            ("Google", "Frontend Engineer", "Develop next-generation web applications.", "New York, NY", "hybrid", 150000, 280000, ["React", "TypeScript", "CSS", "Web Performance"], "mid"),
            ("Stripe", "Backend Engineer", "Build payment infrastructure APIs.", "San Francisco, CA", "remote", 160000, 300000, ["Ruby", "Java", "Kafka", "PostgreSQL"], "mid"),
            ("Stripe", "Developer Advocate", "Create developer content and improve API developer experience.", "Remote", "remote", 140000, 220000, ["API Design", "Writing", "Public Speaking"], "mid"),
            ("Notion", "Full Stack Engineer", "Build the all-in-one workspace.", "New York, NY", "hybrid", 150000, 280000, ["React", "TypeScript", "Go", "PostgreSQL"], "mid"),
            ("Linear", "Product Engineer", "Build better issue tracking and project management.", "Remote", "remote", 140000, 260000, ["React", "TypeScript", "GraphQL", "PostgreSQL"], "mid"),
            ("Vercel", "Frontend Infrastructure Engineer", "Build tools that power the frontend ecosystem.", "Remote", "remote", 150000, 280000, ["React", "Next.js", "Rust", "Webpack"], "mid"),
            ("Anthropic", "Research Engineer", "Advance AI safety through research and engineering.", "San Francisco, CA", "onsite", 200000, 400000, ["Python", "PyTorch", "NLP", "RLHF"], "senior"),
            ("OpenAI", "Applied AI Engineer", "Build production AI systems.", "San Francisco, CA", "onsite", 200000, 450000, ["Python", "PyTorch", "Rust", "Distributed Systems"], "senior"),
            ("Google", "Site Reliability Engineer", "Ensure reliability of Google-scale systems.", "Sunnyvale, CA", "hybrid", 170000, 320000, ["Go", "Kubernetes", "Linux", "Monitoring"], "senior"),
        ]

        for company_name, title, desc, location, remote, salary_min, salary_max, skills, level in jobs_data:
            company = companies[company_name]
            job = Job(
                id=uuid.uuid4(),
                company_id=company.id,
                source=JobSource.MANUAL,
                source_job_id=str(uuid.uuid4()),
                title=title,
                description=desc,
                location=location,
                remote=RemoteType(remote),
                salary_min=salary_min,
                salary_max=salary_max,
                employment_type="full-time",
                experience_level=level,
                skills_required=skills,
                application_url=f"https://example.com/apply/{uuid.uuid4().hex[:8]}",
                created_at=datetime.now(timezone.utc) - timedelta(hours=len(jobs_data)),
            )
            session.add(job)

        await session.commit()
        print("✓ Database seeded!")
        print("  Admin: admin@jobagent.ai / AdminP@ss123")
        print("  Demo:  demo@jobagent.ai / DemoP@ss123")
        print("  10 jobs added across 7 companies")


if __name__ == "__main__":
    asyncio.run(seed())
