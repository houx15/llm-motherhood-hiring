"""Async OpenRouter client: pinned slugs, provider pinning, retries, usage capture.

Spec §6: retries with backoff on 429/5xx/timeouts (max 5); NO retry on content
refusals; record the provider that served each request; request JSON mode.
"""
from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .config import ModelCfg

BASE_URL = "https://openrouter.ai/api/v1"


class RefusalError(Exception):
    """Model declined to answer (content refusal) — never retried."""


class TransportFailure(Exception):
    """Gave up after retries on 429/5xx/timeout."""


def _retryable(exc: BaseException) -> bool:
    if isinstance(exc, RefusalError):
        return False
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    return False


class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL, timeout: float = 180.0):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/llm-hiring-audit",
                "X-Title": "llm-hiring-audit",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        self._live_prices: dict[str, dict[str, float]] = {}

    async def __aenter__(self) -> "OpenRouterClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.client.aclose()

    async def fetch_live_prices(self) -> dict[str, dict[str, float]]:
        """GET /models; returns {slug: {'input': usd_per_mtok, 'output': usd_per_mtok}}."""
        r = await self.client.get("/models")
        r.raise_for_status()
        out: dict[str, dict[str, float]] = {}
        for m in r.json().get("data", []):
            p = m.get("pricing", {})
            try:
                out[m["id"]] = {
                    "input": float(p.get("prompt", 0)) * 1e6,
                    "output": float(p.get("completion", 0)) * 1e6,
                }
            except (TypeError, ValueError):
                continue
        self._live_prices = out
        return out

    def live_price(self, cfg: ModelCfg) -> tuple[float, float] | None:
        """max(live, config) per spec §6: if live is higher, use live."""
        live = self._live_prices.get(cfg.slug)
        if not live:
            return None
        cfg_in = cfg.price_per_mtok.get("input", 0.0)
        cfg_out = cfg.price_per_mtok.get("output", 0.0)
        return max(live["input"], cfg_in), max(live["output"], cfg_out)

    async def chat(self, cfg: ModelCfg, user_prompt: str, system_prompt: str | None = None):
        """One chat completion. Returns dict with content/usage/finish/provider.

        Raises TransportFailure / RefusalError.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        body: dict[str, Any] = {
            "model": cfg.slug,
            "messages": messages,
            "max_tokens": cfg.max_tokens,
            "provider": cfg.provider.model_dump(exclude_none=True),
        }
        if cfg.temperature is not None:
            body["temperature"] = cfg.temperature
        if cfg.reasoning:
            body["reasoning"] = cfg.reasoning
        body["response_format"] = {"type": "json_object"}

        attempts_config: list[dict[str, Any]] = [body, {k: v for k, v in body.items() if k != "response_format"}, {k: v for k, v in body.items() if k not in ("response_format", "reasoning")}]

        last_error: Exception | None = None
        for bi, b in enumerate(attempts_config):
            try:
                return await self._chat_once(cfg, b, user_prompt)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    detail = e.response.text[:500]
                    if any(
                        k in detail.lower()
                        for k in ("response_format", "reasoning", "unsupported", "not supported", "invalid")
                    ) and bi < len(attempts_config) - 1:
                        last_error = e
                        continue
                last_error = e
                if not _retryable(e):
                    raise
            except Exception as e:  # noqa: BLE001
                last_error = e
                if not _retryable(e):
                    raise
        raise TransportFailure(f"gave up: {last_error}")

    async def _chat_once(self, cfg: ModelCfg, body: dict, user_prompt: str) -> dict:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(5),
                wait=wait_exponential(multiplier=1, min=1, max=30, exp_base=2),
                retry=retry_if_exception(_retryable),
                reraise=True,
            ):
                with attempt:
                    req_start = asyncio.get_event_loop().time()
                    r = await self.client.post("/chat/completions", json=body)
                    latency_ms = int((asyncio.get_event_loop().time() - req_start) * 1000)
                    if r.status_code >= 400:
                        raise httpx.HTTPStatusError(
                            f"HTTP {r.status_code}: {r.text[:300]}",
                            request=r.request,
                            response=r,
                        )
                    data = r.json()
                    choice = (data.get("choices") or [{}])[0]
                    message = choice.get("message", {}) or {}
                    content = message.get("content") or ""
                    finish = choice.get("finish_reason")
                    # Content refusal: finish with no content + refusal flag in message
                    if message.get("refusal") or (finish == "content_filter" and not content):
                        raise RefusalError(str(message.get("refusal") or finish))
                    usage = data.get("usage", {}) or {}
                    provider = (
                        data.get("provider")
                        or (choice.get("provider") if isinstance(choice, dict) else None)
                        or data.get("endpoint_provider")
                    )
                    return {
                        "content": content,
                        "finish_reason": finish,
                        "http_status": r.status_code,
                        "latency_ms": latency_ms,
                        "input_tokens": usage.get("prompt_tokens"),
                        "output_tokens": usage.get("completion_tokens"),
                        "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get(
                            "reasoning_tokens"
                        ),
                        "cost_usd": usage.get("cost"),
                        "provider_served": provider.get("name") if isinstance(provider, dict) else provider,
                        "raw": data,
                    }
        except RetryError as e:  # pragma: no cover - reraise=True makes this rare
            raise TransportFailure(str(e)) from e
