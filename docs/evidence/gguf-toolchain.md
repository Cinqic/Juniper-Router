# GGUF toolchain evidence

## Result

The optional export lane is `tested` for the pinned base model only. It is not
an approval of the router adapter and it does not establish Vulkan, GPU, or
throughput performance.

## Reproduction

- llama.cpp revision: `6a1a922d269908a29cbd4b49c27e6a8e7fd10fae`
- host: native Windows AMD64
- compiler: Clang 21.1.0 supplied by Zig 0.16.0
- CMake: 4.1.2; Ninja: 1.13.0
- build flags: `GGML_NATIVE=OFF`, tests off, examples on, server off
- export: pinned `SmolLM2-135M` SafeTensors to F16 GGUF, then `Q4_K_M`
- converter dependency: local `gguf` 0.19.0 and `sentencepiece` 0.2.1
- output: `smollm2-135m-q4_k_m.gguf`, 105,453,568 bytes
- SHA-256: `c7ace3f87bf36de0397c605cedefba5ebe4cd35a691f1ecd0ba7166a77cad599`

llama.cpp completed conversion and quantization. It reported fallback
quantization for 180 of 272 tensors because of the model's tensor shapes; the
artifact is retained with that warning. No router formal evaluation was run on
this base-only artifact.
