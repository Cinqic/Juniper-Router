# Current phase status

| Phase | Status | Evidence |
| --- | --- | --- |
| 0 repository/machine baseline | tested | `PHASE_0_BASELINE.md`, environment report |
| 1 research/requirements | implemented/tested | research ledger and spec |
| 2 contracts/threat model | tested | schemas, validators, adversarial tests |
| 3 skeleton/canonical validation | tested | 14 tests and Ruff pass |
| 4 base acquisition/baselines | tested | pinned safe-format acquisition, local hash checks, raw/prompt-only frozen baselines |
| 5 data/evaluation freeze | implemented/tested | deterministic seed set and frozen manifest |
| 6 training smoke | tested | two-step native Windows CPU SFT saved and reloaded; zero valid decisions |
| 7–13 candidate, export, review, release | planned/untested | no capability or release claim |

The repository is not ready for release unless later phases add evidence that
closes the explicit gates in `docs/evaluation-policy.md`.
