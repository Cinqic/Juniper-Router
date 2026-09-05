# Juniper Router model card

## Status

`NOT READY FOR RELEASE`. This repository contains a reproducible engineering
line and a two-step SFT smoke artifact. It does not contain an approved,
capability-qualified Juniper Router model.

## Intended use

Juniper Router is intended to propose one structured routing decision for a
host-controlled local-first orchestrator. The host owns registry lookup,
permissions, confirmation, budgets, execution, trusted results, and audit.
Model text is never evidence that an operation ran.

## Base model

The base is `HuggingFaceTB/SmolLM2-135M` Base at revision
`93efa2f097d58c2a74874c7e644dbc9b0cee75a2`. The pinned manifest records the
Apache-2.0 license, architecture facts, acquisition allowlist, and SHA-256
hashes in [manifests/base-model.json](manifests/base-model.json).

## Training and evaluation

The checked-in seed generator produces 44 reviewed records and the frozen
test manifest contains 12 examples. The available SFT smoke run used two CPU
updates, sequence length 512, learning rate 2e-5, batch size 1, and seed 42.
It is a pipeline/integrity test, not a capability result. See the recorded
evidence in [docs/evidence/baselines.md](docs/evidence/baselines.md) and
[docs/evidence/sft-smoke.md](docs/evidence/sft-smoke.md).

## Limitations and risks

The model is not assumed to reliably emit routing JSON before measured
training. Unconstrained base and prompt-only runs currently have zero valid
structured decisions on the frozen set. The smoke artifact also has zero
valid structured decisions. No claims are made for broad tool use, agents,
freshness, safety, Vulkan, quantization, or throughput.

## Release decision

Release requires independent Astra and Sol review of one immutable commit and
artifact manifest, green CI, complete provenance, passing constrained and
unconstrained evaluation gates, and an authorized operator. This implementation
session has not approved, merged, tagged, published, or released the model.
