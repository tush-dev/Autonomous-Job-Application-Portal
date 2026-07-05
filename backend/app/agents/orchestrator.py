from typing import Any, Optional
import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class OrchestratorAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        intent = context.get("intent", "unknown")
        self.logger.info("orchestrating", intent=intent)

        if intent == "resume_analysis":
            return await self._route_to_agent("resume_agent", context)
        elif intent == "job_search":
            return await self._route_to_agent("job_search_agent", context)
        elif intent == "resume_tailor":
            return await self._route_to_agent("resume_optimizer", context)
        elif intent == "cover_letter":
            return await self._route_to_agent("cover_letter_agent", context)
        elif intent == "apply":
            return await self._route_to_agent("application_agent", context)
        elif intent == "career_advice":
            return await self._route_to_agent("career_advisor", context)
        else:
            return {"response": "I can help with career-related tasks."}

    async def _route_to_agent(self, agent_name: str, context: dict) -> dict:
        from app.agents.resume_agent import ResumeAgent
        from app.agents.job_search_agent import JobSearchAgent
        from app.agents.resume_optimizer_agent import ResumeOptimizerAgent
        from app.agents.cover_letter_agent import CoverLetterAgent
        from app.agents.application_agent import ApplicationAgent
        from app.agents.career_advisor_agent import CareerAdvisorAgent

        agents = {
            "resume_agent": ResumeAgent,
            "job_search_agent": JobSearchAgent,
            "resume_optimizer": ResumeOptimizerAgent,
            "cover_letter_agent": CoverLetterAgent,
            "application_agent": ApplicationAgent,
            "career_advisor": CareerAdvisorAgent,
        }

        agent_class = agents.get(agent_name)
        if not agent_class:
            return {"error": f"Unknown agent: {agent_name}"}

        agent = agent_class()
        return await agent.run(context)
