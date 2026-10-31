"""API tests in demo mode (no GROQ_API_KEY) plus a scripted-LLM agent-mode test."""

import json

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from marketing_campaign import api, service
from marketing_campaign.data import create_database


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    db = create_database(tmp_path / "products.db")
    original_generate, original_list = service.generate, service.list_products
    monkeypatch.setattr(service, "generate", lambda *a, **k: original_generate(*a, db_path=db, **k))
    monkeypatch.setattr(service, "list_products", lambda: original_list(db))
    return TestClient(api.app)


def test_health_demo(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["demo"] is True


def test_products(client):
    items = client.get("/api/products").json()
    assert [p["product_id"] for p in items] == ["P1011", "P1012", "P1013", "P1014", "P1015"]


def test_demo_campaign_shape_and_checks(client):
    r = client.post("/api/campaigns", json={"product_id": "1012"})
    assert r.status_code == 200
    body = r.json()
    assert body["demo"] is True and body["product"]["product_id"] == "P1012"
    c = body["campaigns"][0]
    assert c["title"] and c["email_body"] and c["cta"]
    assert {x["id"] for x in c["checks"]} >= {"email_length", "no_banned", "product_named"}
    assert all(x["passed"] for x in c["checks"]), c["checks"]


@pytest.mark.parametrize("pid", ["abc", "P1; DROP TABLE products", ""])
def test_invalid_id_is_400(client, pid):
    assert client.post("/api/campaigns", json={"product_id": pid}).status_code == 400


def test_unknown_id_is_404(client):
    assert client.post("/api/campaigns", json={"product_id": "P9999"}).status_code == 404


def test_validation_bounds(client):
    assert client.post("/api/campaigns", json={"product_id": "P1011", "temperature": 5}).status_code == 422
    assert client.post("/api/campaigns", json={"product_id": "P1011", "mode": "nope"}).status_code == 422


def test_agent_mode_with_scripted_llms(tmp_path, monkeypatch):
    """Agent mode: campaign is read from the tool's observation, trace steps are returned."""
    from marketing_campaign import llm as llm_mod

    db = create_database(tmp_path / "products.db")
    monkeypatch.setenv("GROQ_API_KEY", "test")
    campaign_json = json.dumps({"title": "Grow Your Future", "email_subject": "Hello",
                                "email_body": "Golden Future Mutual Fund " + "word " * 110, "cta": "Invest now"})

    class FakeWithStructured(FakeListChatModel):
        def with_structured_output(self, schema, **kw):
            from langchain_core.runnables import RunnableLambda
            return RunnableLambda(lambda _: schema.model_validate_json(campaign_json))

    # Creative mode is off, so one model object serves both agents: script all four replies in order.
    shared = FakeWithStructured(responses=[
        "Thought: query it.\nAction: sql_db_query\nAction Input: SELECT * FROM products WHERE product_id = 'P1011'",
        "Thought: done.\nFinal Answer: product_name: Golden Future Mutual Fund",
        "Thought: use tool.\nAction: Campaign Generator\nAction Input: Golden Future Mutual Fund",
        "Thought: done.\nFinal Answer: Here is your campaign"])
    monkeypatch.setattr(llm_mod, "get_llm", lambda *a, **k: shared)
    out = service.generate("P1011", mode="agent", db_path=db)
    assert out["demo"] is False
    assert out["campaigns"][0]["title"] == "Grow Your Future"
    assert [s["tool"] for s in out["steps"]] == ["sql_db_query", "Campaign Generator"]
