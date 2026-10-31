"""Product database: seed data, creation and a deterministic lookup."""

import re
import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "products.db"

# Same five products the course database ships with.
PRODUCTS = [
    {
        "product_id": "P1011",
        "product_name": "Golden Future Mutual Fund",
        "target_age": "30-50",
        "target_profession": "Salaried Professional",
        "product_details": (
            "The Golden Future Mutual Fund is designed for professionals looking to build "
            "long-term wealth through a blend of growth and stability. It invests in a "
            "diversified portfolio of large-cap stocks and emerging market equities, aiming "
            "to provide robust returns over time. Along with active portfolio management and "
            "periodic reviews, investors can expect a balanced approach to wealth creation."
        ),
    },
    {
        "product_id": "P1012",
        "product_name": "Golden Years Savings Account",
        "target_age": "60-75",
        "target_profession": "Retired Professional",
        "product_details": (
            "Specifically tailored for retirees, the Golden Years Savings Account provides a "
            "secure and accessible way to manage post-retirement finances. With competitive "
            "interest rates, minimal fees, and hassle-free digital banking, this account "
            "ensures that your savings grow steadily with added benefits like loan facilities "
            "and investment options."
        ),
    },
    {
        "product_id": "P1013",
        "product_name": "Balanced Growth Investment Fund",
        "target_age": "30-55",
        "target_profession": "Salaried Professional",
        "product_details": (
            "This fund offers a balanced investment strategy that combines the growth "
            "potential of equities with the relative safety of fixed-income securities. Ideal "
            "for mid-career professionals planning for future family needs and retirement, the "
            "Balanced Growth Investment Fund focuses on diversified asset allocation to "
            "optimize returns while managing risk."
        ),
    },
    {
        "product_id": "P1014",
        "product_name": "Senior Advantage Fixed Deposit",
        "target_age": "60-75",
        "target_profession": "Retired and Semi-Retired Professionals",
        "product_details": (
            "The Senior Advantage Fixed Deposit is designed exclusively for retirees looking "
            "for secure and higher returns on their savings. Enjoy attractive interest "
            "bonuses, flexible tenure options, and minimal penalties for urgent withdrawals. "
            "Detailed risk assessments and regular reviews ensure that your investments are "
            "aligned with your financial goals."
        ),
    },
    {
        "product_id": "P1015",
        "product_name": "Dynamic Opportunity Savings & Investment Combo",
        "target_age": "40-65",
        "target_profession": "Salaried and Semi-Retired Professionals",
        "product_details": (
            "This innovative product combines the benefits of a high-interest savings account "
            "with the growth potential of a low-to-moderate risk investment portfolio. Ideal "
            "for professionals transitioning into retirement or seeking a hybrid financial "
            "solution, the Dynamic Opportunity Combo offers flexible account management and "
            "the potential for higher returns on savings."
        ),
    },
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    product_id        TEXT PRIMARY KEY,
    product_name      TEXT NOT NULL,
    target_age        TEXT,
    target_profession TEXT,
    product_details   TEXT
)
"""


def create_database(path=DEFAULT_DB_PATH) -> Path:
    """Create (or refresh) the SQLite products database and return its path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(SCHEMA)
        conn.executemany(
            "INSERT OR REPLACE INTO products VALUES "
            "(:product_id, :product_name, :target_age, :target_profession, :product_details)",
            PRODUCTS,
        )
    return path


def normalize_product_id(raw: str) -> str:
    """Accept '1011', 'p1011' or ' P1011 ' and return 'P1011'."""
    match = re.fullmatch(r"\s*[pP]?\s*(\d{3,6})\s*", raw or "")
    if not match:
        raise ValueError(f"Invalid Product ID: {raw!r} (expected something like P1011)")
    return f"P{match.group(1)}"


def fetch_product(product_id: str, db_path=DEFAULT_DB_PATH) -> Optional[dict]:
    """Deterministic, parameterised lookup -- no LLM involved."""
    uri = f"file:{Path(db_path)}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM products WHERE product_id = ?", (normalize_product_id(product_id),)
        ).fetchone()
    return dict(row) if row else None


def format_product(product: dict) -> str:
    """Render a product row as the text block the campaign prompt expects."""
    return "\n".join(f"{key}: {value}" for key, value in product.items())


if __name__ == "__main__":
    print(f"Created {create_database()}")
