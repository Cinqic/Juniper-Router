"""Canonical repository validator used locally and by CI."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import compileall
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.contracts.models import Decision, Registry
from juniper_router.data.fixtures import default_registry
from juniper_router.data.generate import build_records
from juniper_router.data.validate import validate_records
from juniper_router.provenance.hashing import sha256_file
from juniper_router.rendering.chatml import RUNTIME_PERSONALITY_SHA256, render_chatml


def check_json_files() -> None:
    files = (
        list((ROOT / "schemas").glob("*.json"))
        + list((ROOT / "configs").rglob("*.json"))
        + list((ROOT / "evals").rglob("*.json"))
        + list((ROOT / "manifests").rglob("*.json"))
    )
    for path in files:
        json.loads(path.read_text(encoding="utf-8"))
    if len(files) < 10:
        raise AssertionError("too few checked-in JSON contract/config files")


def check_contracts() -> None:
    registry = default_registry()
    valid = {
        "schema_version": "juniper-router-decision-v1",
        "decision": "answer_directly",
        "status": "ok",
        "target_id": None,
        "arguments": None,
        "message": "ok",
        "reason_code": "direct_answer_within_capability",
        "confidence": "high",
    }
    if Decision.from_dict(valid).to_dict() != valid:
        raise AssertionError("decision round-trip changed data")
    if Registry.from_dict(registry.to_dict()).to_dict() != registry.to_dict():
        raise AssertionError("registry round-trip changed data")
    if not render_chatml([{"role": "user", "content": "hello"}]).endswith("<|im_end|>\n"):
        raise AssertionError("renderer delimiter contract failed")
    if len(RUNTIME_PERSONALITY_SHA256) != 64:
        raise AssertionError("personality hash missing")


def check_data() -> None:
    first = build_records()
    second = build_records()
    encoded_first = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in first)
    encoded_second = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) for row in second
    )
    if (
        hashlib.sha256(encoded_first.encode()).hexdigest()
        != hashlib.sha256(encoded_second.encode()).hexdigest()
    ):
        raise AssertionError("data generator is not deterministic")
    result = validate_records(first)
    if not result["valid"]:
        raise AssertionError("data validation failed: " + "; ".join(result["errors"][:5]))
    if result["records"] < 40:
        raise AssertionError("frozen seed set is unexpectedly small")


def check_base_manifest() -> None:
    manifest = json.loads((ROOT / "manifests" / "base-model.json").read_text(encoding="utf-8"))
    if manifest["calculated_trainable_parameters"] != 134_515_008:
        raise AssertionError("base parameter count is not the verified tied-embedding count")
    if manifest["revision"] != "93efa2f097d58c2a74874c7e644dbc9b0cee75a2":
        raise AssertionError("base revision changed without an explicit manifest update")


def check_frozen_eval() -> None:
    path = ROOT / "evals" / "frozen" / "router-eval-v1.jsonl"
    manifest_path = ROOT / "evals" / "manifests" / "frozen-v1.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not path.exists() or manifest["sha256"] != sha256_file(path):
        raise AssertionError("frozen evaluation file and manifest disagree")


def check_formal_eval() -> None:
    path = ROOT / "evals" / "frozen" / "router-eval-v2.jsonl"
    manifest_path = ROOT / "evals" / "manifests" / "formal-v2.json"
    policy_path = ROOT / "configs" / "evaluation" / "formal-policy-v2.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not path.exists() or manifest["eval_sha256"] != sha256_file(path):
        raise AssertionError("formal v2 evaluation file and manifest disagree")
    if (
        manifest["examples"] < 300
        or manifest["policy"] != "configs/evaluation/formal-policy-v2.json"
    ):
        raise AssertionError("formal v2 manifest is incomplete")
    if policy["status"] != "frozen-before-formal-candidate-evaluation":
        raise AssertionError("formal v2 policy is not frozen")
    if policy["hard_gates"]["constrained_syntactic_validity"] != 1.0:
        raise AssertionError("constrained validity gate was weakened")


def check_experiment_registry() -> None:
    path = ROOT / "experiments" / "registry.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not rows or any(not row.get("experiment_id") or not row.get("status") for row in rows):
        raise AssertionError("experiment registry must contain identified status records")


def run_tool(command: list[str], label: str) -> None:
    selected = command
    if command[0] == sys.executable:
        module = command[2] if len(command) > 2 and command[1] == "-m" else None
        if module is not None:
            try:
                __import__(module)
            except ImportError:
                venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
                if venv_python.exists():
                    selected = [str(venv_python), *command[1:]]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(selected, cwd=ROOT, text=True, env=env)
    if result.returncode:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="run the complete local gate")
    args = parser.parse_args()
    try:
        check_json_files()
        check_contracts()
        check_data()
        check_base_manifest()
        check_frozen_eval()
        check_formal_eval()
        check_experiment_registry()
        if not compileall.compile_dir(str(ROOT / "src"), quiet=1):
            raise RuntimeError("Python compilation failed")
        if args.all:
            run_tool([sys.executable, "-m", "pytest", "tests"], "pytest")
            run_tool([sys.executable, "-m", "ruff", "check", "src", "scripts", "tests"], "ruff")
        print("PASS: Juniper Router canonical validation")
        return 0
    except (AssertionError, OSError, RuntimeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
