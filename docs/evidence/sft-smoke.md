# SFT smoke evidence

Status: `tested`, `smoke-only-not-a-candidate`.

Configuration: pinned `HuggingFaceTB/SmolLM2-135M` Base, ChatML renderer
`chatml-v1`, sequence length 512, learning rate `2e-5`, batch size 1, seed 42,
two CPU updates, native Windows.

The two observed losses were 4.759650230407715 and 4.370449066162109. The
run took 61.53100000001723 seconds according to the training process. The
checkpoint sidecar matched the checkpoint SHA-256
`b5b3ad21b4db8b48344962b5458afb20d18e58142216b8abd40180818889bbcb`.
The saved model safetensors hash was
`21a3c0412cbd0d78a7f329a8c0f0599f9cb01a6b97a22c4555ef15c7c1eeb612`.

The artifact saved successfully and reloaded for evaluation, but produced
zero valid structured decisions on the 12-example frozen set. It is therefore
not a candidate checkpoint and must not be used to claim tool-use or routing
reliability.
