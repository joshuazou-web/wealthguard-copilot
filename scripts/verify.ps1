$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

function Invoke-Checked {
    param([string]$Name, [scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Invoke-Checked "Ruff format check" {
    & $Python -m ruff format --check (Join-Path $ProjectRoot "backend") (Join-Path $ProjectRoot "tests") (Join-Path $ProjectRoot "scripts")
}
Invoke-Checked "Ruff lint" {
    & $Python -m ruff check (Join-Path $ProjectRoot "backend") (Join-Path $ProjectRoot "tests") (Join-Path $ProjectRoot "scripts")
}
Invoke-Checked "Python tests" {
    & $Python -m pytest $ProjectRoot
}
Invoke-Checked "Deterministic evaluation" {
    & $Python -m wealthguard.evaluation.runner
}
Invoke-Checked "Official citation evaluation" {
    & $Python (Join-Path $ProjectRoot "scripts\run_citation_evaluation.py")
}
Invoke-Checked "Frontend typecheck" {
    pnpm --dir (Join-Path $ProjectRoot "frontend") typecheck
}
Invoke-Checked "Frontend build" {
    pnpm --dir (Join-Path $ProjectRoot "frontend") build
}

Write-Host "All verification stages completed."
