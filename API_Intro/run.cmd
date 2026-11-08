@echo off
rem Usage: run.cmd 01_echo_get.py   (runs the Python script inside the lab container)
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: run.cmd 01_echo_get.py
  exit /b 1
)
docker compose run --rm py %*
