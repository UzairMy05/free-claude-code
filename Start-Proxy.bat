@echo off
title Claude Proxy Server
cd C:\Users\User\.gemini\antigravity\scratch\free-claude-code

echo Checking for existing process on port 8082...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8082 ^| findstr LISTENING') do (
    echo Killing existing process with PID %%a...
    taskkill /PID %%a /F >nul 2>&1
)

echo Starting the proxy server... Please leave this window open!
C:\Users\User\.local\bin\uv.exe run uvicorn server:app --host 0.0.0.0 --port 8082
pause
