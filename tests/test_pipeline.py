"""Offline tests: scripted fake LLMs stand in for Groq, so no API key is needed."""

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from marketing_campaign import agents
from marketing_campaign.data import create_database, fetch_product, normalize_product_id


@pytest.fixture
def db_path(tmp_path):
    return create_database(tmp_path / "products.db")


@pytest.mark.parametrize("raw", ["P1011", "p1011", "1011", "  P1011 "])
def test_normalize_product_id(raw):
    assert normalize_product_id(raw) == "P1011"


@pytest.mark.parametrize("raw", ["", "abc", "P10; DROP TABLE products"])
def test_normalize_product_id_rejects_garbage(raw):
    with pytest.raises(ValueError):
        normalize_product_id(raw)


def test_fetch_product(db_path):
    assert fetch_product("1012", db_path)["product_name"] == "Golden Years Savings Account"
    assert fetch_product("P9999", db_path) is None


def test_database_is_read_only_for_agent(db_path):
    db = agents.load_database(db_path)
    assert "P1013" in db.run("SELECT product_id FROM products WHERE product_id='P1013'")
    with pytest.raises(Exception):
        db.run("DELETE FROM products")


SQL_SCRIPT = [
    "Thought: I should query the products table.\n"
    "Action: sql_db_query\n"
    "Action Input: SELECT * FROM products WHERE product_id = 'P1011'",
    "Thought: I now know the final answer.\n"
    "Final Answer: product_name: Golden Future Mutual Fund, target_age: 30-50",
]

CAMPAIGN_SCRIPT = [
    "Thought: I should use the campaign tool.\n"
    "Action: Campaign Generator\n"
    "Action Input: Golden Future Mutual Fund, target_age: 30-50",
    "Thought: I now know the final answer.\n"
    "Final Answer: **Marketing Title:** Grow Your Future",
]


def test_sql_agent_returns_product_text(db_path):
    sql_agent = agents.build_sql_agent(FakeListChatModel(responses=SQL_SCRIPT), db_path)
    assert "Golden Future Mutual Fund" in agents.fetch_product_with_agent(sql_agent, "1011")


def test_end_to_end_with_fake_llms(db_path):
    sql_agent = agents.build_sql_agent(FakeListChatModel(responses=SQL_SCRIPT), db_path)
    campaign_agent = agents.build_campaign_agent(
        FakeListChatModel(responses=CAMPAIGN_SCRIPT),
        tool_llm=FakeListChatModel(responses=["**Marketing Title:** Grow Your Future"]),
    )
    assert "Grow Your Future" in agents.generate_campaign("P1011", sql_agent, campaign_agent)
