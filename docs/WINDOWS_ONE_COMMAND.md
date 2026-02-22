# Windows: one command to apply + validate + push

If you get:
`"scripts\windows_apply_and_push.cmd" is not recognized...`
it means this file is not yet present in your local clone. First sync repo, then run helper.

## 0) Sync repository

```bat
git fetch origin
git checkout main
git pull origin main
dir scripts
```

You should see both files in `scripts\`:
- `local_apply_baseline.py`
- `windows_apply_and_push.cmd`

## 1) Run one command from repo root

```bat
apply_and_push.cmd
```

Alternative (direct path):

```bat
scripts\windows_apply_and_push.cmd
```

Optional custom branch name:

```bat
apply_and_push.cmd fix/baseline-restore
```

What it does:
1. Runs `scripts\local_apply_baseline.py`.
2. Runs `ruff` and `pytest`.
3. Creates/resets the branch.
4. Commits only if there are actual file changes.
5. Pushes branch to GitHub.

PR link format:
`https://github.com/hohopilya-ctrl/neon_gridiron/compare/main...<branch_name>`
