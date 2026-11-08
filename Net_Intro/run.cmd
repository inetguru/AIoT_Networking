@echo off
rem Usage: run.cmd 01_network_tour.py   or   run.cmd capture.py http
rem Runs a Python file in the lab container (servers start automatically).
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: run.cmd 01_network_tour.py
  echo        run.cmd capture.py http
  exit /b 1
)
docker compose run --rm py %*
