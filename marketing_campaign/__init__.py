"""AI-based Marketing Campaign Generator.

Fetches product details from a SQLite database (via a LangChain SQL agent)
and generates a marketing Title, Email Draft and Call-to-Action with an LLM.
"""

from marketing_campaign.data import PRODUCTS, create_database, fetch_product
from marketing_campaign.schemas import CampaignAssets

__all__ = ["PRODUCTS", "create_database", "fetch_product", "CampaignAssets"]
