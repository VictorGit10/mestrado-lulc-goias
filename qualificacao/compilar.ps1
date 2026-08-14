# Compila o texto de qualificação (pdflatex -> bibtex -> pdflatex x2).
# Uso: .\compilar.ps1  (de qualquer diretório)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

pdflatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { throw "pdflatex falhou (1a passada) - ver main.log" }

bibtex main
# bibtex retorna 1 para warnings; só interrompe em erro fatal (sem .bbl)
if (-not (Test-Path main.bbl)) { throw "bibtex nao gerou main.bbl - ver main.blg" }

pdflatex -interaction=nonstopmode -halt-on-error main.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex falhou (2a passada) - ver main.log" }

pdflatex -interaction=nonstopmode -halt-on-error main.tex
if ($LASTEXITCODE -ne 0) { throw "pdflatex falhou (3a passada) - ver main.log" }

Write-Host "`nOK -> $PSScriptRoot\main.pdf"
