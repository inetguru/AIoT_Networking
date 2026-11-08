@echo off
rem Wrapper: runs check.ps1 regardless of the PowerShell execution policy.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check.ps1"
echo.
pause
