@echo off
setlocal

REM Publish a feature branch into main and push to GitHub.
REM Usage:
REM   scripts\publish_branch_to_main.cmd fix/baseline-restore

set SOURCE_BRANCH=%1
if "%SOURCE_BRANCH%"=="" (
  echo [ERROR] Source branch is required.
  echo [USAGE] scripts\publish_branch_to_main.cmd ^<branch_name^>
  exit /b 1
)

echo [1/5] Fetching from origin...
git fetch origin || exit /b 1

echo [2/5] Switching to main...
git checkout main || exit /b 1

echo [3/5] Syncing main...
git pull --ff-only origin main || exit /b 1

echo [4/5] Merging %SOURCE_BRANCH% into main...
git merge --no-ff %SOURCE_BRANCH% -m "Merge %SOURCE_BRANCH% into main" || exit /b 1

echo [5/5] Pushing main...
git push origin main || exit /b 1

echo [DONE] Changes are now in main on GitHub.
endlocal
