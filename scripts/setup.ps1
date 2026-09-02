$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Invoke-Checked {
    param([string]$Name, [scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot ".venv"))) {
    python -m venv (Join-Path $ProjectRoot ".venv")
}

Invoke-Checked "Python dependency installation" {
    & (Join-Path $ProjectRoot ".venv\Scripts\python.exe") -m pip install -e "$ProjectRoot[dev]"
}
Invoke-Checked "Frontend dependency installation" {
    pnpm --dir (Join-Path $ProjectRoot "frontend") install
}

Write-Host "Setup complete. Start the API and UI using the commands in README.md."
