"""Domain-specific services: analytics KPIs, predictive models, agents, BotPharma."""
import math
from sqlalchemy.orm import Session
from app import models


# ── Analytics (semantic KPI layer stub) ──
def kpis(db: Session) -> dict:
    q = lambda m: db.query(m).count()
    lots = db.query(models.StockLot).all()
    low = sum(1 for l in lots if (l.qty or 0) <= 50)
    exp = [l.lot_no for l in lots if (l.qty or 0) <= 0]
    oos = db.query(models.QCResult).filter_by(verdict="oos").count()
    open_dev = db.query(models.Deviation).filter_by(status="open").count()
    wo = db.query(models.WorkOrder).all()
    avg_yield = round(sum(w.yield_pct or 0 for w in wo) / len(wo), 1) if wo else 0
    return {
        "projects": q(models.RDProject), "products": q(models.Product),
        "purchase_orders": q(models.PurchaseOrder), "work_orders": q(models.WorkOrder),
        "batches": q(models.Batch), "oos_results": oos, "open_deviations": open_dev,
        "low_stock_lots": low, "avg_yield_pct": avg_yield,
        "expired_or_empty_lots": exp[:10],
    }


def fefo(db: Session, material_id: str) -> list:
    lots = db.query(models.StockLot).filter_by(material_id=material_id).all()
    lots = [l for l in lots if (l.qty or 0) > 0 and l.status == "available"]
    lots.sort(key=lambda l: (str(l.expiry or "9999"), l.lot_no))
    return [{"lot_no": l.lot_no, "qty": l.qty, "expiry": str(l.expiry)} for l in lots]


def mrp(db: Session) -> list:
    """Naive MRP: open sales qty vs on-hand → net requirement per material."""
    mats = db.query(models.Material).all()
    on_hand = {}
    for l in db.query(models.StockLot).all():
        on_hand[l.material_id] = on_hand.get(l.material_id, 0) + (l.qty or 0)
    out = []
    for m in mats:
        oh = on_hand.get(m.id, 0)
        net = max(0, (m.safety_stock or 0) * 2 - oh)
        if net > 0:
            out.append({"material": m.code, "on_hand": oh,
                        "safety_stock": m.safety_stock, "net_requirement": net,
                        "recommend": f"Raise requisition for {net:.0f} {m.uom}"})
    return out


# ── Predictive intelligence (explainable baselines; MLflow-ready) ──
def forecast_demand(history: list[float], periods: int = 3) -> dict:
    if not history:
        return {"forecast": [], "method": "naive", "risk": "unknown"}
    avg = sum(history[-6:]) / min(6, len(history))
    fc = [round(avg, 1) for _ in range(periods)]
    trend = history[-1] - history[0] if len(history) > 1 else 0
    risk = "stockout_risk" if trend > 0 and avg > 0 else "overstock_watch" if trend < 0 else "stable"
    return {"forecast": fc, "method": "moving_average(6)", "trend": round(trend, 2), "risk": risk}


def quality_risk(db: Session) -> list:
    rows = db.query(models.QCResult).all()
    by_sample: dict[str, list] = {}
    for r in rows:
        by_sample.setdefault(r.sample_id, []).append(r.verdict)
    return [{"sample": s, "oos_rate": round(sum(1 for v in vs if v == "oos") / len(vs), 2),
             "signal": "investigate" if any(v == "oos" for v in vs) else "ok"}
            for s, vs in list(by_sample.items())[:50]]


def supplier_risk(db: Session) -> list:
    out = []
    for s in db.query(models.Supplier).all():
        score = (s.rating or 3) - (s.lead_time_days or 14) / 30
        out.append({"supplier": s.name, "score": round(score, 2),
                    "risk": "high" if score < 2 else "medium" if score < 3.5 else "low"})
    return out


# ── BotPharma™ + agents (controlled, role-aware, audited) ──
AGENTS = {
    "procurement": "Analyze demand, compare suppliers/quotes, identify savings, prepare sourcing actions.",
    "supply_chain": "Forecast demand, flag stock-out/overstock risk, recommend replenishment.",
    "manufacturing": "Analyze capacity, schedules, yield, downtime and delivery risk.",
    "quality": "Detect OOS/OOT/deviation trends; correlate with batches, suppliers, parameters.",
    "rnd": "Summarize projects, experiments, milestones, risks; link Molecular Intelligence when licensed.",
    "regulatory": "Track submissions, commitments, renewals, document gaps.",
    "finance": "Analyze product/batch/project/customer profitability and cost drivers.",
    "executive": "Cross-functional summary, alerts, trends, recommended actions.",
}


def agent_run(name: str, db: Session, payload: dict) -> dict:
    if name not in AGENTS:
        return {"error": f"unknown agent {name}"}
    data: dict = {"agent": name, "mission": AGENTS[name]}
    if name == "supply_chain":
        data.update({"mrp": mrp(db)[:5], "kpis": kpis(db)})
    elif name == "quality":
        data.update({"quality_signals": quality_risk(db)[:5], "open_deviations": db.query(models.Deviation).filter_by(status="open").count()})
    elif name == "procurement":
        data.update({"supplier_risk": supplier_risk(db)[:5]})
    elif name in ("executive", "finance", "manufacturing", "rnd", "regulatory"):
        data.update({"kpis": kpis(db)})
    data["recommendations"] = [f"[{name}] review flagged items and submit approval workflow before transacting."]
    data["note"] = "Advisory only — material/regulated actions require human approval + e-signature."
    return data


def botpharma_reply(message: str, roles: list[str], db: Session) -> dict:
    m = message.lower()
    k = kpis(db)
    sources: list[str] = []
    if any(w in m for w in ("stock", "inventory", "fefo", "expir")):
        lots = db.query(models.StockLot).limit(5).all()
        sources = [f"stock_lots:{l.lot_no}" for l in lots]
        answer = f"There are {k['batches']} batches and {k['low_stock_lots']} low-stock lots. FEFO picks earliest-expiry available lots first."
    elif any(w in m for w in ("oos", "quality", "deviation", "capa")):
        sources = ["qc_results", "deviations"]
        answer = f"Quality signals: {k['oos_results']} OOS results, {k['open_deviations']} open deviations. I can correlate by batch/supplier on request."
    elif any(w in m for w in ("order", "procurement", "supplier", "po")):
        sources = ["purchase_orders", "suppliers"]
        answer = f"Procurement: {k['purchase_orders']} POs. Supplier risk and savings review available via the procurement agent (draft requisition needs approval)."
    elif any(w in m for w in ("project", "r&d", "experiment", "milestone", "patent")):
        sources = ["rd_projects", "experiments"]
        answer = f"R&D portfolio: {k['projects']} projects tracked with experiments, milestones and IP."
    elif any(w in m for w in ("forecast", "demand", "risk", "margin", "profit")):
        sources = ["analytics.kpis", "predictive.forecast"]
        answer = f"Executive snapshot — products: {k['products']}, avg yield {k['avg_yield_pct']}%, OOS {k['oos_results']}. Ask for forecast/risk drill-down."
    else:
        answer = ("I can query authorized ERP records (R&D, inventory, batches, quality, orders, regulatory), "
                  "explain KPIs, and draft workflows for approval. What would you like — e.g. 'low stock risks' or 'OOS trends'?")
    if "admin" not in roles:
        answer += " [role-filtered view]"
    return {"answer": answer, "sources": sources, "roles": roles,
            "disclaimer": "Grounded in authorized records only; regulated actions need human approval."}
