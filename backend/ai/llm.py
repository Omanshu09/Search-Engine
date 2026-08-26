"""
LLM client abstraction.

Supports Anthropic and OpenAI's chat-completion REST APIs directly via
httpx (no SDK dependency). If no provider/key is configured, `is_configured`
is False and callers (rag.py, claim_extractor.py) are expected to fall back
to non-LLM behavior instead of calling complete().
"""
import httpx

from backend.utils.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4o-mini",
}


class LLMClient:
    def __init__(self, provider: str = "", api_key: str = "", model: str = ""):
        self.provider = provider.lower().strip()
        self.api_key = api_key
        self.model = model or _DEFAULT_MODELS.get(self.provider, "")

    @property
    def is_configured(self) -> bool:
        return bool(self.provider and self.api_key)

    def complete(self, prompt: str, max_tokens: int = 1000) -> str:
        if not self.is_configured:
            raise RuntimeError("LLMClient.complete() called without a configured provider/key")

        if self.provider == "anthropic":
            return self._complete_anthropic(prompt, max_tokens)
        if self.provider == "openai":
            return self._complete_openai(prompt, max_tokens)
        raise ValueError(f"Unsupported LLM provider: {self.provider!r}")

    def _complete_anthropic(self, prompt: str, max_tokens: int) -> str:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return "".join(block.get("text", "") for block in data.get("content", []))

    def _complete_openai(self, prompt: str, max_tokens: int) -> str:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
