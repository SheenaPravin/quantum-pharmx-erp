"""Tamper-evident audit trail (append-only) + e-signature helper.

Production: ship to immutable store (S3 Object Lock / CloudWatch / SIEM) and
enforce 21 CFR Part 11 controls (unique logins, e-signatures, record retention).
"""
import hashlib
import json
from datetime import datetime

AUDIT_LOG: list[dict] = []
_prev_hash = "GENESIS"


def audit(action: str, entity: str, entity_id: str, actor: str, details: dict | None = None) -> dict:
    global _prev_hash
    ts = datetime.utcnow().isoformat()
    body = json.dumps({"ts": ts, "actor": actor, "action": action,
                       "entity": entity, "id": entity_id, "details": details or {},
                       "prev": _prev_hash}, sort_keys=True)
    h = hashlib.sha256(body.encode()).hexdigest()
    rec = json.loads(body) | {"hash": h}
    _prev_hash = h
    AUDIT_LOG.append(rec)
    return rec


def esign(record_id: str, signer: str, meaning: str) -> dict:
    return audit("ESIGN", "record", record_id, signer, {"meaning": meaning})
