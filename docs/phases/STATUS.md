# Current phase status

| Phase | Status | Evidence |
| --- | --- | --- |
| 0 repository/machine baseline | tested | `PHASE_0_BASELINE.md`, environment report |
| 1 research/requirements | implemented/tested | research ledger and spec |
| 2 contracts/threat model | tested | schemas, validators, adversarial tests |
| 3 skeleton/canonical validation | tested | 23 tests and Ruff pass |
| 4 base acquisition/baselines | tested | pinned safe-format acquisition, local hash checks, raw/prompt-only frozen baselines |
| 5 data/evaluation freeze | tested | deterministic v2 corpus, balanced 350-case suite, frozen manifest |
| 6 training smoke/pilot | tested | v1 smoke preserved; 30-step pilot and 90-step ordered-target native Windows CPU LoRA continuation completed; the continuation reached 118/350 syntactically valid but only 30/350 semantic-validator passes |
| 7–13 candidate, export, review, release | measured-negative / planned | formal v2 gates fail; base-only GGUF lane tested; no capability or release claim |

The repository is not ready for release unless later phases add evidence that
closes the explicit gates in `docs/evaluation-policy.md`.
