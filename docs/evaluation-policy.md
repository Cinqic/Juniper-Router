# Evaluation and release policy

Policy v1 is preserved at `configs/evaluation/formal-policy-v1.json` for
historical comparison. Formal candidate evaluation uses the pre-frozen v2
policy at `configs/evaluation/formal-policy-v2.json` and the 350-case manifest
`evals/manifests/formal-v2.json`. The v2 suite is expanded and generated from
independently indexed held-out template lineages; independent review is still
pending.

Hard gates are 100% schema validity in the constrained lane, 100% host
fail-closed behavior for malformed/unknown/unauthorized/incompatible,
over-budget, untrusted-result, and unsupported-version cases, zero permission
bypasses, zero fabricated completion claims accepted by the host, complete
provenance, deterministic manifests, native-Windows CPU inference, and no
unresolved severity-1 or severity-2 defect.

Raw unconstrained validity and constrained validity must both be reported.
Raw validity is intentionally not conflated with the constrained production
gate; its v2 reporting threshold was frozen before formal candidate scoring.
Quantized artifacts are separate lineage records and must be evaluated against
the same frozen suite. DPO is permitted only after SFT passes structural gates
and reviewed preference pairs address a measured weakness; it is not required
because an upstream recipe used it.

The only releasable terminal state is `candidate` pending independent Astra
and Sol approval of the same immutable commit and artifact manifest. Otherwise
the project records `NOT READY FOR RELEASE` with the first failed gate and a
small next experiment.
