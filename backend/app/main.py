"""FastAPI entrypoint — API gateway + domain services + AI layer.

Also serves the bundled web UI (Next.js static export) when present, so the
Windows desktop exe runs as a single process: API + UI on one port.
"""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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


def web_dir() -> Path | None:
    """Locate the bundled static UI (PyInstaller data dir, repo layout, or CWD)."""
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(getattr(sys, "_MEIPASS", "")) / "web")
        candidates.append(Path(sys.executable).resolve().parent / "web")
    here = Path(__file__).resolve().parent
    candidates += [
        here.parent.parent / "frontend" / "out",  # repo layout: backend/app -> frontend/out
        Path.cwd() / "frontend" / "out",
        Path.cwd() / "web",
    ]
    for c in candidates:
        if c.is_dir() and (c / "index.html").is_file():
            return c
    return None


WEB = web_dir()
if WEB is not None:
    # Hashed JS/CSS chunks — cacheable, served directly.
    if (WEB / "_next").is_dir():
        app.mount("/_next", StaticFiles(directory=WEB / "_next"), name="next-static")

    @app.get("/{full_path:path}", include_in_schema=False)
    def _spa(full_path: str):
        # API + docs keep their own handlers registered above; anything else
        # that looks like an API call is a genuine 404, not the SPA shell.
        if full_path.startswith("api/"):
            raise HTTPException(404, "Not found")
        target = (WEB / full_path) if full_path else WEB
        if target.is_file():
            return FileResponse(target)
        if (target / "index.html").is_file():  # trailingSlash export: /rnd -> /rnd/index.html
            return FileResponse(target / "index.html")
        return FileResponse(WEB / "index.html")
