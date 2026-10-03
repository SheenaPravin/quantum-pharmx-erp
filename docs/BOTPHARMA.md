# BotPharma™ spec

Enterprise agent layer, not a chatbot:
- NL interface for mgmt/R&D/mfg/QC/procurement/supply/finance/regulatory
- Retrieval from *authorized* ERP records, SOPs, specs, reports (`services.botpharma_reply`)
- Tool calling: read data; draft workflows (requisition/approval) — never silent controlled writes
- Role-aware filtering; source-grounded answers with record refs
- Human approval for material/regulated actions; full prompt/tool/decision audit trail
- Endpoints: `POST /api/v1/botpharma/chat`, `POST /api/v1/agents/{name}/run`, `GET /api/v1/agents`
