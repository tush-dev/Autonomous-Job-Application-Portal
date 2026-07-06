import logging
import time

from google.genai import types as genai_types

from app.core.ai.models import AIRequest, AIResponse, RateLimitError, ServerError, TimeoutError_, ProviderError
from app.core.ai.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, config):
        super().__init__(config)
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            self.client = genai.Client(api_key=self.config.api_key)
            logger.info(f"Gemini client initialized (model={self.model})")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None

    def is_available(self) -> bool:
        return bool(self.config.api_key) and self.client is not None

    async def generate(self, request: AIRequest) -> AIResponse:
        start = time.monotonic()
        try:
            contents = []
            if request.system_prompt:
                contents.append(f"System: {request.system_prompt}\n\nUser: {request.prompt}")
            else:
                contents.append(request.prompt)

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_tokens,
                ),
            )

            elapsed = time.monotonic() - start
            text = response.text or ""
            usage = getattr(response, "usage_metadata", None)
            tokens_in = usage.prompt_token_count if usage else 0
            tokens_out = usage.candidates_token_count if usage else 0

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

            if any(x in err_str for x in ["429", "resource_exhausted", "quota"]):
                raise RateLimitError(f"Gemini quota exceeded (latency={round(elapsed*1000)}ms)") from e
            if any(x in err_str for x in ["500", "502", "503", "504", "internal", "unavailable"]):
                raise ServerError(f"Gemini server error (latency={round(elapsed*1000)}ms)") from e
            if any(x in err_str for x in ["deadline", "timeout", "timed out"]):
                raise TimeoutError_(f"Gemini timeout (latency={round(elapsed*1000)}ms)") from e

            raise ProviderError(f"Gemini error: {e}") from e
