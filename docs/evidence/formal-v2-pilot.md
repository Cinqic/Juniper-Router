# Formal v2 training and evaluation evidence

## Status

The 30-step pilot and the longer 90-step ordered-target continuation are
measured negative results. Neither is a candidate for independent release
review. The v2 policy hard gates remain unmet.

## Frozen inputs

- Base: `HuggingFaceTB/SmolLM2-135M` revision
  `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`
- Dataset: `juniper-router-dataset-v2`
- Renderer: `chatml-router-compact-v1`
- Formal suite: `evals/frozen/router-eval-v2.jsonl`, 350 cases
- Policy: `configs/evaluation/formal-policy-v2.json`
- Historical training: LoRA rank 8, alpha 16, dropout 0.05, learning rate
  2e-4, sequence length 512, batch size 1, seed 42, 30 optimizer steps
- Platform: native Windows CPU; no CUDA, Linux, WSL, or cloud execution

## Historical 30-step pilot

The adapter was evaluated offline with greedy generation and a 96-token cap.
All 350 predictions were invalid or unparseable:

| Metric | Result | v2 hard gate |
| --- | ---: | ---: |
| constrained syntactic validity | 0.000 | 1.000 |
| semantic validator pass | 0.000 | 1.000 |
| decision accuracy | 0.000 | 0.950 |
| macro-F1 | 0.000 | 0.930 |
| target accuracy when required | 0.000 | 0.950 |
| argument semantic correctness | 0.000 | 0.950 |
| critical escalation recall | 0.000 | 0.980 |
| invalid predictions | 350/350 | 0 |

Raw JSONL output and metrics are retained outside the repository under the
machine-local artifact root. The output clusters show schema copying and
truncated malformed JSON; this evidence is preserved rather than repaired in
post-processing.

## Decision

The pilot was not ready for independent review. Its raw JSONL and metrics are
retained externally as a historical negative result.

## 90-step ordered-target continuation

The continuation used the same pinned base, v2 dataset, compact renderer, and
native Windows CPU lane, with `ordered-v1` target serialization and 90 LoRA
optimizer steps. The run took 10,424.875 seconds wall-clock according to the
training process result and saw 43,880 training tokens. The final local
validation loss was 0.5922238752. The adapter and full formal evaluation are
retained under the external project-specific artifact root.

| Metric | Result | v2 hard gate |
| --- | ---: | ---: |
| constrained syntactic validity | 0.3371 (118/350) | 1.000 |
| semantic validator pass | 0.0857 (30/350) | 1.000 |
| decision accuracy | 0.2086 | 0.950 |
| macro-F1 | 0.1992 | 0.930 |
| target accuracy when required | 0.0000 | 0.950 |
| argument semantic correctness | 0.0000 | 0.950 |
| critical escalation recall | 0.2000 | 0.980 |
| invalid predictions | 320/350 | 0 |

The authoritative critical-escalation value above was recomputed by joining
the raw predictions to the frozen suite's `risk_tags` by `example_id`. The
first batch-8 process began before the evaluator's risk-tag output fix, so its
raw metrics are retained separately and the corrected metrics are the value
used for this report. No prediction was repaired or relabeled.

The longer run improved syntax over the 30-step pilot but still generated
invalid decision names, missing/incorrect targets, and malformed continuations
on most cases. It fails the first constrained gate and all capability gates;
the project remains `NOT READY FOR INDEPENDENT REVIEW` and no PR, merge,
release, or approval is being presented.

## Next experiment

Before spending another long CPU run, make structured decoding or a narrower
verbatim target representation a separately measured experiment. Re-run a
small held-out slice first, then repeat the complete frozen suite only if the
slice clears syntax, target, and semantic-validator checks. Keep the current
negative artifacts immutable.
