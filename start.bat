@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Asystent dokumentow / Document assistant
echo.

set "PY=python"
where py >nul 2>nul && set "PY=py -3"
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Brak Pythona 3. Zainstaluj Python 3.10+ z https://www.python.org/downloads/
  echo Python not found. Install Python 3.10+ from https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Tworze srodowisko i instaluje zaleznosci / Creating environment (may take a while)...
  %PY% -m venv .venv
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

where ollama >nul 2>nul
if errorlevel 1 (
  echo Nie znaleziono Ollamy. Zainstaluj ja z https://ollama.com/download
  echo Ollama not found. Install it from https://ollama.com/download
  pause
  exit /b 1
)

powershell -NoProfile -Command "try { Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 3 | Out-Null } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
  echo Uruchamiam Ollame w tle / Starting Ollama in the background...
  start "" /b ollama serve
  timeout /t 6 /nobreak >nul
)

ollama list | findstr /B /C:"nomic-embed-text" >nul 2>nul
if errorlevel 1 (
  echo Pobieram model nomic-embed-text / Downloading nomic-embed-text ...
  ollama pull nomic-embed-text
)

ollama list | findstr /B /C:"llama3.1" >nul 2>nul
if errorlevel 1 (
  echo Pobieram model llama3.1 / Downloading llama3.1 ...
  ollama pull llama3.1
)

set "PORT=8501"
echo Uruchamiam aplikacje / Starting the app: http://localhost:%PORT%
start "" powershell -NoProfile -Command "Start-Sleep -Seconds 6; Start-Process 'http://localhost:%PORT%'"
set "PYTHONPATH=src"
".venv\Scripts\python.exe" -m streamlit run app\simple_app.py --server.port %PORT% --server.headless true --browser.gatherUsageStats false

pause
