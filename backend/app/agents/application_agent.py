from app.agents.base import BaseAgent


class ApplicationAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        return {"type": "application", "status": "submitted", "result": {}}
