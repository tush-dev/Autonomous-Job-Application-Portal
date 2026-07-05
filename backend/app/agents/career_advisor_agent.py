from app.agents.base import BaseAgent


class CareerAdvisorAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        return {"type": "career_advice", "suggestions": [], "roadmap": []}
