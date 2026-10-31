"""SQL agent, campaign tool/agent and the end-to-end pipeline."""

from pathlib import Path
from typing import Optional

from langchain.agents import AgentType, Tool, initialize_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage

from marketing_campaign.data import DEFAULT_DB_PATH, fetch_product, format_product, normalize_product_id
from marketing_campaign.schemas import CampaignAssets

SQL_SYSTEM_MESSAGE = (
    "You are an SQL assistant. Your role is to efficiently fetch and retrieve product data "
    "from the database. Only run read-only SELECT queries.\n\n"
)

CAMPAIGN_PROMPT = """
You are a marketing campaign generator. Your task is to create a compelling marketing title, an
engaging email draft, and a strong call-to-action (CTA) based on the provided product details.
Ensure the content is professional, polite, and aligned with the product's marketing objectives.
Do not invent returns, guarantees or numbers that are not in the product details.

### Product Details:
{product_details}

Please generate:
1. **Marketing Title:** (A short, catchy, and memorable tagline)
2. **Email Draft:** (A professional, polite, and engaging email to promote the product, around 100-150 words)
3. **Call-to-Action (CTA):** (A persuasive instruction that motivates the target audience to take the desired action)
"""


def load_database(db_path=DEFAULT_DB_PATH) -> SQLDatabase:
    """Open the products database read-only so the agent cannot modify data."""
    return SQLDatabase.from_uri(
        f"sqlite:///file:{Path(db_path)}?mode=ro&uri=true", include_tables=["products"]
    )


def build_sql_agent(llm, db_path=DEFAULT_DB_PATH, verbose: bool = False, return_steps: bool = False):
    """ReAct SQL agent: LLM decides which SQL tools to call (list tables, schema, query)."""
    return create_sql_agent(
        llm=llm,
        db=load_database(db_path),
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prefix=SQL_SYSTEM_MESSAGE + "You have access to the following tools:",
        verbose=verbose,
        max_iterations=8,
        agent_executor_kwargs={"handle_parsing_errors": True, "return_intermediate_steps": return_steps},
    )


def make_campaign_tool(llm, structured: bool = False) -> Tool:
    """Wrap campaign generation as a LangChain Tool an agent can call.

    With structured=True the tool returns CampaignAssets as JSON, so callers can read the
    tool's observation instead of trusting the agent to repeat it verbatim.
    """

    def campaign_generation_func(product_details: str) -> str:
        if structured:
            return generate_structured_campaign(llm, product_details).model_dump_json()
        prompt = CAMPAIGN_PROMPT.format(product_details=product_details)
        return llm.invoke([HumanMessage(content=prompt)]).content.strip()

    return Tool(
        name="Campaign Generator",
        func=campaign_generation_func,
        description=(
            "Generates marketing campaign assets (title, email, CTA) based on product details. "
            "Input should be the full product details text."
        ),
    )


def build_campaign_agent(llm, tool_llm=None, verbose: bool = False, structured: bool = False,
                         return_steps: bool = False):
    """Zero-shot ReAct agent that uses the Campaign Generator tool."""
    return initialize_agent(
        [make_campaign_tool(tool_llm or llm, structured=structured)],
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=verbose,
        handle_parsing_errors=True,
        max_iterations=4,
        return_intermediate_steps=return_steps,
    )


def fetch_product_with_agent(sql_agent, product_id: str) -> str:
    product_id = normalize_product_id(product_id)
    result = sql_agent.invoke({"input": f"Fetch all columns for Product ID {product_id}"})
    return result["output"]


def generate_campaign(product_id: str, sql_agent, campaign_agent) -> str:
    """Notebook flow: SQL agent -> product text -> campaign agent -> Title/Email/CTA."""
    product_detail = fetch_product_with_agent(sql_agent, product_id)
    agent_prompt = f"Generate a marketing campaign for the following product details: {product_detail}"
    return campaign_agent.invoke({"input": agent_prompt})["output"]


def generate_structured_campaign(llm, product_details: str) -> CampaignAssets:
    """Single LLM call that returns a validated Pydantic object instead of free text."""
    structured_llm = llm.with_structured_output(CampaignAssets)
    return structured_llm.invoke(CAMPAIGN_PROMPT.format(product_details=product_details))


def generate_campaign_direct(product_id: str, llm, db_path=DEFAULT_DB_PATH) -> Optional[CampaignAssets]:
    """Cheaper, deterministic path: parameterised SQL lookup + one structured LLM call."""
    product = fetch_product(product_id, db_path)
    if product is None:
        return None
    return generate_structured_campaign(llm, format_product(product))


def is_safe(text: str, guard_llm) -> bool:
    """Moderate generated copy with a Llama Guard model (replies 'safe' or 'unsafe\\n<codes>')."""
    verdict = guard_llm.invoke([HumanMessage(content=text)]).content.strip().lower()
    return verdict.startswith("safe")
