"""Seed demo data covering every module (idempotent-ish for dev)."""
from datetime import date, timedelta
from app.core.database import SessionLocal, engine, Base
from app import models

Base.metadata.create_all(bind=engine)

def run():
    db = SessionLocal()
    if db.query(models.Material).first():
        print("seed: already seeded")
        return
    co = models.Company(name="MEDxAI Pharma", code="MEDX"); db.add(co); db.commit()
    pl = models.Plant(company_id=co.id, name="Hyderabad Plant", location="Hyderabad, IN"); db.add(pl); db.commit()
    wh = models.Warehouse(plant_id=pl.id, name="WH-01"); db.add(wh); db.commit()

    rms = [
        ("RM-PARA", "Paracetamol API", "api", 100, 12.5),
        ("RM-LACT", "Lactose Monohydrate", "excipient", 200, 3.2),
        ("RM-STARCH", "Starch 1500", "excipient", 150, 2.1),
        ("PK-BLISTER", "Alu Blister Foil", "packaging", 500, 0.8),
        ("FG-PARA500", "Paracetamol 500mg Tablets", "finished", 300, 0.0),
    ]
    mats = {}
    for code, name, kind, ss, cost in rms:
        m = models.Material(code=code, name=name, kind=kind, safety_stock=ss, unit_cost=cost)
        db.add(m); db.commit(); mats[code] = m
    db.add(models.StockLot(material_id=mats["RM-PARA"].id, lot_no="L-PARA-001", qty=40,
                           expiry=date.today() + timedelta(days=400)))
    db.add(models.StockLot(material_id=mats["RM-LACT"].id, lot_no="L-LACT-009", qty=500,
                           expiry=date.today() + timedelta(days=700)))
    db.add(models.StockLot(material_id=mats["RM-STARCH"].id, lot_no="L-ST-003", qty=5,
                           expiry=date.today() + timedelta(days=60)))

    p = models.RDProject(code="RD-001", title="Paracetamol SR formulation", stage="phase1",
                         budget=250000, owner="rnd@pharmx.local"); db.add(p); db.commit()
    db.add(models.Experiment(project_id=p.id, title="Dissolution profile T12",
                             objective="12h release", result="88% at 12h", status="complete"))
    db.add(models.Milestone(project_id=p.id, name="Phase-1 dossier", due=date.today() + timedelta(days=60)))
    db.add(models.Patent(project_id=p.id, title="Sustained-release matrix", filing_no="IN-2026-001", status="filed"))

    prod = models.Product(code="PRD-PARA500", name="Paracetamol 500mg Tablets",
                          dosage_form="tablet", strength="500mg", status="commercial")
    db.add(prod); db.commit()
    import json
    db.add(models.Formulation(product_id=prod.id, version="v2.1",
        lines=json.dumps([{"material": "RM-PARA", "qty": 0.5}, {"material": "RM-LACT", "qty": 0.2}])))
    s1 = models.Supplier(code="SUP-01", name="Auro API Suppliers", rating=4.2, lead_time_days=12, approved=True)
    s2 = models.Supplier(code="SUP-02", name="Budget Excipients Co", rating=2.4, lead_time_days=30, approved=False)
    db.add_all([s1, s2]); db.commit()
    db.add(models.Requisition(material_id=mats["RM-PARA"].id, qty=200, requester="rnd@pharmx.local", status="submitted"))
    db.add(models.PurchaseOrder(supplier_id=s1.id, total=15000, status="sent",
        lines=json.dumps([{"material": "RM-PARA", "qty": 200}])))
    wo = models.WorkOrder(product_id=prod.id, qty_planned=10000, qty_actual=9600,
                          yield_pct=96.0, downtime_min=45, status="complete")
    db.add(wo); db.commit()
    db.add(models.Batch(product_id=prod.id, work_order_id=wo.id, batch_no="B-2026-001",
        expiry=date.today() + timedelta(days=730), status="qc_pending",
        genealogy=json.dumps({"lots": ["L-PARA-001"], "equipment": "RMG-02", "operators": ["OP-11"]}))); db.commit()
    db.add(models.Specification(material_or_product="PRD-PARA500",
        tests=json.dumps([{"param": "assay", "min": 95, "max": 105, "unit": "%"}])))
    db.add(models.Sample(batch_id="B-2026-001", status="tested"))
    db.add(models.QCResult(sample_id="S-1", param="assay", value=99.2, verdict="pass"))
    db.add(models.QCResult(sample_id="S-2", param="assay", value=112.0, verdict="oos"))
    db.add(models.Deviation(ref="DEV-001", severity="major", description="Assay OOS in batch B-2026-001"))
    db.add(models.CAPA(deviation_id="DEV-001", action="Investigate RMG-02 blending", owner="qa@pharmx.local",
        due=date.today() + timedelta(days=14)))
    c = models.Customer(code="CUS-01", name="City Hospitals", credit_limit=100000); db.add(c); db.commit()
    db.add(models.SalesOrder(customer_id=c.id, total=42000, status="confirmed",
        delivery_date=date.today() + timedelta(days=10)))
    db.add(models.Registration(product_id=prod.id, country="IN", dossier_no="CDSCO-8891", status="approved",
        expiry=date.today() + timedelta(days=900)))
    db.add(models.CostRecord(kind="batch", ref_id="B-2026-001", material_cost=8200,
        mfg_cost=3100, overhead=900, revenue=15000, margin=3800))
    db.commit(); db.close()
    print("seed: done")

if __name__ == "__main__":
    run()
