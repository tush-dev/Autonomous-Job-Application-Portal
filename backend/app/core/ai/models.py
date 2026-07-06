from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AIRequest:
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    cached: bool = False
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0


@dataclass
class ProviderConfig:
    api_key: str
    model: str
    timeout: int = 30


class RateLimitError(Exception):
    ...


class ServerError(Exception):
    ...


class TimeoutError_(Exception):
    ...


class ProviderError(Exception):
    ...


class AllProvidersExhausted(Exception):
    ...

