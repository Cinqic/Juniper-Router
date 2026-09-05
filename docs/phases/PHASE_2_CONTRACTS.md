# Phase 2 — contracts, threat model, and host boundary

Status: `tested`.

Schemas are under `schemas/`; typed values are under
`src/juniper_router/contracts/`; semantic and permission checks are in
`runtime/validator.py`; bounded execution is in `runtime/host.py`. The host
rejects duplicate keys, non-standard numeric constants, unknown target IDs,
unknown capability, incompatible arguments, missing confirmation, untrusted
completion, and exhausted budgets. Tests in `tests/contract/`,
`tests/integration/`, and `tests/adversarial/` exercise these failure paths.
