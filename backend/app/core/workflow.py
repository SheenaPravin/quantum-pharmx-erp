"""Configurable approval workflows (Camunda-ready).

Dev implementation: in-memory state machine with an approval matrix and
segregation-of-duties guard. Production: delegate to Camunda (long-running
controlled processes: procurement approval, QA release, CAPA, change control,
regulatory submission).
"""
from datetime import datetime
from typing import Literal

STORE: dict[str, dict] = {}

# requester may not approve own request (SoD)
def submit_workflow(kind: str, ref: str, requester: str, amount: float = 0) -> dict:
    steps = ["manager", "qa"] if kind in ("qa_release", "capa", "change_control") else ["manager"]
    if amount and amount > 50000:
        steps.append("finance")
    wf = {"kind": kind, "ref": ref, "requester": requester,
          "steps": steps, "current": 0, "status": "pending",
          "history": [{"by": requester, "action": "submit", "at": datetime.utcnow().isoformat()}]}
    STORE[ref] = wf
    return wf


def approve(ref: str, approver: str, decision: Literal["approve", "reject"], comment: str = "") -> dict:
    wf = STORE.get(ref)
    if not wf or wf["status"] != "pending":
        raise ValueError("workflow not pending")
    if approver == wf["requester"]:
        raise ValueError("segregation of duties: requester cannot approve own request")
    entry = {"by": approver, "action": decision, "comment": comment,
             "at": datetime.utcnow().isoformat()}
    wf["history"].append(entry)
    if decision == "reject":
        wf["status"] = "rejected"
    else:
        wf["current"] += 1
        wf["status"] = "approved" if wf["current"] >= len(wf["steps"]) else "pending"
    return wf
