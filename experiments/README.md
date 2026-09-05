# Experiment registry

`registry.jsonl` is append-only evidence for bounded runs. Each record names
the immutable base/eval inputs, command, machine lane, status, artifact hashes,
and next decision. Large model and prediction artifacts remain outside Git;
their hashes and results are recorded here and in `docs/evidence/`.
