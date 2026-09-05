# ADR-0005: separate raw validity from constrained production validity

Status: accepted for formal evaluation.

Policy v1 used `raw_syntactic_validity: 1.0` as a hard gate while the design
described 100% validity as a requirement of the constrained production lane
and separately required raw unconstrained validity to be reported. Those are
different measurements: unconstrained generation tests learned formatting,
while constrained generation tests the host-facing production contract.

Policy v2 preserves both measurements. Constrained syntax, semantic host
validation, and host fail-closed behavior remain hard gates. Raw validity is a
reported threshold chosen before the formal candidate evaluation, not a reason
to hide or reinterpret unconstrained failures. The v1 policy and its evidence
remain immutable historical context.
