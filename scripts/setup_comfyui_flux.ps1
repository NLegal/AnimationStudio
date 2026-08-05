<#
    setup_comfyui_flux.ps1 - Install ComfyUI + the fp8 Flux checkpoint (Windows).

    Windows alternative to scripts/setup_comfyui_flux.sh.

    ComfyUI is an R&D-only generation backend in this studio (D-08); it is
    never used in the production pipeline.  This script installs it and makes
    the local backend (`--backend comfyui`) usable on Windows.

    Environment notes
      * This box has a GPU, so the server starts with CUDA by default
        (add -Cpu only for CPU-only machines).  Flux on GPU is fast
        (seconds per image); cloud backends (`FAL_API_KEY` /
        `REPLICATE_API_KEY` / `BFL_API_KEY`) remain an alternative when
        keys are available.
      * We download the fp8 Flux (dev) safetensors (~ 12GB) because the
        workflow templates reference it via CheckpointLoaderSimple.  Needs
        roughly 12-16GB RAM/VRAM.

    Usage (PowerShell):
      .\scripts\setup_comfyui_flux.ps1                 # install + download
      .\scripts\setup_comfyui_flux.ps1 -Serve          # just start the server (GPU)
      .\scripts\setup_comfyui_flux.ps1 -Serve -Cpu     # start the server on CPU
      .\scripts\setup_comfyui_flux.ps1 -SkipDownload   # skip the model download

    Env vars:  $env:PYTHON       (python executable override)
               $env:COMFYUI_DIR  (install dir, default: tools\comfyui)
               $env:COMFYUI_PORT (server port, default: 8188)

    Python resolution order: $env:PYTHON -> the Python 3.14 install found in
    the user AppData layout (python3.exe, then python.exe) -> python/python3
    on PATH.  Requires: git.  Run in PowerShell; if the execution policy
    blocks scripts, run:
      Set-ExecutionPolicy -Scope Process Bypass
#>

[CmdletBinding()]
param(
    [switch]$Serve,
    [switch]$SkipDownload,
    [switch]$Cpu
)

$ErrorActionPreference = "Stop"

$ScriptDir     = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot   = Split-Path -Parent $ScriptDir
$ComfyDir      = if ($env:COMFYUI_DIR) { $env:COMFYUI_DIR } else { Join-Path $ProjectRoot "tools\comfyui" }
$Port          = if ($env:COMFYUI_PORT) { $env:COMFYUI_PORT } else { 8188 }

# Checkpoint filename the workflow templates reference
# (src\generation_engine\workflows\*.json -> "flux1-dev.safetensors").
$CkptName = "flux1-dev.safetensors"

# fp8 Flux (dev) safetensors - loads via CheckpointLoaderSimple, ~ 12GB.
$CkptUrl  = "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors"
$CkptDest = Join-Path $ComfyDir "models\checkpoints\$CkptName"

function Log($msg)  { Write-Host "`n[setup] $msg" -ForegroundColor Cyan }
function Die($msg)  { Write-Host "[setup] ERROR: $msg" -ForegroundColor Red; exit 1 }

function Download-Checkpoint {
    param([string]$Url, [string]$Dest)

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Dest) | Out-Null

    # 1) curl.exe - ships with Windows 10 1803+. Follows HuggingFace's 302 ->
    #    CDN redirect, retries on transient errors, resumes partial files.
    #    (.NET WebClient fails on those redirects -> "exception during a
    #    WebClient request".)
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($curl) {
        Log "Downloading with curl.exe (follows redirects, resumable) ..."
        & $curl.Source -L --fail --retry 3 --retry-delay 2 -C - --progress-bar -o $Dest $Url
        if ($LASTEXITCODE -eq 0 -and (Test-Path $Dest) -and (Get-Item $Dest).Length -gt 0) {
            return $true
        }
        Log "curl download failed (exit $LASTEXITCODE). Falling back to BITS ..."
        if (Test-Path $Dest) { Remove-Item $Dest -Force }
    }

    # 2) BITS - native Windows transfer service, follows redirects, resumable.
    try {
        Import-Module BitsTransfer -ErrorAction Stop
        Log "Downloading with Start-BitsTransfer ..."
        Start-BitsTransfer -Source $Url -Destination $Dest -DisplayName "Flux fp8 checkpoint"
        if ((Test-Path $Dest) -and (Get-Item $Dest).Length -gt 0) {
            return $true
        }
    } catch {
        Log "BITS transfer failed: $($_.Exception.Message)"
    }

    # 3) Last resort - Invoke-WebRequest (slow on 12GB, no resume).
    Log "Downloading with Invoke-WebRequest (slow) ..."
    Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing
    return ((Test-Path $Dest) -and (Get-Item $Dest).Length -gt 0)
}

function Resolve-Python {
    # 1. Explicit override.
    if ($env:PYTHON -and (Test-Path $env:PYTHON)) { return $env:PYTHON }

    # 2. The studio's Python 3.14 install (user AppData layout).  The
    #    installer drops both python.exe and python3.exe beside each other;
    #    prefer python3.exe to match the *nix scripts, fall back to python.exe.
    $Py314Dir = Join-Path $env:LOCALAPPDATA "Programs\Python\Python314"
    foreach ($candidate in @("python3.exe", "python.exe")) {
        $candidatePath = Join-Path $Py314Dir $candidate
        if (Test-Path $candidatePath) { return $candidatePath }
    }

    # 3. PATH fallback.
    foreach ($candidate in @("python", "python3")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }

    Die "No Python found. Set `$env:PYTHON, or install Python 3.14 to $Py314Dir, or add python to PATH."
}

$Py = Resolve-Python
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

Log "Installing Python requirements (ComfyUI) ..."
& $Py -m pip install -r (Join-Path $ComfyDir "requirements.txt")
if (-not $?) { Die "ComfyUI requirements install failed." }

# --------------------------------------------------------------------------- #
# 2. Download the fp8 Flux checkpoint
# --------------------------------------------------------------------------- #
if ($SkipDownload) {
    Log "Skipping model download (-SkipDownload)."
} elseif (Test-Path $CkptDest) {
    Log "Checkpoint already present: $CkptDest"
} else {
    Log "Downloading fp8 Flux (dev) ~ 12GB - this may take a while ..."
    if (-not (Download-Checkpoint -Url $CkptUrl -Dest $CkptDest)) {
        Die "Model download failed. Check the URL / network and re-run the script - a partial file is removed and the download restarts."
    }
}

if (-not (Test-Path $CkptDest)) { Die "checkpoint not found at $CkptDest" }

# --------------------------------------------------------------------------- #
# 3. Start the server (GPU by default, --cpu only with -Cpu)
# --------------------------------------------------------------------------- #
if ($Serve) {
    $args = @(".\main.py", "--port", $Port, "--listen", "127.0.0.1")
    if ($Cpu) {
        Log "Starting ComfyUI on :$Port (--cpu) ..."
        $args = @(".\main.py", "--cpu", "--port", $Port, "--listen", "127.0.0.1")
    } else {
        Log "Starting ComfyUI on :$Port (CUDA) ..."
    }
    Push-Location $ComfyDir
    & $Py @args
    Pop-Location
    exit 0
}

Log "Done. Start it with:"
Log "  .\scripts\setup_comfyui_flux.ps1 -Serve"
Log "Then generate with:"
Log "  python scripts\generate_phase1_library.py --backend comfyui --comfyui-url http://localhost:$Port"
