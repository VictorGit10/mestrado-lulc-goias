# servir.ps1 - serve o site localmente em http://127.0.0.1:8765
# Necessario porque o site usa fetch() para carregar dados, que nao
# funciona via file:// (CORS). Mesmo comportamento do GitHub Pages.

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "Servindo $here"
Write-Host "URL: http://127.0.0.1:8765/"
Write-Host "Ctrl+C para parar."
Write-Host ""

Start-Process "http://127.0.0.1:8765/"
python -m http.server 8765 --directory $here
