<#
    setup_comfyui_flux.ps1 - Install ComfyUI + a quantized Flux checkpoint (Windows).

    Windows alternative to scripts/setup_comfyui_flux.sh.

    ComfyUI is an R&D-only generation backend in this studio (D-08); it is
    never used in the production pipeline.  This script installs it and makes
    the local backend (`--backend comfyui`) usable on Windows.

    Environment notes
      * No GPU here -> the server runs with --cpu.  Flux on CPU is *slow*
        (minutes per image); treat it as an offline fallback and prefer the
        cloud backends (`FAL_API_KEY` / `REPLICATE_API_KEY` / `BFL_API_KEY`)
        when keys are available.
      * 15GiB RAM -> a quantized Flux checkpoint (Q4 GGUF ~ 9GB) fits.

    Usage (PowerShell):
      .\scripts\setup_comfyui_flux.ps1                 # install + download
      .\scripts\setup_comfyui_flux.ps1 -Serve          # just start the server
      .\scripts\setup_comfyui_flux.ps1 -SkipDownload   # skip the model download

    Env vars:  $env:COMFYUI_DIR   (install dir, default: tools\comfyui)
               $env:COMFYUI_PORT  (server port, default: 8188)

    Requires:  git, python (3.10+) on PATH.  Run in PowerShell; if the
    execution policy blocks scripts, run:
      Set-ExecutionPolicy -Scope Process Bypass
#>

[CmdletBinding()]
param(
    [switch]$Serve,
    [switch]$SkipDownload
)

$ErrorActionPreference = "Stop"

$ScriptDir     = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot   = Split-Path -Parent $ScriptDir
$ComfyDir      = if ($env:COMFYUI_DIR) { $env:COMFYUI_DIR } else { Join-Path $ProjectRoot "tools\comfyui" }
$Port          = if ($env:COMFYUI_PORT) { $env:COMFYUI_PORT } else { 8188 }

# Checkpoint filename the workflow templates reference
# (src\generation_engine\workflows\*.json -> "flux1-dev.safetensors").
$CkptName = "flux1-dev.safetensors"

# Quantized Flux (dev) GGUF - Q4_K_S ~ 9GB.
$GgufUrl  = "https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q4_K_S.gguf"
$GgufSave = Join-Path $ComfyDir "models\checkpoints\$CkptName.gguf"
$CkptDest = Join-Path $ComfyDir "models\checkpoints\$CkptName"

function Log($msg)  { Write-Host "`n[setup] $msg" -ForegroundColor Cyan }
function Die($msg)  { Write-Host "[setup] ERROR: $msg" -ForegroundColor Red; exit 1 }

# Pick a Python launcher (python3 on *nix shells, python on Windows cmd/PowerShell).
$Python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Python) { Die "python / python3 not found on PATH." }
$Py = $Python.Source
Log "Using Python: $Py"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Die "git is not on PATH." }

# --------------------------------------------------------------------------- #
# 1. Clone + install ComfyUI
# --------------------------------------------------------------------------- #
if (-not (Test-Path (Join-Path $ComfyDir ".git"))) {
    Log "Cloning ComfyUI into $ComfyDir ..."
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $ComfyDir) | Out-Null
    git clone https://github.com/comfyanonymous/ComfyUI.git $ComfyDir
    if (-not $?) { Die "git clone of ComfyUI failed." }
} else {
    Log "ComfyUI already present ($ComfyDir)."
}

# ComfyUI-GGUF custom node - required to load .gguf Flux weights.
$GgufNode = Join-Path $ComfyDir "custom_nodes\ComfyUI-GGUF"
if (-not (Test-Path (Join-Path $GgufNode ".git"))) {
    Log "Installing ComfyUI-GGUF custom node ..."
    git clone https://github.com/city96/ComfyUI-GGUF.git $GgufNode
    if (-not $?) { Die "git clone of ComfyUI-GGUF failed." }
} else {
    Log "ComfyUI-GGUF already present."
}

Log "Installing Python requirements (ComfyUI + GGUF) ..."
& $Py -m pip install -r (Join-Path $ComfyDir "requirements.txt")
if (-not $?) { Die "ComfyUI requirements install failed." }
& $Py -m pip install -r (Join-Path $GgufNode "requirements.txt")
if (-not $?) { Die "ComfyUI-GGUF requirements install failed." }

# --------------------------------------------------------------------------- #
# 2. Download the quantized Flux checkpoint
# --------------------------------------------------------------------------- #
if ($SkipDownload) {
    Log "Skipping model download (-SkipDownload)."
} elseif (Test-Path $CkptDest) {
    Log "Checkpoint already present: $CkptDest"
} elseif (Test-Path $GgufSave) {
    Log "GGUF already downloaded: $GgufSave"
    Copy-Item $GgufSave $CkptDest -Force
} else {
    Log "Downloading quantized Flux (Q4 GGUF ~ 9GB) - this may take a while ..."
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $GgufSave) | Out-Null
    # Use .NET WebClient for a progress bar (Invoke-WebRequest is slow on PS5).
    $wc = New-Object System.Net.WebClient
    try {
        $wc.DownloadFile($GgufUrl, $GgufSave)
    } finally {
        $wc.Dispose()
    }
    if (-not (Test-Path $GgufSave)) { Die "Model download failed." }
    Copy-Item $GgufSave $CkptDest -Force
}

if (-not (Test-Path $CkptDest)) { Die "checkpoint not found at $CkptDest" }

# --------------------------------------------------------------------------- #
# 3. Start the server (CPU mode)
# --------------------------------------------------------------------------- #
if ($Serve) {
    Log "Starting ComfyUI on :$Port (--cpu) ..."
    Push-Location $ComfyDir
    & $Py .\main.py --cpu --port $Port --listen 127.0.0.1
    Pop-Location
    exit 0
}

Log "Done. Start it with:"
Log "  .\scripts\setup_comfyui_flux.ps1 -Serve"
Log "Then generate with:"
Log "  python scripts\generate_phase1_library.py --backend comfyui --comfyui-url http://localhost:$Port"
