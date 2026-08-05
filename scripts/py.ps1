<#
    py.ps1 - generic Windows wrapper for scripts\*.py entry points.

    Usage:
      .\scripts\py.ps1 <script-name> [args...]
      .\scripts\py.ps1 seed_universe -db catalog.db
      .\scripts\py.ps1 generate_phase1_library -backend comfyui -jobs 12

    Python resolution order: $env:PYTHON -> the Python 3.14 install in the
    user AppData layout (python3.exe, then python.exe) -> python on PATH.
    Set $env:PYTHON explicitly to override.
#>

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($args.Count -lt 1) {
    Write-Host "usage: py.ps1 <script-name> [args...]" -ForegroundColor Yellow
    exit 1
}
$ScriptName = $args[0]
$Forwarded  = @($args[1..($args.Count - 1)])

# Resolve Python.
$Py = $null
if ($env:PYTHON -and (Test-Path $env:PYTHON)) {
    $Py = $env:PYTHON
} else {
    $Py314Dir = Join-Path $env:LOCALAPPDATA "Programs\Python\Python314"
    foreach ($candidate in @("python3.exe", "python.exe")) {
        $candidatePath = Join-Path $Py314Dir $candidate
        if (Test-Path $candidatePath) { $Py = $candidatePath; break }
    }
    if (-not $Py) {
        $cmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $cmd) { $cmd = Get-Command python3 -ErrorAction SilentlyContinue }
        if (-not $cmd) {
            Write-Host "No Python found. Set `$env:PYTHON or add python to PATH." -ForegroundColor Red
            exit 1
        }
        $Py = $cmd.Source
    }
}

$ProjectRoot = Split-Path -Parent $ScriptDir
Push-Location $ProjectRoot
try {
    & $Py ("scripts\{0}.py" -f $ScriptName) @Forwarded
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
