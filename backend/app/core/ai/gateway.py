import logging
import time
from typing import Optional

from app.core.ai.models import (
    AIRequest, AIResponse, ProviderConfig,
    RateLimitError, ServerError, TimeoutError_, ProviderError, AllProvidersExhausted,
)
from app.core.ai.cache import AICache
from app.core.ai.providers.gemini import GeminiProvider
from app.core.ai.providers.groq import GroqProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIGateway:
    def __init__(self):
        self._providers: dict[str, object] = {}
        self._primary_provider: Optional[str] = None
        self._fallback_chain: list[str] = []
        self._initialized = False

    def initialize(self):
        gemini_key = settings.GEMINI_API_KEY
        groq_key = settings.GROQ_API_KEY
        default_model = settings.AI_DEFAULT_MODEL
        fallback_model = settings.AI_FALLBACK_MODEL

        if gemini_key:
            self._providers["gemini"] = GeminiProvider(
                ProviderConfig(api_key=gemini_key, model=default_model)
            )
        if groq_key:
            self._providers["groq"] = GroqProvider(
                ProviderConfig(api_key=groq_key, model="llama-3.3-70b-versatile")
            )

        primary = settings.AI_PRIMARY_PROVIDER.lower()
        if primary in self._providers and self._providers[primary].is_available():
            self._primary_provider = primary
        else:
            for name, prov in self._providers.items():
                if prov.is_available():
                    self._primary_provider = name
                    break

        self._fallback_chain = [p for p in ["gemini", "groq"] if p in self._providers and p != self._primary_provider]

        if self._primary_provider:
            logger.info(f"AI gateway ready: primary={self._primary_provider}, fallbacks={self._fallback_chain}")
        else:
            logger.warning("AI gateway initialized with no available providers")

        self._initialized = True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_cache: bool = True,
    ) -> AIResponse:
        if not self._initialized:
            self.initialize()

        if not self._providers:
            return AIResponse(
                content="AI features are not configured. Please add GEMINI_API_KEY or GROQ_API_KEY.",
                provider="none",
                model="none",
            )

        request = AIRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if self._primary_provider:
            providers_to_try = [self._primary_provider] + self._fallback_chain
        else:
            providers_to_try = list(self._providers.keys())

        last_error = None
        for provider_name in providers_to_try:
            provider = self._providers.get(provider_name)
            if not provider or not provider.is_available():
                continue

            if use_cache and provider_name == self._primary_provider:
                cached = await AICache.get(prompt, provider.model)
                if cached is not None:
                    return AIResponse(
                        content=cached,
                        provider=provider_name,
                        model=provider.model,
                        cached=True,
                    )

            try:
                response = await provider.generate(request)

                if use_cache and response.content:
                    await AICache.set(prompt, provider.model, response.content)

                logger.info(
                    "ai_gateway_success provider=%s model=%s latency_ms=%s tokens_in=%s tokens_out=%s",
                    provider_name, provider.model, response.latency_ms,
                    response.tokens_in, response.tokens_out,
                )
                return response

            except RateLimitError as e:
                logger.warning(f"Provider {provider_name} rate limited, trying next: {e}")
                last_error = e
                continue

            except ServerError as e:
                logger.warning(f"Provider {provider_name} server error, trying next: {e}")
                last_error = e
                continue

            except TimeoutError_ as e:
                logger.warning(f"Provider {provider_name} timeout, trying next: {e}")
                last_error = e
                continue

            except ProviderError as e:
                logger.error(f"Provider {provider_name} error: {e}")
                last_error = e
                continue

        logger.error(f"All providers exhausted: {last_error}")
        return AIResponse(
            content="AI service is temporarily unavailable. Please try again later.",
            provider="none",
            model="none",
        )

    async def analyze_resume(self, resume_text: str, job_description: Optional[str] = None) -> dict:
        import json
        prompt = f"""Analyze this resume{' for the following job description: ' + job_description if job_description else ''}.

Resume:
{resume_text}

Return ONLY valid JSON with these exact keys (no markdown):
- strengths: list of key strengths
- weaknesses: list of areas for improvement
- missing_skills: list of important missing skills
- ats_score: estimated ATS compatibility (0-100)
- recommendations: list of actionable recommendations"""
        response = await self.generate(prompt, system_prompt="You are an expert resume analyst.")
        return self._parse_json(response.content, {
            "strengths": [], "weaknesses": [], "missing_skills": [],
            "ats_score": 50, "recommendations": [],
        })

    async def generate_cover_letter(
        self, resume_text: str, job_title: str, company_name: str,
        job_description: str, tone: str = "professional"
    ) -> str:
        prompt = f"""Write a {tone} cover letter for:

Job Title: {job_title}
Company: {company_name}
Job Description: {job_description}

Resume:
{resume_text}

Write a compelling cover letter."""
        response = await self.generate(prompt, system_prompt="You are a professional cover letter writer.")
        return response.content

    async def suggest_career_path(self, resume_text: str, preferences: Optional[str] = None) -> dict:
        import json
        prompt = f"""Based on this resume{' and preferences: ' + preferences if preferences else ''}:

{resume_text}

Return ONLY valid JSON (no markdown):
- suggested_roles: list of suitable job roles
- skills_to_develop: list of skills to acquire
- potential_industries: list of matching industries
- next_steps: list of actionable next steps"""
        response = await self.generate(prompt, system_prompt="You are a career advisor.")
        return self._parse_json(response.content, {
            "suggested_roles": [], "skills_to_develop": [],
            "potential_industries": [], "next_steps": [],
        })

    async def interview_prep(
        self, job_title: str, company_name: str, job_description: str, resume_text: str
    ) -> dict:
        import json
        prompt = f"""Prepare interview questions for:

Job: {job_title}
Company: {company_name}
Description: {job_description}

Resume:
{resume_text}

Return ONLY valid JSON (no markdown):
- technical_questions: list of technical questions with answers
- behavioral_questions: list of behavioral questions with answers
- tips: list of preparation tips
- key_topics: list of topics to review"""
        response = await self.generate(prompt, system_prompt="You are an interview coach.")
        return self._parse_json(response.content, {
            "technical_questions": [], "behavioral_questions": [],
            "tips": [], "key_topics": [],
        })

    def _parse_json(self, text: str, default: dict) -> dict:
        import json
        try:
            cleaned = text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, Exception):
            return default


gateway = AIGateway()


def get_gateway() -> AIGateway:
    return gateway
