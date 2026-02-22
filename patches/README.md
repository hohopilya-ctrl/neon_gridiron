# Patch bundle for local apply (Variant A)

This folder contains a ready-to-apply patch with the full fix set from commit `e753ff6`.

## Files
- `e753ff6_restore_baseline.patch` — mailbox patch generated via `git format-patch -1 e753ff6 --stdout`.

## Apply on your local clone

From repository root:

```bash
git checkout main
git pull
git am patches/e753ff6_restore_baseline.patch
```

If your local branch diverged and `git am` fails, use a 3-way fallback:

```bash
git am --abort
git apply --3way patches/e753ff6_restore_baseline.patch
git add -A
git commit -m "Apply baseline restore patch (e753ff6)"
```
