# Juniper Router

Status: `candidate engineering line` — not independently approved or released.

Juniper Router is a bounded experiment around HuggingFaceTB/SmolLM2-135M Base.
The product claim is narrow: a small local model proposes one routing decision,
and a host validates, authorizes, budgets, executes, and records it. The model
is never the security boundary and its text never proves that an operation ran.

The repository currently contains the tested contract/runtime/data core and the
optional real Transformers SFT path. A trained candidate, GGUF export, Windows
Vulkan result, and Linux/FLOWBOX review are not claimed until their manifests
and measurements exist.

## Quick validation

The canonical command is:

```powershell
py -3.12 scripts/validate_repo.py --all
```

The canonical environment is Python 3.12 on native Windows or Linux CPU. The
contract and mock-runtime tests need no model download. Generate the reviewed
seed corpus with `py -3.12 scripts/build_data.py`; it is deterministic and
reconstructible, while frozen evaluation records live under `evals/frozen/`.

## Safe local routing demo

```powershell
$env:PYTHONPATH = "$PWD\src"
py -3.12 -m juniper_router route "Calculate 2 + 2" --confirm
py -3.12 -m juniper_router route "Search for today's weather" --confirm
```

`--confirm` simulates an explicit host permission grant for the harmless mock
fixtures. Without it, the host rejects the proposed operation. No shell,
network, or arbitrary-code tool is exposed by the reference runtime.

## Optional model path

Install the model environment from `requirements-model.lock` (the `.in` file is
the reviewed intent), acquire the pinned safe-format base with `py -3.12
scripts/acquire_base.py --output <cache>`, then run the bounded SFT entry point
in `scripts/train.py`. Acquisition records SHA-256 hashes in a local manifest
and stores weights outside Git. Training is an experiment, not evidence of
capability; evaluate against the frozen suites and preserve failures before
calling anything a candidate. LoRA is supported through the pinned PEFT
dependency; the compact router prompt is a distinct measured renderer mode.

## Design and evidence

- [Architecture and trust boundary](docs/architecture/overview.md)
- [Versioned behavior specification](docs/spec/juniper-router-v1.md)
- [Research ledger](docs/research/research-ledger.md)
- [Security model](SECURITY.md)
- [Windows recovery](docs/recovery/FRESH_CLONE.md)
- [Evaluation and release policy](docs/evaluation-policy.md)
- [Independent review protocol](docs/review/RELEASE_PROTOCOL.md)

The normal user path is local-first and CPU-capable. CUDA, DirectML, Vulkan,
and llama.cpp are optional lanes and are advertised only when tested.

The checked-in `scripts/export_gguf.py` is the reproducible GGUF handoff path;
it requires a separately built llama.cpp converter and quantizer. The pinned
base has a tested CPU-only Q4_K_M export recorded in
`docs/evidence/gguf-toolchain.md`; this is not a router-capability or hardware
acceleration claim.
