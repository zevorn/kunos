# Contributing

Contributions should keep the layer small, machine-scoped, and reproducible.

## Patch Requirements

* Base changes on the `main` branch.
* Keep K230-specific changes behind `COMPATIBLE_MACHINE` or machine overrides.
* Do not add binary firmware or generated build artifacts to this repository.
* Include `Upstream-Status` in patches that are carried against upstream
  projects.
* Run `scripts/check-layer.sh` before sending changes.

## Commit Sign-off

Commits must include:

```
Signed-off-by: Chao Liu chao.liu.zevorn@gmail.com
```

Do not add AI-generated signature trailers.
