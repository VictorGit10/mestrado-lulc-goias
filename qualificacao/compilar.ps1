# Compila o texto de qualificação (pdflatex -> bibtex -> pdflatex x2).
# Uso: .\compilar.ps1  (de qualquer diretório)
#
# -synctex=1 grava main.synctex.gz, o mapa linha-do-.tex <-> ponto-na-pagina
# que o editor usa para o ctrl+click entre texto e PDF. Nao muda o PDF.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

pdflatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { throw "pdflatex falhou (1a passada) - ver main.log" }

bibtex main
# bibtex retorna 1 para warnings; só interrompe em erro fatal (sem .bbl)
if (-not (Test-Path main.bbl)) { throw "bibtex nao gerou main.bbl - ver main.blg" }

pdflatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex falhou (2a passada) - ver main.log" }

pdflatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { throw "pdflatex falhou (3a passada) - ver main.log" }

# Trava de convergencia. As tres passadas bastaram em todo caso testado em
# 21/ago/2026, inclusive partindo de um .aux truncado de proposito por uma
# sessao com \includeonly (45 paginas -> 106, mesmo tamanho de arquivo). Ela
# nao esta aqui porque a falha foi observada, e sim porque o modo de falha e
# silencioso: o PDF sairia completo, com um numero de pagina ou de figura
# desatualizado em alguma referencia cruzada, e nada no console diria. O
# proprio LaTeX avisa no .log; o que faltava era interromper.
$log = Get-Content main.log -Raw
if ($log -match 'Rerun to get|Label\(s\) may have changed') {
    pdflatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "pdflatex falhou (4a passada) - ver main.log" }
    $log = Get-Content main.log -Raw
    if ($log -match 'Rerun to get|Label\(s\) may have changed') {
        throw "referencias cruzadas nao convergiram em 4 passadas - ver main.log"
    }
    Write-Host "  (4a passada foi necessaria: o .aux vinha desatualizado)"
}

Write-Host "`nOK -> $PSScriptRoot\main.pdf"
