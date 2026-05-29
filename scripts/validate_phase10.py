"""
Phase 10 — Final submission validation.
Run: py scripts/validate_phase10.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    "README.md",
    "SYSTEM_OVERVIEW.md",
    "DEFENSE_GUIDE.md",
    "INSTALLATION_GUIDE.md",
    "DEMO_SCRIPT.md",
    "DEMO_CHECKLIST.md",
    "PROJECT_STRUCTURE.md",
    "FINAL_CHECKLIST.md",
]
FORBIDDEN_IN_APP = [
    "import sqlite3",
    "from sqlite3",
    "client_storage",
    "import flet_core",
    "from flet_core",
]
SCAN_DIRS = ["pages", "controllers", "services", "repositories", "database", "components", "utils", "router.py", "app.py", "main.py"]


def main() -> int:
    print("=== Phase 10 Final Submission Validation ===\n")
    failed = False

    # Documentation
    print("[1] Documentation files")
    for name in DOCS:
        path = ROOT / name
        if path.is_file():
            print(f"  [OK] {name}")
        else:
            print(f"  [FAIL] Missing {name}")
            failed = True

    # Requirements
    print("\n[2] requirements.txt")
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    if "flet" in req and "mysql-connector-python" in req and "sqlite" not in req:
        print("  [OK] flet + mysql-connector-python only")
    else:
        print("  [FAIL] requirements.txt")
        failed = True

    # Forbidden tech in app code
    print("\n[3] Forbidden technology scan (app code)")
    forbidden_hit = False
    for rel in SCAN_DIRS:
        target = ROOT / rel
        paths = [target] if target.is_file() else list(target.rglob("*.py"))
        for p in paths:
            text = p.read_text(encoding="utf-8", errors="ignore")
            for token in FORBIDDEN_IN_APP:
                if token in text:
                    print(f"  [FAIL] {token} in {p.relative_to(ROOT)}")
                    forbidden_hit = True
                    failed = True
    if not forbidden_hit:
        print("  [OK] No forbidden imports in application code")

    # Architecture: SQL in pages/controllers
    print("\n[4] Architecture scan")
    arch_ok = True
    for folder in ("pages", "controllers"):
        for p in (ROOT / folder).rglob("*.py"):
            if "execute(" in p.read_text(encoding="utf-8", errors="ignore"):
                print(f"  [FAIL] SQL execute() in {p.relative_to(ROOT)}")
                arch_ok = False
                failed = True
    if arch_ok:
        print("  [OK] No SQL in pages/controllers")

    # Run Phase 9 suite
    print("\n[5] Phase 9 regression suite")
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_phase9.py")], cwd=str(ROOT))
    if result.returncode != 0:
        failed = True

    print("\n=== Phase 10 Summary ===")
    if failed:
        print("SOME CHECKS FAILED — review output above.")
        return 1
    print("ALL PHASE 10 CHECKS PASSED — submission ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
