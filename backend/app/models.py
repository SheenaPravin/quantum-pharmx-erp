"""Unified pharma data foundation — one master-data model, no departmental silos.

Covers §8 core entities: Organization, Material, Commercial, Manufacturing,
Quality, R&D, Regulatory, Finance.
"""
import uuid
from datetime import date, datetime
from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, String, Text)
from app.core.database import Base


def uid() -> str:
    return uuid.uuid4().hex[:12]


class Mixin:
    id = Column(String, primary_key=True, default=uid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Organization ──────────────────────────────────────────────
class Company(Base, Mixin):
    __tablename__ = "companies"
    name = Column(String, nullable=False)
    code = Column(String, unique=True)


class Plant(Base, Mixin):
    __tablename__ = "plants"
    company_id = Column(String, ForeignKey("companies.id"))
    name = Column(String, nullable=False)
    location = Column(String, default="")


class Warehouse(Base, Mixin):
    __tablename__ = "warehouses"
    plant_id = Column(String, ForeignKey("plants.id"))
    name = Column(String, nullable=False)


# ── Material master ───────────────────────────────────────────
class Material(Base, Mixin):
    __tablename__ = "materials"
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    kind = Column(String, default="raw")  # raw|api|excipient|intermediate|packaging|finished
    uom = Column(String, default="kg")
    safety_stock = Column(Float, default=0)
    unit_cost = Column(Float, default=0)


class StockLot(Base, Mixin):
    __tablename__ = "stock_lots"
    material_id = Column(String, ForeignKey("materials.id"))
    lot_no = Column(String, nullable=False)
    qty = Column(Float, default=0)
    expiry = Column(Date, nullable=True)
    warehouse = Column(String, default="WH-01")
    status = Column(String, default="available")  # available|quarantine|blocked|released


class StockMove(Base, Mixin):
    __tablename__ = "stock_moves"
    material_id = Column(String)
    lot_no = Column(String, default="")
    qty = Column(Float, default=0)
    direction = Column(String, default="in")  # in|out
    reason = Column(String, default="")


# ── R&D ───────────────────────────────────────────────────────
class RDProject(Base, Mixin):
    __tablename__ = "rd_projects"
    code = Column(String, unique=True)
    title = Column(String, nullable=False)
    stage = Column(String, default="discovery")  # discovery|preclinical|phase1|phase2|phase3|filed
    status = Column(String, default="active")
    budget = Column(Float, default=0)
    owner = Column(String, default="")


class Experiment(Base, Mixin):
    __tablename__ = "experiments"
    project_id = Column(String, ForeignKey("rd_projects.id"))
    title = Column(String, nullable=False)
    objective = Column(Text, default="")
    result = Column(Text, default="")
    status = Column(String, default="planned")  # planned|running|complete|failed


class Milestone(Base, Mixin):
    __tablename__ = "milestones"
    project_id = Column(String, ForeignKey("rd_projects.id"))
    name = Column(String, nullable=False)
    due = Column(Date, nullable=True)
    done = Column(Boolean, default=False)


class Patent(Base, Mixin):
    __tablename__ = "patents"
    project_id = Column(String, ForeignKey("rd_projects.id"))
    title = Column(String, nullable=False)
    filing_no = Column(String, default="")
    status = Column(String, default="draft")


# ── Product / Formulation ─────────────────────────────────────
class Product(Base, Mixin):
    __tablename__ = "products"
    code = Column(String, unique=True)
    name = Column(String, nullable=False)
    dosage_form = Column(String, default="tablet")
    strength = Column(String, default="")
    version = Column(String, default="v1.0")
    status = Column(String, default="development")  # development|commercial|retired


class Formulation(Base, Mixin):
    __tablename__ = "formulations"
    product_id = Column(String, ForeignKey("products.id"))
    version = Column(String, default="v1.0")
    lines = Column(Text, default="[]")  # JSON [{material_id, qty_per_unit}]
    customer_spec = Column(Text, default="")


# ── Procurement ───────────────────────────────────────────────
class Supplier(Base, Mixin):
    __tablename__ = "suppliers"
    code = Column(String, unique=True)
    name = Column(String, nullable=False)
    rating = Column(Float, default=3.0)
    lead_time_days = Column(Integer, default=14)
    approved = Column(Boolean, default=False)


class Requisition(Base, Mixin):
    __tablename__ = "requisitions"
    material_id = Column(String)
    qty = Column(Float, default=0)
    requester = Column(String, default="")
    status = Column(String, default="draft")  # draft|submitted|approved|rejected|ordered


class PurchaseOrder(Base, Mixin):
    __tablename__ = "purchase_orders"
    supplier_id = Column(String, ForeignKey("suppliers.id"))
    total = Column(Float, default=0)
    status = Column(String, default="draft")  # draft|sent|received|invoiced|closed
    lines = Column(Text, default="[]")


class GoodsReceipt(Base, Mixin):
    __tablename__ = "goods_receipts"
    po_id = Column(String)
    lot_no = Column(String, default="")
    qty = Column(Float, default=0)
    status = Column(String, default="quarantine")


# ── Manufacturing / Batch ─────────────────────────────────────
class WorkOrder(Base, Mixin):
    __tablename__ = "work_orders"
    product_id = Column(String, ForeignKey("products.id"))
    qty_planned = Column(Float, default=0)
    qty_actual = Column(Float, default=0)
    yield_pct = Column(Float, default=0)
    downtime_min = Column(Integer, default=0)
    status = Column(String, default="planned")  # planned|released|in_process|complete|closed


class Batch(Base, Mixin):
    __tablename__ = "batches"
    product_id = Column(String)
    work_order_id = Column(String, default="")
    batch_no = Column(String, unique=True)
    mfg_date = Column(Date, default=date.today)
    expiry = Column(Date, nullable=True)
    genealogy = Column(Text, default="{}")  # {input lots, equipment, operators, params}
    status = Column(String, default="in_process")  # in_process|qc_pending|released|rejected


# ── Quality ───────────────────────────────────────────────────
class Specification(Base, Mixin):
    __tablename__ = "specifications"
    material_or_product = Column(String)
    tests = Column(Text, default="[]")  # JSON [{param, min, max, unit}]
    version = Column(String, default="v1.0")


class Sample(Base, Mixin):
    __tablename__ = "samples"
    batch_id = Column(String, default="")
    spec_id = Column(String, default="")
    status = Column(String, default="pending")


class QCResult(Base, Mixin):
    __tablename__ = "qc_results"
    sample_id = Column(String)
    param = Column(String)
    value = Column(Float, default=0)
    verdict = Column(String, default="pass")  # pass|oos|oot


class Deviation(Base, Mixin):
    __tablename__ = "deviations"
    ref = Column(String, default="")
    severity = Column(String, default="minor")  # minor|major|critical
    description = Column(Text, default="")
    status = Column(String, default="open")


class CAPA(Base, Mixin):
    __tablename__ = "capas"
    deviation_id = Column(String, default="")
    action = Column(Text, default="")
    owner = Column(String, default="")
    due = Column(Date, nullable=True)
    status = Column(String, default="open")


class ChangeControl(Base, Mixin):
    __tablename__ = "change_controls"
    title = Column(String)
    impact = Column(String, default="low")
    status = Column(String, default="draft")


# ── Sales ─────────────────────────────────────────────────────
class Customer(Base, Mixin):
    __tablename__ = "customers"
    code = Column(String, unique=True)
    name = Column(String, nullable=False)
    credit_limit = Column(Float, default=0)


class SalesOrder(Base, Mixin):
    __tablename__ = "sales_orders"
    customer_id = Column(String, ForeignKey("customers.id"))
    total = Column(Float, default=0)
    delivery_date = Column(Date, nullable=True)
    status = Column(String, default="draft")
    lines = Column(Text, default="[]")


# ── Regulatory ────────────────────────────────────────────────
class Registration(Base, Mixin):
    __tablename__ = "registrations"
    product_id = Column(String)
    country = Column(String)
    dossier_no = Column(String, default="")
    status = Column(String, default="draft")  # draft|submitted|approved|renewal_due
    expiry = Column(Date, nullable=True)


class Submission(Base, Mixin):
    __tablename__ = "submissions"
    registration_id = Column(String, default="")
    kind = Column(String, default="new")  # new|variation|renewal
    status = Column(String, default="draft")
    due = Column(Date, nullable=True)


# ── Finance ───────────────────────────────────────────────────
class CostRecord(Base, Mixin):
    __tablename__ = "cost_records"
    kind = Column(String)  # product|batch|project|customer
    ref_id = Column(String)
    material_cost = Column(Float, default=0)
    mfg_cost = Column(Float, default=0)
    overhead = Column(Float, default=0)
    revenue = Column(Float, default=0)
    margin = Column(Float, default=0)


# ── RAG / knowledge base (BotPharma™ grounding) ──────────────────
# Vector(768) on Postgres+pgvector; plain Text fallback on SQLite.
try:
    from pgvector.sqlalchemy import Vector as _Vector  # type: ignore
    _Embedding = _Vector(768)
except Exception:  # pgvector lib missing (SQLite fallback)
    _Embedding = Text  # type: ignore


class DocChunk(Base, Mixin):
    __tablename__ = "doc_chunks"
    source = Column(String, default="")  # e.g. SOP-014, spec PRD-PARA500, report id
    title = Column(String, default="")
    content = Column(Text, default="")
    embedding = Column(_Embedding, nullable=True)  # set once LLM-gateway embeddings land


ALL_MODELS = [Company, Plant, Warehouse, Material, StockLot, StockMove,
              RDProject, Experiment, Milestone, Patent, Product, Formulation,
              Supplier, Requisition, PurchaseOrder, GoodsReceipt, WorkOrder,
              Batch, Specification, Sample, QCResult, Deviation, CAPA,
              ChangeControl, Customer, SalesOrder, Registration, Submission,
              CostRecord, DocChunk]
