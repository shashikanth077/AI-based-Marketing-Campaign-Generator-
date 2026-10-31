PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup dev start test clean

# One-time install of Python + Node dependencies
setup:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt
	cd frontend && npm install
	@test -f .env || cp .env.example .env

# Development: API with auto-reload on :8000 and Vite dev server on :5173 (open http://localhost:5173)
dev:
	$(PY) -m uvicorn marketing_campaign.api:app --reload --port 8000 & \
	cd frontend && npm run dev; kill %1 2>/dev/null || true

# Single-process demo: build the React app, FastAPI serves UI + API on http://localhost:8000
start:
	cd frontend && npm run build
	$(PY) -m uvicorn marketing_campaign.api:app --port 8000

test:
	$(PY) -m pytest -q

clean:
	rm -rf frontend/dist frontend/node_modules .pytest_cache
