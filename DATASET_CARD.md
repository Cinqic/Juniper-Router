# Juniper Router dataset card

## Status

`reviewed seed / frozen evaluation`, not a claim of production data quality.

## Composition

The deterministic generator creates 44 records across direct answers,
deterministic tools, clarification, freshness routing, delegation, risk
escalation, security boundaries, and orchestration/state. The frozen test
subset has 12 examples and is tracked under `evals/frozen/` with a SHA-256
manifest.

## Provenance and licensing

The checked-in records are authored from the user-provided Juniper Router
specification and marked `Apache-2.0` in each record. No external corpus is
required to reproduce this seed set. External data may be added only with
dataset-level provenance, license, consent/privacy review, derivation records,
and split-isolation checks.

## Quality controls

Rows have closed schema versions, exact-key validation, content hashes,
lineage IDs, review status, risk tags, and deterministic generation. The
validator rejects duplicate IDs/hashes, invalid decisions, changed content,
and lineage crossover between splits.

## Limitations

This is a small reviewed seed set, not evidence of generalization. It does not
support claims about broad tool use, long-horizon agents, real-world safety, or
freshness quality. Failures must remain visible in evaluation artifacts.
