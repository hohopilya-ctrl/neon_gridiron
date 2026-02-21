@echo off
set NEON_PATCH=season_03
echo --- LAUNCHING NEON GRIDIRON PRO LEAGUE ---

start "PBT_LEAGUE" cmd /k ".\venv\Scripts\python.exe pbt_league.py"
timeout /t 2
start "TELEMETRY_STREAM" cmd /k ".\venv\Scripts\python.exe test_env.py"

echo.
echo Check the new windows for logs. 
echo If they close immediately, read the error message in the window.
pause
