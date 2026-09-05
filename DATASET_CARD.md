# Juniper Router dataset card

## Status

`generated-stratified-reviewed / frozen evaluation`, not a claim of production
data quality. Independent review remains pending.

## Composition

The historical v1 generator creates 44 records across direct answers,
deterministic tools, clarification, freshness routing, delegation, risk
escalation, security boundaries, and orchestration/state. The v2 generator
creates 2,100 records: 1,300 train, 450 development, and 350 frozen formal
test examples. The formal test is balanced across 12 decision classes,
including agent and subagent delegation, and is tracked under
`evals/frozen/` with a SHA-256 manifest.

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

The generated corpus is deterministic and deliberately templated; its size is
not evidence of broad generalization. It does not support claims about broad
tool use, long-horizon agents, real-world safety, or freshness quality.
Independent review, adversarial expansion, and held-out naturalistic data are
still required. Failures must remain visible in evaluation artifacts.
