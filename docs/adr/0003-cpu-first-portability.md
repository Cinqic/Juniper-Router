# ADR-0003: CPU-first portability

Status: accepted.

Native Windows CPU is the normative path. DirectML, ROCm, Vulkan, CUDA, and
llama.cpp are optional measured lanes. Unsupported acceleration must fail
clearly back to CPU and cannot be used to justify a platform claim.
