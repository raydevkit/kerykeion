@echo off
REM Development Server Launcher for Windows
REM Usage: dev.bat

echo Starting Kerykeion-Kabalah Development Server...
py -m poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
