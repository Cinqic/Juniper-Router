# ADR-0001: host-owned trust boundary

Status: accepted.

The model emits one untrusted decision envelope. The host parses, schema-checks,
semantically validates, checks the dynamic registry and tri-state capability,
requests permission, applies budgets, and invokes an allowlisted executor. Only
host code can author a trusted result. This prevents a small model, prompt
injection, or tool text from becoming an execution authority.
