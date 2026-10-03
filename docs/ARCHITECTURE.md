# Architecture — Quantum PharmX™ BI

API-first modular monolith (FastAPI) → splittable into Java/Spring Boot services
for high-volume domains. See spec §3–§5.

- UX: Next.js web, Flutter mobile, BotPharma™ agent UI
- API & security: gateway + OAuth2/OIDC (Entra ID/Keycloak/Auth0), RBAC/ABAC, audit
- Services: R&D, Product, Procurement, Inventory, Manufacturing, Batch, Quality,
  Supply, Sales, Regulatory, Costing (+ `backend/app/api/v1.py`)
- Workflow: approval matrix + SoD now; Camunda for controlled/long-running flows
- Data: PostgreSQL (RDS) + Redis + S3 + OpenSearch; events RabbitMQ → Kafka at scale
- Analytics: KPI semantic layer (`services.kpis/mrp/fefo`) → warehouse/lakehouse
- AI: scikit-learn baselines + MLflow-ready; LLM via provider-agnostic gateway;
  RAG pgvector → Qdrant/Milvus; agent orchestration with tool permissions + audit
- Integration: SAP S/4HANA, Ariba, LIMS, MES, CRM, IoT/SCADA via REST/OData/webhooks
