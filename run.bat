@echo off
setlocal

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

if not defined API_HOST set "API_HOST=127.0.0.1"
if not defined API_PORT set "API_PORT=8000"
if not defined FRONTEND_PORT set "FRONTEND_PORT=8080"

set "BACKEND_PY=%ROOT_DIR%\backend\venv\Scripts\python.exe"

cd /d "%ROOT_DIR%\backend"
start "backend" /b "%BACKEND_PY%" -m uvicorn main:app --host %API_HOST% --port %API_PORT%

cd /d "%ROOT_DIR%"
echo API: http://%API_HOST%:%API_PORT%
echo Frontend: http://127.0.0.1:%FRONTEND_PORT%/index.html

py -3 -m http.server %FRONTEND_PORT% --directory frontend