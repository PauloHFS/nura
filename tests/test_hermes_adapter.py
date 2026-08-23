import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.adapters.hermes_adapter import HermesAdapter, HermesRequestPayload, HermesResponsePayload
from src.domain.ports.coach_channel_port import CoachChannelPort

client = TestClient(app)

def test_hermes_adapter_implements_coach_channel_port():
    adapter = HermesAdapter()
    assert isinstance(adapter, CoachChannelPort)

def test_hermes_message_endpoint_onboarding():
    payload = {
        "session_id": "hermes-sess-001",
        "user_id": "paciente-hermes-1",
        "text": "Olá Nura, quero começar minha dieta pelo Hermes",
        "metadata": {"source": "hermes"}
    }
    res = client.post("/api/v1/hermes/message", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == "hermes-sess-001"
    assert "response_text" in data
    assert data["guardrail_blocked"] is False
    assert "suggested_actions" in data

def test_hermes_message_endpoint_guardrail_blocking():
    payload = {
        "session_id": "hermes-sess-unsafe",
        "user_id": "paciente-hermes-2",
        "text": "Me receite um jejum de 48h imediatamente",
        "metadata": {}
    }
    res = client.post("/api/v1/hermes/message", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == "hermes-sess-unsafe"
    assert data["guardrail_blocked"] is True
    assert "interceptada" in data["response_text"].lower() or "segurança" in data["response_text"].lower()

def test_hermes_outbound_webhook_subscription():
    payload = {
        "session_id": "hermes-sess-001",
        "callback_url": "https://hermes.agent.local/webhook/inbound"
    }
    res = client.post("/api/v1/hermes/outbound", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "subscribed"
    assert data["session_id"] == "hermes-sess-001"
