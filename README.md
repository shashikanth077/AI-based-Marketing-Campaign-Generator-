# AI-Based Marketing Campaign Generator

Give it a **Product ID**; it fetches the product from a SQLite database with a LangChain **SQL agent**
and generates a **Marketing Title**, an **Email Draft** and a **Call-to-Action** with Llama 4 on Groq.

```
Product ID ─► normalise ("1011" → "P1011")
           ─► SQL Agent (ReAct, temp 0) ⇄ products.db (read-only)
           ─► Campaign Agent (ReAct) ⇄ "Campaign Generator" tool (LLM prompt)
           ─► [optional Llama Guard check] ─► Title + Email + CTA
```

## Contents

| Path | What it is |
|---|---|
| `notebooks/AI_Based_Marketing_Campaign_Generator.ipynb` | Completed course notebook (Colab-ready) + bonus cells: Pydantic output, A/B variants, Llama Guard |
| `marketing_campaign/` | Same pipeline as a reusable Python package and CLI |
| `data/products.db` | The 5-product SQLite database (rebuild with `python -m marketing_campaign.data`) |
| `tests/` | Offline tests using scripted fake LLMs — no API key needed |
| `docs/learning-guide.html` | Interactive study guide: theory, ReAct trace, temperature lab, code walkthrough, fill-the-blanks, flashcards, quiz, 48 interview Q&As |

## Quick start

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key            # https://console.groq.com/keys
python -m marketing_campaign.cli --list
python -m marketing_campaign.cli --product-id P1011           # two-agent flow (as in the notebook)
python -m marketing_campaign.cli --product-id 1012 --direct   # one SQL query + one structured LLM call
python -m marketing_campaign.cli --product-id P1013 --creative --safety-check --verbose
pytest -q
```

In Colab: open the notebook, add `GROQ_API_KEY` under **Secrets**, run all cells.
Open `docs/learning-guide.html` in any browser to study.

## Improvements over the original notebook

- `llm.predict` / `llm([...])` / `agent.run` → `.invoke` (current LangChain API)
- `handle_parsing_errors` moved to `agent_executor_kwargs`, where `create_sql_agent` actually applies it
- Built-in SQL ReAct prompt instead of `hub.pull(...)` (no network dependency)
- Product IDs validated and normalised (`1011` → `P1011`), blocking injected input
- Database opened read-only, restricted to the `products` table
- Structured output (`CampaignAssets` Pydantic model), optional Llama Guard moderation
- Offline test suite
