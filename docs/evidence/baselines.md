# Baseline and smoke evaluation evidence

Run date: `2026-09-05` on native Windows CPU. The frozen set is
`evals/frozen/router-eval-v1.jsonl`, 12 examples, SHA-256
`ffaba2cc2f59b6b6e9913597c144b9812ec5aac4073e66c7593ad799e29b40cf`.

## Results

| Run | Prompt lane | Valid structured decisions | Decision accuracy | Target accuracy | Macro-F1 | Semantic validator pass |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| pinned base | raw user text | 0/12 | 0.0 | 0.0 | 0.0 | 0.0 |
| pinned base | explicit router prompt | 0/12 | 0.0 | 0.0 | 0.0 | 0.0 |
| two-step SFT smoke | explicit router prompt | 0/12 | 0.0 | 0.0 | 0.0 | 0.0 |

The raw and prompt-only base JSONL files are local ignored artifacts. Their
recorded hashes are
`e86e4fea1d8c71eefeb478b507a7024c3a54fd978c2f270f6ea20d9452a31bea` and
`99ec8ef995da1e43845baa16d6c9ae3d8f1d0828a34e00e5650f1e7d9480f36e`.
The two-step smoke prompt-lane output hash is
`99ec8ef995da1e43845baa16d6c9ae3d8f1d0828a34e00e5650f1e7d9480f36e`.

These are negative results, retained to prevent an accidental reliability
claim. The result does not imply the architecture is ineffective; it shows
that this base and this two-update smoke artifact do not yet satisfy the
structured-output gate.

## Reproduction

```powershell
$env:PYTHONPATH = "$PWD\src"
py -3.12 scripts/run_baseline.py --model <pinned-cache> --max-new-tokens 8
py -3.12 scripts/evaluate.py --predictions artifacts-local/baselines/prompt-only-base.jsonl
```

The script preserves raw continuations beside parsed predictions. A future
candidate must report both raw unconstrained and constrained-lane metrics on
the same frozen manifest.
