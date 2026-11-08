@echo off
rem Runs the Gemini access check inside the lab container.
cd /d "%~dp0"
docker compose run --rm py check_gemini.py
