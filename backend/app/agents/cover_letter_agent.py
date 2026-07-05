from app.agents.base import BaseAgent


class CoverLetterAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        return {"type": "cover_letter", "content": "", "tone": "professional"}


class ApplicationAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        return {"type": "application", "status": "submitted", "result": {}}


class CareerAdvisorAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        return {"type": "career_advice", "suggestions": [], "roadmap": []}
