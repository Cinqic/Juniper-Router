# Phase 0 — repository and machine baseline

Status: `tested` for repository inspection and environment capture.

Canonical base commit: `4f8f7e393d38274995d61e084191e2c95c91d127`.
Candidate branch: `feat/juniper-router-v0.1-candidate`.

The current Spend machine is Windows 11 Pro build 26200, x64, Ryzen 5 3600
6C/12T, 15.93 GiB RAM, AMD Radeon RX 6600 XT, driver `32.0.21045.5002`, Git
2.53.0, Python 3.14.6 initially and Python 3.12.10 installed for this goal.
CMake and Ninja were absent at inspection; `vulkaninfo.exe` is present. Free
space was approximately 10.9 GB on `C:` and 1.0 TB on `D:`. No serial numbers,
account data, or unrelated personal files were collected.

The generated Python report is [environment-report.json](environment-report.json).
The workspace path contains literal braces, which caused setuptools editable
install to fail during bootstrap (`KeyError: 'Spend Windows PC'`). This is a
local path/tooling finding; validation was run from the venv with `PYTHONPATH`
and the canonical package remains path-relative.
