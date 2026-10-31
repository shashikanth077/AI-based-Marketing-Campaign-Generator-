"""Rule-based quality and compliance checks on generated campaigns."""

import re
from typing import List

from marketing_campaign.schemas import CampaignAssets

BANNED_PHRASES = ["guaranteed", "guarantee", "risk-free", "risk free", "assured returns", "no risk", "double your money"]
DISCLAIMER = (
    "Investments and savings products are subject to market and other risks. "
    "Read all scheme/product documents carefully. Past performance is not indicative of future returns."
)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'&-]+\b", text))


def run_checks(campaign: CampaignAssets, product: dict) -> List[dict]:
    """Return a list of {id, label, passed, detail} results."""
    body_words = word_count(campaign.email_body)
    title_words = word_count(campaign.title)
    full_text = " ".join([campaign.title, campaign.email_subject, campaign.email_body, campaign.cta]).lower()
    banned = [p for p in BANNED_PHRASES if p in full_text]
    return [
        {"id": "email_length", "label": "Email is 100-150 words", "passed": 100 <= body_words <= 150,
         "detail": f"{body_words} words"},
        {"id": "title_length", "label": "Title is 10 words or fewer", "passed": 0 < title_words <= 10,
         "detail": f"{title_words} words"},
        {"id": "cta_present", "label": "Call-to-action present", "passed": len(campaign.cta.strip()) > 3,
         "detail": f"{word_count(campaign.cta)} words"},
        {"id": "product_named", "label": "Product is mentioned by name",
         "passed": product["product_name"].lower() in full_text, "detail": product["product_name"]},
        {"id": "no_banned", "label": "No guarantee / risk-free claims", "passed": not banned,
         "detail": ", ".join(banned) if banned else "none found"},
    ]
