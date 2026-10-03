"""Generic CRUD factory — one system of record per domain, uniform API shape."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import audit as auditlog


def crud_router(model, prefix: str, tag: str) -> APIRouter:
    r = APIRouter(prefix=prefix, tags=[tag])

    @r.get("")
    def list_items(db: Session = Depends(get_db)):
        return db.query(model).order_by(model.created_at.desc()).limit(500).all()

    @r.post("", status_code=201)
    def create_item(payload: dict, db: Session = Depends(get_db)):
        cols = {c.name for c in model.__table__.columns}
        obj = model(**{k: v for k, v in payload.items() if k in cols})
        db.add(obj)
        db.commit()
        db.refresh(obj)
        auditlog.audit("CREATE", model.__tablename__, obj.id, "api", payload)
        return obj

    @r.get("/{item_id}")
    def get_item(item_id: str, db: Session = Depends(get_db)):
        obj = db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        return obj

    @r.patch("/{item_id}")
    def update_item(item_id: str, payload: dict, db: Session = Depends(get_db)):
        obj = db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        cols = {c.name for c in model.__table__.columns}
        for k, v in payload.items():
            if k in cols and k != "id":
                setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        auditlog.audit("UPDATE", model.__tablename__, obj.id, "api", payload)
        return obj

    @r.delete("/{item_id}")
    def delete_item(item_id: str, db: Session = Depends(get_db)):
        obj = db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        db.delete(obj)
        db.commit()
        auditlog.audit("DELETE", model.__tablename__, item_id, "api", {})
        return {"ok": True}

    return r
