# AI-Based Marketing Campaign Generator

Give it a **Product ID**; it fetches the product from a SQLite database with a LangChain **SQL agent**
and generates a **Marketing Title**, an **Email Draft** and a **Call-to-Action** with Llama 4 on Groq.

```
Product ID ─► normalise ("1011" → "P1011")
           ─► SQL Agent (ReAct, temp 0) ⇄ products.db (read-only)
           ─► Campaign Agent (ReAct) ⇄ "Campaign Generator" tool (LLM prompt)
           ─► [optional Llama Guard check] ─► Title + Email + CTA
```

## Full-stack demo (React UI + FastAPI backend)

```
React (Vite) ──/api──► FastAPI ──► LangChain agents ──► Groq (Llama 4)
                            └────► SQLite products.db (read-only)
```

Prerequisites: **Python 3.10+** and **Node 18+**. A free [Groq API key](https://console.groq.com/keys) is optional:
without one the app runs in clearly labelled **demo mode** (template output instead of an LLM), so the whole UI is
still demonstrable offline.

```bash
make setup                     # venv + pip install + npm install, creates .env
# put your key in .env:  GROQ_API_KEY=gsk_...
make start                     # builds the UI, serves everything on http://localhost:8000
```

For development with hot reload use `make dev` and open <http://localhost:5173>.
Without `make` (e.g. Windows):

```bash
python -m venv .venv && .venv/Scripts/activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
uvicorn marketing_campaign.api:app --port 8000
```

### What the UI shows
- Product picker (data fetched from the API) and options: **Direct** vs **Agents** pipeline, creative temperature,
  A/B variants (1-3), Llama Guard safety check
- Title, email (subject + body) and CTA cards with copy buttons and a compliance disclaimer
- Automatic quality checks: email 100-150 words, short title, CTA present, product named, no "guaranteed" claims
- **Agent reasoning trace**: every SQL / tool call the ReAct agents made, with inputs and observations
- Live/demo badge, latency, recent-runs history, dark mode, cancel button, error states

### API
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | status, `demo` flag, model names |
| GET | `/api/products` | all products |
| POST | `/api/campaigns` | `{product_id, mode: "direct"\|"agent", creative, temperature, safety_check, variants}` |

Interactive docs: <http://localhost:8000/docs>.

## Contents

| Path | What it is |
|---|---|
| `notebooks/AI_Based_Marketing_Campaign_Generator.ipynb` | Completed course notebook (Colab-ready) + bonus cells: Pydantic output, A/B variants, Llama Guard |
| `marketing_campaign/` | Pipeline as a Python package: agents, service layer, FastAPI app (`api.py`), CLI |
| `frontend/` | React + Vite UI |
| `data/products.db` | 5-product SQLite database, auto-created on first start (not committed) |
| `tests/` | Offline tests using scripted fake LLMs — no API key needed |
| `docs/learning-guide.html` | Interactive study guide: theory, ReAct trace, temperature lab, code walkthrough, fill-the-blanks, flashcards, quiz, 48 interview Q&As |

## CLI

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
