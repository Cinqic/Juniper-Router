# Independent review and release protocol

This candidate is not approved by the implementation session. Astra and Sol
must independently inspect the full immutable candidate commit and artifact
manifest from clean FLOWBOX checkouts. They must not treat this packet or the
other reviewer as proof.

Each reviewer must verify the commit/tree/hashes, recreate the Python
environment, run the canonical validator on Linux CPU, run the frozen
evaluation independently, inspect all critical failures and a stratified data
sample, challenge host validation/permissions/spoofing/budgets/cancellation/
loops, audit licenses and README claims, and record their own time. CUDA on the
RTX 2060 is optional; it is not a user requirement. At least one distributed
artifact must be rebuilt from documented source/checkpoint when such an
artifact exists.

Each reviewer issues an explicit verdict for the exact commit:
`APPROVE`, `REQUEST_CHANGES`, or `REJECT`. Any code, data, model, or artifact
change invalidates prior approvals. Release requires both approvals for the
same commit and manifest, green CI, no severity-1/2 findings, and a mechanical
release by an authorized operator. The implementation engineer must not merge,
tag, publish, or call the candidate released.
