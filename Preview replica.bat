@echo off
rem Serves the PHT replica at http://localhost:8765 so it behaves like the live site.
rem YouTube players need a real web address; opening the .html files directly will not play them.
cd /d "%~dp0"
start "" /b python -m http.server 8765 --bind 127.0.0.1
timeout /t 1 >nul
start "" "http://localhost:8765/index.html"
echo.
echo  PHT replica preview is running at http://localhost:8765
echo  Close this window to stop it.
pause >nul
