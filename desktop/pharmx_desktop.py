"""Quantum PharmX desktop launcher — double-click entry point for the Windows exe.

Starts the FastAPI backend (which also serves the bundled web UI) using a
local SQLite database, seeds demo data on first launch, and opens the app
in the default browser. No Python, Node, Postgres, or internet needed.

Source-mode usage (dev):
    python desktop/pharmx_desktop.py [--port 8000] [--no-browser]
"""
import argparse
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)

if FROZEN:
    BASE_DIR = Path(sys.executable).resolve().parent  # folder with the .exe
    DATA_DIR = BASE_DIR / "pharmx-data"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent  # repo root
    DATA_DIR = BASE_DIR / "backend"
    sys.path.insert(0, str(BASE_DIR / "backend"))  # make `app` importable


def find_port(preferred: int) -> int:
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit(f"No free port found near {preferred}.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Quantum PharmX desktop demo")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--no-browser", action="store_true", help="don't auto-open the browser")
    p.add_argument("--data-dir", type=Path, default=DATA_DIR, help="SQLite database directory")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    db_path = args.data_dir / "pharmx.db"

    # Must be set before `app.*` is imported (engine binds at import time).
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{db_path}")

    from app.seed import run as seed_run  # noqa: E402

    fresh = not db_path.is_file() or db_path.stat().st_size == 0
    try:
        seed_run()
    except Exception as e:  # seed is best-effort; existing DBs just work
        print(f"note: seed skipped ({e})")
    print(f"database: {db_path}{' (seeded fresh)' if fresh else ''}")

    port = find_port(args.port)
    url = f"http://127.0.0.1:{port}"

    import uvicorn  # noqa: E402

    print("=" * 60)
    print("  Quantum PharmX BI — desktop demo")
    print(f"  Open: {url}")
    print("  Login: admin@pharmx.local / Admin123!")
    print("  Stop: close this window (or Ctrl+C)")
    print("=" * 60)
    if not args.no_browser:
        threading.Timer(1.5, webbrowser.open, args=[url]).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
