@echo off
rem Usage: run.cmd 01_hello_llm.py
rem Runs a Python file in the lab container (servers start automatically).
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: run.cmd 01_hello_llm.py
  exit /b 1
)
docker compose run --rm py %*
