@echo off
setlocal

REM Root-level launcher so users can run from repo root:
REM   apply_and_push.cmd

if exist scripts\windows_apply_and_push.cmd (
  call scripts\windows_apply_and_push.cmd %*
  exit /b %errorlevel%
)

echo [ERROR] scripts\windows_apply_and_push.cmd is missing in this clone.
echo [HINT] Run:
echo        git fetch origin
echo        git pull origin main
echo        dir scripts
exit /b 1
