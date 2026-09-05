# Phase 1 — research and feasibility

Status: `implemented` and `tested` for the research ledger and traceability
inputs; model feasibility remains `unproven`.

The supplied specification is normalized in `docs/spec/juniper-router-v1.md`.
The principal feasibility warning is retained: small-model post-training work
does not make reliable function calling at 135M a given. The design therefore
specializes the output envelope, supplies dynamic state, constrains formatting
where a backend permits it, and treats escalation/clarification as successful
routes when evidence requires them.

The research ledger records exact access dates, primary URLs, claims, limits,
and refreshed Cinqic commits. No upstream instruct checkpoint is substituted
for the requested Base lineage.
