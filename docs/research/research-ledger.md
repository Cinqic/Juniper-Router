# Research ledger

Access date for the public sources below: 2026-09-05 UTC. Claims are limited
to the cited source and are not a substitute for local measurements.

| Source | Relevant claim used here | Applicability / limitation |
| --- | --- | --- |
| [SmolLM2-135M model card](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) | Base model is Apache-2.0 tagged; the 135M model was trained on roughly 2T tokens; Transformers loading is supported. | Does not establish Juniper routing or tool-use capability. |
| [SmolLM2 config](https://huggingface.co/HuggingFaceTB/SmolLM2-135M/blob/main/config.json) | Llama architecture, 576 hidden, 1536 intermediate, 30 layers, 9 heads, 3 KV heads, 49,152 vocab, tied embeddings, 8,192 positions. | Pinned locally to revision `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`; head dimension is implied as 64. |
| [SmolLM2 tokenizer config](https://huggingface.co/HuggingFaceTB/SmolLM2-135M/blob/main/tokenizer_config.json) | Upstream tokenizer/special-token configuration is the compatibility surface. | The pinned file currently has no `chat_template` field; the renderer preserves ChatML delimiters explicitly. |
| [SmolLM2 paper](https://arxiv.org/abs/2502.02737) | Data-centric small-model training and model-family context. | Research context, not a Juniper result. |
| [SmolLM2 SFT recipe](https://github.com/huggingface/alignment-handbook/blob/main/recipes/smollm2/sft/config_smol.yaml) | Upstream SFT recipe is a reference for adaptation. | Hardware, precision, sequence, and batch assumptions are not copied blindly. |
| [SmolLM2 DPO recipe](https://github.com/huggingface/alignment-handbook/blob/main/recipes/smollm2/dpo/config_smol.yaml) | Upstream DPO recipe exists. | DPO is optional and evidence-gated here. |
| [SmolTalk dataset card](https://huggingface.co/datasets/HuggingFaceTB/smoltalk) | External data needs dataset-level provenance and terms review. | No external corpus is required for the checked-in seed set. |
| [Transformers chat templating](https://huggingface.co/docs/transformers/chat_templating) | Templates are part of tokenization and should be kept consistent. | Juniper uses a versioned deterministic renderer to preserve the pinned delimiters. |
| [PEFT LoRA reference](https://huggingface.co/docs/peft/package_reference/lora) | LoRA is a viable adaptation option with explicit target modules/rank. | Must be compared to bounded full tuning on this small model. |
| [TRL DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer) | DPO implementation reference. | Not installed or enabled unless its preconditions are met. |
| [PyTorch Windows guidance](https://pytorch.org/get-started/locally/) | Stable CPU installation is a supported Windows route; Python 3.10+ is required by the current page. | Canonical project target remains Python 3.12 for reproducibility. |
| [Microsoft DirectML guidance](https://learn.microsoft.com/en-us/windows/ai/directml/pytorch-windows) | DirectML has its own compatibility path. | Isolated optional experiment only. |
| [AMD HIP SDK Windows requirements](https://rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html) | Windows AMD acceleration has a specific support matrix. | RX 6600 XT is not used as a claimed ROCm training target. |
| [llama.cpp build guide](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) | CPU/Vulkan builds are plausible deployment lanes. | A build and inference result are required before claiming either. |
| [llama.cpp grammars](https://github.com/ggml-org/llama.cpp/tree/master/grammars) | Grammar-constrained generation can help formatting. | Grammar is not a security boundary; host validation remains mandatory. |
| [RouteLLM](https://arxiv.org/abs/2406.18665) | Routing can be evaluated as a decision problem. | Juniper's dynamic registry and host gates are specialized to this project. |
| [BFCL](https://proceedings.mlr.press/v267/patil25a.html) | Function-call evaluation should measure structured correctness. | Juniper uses adapted exact/semantic checks, not a claimed BFCL score. |
| [tau-bench](https://arxiv.org/abs/2406.12045) | Multi-turn tool-agent-user state matters. | Juniper uses bounded deterministic mock orchestration. |
| [ToolACE](https://arxiv.org/abs/2409.00920) | Tool-call data needs breadth and quality controls. | Generated examples remain provenance-labelled and held-out cases are frozen. |
| [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) | License obligations and notices govern redistribution. | Third-party artifact terms remain separate from repository source. |
| [Hugging Face model cards](https://huggingface.co/docs/hub/model-cards) | Model cards should state lineage, use, data, limits, and evaluation. | Candidate model cards must use measured evidence only. |
| [Model release checklist](https://huggingface.co/docs/hub/model-release-checklist) | Release artifacts need metadata, files, license, and validation checks. | No release is authorized by this implementation session. |

## Refreshed Cinqic repository commits

| Repository | Exact `main` commit reviewed | Reused lesson |
| --- | --- | --- |
| Juniper Router | `4f8f7e393d38274995d61e084191e2c95c91d127` | Initial README and Apache-2.0 source baseline. |
| Juniper-Auto | `2c0bb824b62f07dc4951ab4e835ce97a350c5233` | Retain negative results, phase reports, manifests, recovery, and time separation. |
| cinqic.com | `de644adf25e97f77e263dfd0792f2bdf8d9fa597` | GitHub-canonical facts and no unverified product claims. |
| juniper-math-1 | `15f499f409bd4a1fc6239c7df8c6fa20db92da18` | Frozen evaluations, deterministic data, checkpoint trust model, failed-run retention. |
| Juniper-App | `2f00abba01e0ef956f86859fdef914a9fe8508f5` | Host-authored results, tri-state capabilities, permission scopes, bounded loops. |
| Cinqic-Notes | `176ead59a83cdef395f2b34fc8568a9bf9cf572c` | Local-first source of truth and native safety boundary. |
| Cinqic-Calculator | `8024cf107d6240386fa42b6c5193dd8b34848032` | Minimal dependencies and behavior-focused tests. |
