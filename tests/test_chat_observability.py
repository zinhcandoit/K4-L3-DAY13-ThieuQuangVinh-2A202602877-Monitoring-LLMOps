from __future__ import annotations

import json
import asyncio
from pathlib import Path

import httpx

from app import logging_config
from app.main import app


def test_chat_response_log_exposes_quality_for_dashboard(
    monkeypatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    async def send_request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            return await client.post(
                "/chat",
                json={
                    "user_id": "student-01",
                    "session_id": "session-01",
                    "feature": "qa",
                    "message": "Explain observability",
                },
            )

    response = asyncio.run(send_request())

    assert response.status_code == 200
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    response_event = next(event for event in events if event["event"] == "response_sent")
    assert response_event["quality_score"] == response.json()["quality_score"]
    assert response_event["ttft_ms"] == response.json()["ttft_ms"]
    assert response_event["tool_name"] == "retrieval"
    assert response_event["tool_success"] is True


def test_correlation_id_headers_and_log_enrichment(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    async def send_request(headers=None) -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            return await client.post(
                "/chat",
                headers=headers or {},
                json={
                    "user_id": "u01",
                    "session_id": "s01",
                    "feature": "qa",
                    "message": "My email is test@domain.com and phone is 0901234567",
                },
            )

    # 1. Custom x-request-id provided
    res1 = asyncio.run(send_request(headers={"x-request-id": "req-custom01"}))
    assert res1.status_code == 200
    assert res1.headers.get("x-request-id") == "req-custom01"
    assert "x-response-time-ms" in res1.headers

    # 2. Auto-generated x-request-id
    res2 = asyncio.run(send_request())
    assert res2.status_code == 200
    generated_id = res2.headers.get("x-request-id")
    assert generated_id.startswith("req-")
    assert len(generated_id) == 12  # req- + 8 hex chars
    assert "x-response-time-ms" in res2.headers

    lines = log_path.read_text(encoding="utf-8").splitlines()
    records = [json.loads(l) for l in lines]
    for r in records:
        if r.get("service") == "api":
            assert r.get("correlation_id") in ("req-custom01", generated_id)
            assert "user_id_hash" in r
            assert "session_id" in r
            assert "feature" in r
            assert "model" in r
            # Verify no raw PII in any log record
            raw = json.dumps(r)
            assert "test@domain.com" not in raw
            assert "0901234567" not in raw

    request_events = [r for r in records if r.get("event") == "request_received"]
    assert len(request_events) == 2
    for req_ev in request_events:
        raw_req = json.dumps(req_ev)
        assert "[REDACTED_EMAIL]" in raw_req
        assert "[REDACTED_PHONE_VN]" in raw_req


