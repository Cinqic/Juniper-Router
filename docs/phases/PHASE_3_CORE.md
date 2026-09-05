# Phase 3 — project skeleton and canonical validation

Status: `tested`.

`py -3.12 scripts/validate_repo.py --all` is the one local gate and runs the
same repository tests and Ruff checks used by CI. The core does not download a
model or use the network. Optional model acquisition/training is explicit and
outside normal inference.
