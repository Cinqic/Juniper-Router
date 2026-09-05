# Security

## Boundary

Juniper model output is untrusted data. The host performs strict JSON parsing,
closed-vocabulary checks, schema and semantic validation, registry lookup,
capability checks, permission confirmation, privacy checks, and step/retry/
payload budgets before execution. Only host code can create a trusted result.

Unknown capability is fail-closed. User content, model text, tool text, and
model metadata cannot change policy or forge completion. The default fixtures
are harmless and no arbitrary shell tool exists.

## Threat controls

Prompt injection, duplicate JSON keys, non-finite JSON values, unknown target
IDs, extra arguments, unsupported schema versions, permission bypass, forged
trusted results, oversized payloads, retry exhaustion, and loop exhaustion are
covered by contract and adversarial tests. Audit logging is opt-in, bounded,
and redacts common secret-shaped fields.

## Reporting

Please report suspected vulnerabilities privately to the Cinqic maintainers
with the affected commit, platform, reproduction, and impact. Do not include
private prompts, model caches, credentials, or unrelated personal files.
