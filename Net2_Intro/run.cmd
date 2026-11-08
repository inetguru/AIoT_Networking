@echo off
rem Usage: run.cmd 01_load_client.py   or   run.cmd capture.py mqtt
rem Runs a Python file in the lab container (servers start automatically).
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: run.cmd 01_load_client.py
  echo        run.cmd capture.py mqtt
  exit /b 1
)
docker compose run --rm py %*
