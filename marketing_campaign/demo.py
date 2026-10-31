"""Offline demo generator used when no GROQ_API_KEY is configured.

It is a simple template, NOT an LLM. The API labels every response produced here as demo mode
so nobody mistakes it for model output.
"""

from marketing_campaign.schemas import CampaignAssets


def _first_age(target_age: str) -> int:
    try:
        return int(target_age.replace("–", "-").split("-")[0])
    except ValueError:
        return 40


def demo_campaign(product: dict) -> CampaignAssets:
    name = product["product_name"]
    audience = product["target_profession"].lower()
    retiree = _first_age(product["target_age"]) >= 60
    if retiree:
        title = "Peace of Mind for Your Golden Years"
        hook = "You have spent a lifetime building your savings. Now it is time to let them work quietly and securely for you."
        benefits = "steady returns, flexible access and minimal fees, backed by regular reviews so you always know where you stand"
        cta = f"Visit your nearest branch or book a call to open your {name} today."
    else:
        title = "Build Tomorrow, Starting Today"
        hook = "Your career is at its most productive. Your money should be too."
        benefits = "a diversified, actively reviewed approach that balances long-term growth with sensible risk management"
        cta = f"Book a free consultation and start your {name} journey today."
    body = (
        f"Dear [Name],\n\n{hook}\n\n"
        f"We are pleased to introduce the {name}, created especially for {audience}. "
        f"It offers {benefits}. Whether you are planning for family, retirement or simply greater financial "
        f"confidence, our advisers are ready to help you choose the option that fits your goals and your comfort with risk.\n\n"
        f"Take a few minutes to explore the details and see how the {name} could support your plans. "
        f"There is no obligation, and our team will gladly answer every question.\n\n"
        f"Warm regards,\n[Your Name]"
    )
    return CampaignAssets(title=title, email_subject=f"Introducing the {name}", email_body=body, cta=cta)


def demo_steps(product_id: str, mode: str) -> list:
    """Illustrative trace so the UI is demonstrable offline. Marked simulated=True."""
    base = [
        {"agent": "SQL agent", "kind": "action", "tool": "sql_db_list_tables", "input": "", "observation": "products"},
        {"agent": "SQL agent", "kind": "action", "tool": "sql_db_schema", "input": "products",
         "observation": "CREATE TABLE products (product_id TEXT, product_name TEXT, target_age TEXT, ...)"},
        {"agent": "SQL agent", "kind": "action", "tool": "sql_db_query",
         "input": f"SELECT * FROM products WHERE product_id = '{product_id}'", "observation": "[(...1 row...)]"},
        {"agent": "Campaign agent", "kind": "action", "tool": "Campaign Generator",
         "input": "<product details>", "observation": "<title, email, CTA>"},
    ]
    return base if mode == "agent" else []
