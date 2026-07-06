import logging
from abc import ABC, abstractmethod
from typing import Optional

from app.core.ai.models import AIRequest, AIResponse, ProviderConfig

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    name: str = ""
    model: str = ""
    client = None

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.model = config.model

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        ...

    def _build_response(self, content: str, tokens_in: int = 0, tokens_out: int = 0, latency_ms: int = 0) -> AIResponse:
        return AIResponse(
            content=content,
            provider=self.name,
            model=self.model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
        )

    def _error_response(self, message: str) -> AIResponse:
        return self._build_response(content=message)

    def is_available(self) -> bool:
        return bool(self.config.api_key)

    def _log_call(self, request: AIRequest, response: AIResponse, duration: float):
        logger.info(
            "ai_provider_call",
            provider=self.name,
            model=self.model,
            prompt_len=len(request.prompt),
            response_len=len(response.content),
            duration_ms=round(duration * 1000),
            cached=response.cached,
        )
