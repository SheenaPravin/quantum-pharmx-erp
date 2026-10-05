from fastapi.testclient import TestClient
from app.main import app
import uuid

c = TestClient(app)

def test_health():
    assert c.get("/health").json()["ok"] is True

def test_login_and_crud():
    r = c.post("/api/v1/auth/login", json={"username": "admin@pharmx.local", "password": "Admin123!"})
    assert r.status_code == 200, r.text
    tok = r.json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    assert c.get("/api/v1/analytics/kpis", headers=h).status_code == 200
    m = c.post("/api/v1/materials", headers=h,
               json={"code": f"T-{uuid.uuid4().hex[:8]}", "name": "Test API", "kind": "raw"}).json()
    assert c.get(f"/api/v1/materials/{m['id']}", headers=h).status_code == 200
    assert c.post("/api/v1/botpharma/chat", headers=h,
                  json={"message": "low stock risks"}).status_code == 200
    assert c.post("/api/v1/agents/supply_chain/run", headers=h, json={}).status_code == 200

def test_anonymous_mutations_blocked_reads_open():
    assert c.get("/api/v1/materials").status_code == 200  # browseable for reviewers
    assert c.post("/api/v1/materials", json={"code": "X", "name": "anon"}).status_code == 401
    assert c.patch("/api/v1/materials/nope", json={"name": "anon"}).status_code == 401
    assert c.delete("/api/v1/materials/nope").status_code == 401
