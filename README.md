# Quantum PharmX™ Business Intelligence

AI-powered pharmaceutical R&D, manufacturing & business operations platform.

Modular, API-first enterprise ERP covering: R&D, Product/Formulation, Procurement,
Inventory, Manufacturing, Batch, Quality, Supply Chain, Sales, Regulatory,
Costing, Analytics, Predictive Intelligence, AI Agents and **BotPharma™**.

> Standalone product, or the business/operations layer alongside
> Quantum PharmX™ Molecular Intelligence.

## Monorepo layout

```
backend/    Python + FastAPI API (system of record + AI/data services)
frontend/   Next.js + TypeScript + MUI + TanStack Query + ECharts
mobile/     Flutter skeleton (warehouse / production / QC / approvals)
infra/      Terraform + K8s stubs (AWS: ECS/EKS, RDS, S3, ElastiCache, OpenSearch, MSK)
docs/       Architecture, compliance, SAP integration, BotPharma specs
```

## Quickstart (dev)

```bash
# backend (Postgres 17 + pgvector via Homebrew — no cloud account needed)
brew install postgresql@17 pgvector
brew services start postgresql@17
psql postgres -c "CREATE USER pharmx WITH PASSWORD 'pharmx' CREATEDB;"
psql postgres -c "CREATE DATABASE pharmx OWNER pharmx;"
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # DATABASE_URL → local Postgres
python -m app.seed
uvicorn app.main:app --reload --port 8000
# API docs → http://localhost:8000/docs

# frontend
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

Seeded demo user: `admin@pharmx.local / Admin123!` (roles: admin, qa, rnd, manufacturing…).

## Production topology (reference)

Users → Web / Mobile / BotPharma™ → API Gateway & Identity →
Domain Services (R&D | Product | Procurement | Inventory | Manufacturing |
Batch | Quality | Supply Chain | Sales | Regulatory | Costing) →
Workflow & Event Bus → PostgreSQL + Redis + S3 + OpenSearch →
Warehouse/Lakehouse → AI Platform (RAG + ML + LLM gateway + agents) →
SAP S/4HANA | Ariba | LIMS | MES | CRM | IoT/SCADA.

See `docs/ARCHITECTURE.md`.
