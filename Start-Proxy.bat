@echo off
title Claude Proxy Server
cd C:\Users\User\.gemini\antigravity\scratch\free-claude-code
echo Starting the proxy server... Please leave this window open!
C:\Users\User\.local\bin\uv.exe run uvicorn server:app --host 0.0.0.0 --port 8082
pause
