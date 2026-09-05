# Formal v2 pilot evidence

## Status

The 30-step LoRA run is a measured negative result and is not a candidate for
independent release review. The v2 policy hard gates remain unmet.

## Frozen inputs

- Base: `HuggingFaceTB/SmolLM2-135M` revision
  `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`
- Dataset: `juniper-router-dataset-v2`
- Renderer: `chatml-router-compact-v1`
- Formal suite: `evals/frozen/router-eval-v2.jsonl`, 350 cases
- Policy: `configs/evaluation/formal-policy-v2.json`
- Training: LoRA rank 8, alpha 16, dropout 0.05, learning rate 2e-4,
  sequence length 512, batch size 1, seed 42, 30 optimizer steps
- Platform: native Windows CPU; no CUDA, Linux, WSL, or cloud execution

## Candidate result

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

The pilot is not ready for independent review. A longer continuation is
required before the training line can be judged, and no release or PR should
be presented from this result.
