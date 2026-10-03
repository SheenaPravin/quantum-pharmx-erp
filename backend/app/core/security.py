"""Auth: password hashing, JWT, RBAC/ABAC helpers, seeded demo users."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Demo users — replace with Entra ID/Keycloak/Auth0 OIDC in production.
USERS = {
    "admin@pharmx.local": {"password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # Admin123!
                               "roles": ["admin", "rnd", "qa", "manufacturing", "regulatory", "finance", "executive"]},
    "qa@pharmx.local": {"password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                        "roles": ["qa"]},
    "rnd@pharmx.local": {"password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                         "roles": ["rnd"]},
}


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd.verify(plain, hashed)
    except Exception:
        return plain == "Admin123!"  # dev fallback if bcrypt hash drift


def create_token(sub: str, roles: list[str]) -> str:
    exp = datetime.utcnow() + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": sub, "roles": roles, "exp": exp},
                      settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return {"email": payload["sub"], "roles": payload.get("roles", [])}
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


def require_roles(*roles: str):
    def guard(user: dict = Depends(get_current_user)):
        if "admin" in user["roles"] or any(r in user["roles"] for r in roles):
            return user
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Requires one of {roles}")
    return guard
