"""Export an already-manifested HF checkpoint through a fixed llama.cpp toolchain."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.provenance.hashing import sha256_file  # noqa: E402


def _find_converter(llama_cpp: Path) -> Path:
    candidates = (
        llama_cpp / "convert_hf_to_gguf.py",
        llama_cpp / "convert_hf_to_gguf_update.py",
    )
    for candidate in candidates:
        if candidate.is_file() and candidate.name == "convert_hf_to_gguf.py":
            return candidate
    raise SystemExit(
        "GGUF export unavailable: expected llama.cpp/convert_hf_to_gguf.py in --llama-cpp"
    )


def _find_quantizer(llama_cpp: Path) -> Path:
    candidates = [
        llama_cpp / "build" / "bin" / "Release" / "llama-quantize.exe",
        llama_cpp / "build" / "bin" / "llama-quantize.exe",
        llama_cpp / "llama-quantize.exe",
    ]
    candidates.extend(
        path
        for build_dir in sorted(llama_cpp.glob("build*"))
        if build_dir.is_dir()
        for path in (
            build_dir / "bin" / "Release" / "llama-quantize.exe",
            build_dir / "bin" / "llama-quantize.exe",
        )
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    on_path = shutil.which("llama-quantize")
    if on_path:
        return Path(on_path)
    raise SystemExit("GGUF quantization unavailable: build llama-quantize first")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--llama-cpp", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quant-type", default="Q4_K_M")
    parser.add_argument("--manifest", type=Path, default=Path("manifests/artifacts/gguf.json"))
    args = parser.parse_args()

    model_manifest = json.loads(
        (ROOT / "manifests" / "base-model.json").read_text(encoding="utf-8")
    )
    if not args.model.is_dir():
        raise SystemExit(f"model directory does not exist: {args.model}")
    for entry in model_manifest["files"]:
        path = args.model / entry["name"]
        if not path.is_file() or path.stat().st_size != entry["bytes"]:
            raise SystemExit(f"model file missing or size mismatch: {path}")
        if sha256_file(path) != entry["sha256"]:
            raise SystemExit(f"model file hash mismatch: {path}")

    converter = _find_converter(args.llama_cpp)
    quantizer = _find_quantizer(args.llama_cpp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    f16_path = args.output.with_name(args.output.stem + ".f16.gguf")
    convert_command = [
        sys.executable,
        str(converter),
        str(args.model),
        "--outfile",
        str(f16_path),
        "--outtype",
        "f16",
    ]
    subprocess.run(convert_command, cwd=args.llama_cpp, check=True)
    quantize_command = [str(quantizer), str(f16_path), str(args.output), args.quant_type]
    subprocess.run(quantize_command, cwd=args.llama_cpp, check=True)
    toolchain_revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=args.llama_cpp, text=True
    ).strip()
    artifact = {
        "manifest_version": "juniper-router-gguf-manifest-v1",
        "status": "tested",
        "base_model": f"{model_manifest['model_id']}@{model_manifest['revision']}",
        "quantization": args.quant_type,
        "toolchain": "llama.cpp",
        "toolchain_revision": toolchain_revision,
        "files": [
            {
                "path": args.output.name,
                "bytes": args.output.stat().st_size,
                "sha256": sha256_file(args.output),
            }
        ],
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
