import json
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.providers import LLMProvider, MockProvider, ProviderError, get_provider

@pytest.fixture(autouse=True)
def mock_mode(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")

def test_demo_api():
    client = TestClient(app)
    response = client.post("/analyze", json={"text": "FICTITIOUS invoice payment on 2025-01-20."})
    assert response.status_code == 200
    assert response.json()["provider"] == "mock"
    assert response.json()["analysis"]["category"] == "financial"
    assert response.json()["analysis"]["dates"] == ["2025-01-20"]

@pytest.mark.parametrize("text", ["short", " " * 30, "x" * 20001])
def test_input_limits(text):
    assert TestClient(app).post("/analyze", json={"text": text}).status_code == 422

def test_technical_and_general():
    assert MockProvider().analyze("FICTITIOUS API database error").category == "technical"
    assert MockProvider().analyze("FICTITIOUS meeting about activities").category == "general"

def test_llm_success(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-only-placeholder")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    result = MockProvider().analyze("FICTITIOUS invoice payment").model_dump()
    def handler(request):
        payload = json.loads(request.content)
        assert payload["response_format"]["type"] == "json_object"
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(result)}}]})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert LLMProvider(client).analyze("FICTITIOUS invoice").category == "financial"

@pytest.mark.parametrize("status,body", [(429, {}), (200, {}), (200, {"choices": [{"message": {"content": "{}"}}]})])
def test_llm_failures(monkeypatch, status, body):
    monkeypatch.setenv("LLM_API_KEY", "test-only-placeholder")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, json=body))) as client:
        with pytest.raises(ProviderError):
            LLMProvider(client).analyze("FICTITIOUS")

def test_configuration_errors(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        LLMProvider()
    monkeypatch.setenv("AI_PROVIDER", "invalid")
    assert TestClient(app).post("/analyze", json={"text": "FICTITIOUS document for analysis."}).status_code == 502
