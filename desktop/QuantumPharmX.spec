# PyInstaller build for the Quantum PharmX Windows desktop demo.
# Built on windows-latest via .github/workflows/desktop.yml (PyInstaller
# cannot cross-compile, so the .exe must be built on Windows).
#
#   pyinstaller desktop/QuantumPharmX.spec
#
# Inputs (built beforehand by CI): backend/ source + frontend/out static UI.
# Output: dist/QuantumPharmX/QuantumPharmX.exe (single folder, double-click).
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

ROOT = Path(SPECPATH).parent  # desktop/
REPO = ROOT.parent
BACKEND = REPO / "backend"
WEB_OUT = REPO / "frontend" / "out"

APP_MODULES = [
    "app.main",
    "app.models",
    "app.schemas",
    "app.seed",
    "app.services",
    "app.api.v1",
    "app.api.crud",
    "app.core.audit",
    "app.core.config",
    "app.core.database",
    "app.core.security",
    "app.core.workflow",
]

a = Analysis(  # noqa: F821 — provided by PyInstaller at build time
    [str(ROOT / "pharmx_desktop.py")],
    pathex=[str(BACKEND)],
    binaries=[],
    # Static web UI served by the backend itself (see app/main.py web_dir()).
    datas=[(str(WEB_OUT), "web")],
    hiddenimports=APP_MODULES
    + collect_submodules("uvicorn")
    + collect_submodules("starlette")
    + collect_submodules("anyio")
    + [
        "passlib.handlers.bcrypt",
        "jose",
        "sqlite3",
        "sklearn",
        "sklearn.ensemble",
        "sklearn.linear_model",
        "sklearn.preprocessing",
        "pandas",
        "numpy",
        "scipy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="QuantumPharmX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # keep the terminal: shows the URL + logs, aids troubleshooting
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="QuantumPharmX",
)
