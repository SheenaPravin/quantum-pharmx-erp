"""Generic CRUD factory — one system of record per domain, uniform API shape.

Reads are open (review/browse); every mutation requires a logged-in user and is
audit-attributed to that user. Anonymous POST/PATCH/DELETE → 401.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import audit as auditlog
from app.core import security as sec


def crud_router(model, prefix: str, tag: str) -> APIRouter:
    r = APIRouter(prefix=prefix, tags=[tag])

    @r.get("")
    def list_items(db: Session = Depends(get_db)):
        return db.query(model).order_by(model.created_at.desc()).limit(500).all()

    @r.post("", status_code=201)
    def create_item(payload: dict, db: Session = Depends(get_db),
                    user: dict = Depends(sec.get_current_user)):
        cols = {c.name for c in model.__table__.columns}
        obj = model(**{k: v for k, v in payload.items() if k in cols})
        db.add(obj)
        db.commit()
        db.refresh(obj)
        auditlog.audit("CREATE", model.__tablename__, obj.id, user["email"], payload)
        return obj

    @r.get("/{item_id}")
    def get_item(item_id: str, db: Session = Depends(get_db)):
        obj = db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        return obj

    @r.patch("/{item_id}")
    def update_item(item_id: str, payload: dict, db: Session = Depends(get_db),
                    user: dict = Depends(sec.get_current_user)):
        obj = db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        cols = {c.name for c in model.__table__.columns}
        for k, v in payload.items():
            if k in cols and k != "id":
                setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        auditlog.audit("UPDATE", model.__tablename__, obj.id, user["email"], payload)
        return obj

    @r.delete("/{item_id}")
    def delete_item(item_id: str, db: Session = Depends(get_db),
                    user: dict = Depends(sec.get_current_user)):
        obj = db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Not found")
        db.delete(obj)
        db.commit()
        auditlog.audit("DELETE", model.__tablename__, item_id, user["email"], {})
        return {"ok": True}

    return r
