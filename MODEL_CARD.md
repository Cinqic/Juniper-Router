# Juniper Router model card

## Status

`NOT READY FOR RELEASE`. This repository contains a reproducible engineering
line, an expanded formal evaluation, and measured training artifacts. It does
not contain an approved, capability-qualified Juniper Router model.

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

The checked-in seed generator remains preserved as historical v1 evidence. The
formal v2 generator produces 2,100 deterministic records and a frozen,
balanced 350-case test suite with 12 decision classes. A 30-step LoRA pilot and
a 90-step ordered-target continuation ran on native Windows CPU. The
continuation produced 118/350 syntactically valid decisions, 30/350 semantic
validator passes, 0.2086 decision accuracy, 0.1992 macro-F1, and 0.20 critical
escalation recall. These results fail the v2 gates and are a measured negative
capability result, not a release candidate. See the recorded evidence in
[docs/evidence/baselines.md](docs/evidence/baselines.md),
[docs/evidence/sft-smoke.md](docs/evidence/sft-smoke.md), and
[docs/evidence/formal-v2-pilot.md](docs/evidence/formal-v2-pilot.md).

## Limitations and risks

The model is not assumed to reliably emit routing JSON before measured
training. The v2 LoRA pilot currently has zero valid structured decisions on
the frozen set. No claims are made for broad tool use, agents, freshness,
safety, Vulkan, quantization, or throughput. Invalid model text remains
fail-closed at the host boundary.

## Release decision

Release requires independent Astra and Sol review of one immutable commit and
artifact manifest, green CI, complete provenance, passing constrained and
unconstrained evaluation gates, and an authorized operator. This implementation
session has not approved, merged, tagged, published, or released the model.
