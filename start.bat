@echo off
REM Production Server Launcher for Windows
REM Usage: start.bat

echo Starting Kerykeion-Kabalah Production Server...
py -m poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
