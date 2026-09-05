# Contributing

Use Python 3.12 and keep GitHub `main` canonical. Work on a focused branch,
preserve failed experiments, and do not commit model weights, caches, secrets,
private datasets, or machine-specific absolute paths.

Run the canonical check before handoff:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -3.12 scripts/validate_repo.py --all
```

Changes to schemas, renderers, data generators, evaluation manifests, or
policies require a versioned ADR or manifest update and regression tests.
Do not describe a tested, candidate, approved, or released state without the
corresponding evidence.
