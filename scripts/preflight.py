from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def command_version(name: str) -> str | None:
    path = shutil.which(name)
    if not path:
        return None
    try:
        return (
            subprocess.run(
                [name, "--version"], capture_output=True, text=True, check=False
            ).stdout.strip()
            or path
        )
    except OSError:
        return path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "git": command_version("git"),
        "cmake": command_version("cmake"),
        "ninja": command_version("ninja"),
        "vulkaninfo": shutil.which("vulkaninfo"),
        "status": "tested",
    }
    out = root / "docs" / "phases" / "environment-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
