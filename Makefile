.PHONY: api web test seed
api:
	cd backend && uvicorn app.main:app --reload --port 8000
web:
	cd frontend && npm run dev
test:
	cd backend && pytest -q
seed:
	cd backend && python -m app.seed
