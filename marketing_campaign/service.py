"""Orchestration used by the API: runs the pipeline and shapes a UI-friendly result."""

import json
import os
import time
from typing import List, Optional

from marketing_campaign import agents
from marketing_campaign.checks import DISCLAIMER, run_checks
from marketing_campaign.data import DEFAULT_DB_PATH, PRODUCTS, create_database, fetch_product, format_product, normalize_product_id
from marketing_campaign.demo import demo_campaign, demo_steps
from marketing_campaign.schemas import CampaignAssets


class ProductNotFound(Exception):
    pass


def is_demo_mode() -> bool:
    return not os.getenv("GROQ_API_KEY")


def ensure_db(db_path=DEFAULT_DB_PATH):
    create_database(db_path)


def list_products(db_path=DEFAULT_DB_PATH) -> List[dict]:
    return [fetch_product(p["product_id"], db_path) for p in PRODUCTS]


def _steps_from_intermediate(agent_name: str, intermediate) -> List[dict]:
    steps = []
    for action, observation in intermediate or []:
        log = (getattr(action, "log", "") or "").split("Action:")[0].replace("Thought:", "").strip()
        steps.append({
            "agent": agent_name, "kind": "action", "thought": log, "tool": action.tool,
            "input": str(action.tool_input)[:1500], "observation": str(observation)[:1500],
        })
    return steps


def _campaign_from_steps(intermediate) -> Optional[CampaignAssets]:
    for action, observation in reversed(intermediate or []):
        if action.tool == "Campaign Generator":
            try:
                return CampaignAssets.model_validate(json.loads(observation))
            except (ValueError, TypeError):
                return None
    return None


def generate(product_id: str, mode: str = "direct", creative: bool = False, temperature: float = 1.0,
             safety_check: bool = False, variants: int = 1, db_path=DEFAULT_DB_PATH) -> dict:
    started = time.perf_counter()
    product_id = normalize_product_id(product_id)
    product = fetch_product(product_id, db_path)
    if product is None:
        raise ProductNotFound(product_id)

    warnings: List[str] = []
    steps: List[dict] = []
    campaigns: List[CampaignAssets] = []
    demo = is_demo_mode()
    model = "demo-template (no LLM)"

    if demo:
        campaigns = [demo_campaign(product)]
        steps = demo_steps(product_id, mode)
        if variants > 1:
            warnings.append("Demo mode returns one template; add GROQ_API_KEY for real variants.")
        if safety_check:
            warnings.append("Safety check skipped in demo mode.")
        warnings.append("Demo mode: output comes from a template, not an LLM. Set GROQ_API_KEY for live generation.")
    else:
        from marketing_campaign.llm import DEFAULT_GUARD_MODEL, DEFAULT_MODEL, get_llm

        model = DEFAULT_MODEL
        llm = get_llm(temperature=0)
        writer = get_llm(temperature=temperature) if creative else llm
        if mode == "agent":
            sql_agent = agents.build_sql_agent(llm, db_path, return_steps=True)
            sql_result = sql_agent.invoke({"input": f"Fetch all columns for Product ID {product_id}"})
            steps += _steps_from_intermediate("SQL agent", sql_result.get("intermediate_steps"))
            campaign_agent = agents.build_campaign_agent(llm, tool_llm=writer, structured=True, return_steps=True)
            result = campaign_agent.invoke({
                "input": f"Generate a marketing campaign for the following product details: {sql_result['output']}"})
            steps += _steps_from_intermediate("Campaign agent", result.get("intermediate_steps"))
            campaign = _campaign_from_steps(result.get("intermediate_steps"))
            if campaign is None:
                warnings.append("The agent did not return structured output; used the direct generator instead.")
                campaign = agents.generate_structured_campaign(writer, format_product(product))
            campaigns = [campaign]
        else:
            n = max(1, min(variants, 3))
            campaigns = [agents.generate_structured_campaign(writer, format_product(product)) for _ in range(n)]
            if n > 1 and not creative:
                warnings.append("Variants at temperature 0 are near-identical; enable creative mode for diversity.")

    safety = {"checked": False, "safe": None}
    if safety_check and not demo:
        guard = get_llm(0, DEFAULT_GUARD_MODEL)
        verdicts = [agents.is_safe(c.to_markdown(), guard) for c in campaigns]
        safety = {"checked": True, "safe": all(verdicts), "model": DEFAULT_GUARD_MODEL}
        if not safety["safe"]:
            campaigns = [c for c, ok in zip(campaigns, verdicts) if ok]
            warnings.append("Content flagged as unsafe by Llama Guard was withheld.")

    return {
        "product": product,
        "mode": mode,
        "demo": demo,
        "model": model,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "campaigns": [{**c.model_dump(), "checks": run_checks(c, product)} for c in campaigns],
        "disclaimer": DISCLAIMER,
        "steps": steps,
        "safety": safety,
        "warnings": warnings,
    }
