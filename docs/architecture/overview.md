# Architecture overview

```text
user request + minimal trusted host context
              ↓
        ChatML renderer
              ↓
      Juniper proposes one envelope
              ↓
 parse → schema → semantics → registry → permission → budget
              ↓                         ↘ reject/clarify/escalate
       allowlisted host executor
              ↓
       host-authored trusted result
              ↺ bounded orchestration
```

The model is a proposal generator. `HostValidator` owns the trust boundary;
`HostOrchestrator` owns at most four rounds and eight steps by default. The
registry supplies exact target IDs and tri-state capability (`supported`,
`unsupported`, `unknown`). Unknown is never treated as supported.

The reference implementation is intentionally smaller than Juniper App. It
uses the `juniper-tool-protocol-v1` shape as an adapter boundary and does not
modify Juniper App or expose an unrestricted process runner.
