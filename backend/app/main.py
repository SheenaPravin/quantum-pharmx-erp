"""FastAPI entrypoint — API gateway + domain services + AI layer."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app import models  # noqa: F401 — register tables
from app.api.v1 import router as v1

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quantum PharmX BI", version="0.1.0",
              description="Pharma R&D / manufacturing / business operations + BotPharma")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(v1)


@app.get("/health")
def health():
    return {"ok": True, "service": "quantum-pharmx-bi", "version": "0.1.0"}
