@echo off
setlocal

cd /d "%~dp0"

echo Starting backend on http://127.0.0.1:8000
start "VoiceBridge Backend" cmd /k "cd /d ""%~dp0backend"" && D:\Python2\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo Starting frontend on http://127.0.0.1:5173
start "VoiceBridge Frontend" cmd /k "cd /d ""%~dp0frontend"" && npx vite --host 127.0.0.1 --port 5173"

echo.
echo Frontend: http://127.0.0.1:5173
echo Backend Docs: http://127.0.0.1:8000/docs
echo.
echo Two terminal windows have been opened.
echo Close those windows to stop the servers.

endlocal
