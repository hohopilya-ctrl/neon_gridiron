# One-shot apply on Windows (no missing patch file errors)

If `patches/e753ff6_restore_baseline.patch` is missing on your local machine, use this script-driven path instead.

## 1) Run fixer

In `cmd.exe` from repo root:

```bat
cd /d C:\Users\ilya\Desktop\ant\neon_gridiron
python scripts\local_apply_baseline.py
```

## 2) Validate

```bat
python -m ruff check .
python -m pytest -q
```

## 3) Commit + push

```bat
git checkout -b fix/baseline-restore
git add -A
git commit -m "Restore missing env/ui modules and training fixes"
git push -u origin fix/baseline-restore
```

## 4) Open PR

```text
https://github.com/hohopilya-ctrl/neon_gridiron/compare/main...fix/baseline-restore
```
