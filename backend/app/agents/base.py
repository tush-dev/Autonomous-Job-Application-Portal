from abc import ABC, abstractmethod
from typing import Any, Optional
import structlog

logger = structlog.get_logger()


class BaseAgent(ABC):
    def __init__(self):
        self.logger = logger.bind(agent=self.__class__.__name__)
        self.tools = {}

    def register_tool(self, name: str, func):
        self.tools[name] = func

    @abstractmethod
    async def run(self, context: dict) -> dict:
        pass

    async def execute_tool(self, name: str, **kwargs) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        self.logger.info("executing_tool", tool=name, kwargs=kwargs)
        return await self.tools[name](**kwargs)
