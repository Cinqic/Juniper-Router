# Native-Windows clean recovery

1. Install Git and CPython 3.12 x64. CMake/Ninja are needed only for a
   llama.cpp build; the Python core does not need them.
2. Clone `https://github.com/Cinqic/Juniper-Router.git` and check out the
   candidate commit being reviewed.
3. Create a venv: `py -3.12 -m venv .venv`.
4. Install `requirements-dev.lock` and the package (the `.in` file records
   reviewed dependency intent) and the
   package. On paths containing literal `{`/`}`, setuptools may fail its
   editable-install expansion; use `$env:PYTHONPATH="$PWD\src"` for validation
   and record the path finding rather than changing the code to match one host.
5. Run `$env:PYTHONPATH="$PWD\src"; py -3.12 scripts/validate_repo.py --all`.
6. Run `py -3.12 scripts/build_data.py` to reconstruct the local generated
   dataset. Do not commit model caches or generated training checkpoints.
7. For model work, install the exact optional environment from
   `requirements-model.lock`, acquire the pinned model into a project-specific
   cache outside Git, and verify its local manifest.

The normal runtime is offline after model artifacts are obtained. DirectML,
Vulkan, and llama.cpp are optional and must not replace the CPU fallback.
