# Third-party notices

This repository contains no downloaded model weights or generated corpus.
Third-party inputs used by an artifact must be listed in a machine-readable
manifest before distribution.

| Component | Use | License/status |
| --- | --- | --- |
| HuggingFaceTB/SmolLM2-135M Base | optional model lineage | upstream Apache-2.0 tag; exact revision and hashes required |
| PyTorch, Transformers, Hugging Face Hub, Safetensors, PEFT, Accelerate | optional model path | exact versions recorded in `requirements-model.lock`; upstream licenses apply |
| llama.cpp | optional GGUF runtime/converter | upstream MIT; exact source revision required |

No dependency or dataset is considered distributable merely because it parses.
