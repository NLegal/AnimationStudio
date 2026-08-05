#!/usr/bin/env bash
# setup_comfyui_flux.sh — Install ComfyUI + the fp8 Flux checkpoint.
#
# ComfyUI is an R&D-only generation backend in this studio (D-08); it is
# never used in the production pipeline.  This script installs it and makes
# the local backend (`--backend comfyui`) usable.
#
# Environment notes
#   * On a GPU box the server starts with CUDA by default (--cpu only via
#     the --cpu flag).  Flux on GPU is fast (seconds per image); on CPU it
#     is minutes per image — prefer the cloud backends (`FAL_API_KEY` /
#     `REPLICATE_API_KEY` / `BFL_API_KEY`) in that case.
#   * We download the fp8 Flux (dev) safetensors (≈12GB) because the
#     workflow templates reference it via CheckpointLoaderSimple.  Needs
#     roughly 12–16GB RAM/VRAM.
#
# Usage:
#   bash scripts/setup_comfyui_flux.sh                # install + download
#   bash scripts/setup_comfyui_flux.sh --serve        # just start the server
#   bash scripts/setup_comfyui_flux.sh --serve --cpu  # start on CPU only
#   bash scripts/setup_comfyui_flux.sh --no-download  # skip the model download
#
# Set COMFYUI_DIR to override the install location (default: tools/comfyui).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMFYUI_DIR="${COMFYUI_DIR:-${PROJECT_ROOT}/tools/comfyui}"
PORT="${COMFYUI_PORT:-8188}"

# Checkpoint filename the workflow templates reference
# (src/generation_engine/workflows/*.json → "flux1-dev.safetensors").
CKPT_NAME="flux1-dev.safetensors"

# fp8 Flux (dev) safetensors — loads via CheckpointLoaderSimple, ≈12GB.
CKPT_URL="${FLUX_CKPT_URL:-https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors}"
CKPT_DEST="${COMFYUI_DIR}/models/checkpoints/${CKPT_NAME}"

log()  { printf '\n[setup] %s\n' "$*"; }
die()  { printf '[setup] ERROR: %s\n' "$*" >&2; exit 1; }

command -v git  >/dev/null || die "git is required"
command -v python3 >/dev/null || die "python3 is required"

# --------------------------------------------------------------------------- #
# 1. Clone + install ComfyUI
# --------------------------------------------------------------------------- #
if [ ! -d "${COMFYUI_DIR}/.git" ]; then
    log "Cloning ComfyUI into ${COMFYUI_DIR} …"
    mkdir -p "$(dirname "${COMFYUI_DIR}")"
    git clone https://github.com/comfyanonymous/ComfyUI.git "${COMFYUI_DIR}"
else
    log "ComfyUI already present (${COMFYUI_DIR})."
fi

log "Installing Python requirements (ComfyUI) …"
python3 -m pip install -r "${COMFYUI_DIR}/requirements.txt"

# --------------------------------------------------------------------------- #
# 2. Download the fp8 Flux checkpoint
# --------------------------------------------------------------------------- #
NO_DOWNLOAD=0
for arg in "$@"; do
    [ "${arg}" = "--no-download" ] && NO_DOWNLOAD=1
done

download_checkpoint() {
    local url="$1" dest="$2"
    mkdir -p "$(dirname "${dest}")"

    # 1) curl - follows HuggingFace's 302 -> CDN redirect, retries, resumes.
    if command -v curl >/dev/null 2>&1; then
        log "Downloading with curl (follows redirects, resumable) ..."
        if curl -L --fail --retry 3 --retry-delay 2 -C - --progress-bar -o "${dest}" "${url}"; then
            [ -s "${dest}" ] && return 0
        fi
        log "curl download failed. Falling back to Python urllib ..."
        rm -f "${dest}"
    fi

    # 2) Python urllib fallback.
    log "Downloading with Python urllib ..."
    python3 - "${url}" "${dest}" <<'PY'
import sys
import urllib.request
import pathlib
url, dest = sys.argv[1], sys.argv[2]
pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
tmp = dest + ".part"
urllib.request.urlretrieve(url, tmp)
pathlib.Path(tmp).rename(dest)
print(f"saved {dest}")
PY
    [ -s "${dest}" ]
}

if [ "${NO_DOWNLOAD}" = "1" ]; then
    log "Skipping model download (--no-download)."
elif [ -f "${CKPT_DEST}" ]; then
    log "Checkpoint already present: ${CKPT_DEST}"
else
    log "Downloading fp8 Flux (dev) ≈ 12GB — this may take a while …"
    if ! download_checkpoint "${CKPT_URL}" "${CKPT_DEST}"; then
        die "Model download failed. Check the URL / network and re-run the script."
    fi
fi

[ -f "${CKPT_DEST}" ] || die "checkpoint not found at ${CKPT_DEST}"

# --------------------------------------------------------------------------- #
# 3. Start the server (CUDA by default, --cpu only with --cpu)
# --------------------------------------------------------------------------- #
SERVE=0; CPU=0; LOWVRAM=0
for arg in "$@"; do
    case "${arg}" in
        --serve)        SERVE=1 ;;
        --cpu)          CPU=1 ;;
        --lowvram)      LOWVRAM=1 ;;
    esac
done
if [ "${SERVE}" = "1" ]; then
    # oneDNN/MKL ISA workaround - prevents access-violation crashes in
    # torch.nn.Linear on AMD/older CPUs when the model builds on CPU.
    export ONEDNN_MAX_CPU_ISA="AVX2"
    export MKL_ENABLE_INSTRUCTIONS="AVX2"

    if [ "${CPU}" = "1" ]; then
        log "Starting ComfyUI on :${PORT} (--cpu, forced) ..."
        exec python3 "${COMFYUI_DIR}/main.py" --cpu --port "${PORT}" --listen 127.0.0.1
    fi
    if [ "${LOWVRAM}" = "1" ]; then
        log "Starting ComfyUI on :${PORT} (CUDA, --lowvram) ..."
        exec python3 "${COMFYUI_DIR}/main.py" --lowvram --port "${PORT}" --listen 127.0.0.1
    fi
    if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        log "Starting ComfyUI on :${PORT} (CUDA) ..."
        exec python3 "${COMFYUI_DIR}/main.py" --port "${PORT}" --listen 127.0.0.1
    fi
    log "torch reports no CUDA device - starting with --cpu to avoid an access-violation crash while loading the checkpoint."
    exec python3 "${COMFYUI_DIR}/main.py" --cpu --port "${PORT}" --listen 127.0.0.1
fi

log "Done. Start it with:"
log "  bash scripts/setup_comfyui_flux.sh --serve"
log "Then generate with:"
log "  python scripts/generate_phase1_library.py --backend comfyui --comfyui-url http://localhost:${PORT}"
