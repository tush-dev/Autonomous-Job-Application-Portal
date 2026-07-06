import logging
import time

from app.core.ai.models import AIRequest, AIResponse, RateLimitError, ServerError, TimeoutError_, ProviderError
from app.core.ai.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseProvider):
    name = "groq"

    def __init__(self, config):
        super().__init__(config)
        self._init_client()

    def _init_client(self):
        try:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=self.config.api_key)
            logger.info(f"Groq client initialized (model={self.model})")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def is_available(self) -> bool:
        return bool(self.config.api_key) and self.client is not None

    async def generate(self, request: AIRequest) -> AIResponse:
        start = time.monotonic()
        try:
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            elapsed = time.monotonic() - start
            choice = response.choices[0] if response.choices else None
            text = choice.message.content if choice else ""
            usage = getattr(response, "usage", None)
            tokens_in = usage.prompt_tokens if usage else 0
            tokens_out = usage.completion_tokens if usage else 0

            return self._build_response(
                content=text,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=round(elapsed * 1000),
            )

        except (RateLimitError, ServerError, TimeoutError_):
            raise
        except Exception as e:
            elapsed = time.monotonic() - start
            err_str = str(e).lower()

            if any(x in err_str for x in ["429", "rate_limit", "quota"]):
                raise RateLimitError(f"Groq rate limited (latency={round(elapsed*1000)}ms)") from e
            if any(x in err_str for x in ["500", "502", "503", "504"]):
                raise ServerError(f"Groq server error (latency={round(elapsed*1000)}ms)") from e
            if any(x in err_str for x in ["timeout", "timed out"]):
                raise TimeoutError_(f"Groq timeout (latency={round(elapsed*1000)}ms)") from e

            raise ProviderError(f"Groq error: {e}") from e
