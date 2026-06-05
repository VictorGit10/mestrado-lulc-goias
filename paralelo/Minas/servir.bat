@echo off
REM servir.bat - serve o site localmente em http://127.0.0.1:8765
REM Necessario porque o site usa fetch() para carregar dados, que nao
REM funciona via file:// (CORS). Mesmo comportamento do GitHub Pages.

cd /d "%~dp0"
echo.
echo Servindo %CD%
echo URL: http://127.0.0.1:8765/
echo Ctrl+C para parar.
echo.
start "" "http://127.0.0.1:8765/"
python -m http.server 8765
