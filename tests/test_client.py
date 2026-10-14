"""Client tests with mocked OpenRouter transport: retry on 429, no retry on
refusal, provider mismatch flagging."""
import httpx
import pytest

from audit.client import OpenRouterClient, RefusalError, TransportFailure
from audit.config import ModelCfg, ProviderCfg

CFG = ModelCfg(
    key="deepseek_v41_flash",
    slug="deepseek/deepseek-v4.1-flash",
    verified=True,
    provider=ProviderCfg(order=["DeepSeek"], allow_fallbacks=False),
    reasoning={"enabled": False},
    temperature=None,
    max_tokens=600,
    price_per_mtok={"input": 0.016, "output": 0.891},
    peak_multiplier=2.0,
)

OK_BODY = {
    "choices": [
        {"message": {"content": '{"overall_fit": 8}'}, "finish_reason": "stop",
         "provider": {"name": "DeepSeek"}}
    ],
    "usage": {"prompt_tokens": 100, "completion_tokens": 20, "cost": 0.001},
}


def _client(handler):
    c = OpenRouterClient.__new__(OpenRouterClient)
    c.api_key = "test"
    c.client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://openrouter.test/v1"
    )
    c._live_prices = {}
    return c


async def test_retry_on_429_then_success():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, json={"error": "rate limited"})
        return httpx.Response(200, json=OK_BODY)

    c = _client(handler)
    resp = await c.chat(CFG, "hi")
    assert calls["n"] == 2
    assert resp["provider_served"] == "DeepSeek"
    assert resp["cost_usd"] == 0.001
    await c.client.aclose()


async def test_gives_up_after_5():
    def handler(request):
        return httpx.Response(503, json={"error": "boom"})

    c = _client(handler)
    with pytest.raises((TransportFailure, httpx.HTTPStatusError)):
        await c.chat(CFG, "hi")
    await c.client.aclose()


async def test_refusal_not_retried():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        body = {"choices": [{"message": {"refusal": "I cannot do that"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
        return httpx.Response(200, json=body)

    c = _client(handler)
    with pytest.raises(RefusalError):
        await c.chat(CFG, "hi")
    assert calls["n"] == 1
    await c.client.aclose()


async def test_provider_mismatch_flag():
    def handler(request):
        body = dict(OK_BODY)
        body["choices"] = [dict(OK_BODY["choices"][0], provider={"name": "OtherCorp"})]
        return httpx.Response(200, json=body)

    c = _client(handler)
    resp = await c.chat(CFG, "hi")
    assert resp["provider_served"] == "OtherCorp"  # runner compares to pinned provider
    await c.client.aclose()


async def test_400_response_format_fallback():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(400, text='{"error": "response_format not supported"}')
        return httpx.Response(200, json=OK_BODY)

    c = _client(handler)
    resp = await c.chat(CFG, "hi")
    assert calls["n"] == 2  # retried without response_format
    await c.client.aclose()
