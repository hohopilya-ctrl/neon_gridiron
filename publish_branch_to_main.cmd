@echo off
setlocal

REM Root-level launcher for convenience from repo root:
REM   publish_branch_to_main.cmd fix/baseline-restore

if exist scripts\publish_branch_to_main.cmd (
  call scripts\publish_branch_to_main.cmd %*
  exit /b %errorlevel%
)

echo [ERROR] scripts\publish_branch_to_main.cmd is missing in this clone.
echo [HINT] Sync first, or run manual git commands from docs/GITHUB_VISIBILITY.md
exit /b 1
