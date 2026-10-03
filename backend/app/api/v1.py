"""Assembled v1 API — domain routers + intelligence layer."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import security as sec
from app.core import workflow as wf
from app.core import audit as auditlog
from app.api.crud import crud_router
from app import models
from app.schemas import ChatIn, LoginIn, WorkflowDecision, WorkflowSubmit
from app import services as svc

router = APIRouter(prefix="/api/v1")

# ── Auth ──
@router.post("/auth/login")
def login(body: LoginIn):
    u = sec.USERS.get(body.username)
    if not u or not sec.verify_password(body.password, u["password"]):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": sec.create_token(body.username, u["roles"]),
            "token_type": "bearer", "roles": u["roles"]}

@router.get("/auth/me")
def me(user: dict = Depends(sec.get_current_user)):
    return user

@router.get("/audit")
def audit_trail(user: dict = Depends(sec.require_roles("admin", "qa", "executive"))):
    return auditlog.AUDIT_LOG[-200:]

# ── Domain CRUD (system of record) ──
DOMAINS = [
    (models.Company, "/org/companies", "Organization"),
    (models.Plant, "/org/plants", "Organization"),
    (models.Warehouse, "/org/warehouses", "Organization"),
    (models.Material, "/materials", "Inventory"),
    (models.StockLot, "/inventory/lots", "Inventory"),
    (models.StockMove, "/inventory/moves", "Inventory"),
    (models.RDProject, "/rnd/projects", "R&D"),
    (models.Experiment, "/rnd/experiments", "R&D"),
    (models.Milestone, "/rnd/milestones", "R&D"),
    (models.Patent, "/rnd/patents", "R&D"),
    (models.Product, "/products", "Product"),
    (models.Formulation, "/formulations", "Product"),
    (models.Supplier, "/suppliers", "Procurement"),
    (models.Requisition, "/procurement/requisitions", "Procurement"),
    (models.PurchaseOrder, "/procurement/orders", "Procurement"),
    (models.GoodsReceipt, "/procurement/receipts", "Procurement"),
    (models.WorkOrder, "/manufacturing/orders", "Manufacturing"),
    (models.Batch, "/batches", "Batch"),
    (models.Specification, "/quality/specs", "Quality"),
    (models.Sample, "/quality/samples", "Quality"),
    (models.QCResult, "/quality/results", "Quality"),
    (models.Deviation, "/quality/deviations", "Quality"),
    (models.CAPA, "/quality/capas", "Quality"),
    (models.ChangeControl, "/quality/changes", "Quality"),
    (models.Customer, "/customers", "Sales"),
    (models.SalesOrder, "/sales/orders", "Sales"),
    (models.Registration, "/regulatory/registrations", "Regulatory"),
    (models.Submission, "/regulatory/submissions", "Regulatory"),
    (models.CostRecord, "/costing", "Costing"),
    (models.DocChunk, "/rag/documents", "RAG"),
]
for _model, _prefix, _tag in DOMAINS:
    router.include_router(crud_router(_model, _prefix, _tag))

# ── Workflow / approvals ──
@router.post("/workflows/submit")
def wf_submit(body: WorkflowSubmit, user: dict = Depends(sec.get_current_user)):
    w = wf.submit_workflow(body.kind, body.ref, body.requester or user["email"], body.amount)
    auditlog.audit("WF_SUBMIT", body.kind, body.ref, user["email"], body.model_dump())
    return w

@router.post("/workflows/{ref}/decision")
def wf_decide(ref: str, body: WorkflowDecision, user: dict = Depends(sec.get_current_user)):
    try:
        w = wf.approve(ref, body.approver or user["email"], body.decision, body.comment)  # type: ignore
    except ValueError as e:
        raise HTTPException(400, str(e))
    auditlog.audit("WF_DECISION", "workflow", ref, user["email"], body.model_dump())
    return w

@router.get("/workflows/{ref}")
def wf_get(ref: str, user: dict = Depends(sec.get_current_user)):
    if ref not in wf.STORE:
        raise HTTPException(404, "Not found")
    return wf.STORE[ref]

# ── Supply chain helpers: FEFO + MRP ──
@router.get("/supply/fefo/{material_id}")
def fefo(material_id: str, db: Session = Depends(get_db),
         user: dict = Depends(sec.get_current_user)):
    return svc.fefo(db, material_id)

@router.get("/supply/mrp")
def mrp(db: Session = Depends(get_db), user: dict = Depends(sec.get_current_user)):
    return svc.mrp(db)

# ── Analytics / predictive ──
@router.get("/analytics/kpis")
def kpis(db: Session = Depends(get_db), user: dict = Depends(sec.get_current_user)):
    return svc.kpis(db)

@router.post("/predictive/demand")
def demand(body: dict, user: dict = Depends(sec.get_current_user)):
    return svc.forecast_demand(body.get("history", []), body.get("periods", 3))

@router.get("/predictive/quality-risk")
def qrisk(db: Session = Depends(get_db), user: dict = Depends(sec.get_current_user)):
    return svc.quality_risk(db)

@router.get("/predictive/supplier-risk")
def srisk(db: Session = Depends(get_db), user: dict = Depends(sec.get_current_user)):
    return svc.supplier_risk(db)

# ── Agents + BotPharma™ ──
@router.get("/agents")
def agents(user: dict = Depends(sec.get_current_user)):
    return svc.AGENTS

@router.post("/agents/{name}/run")
def agent_run(name: str, body: dict, db: Session = Depends(get_db),
              user: dict = Depends(sec.get_current_user)):
    out = svc.agent_run(name, db, body)
    auditlog.audit("AGENT_RUN", name, "-", user["email"], body)
    return out

@router.post("/botpharma/chat")
def chat(body: ChatIn, db: Session = Depends(get_db),
          user: dict = Depends(sec.get_current_user)):
    out = svc.botpharma_reply(body.message, user.get("roles", []), db)
    auditlog.audit("BOT_CHAT", "botpharma", "-", user["email"], {"q": body.message[:200]})
    return out

# ── RAG knowledge base (pgvector-ready; keyword search until embeddings land) ──
@router.post("/rag/search")
def rag_search(body: dict, db: Session = Depends(get_db),
               user: dict = Depends(sec.get_current_user)):
    q = (body.get("query") or "")[:500]
    top_k = int(body.get("top_k") or 5)
    chunks = db.query(models.DocChunk).filter(models.DocChunk.content.ilike(f"%{q}%")).limit(top_k).all()
    return {"query": q,
            "hits": [{"source": c.source, "title": c.title,
                      "snippet": (c.content or "")[:400]} for c in chunks],
            "mode": "keyword",
            "note": "Vector cosine search activates once LLM-gateway embeddings populate doc_chunks.embedding."}

# ── Integration stubs (SAP / LIMS / MES / CRM / IoT) ──
@router.get("/integrations/status")
def int_status(user: dict = Depends(sec.get_current_user)):
    return {"sap_s4hana": "ready", "ariba": "ready", "lims": "ready",
            "mes": "ready", "crm": "ready", "iot_scada": "ready",
            "note": "REST/OData + webhooks; SAP Integration Suite / IDoc / BAPI per customer landscape."}

@router.post("/integrations/sync/{system}")
def int_sync(system: str, body: dict, user: dict = Depends(sec.require_roles("admin"))):
    auditlog.audit("INT_SYNC", system, "-", user["email"], body)
    return {"system": system, "status": "queued", "detail": "Connector job queued (stub)."}
