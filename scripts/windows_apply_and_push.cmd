@echo off
setlocal

REM One-shot helper for Windows CMD users.
REM Usage:
REM   scripts\windows_apply_and_push.cmd [branch_name]

set BRANCH_NAME=%1
if "%BRANCH_NAME%"=="" set BRANCH_NAME=fix/baseline-restore

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python is not available in PATH.
  exit /b 1
)

if not exist scripts\local_apply_baseline.py (
  echo [ERROR] scripts\local_apply_baseline.py is missing.
  echo [HINT] Ensure you pulled the branch that contains this file.
  exit /b 1
)

echo [1/6] Applying local baseline fixes...
python scripts\local_apply_baseline.py || exit /b 1

echo [2/6] Running ruff...
python -m ruff check . || exit /b 1

echo [3/6] Running tests...
python -m pytest -q || exit /b 1

echo [4/6] Preparing branch %BRANCH_NAME%...
git checkout -B %BRANCH_NAME% || exit /b 1

echo [5/6] Committing changes if any...
git add -A
for /f %%i in ('git status --porcelain ^| find /c /v ""') do set CHANGED=%%i
if "%CHANGED%"=="0" (
  echo [INFO] No file changes to commit. Skipping commit.
) else (
  git commit -m "Restore baseline fixes via local apply script" || exit /b 1
)

echo [6/6] Pushing branch...
git push -u origin %BRANCH_NAME% || exit /b 1

echo [DONE] Open PR:
echo https://github.com/hohopilya-ctrl/neon_gridiron/compare/main...%BRANCH_NAME%

endlocal
