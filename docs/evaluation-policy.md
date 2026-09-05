# Evaluation and release policy v1

The frozen manifest is `evals/manifests/frozen-v1.json`. It is created before
serious training and contains deterministic reviewed cases split by scenario
lineage. Primary measures are decision accuracy, macro-F1, target accuracy,
raw syntactic validity, and semantic host-validator pass rate.

Hard gates are 100% schema validity in the constrained lane, 100% host
fail-closed behavior for malformed/unknown/unauthorized/incompatible,
over-budget, untrusted-result, and unsupported-version cases, zero permission
bypasses, zero fabricated completion claims accepted by the host, complete
provenance, deterministic manifests, native-Windows CPU inference, and no
unresolved severity-1 or severity-2 defect.

Raw unconstrained validity and constrained validity must both be reported.
Quantized artifacts are separate lineage records and must be evaluated against
the same frozen suite. DPO is permitted only after SFT passes structural gates
and reviewed preference pairs address a measured weakness; it is not required
because an upstream recipe used it.

The only releasable terminal state is `candidate` pending independent Astra
and Sol approval of the same immutable commit and artifact manifest. Otherwise
the project records `NOT READY FOR RELEASE` with the first failed gate and a
small next experiment.
