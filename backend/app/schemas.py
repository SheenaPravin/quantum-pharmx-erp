"""Pydantic schemas — permissive dict-style for rapid ERP coverage with validation."""
from typing import Any, Optional
from pydantic import BaseModel


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    roles: list[str] = []


class ChatIn(BaseModel):
    message: str
    context: dict[str, Any] = {}


class WorkflowSubmit(BaseModel):
    kind: str
    ref: str
    requester: str
    amount: float = 0


class WorkflowDecision(BaseModel):
    approver: str
    decision: str  # approve|reject
    comment: str = ""
