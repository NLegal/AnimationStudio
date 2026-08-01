#!/usr/bin/env bash
# setup_comfyui_flux.sh — Install ComfyUI + a quantized Flux checkpoint.
#
# ComfyUI is an R&D-only generation backend in this studio (D-08); it is
# never used in the production pipeline.  This script installs it and makes
# the local backend (`--backend comfyui`) usable.
#
# Environment notes
#   * No GPU here, so the server runs with --cpu.  Flux on CPU is *slow*
#     (minutes per image); treat it as an offline fallback and prefer the
#     cloud backends (`FAL_API_KEY` / `REPLICATE_API_KEY` / `BFL_API_KEY`)
#     when keys are available.
#   * 15GiB RAM → a quantized Flux checkpoint (Q4 GGUF ≈ 9GB) fits; the
#     fp8/full dev checkpoint is larger and slower on CPU.
#
# Usage:
#   bash scripts/setup_comfyui_flux.sh            # install + download + start
#   bash scripts/setup_comfyui_flux.sh --serve    # just start the server
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

# Quantized Flux (dev) GGUF — Q4_K_S ≈ 9GB, fits the 15GiB RAM machine.
GGUF_URL="${FLUX_GGUF_URL:-https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q4_K_S.gguf}"
GGUF_SAVE="${COMFYUI_DIR}/models/checkpoints/${CKPT_NAME}.gguf"
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

# ComfyUI-GGUF custom node — required to load .gguf Flux weights.
GGUF_NODE="${COMFYUI_DIR}/custom_nodes/ComfyUI-GGUF"
if [ ! -d "${GGUF_NODE}/.git" ]; then
    log "Installing ComfyUI-GGUF custom node …"
    git clone https://github.com/city96/ComfyUI-GGUF.git "${GGUF_NODE}"
else
    log "ComfyUI-GGUF already present."
fi

log "Installing Python requirements (ComfyUI + GGUF) …"
python3 -m pip install -r "${COMFYUI_DIR}/requirements.txt"
python3 -m pip install -r "${GGUF_NODE}/requirements.txt"

# --------------------------------------------------------------------------- #
# 2. Download the quantized Flux checkpoint
# --------------------------------------------------------------------------- #
if [ "${1:-}" = "--no-download" ]; then
    log "Skipping model download (--no-download)."
elif [ -f "${CKPT_DEST}" ]; then
    log "Checkpoint already present: ${CKPT_DEST}"
elif [ -f "${GGUF_SAVE}" ]; then
    log "GGUF already downloaded: ${GGUF_SAVE}"
    cp "${GGUF_SAVE}" "${CKPT_DEST}"
else
    log "Downloading quantized Flux (Q4 GGUF ≈ 9GB) — this may take a while …"
    python3 - "$GGUF_URL" "$GGUF_SAVE" <<'PY'
import sys
import urllib.request
url, dest = sys.argv[1], sys.argv[2]
import pathlib
pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
tmp = dest + ".part"

class Progress(urllib.request.HTTPDefaultErrorHandler):
    pass

urllib.request.urlretrieve(url, tmp)
pathlib.Path(tmp).rename(dest)
print(f"saved {dest}")
PY
    cp "${GGUF_SAVE}" "${CKPT_DEST}"
fi

[ -f "${CKPT_DEST}" ] || die "checkpoint not found at ${CKPT_DEST}"

# --------------------------------------------------------------------------- #
# 3. Start the server (CPU mode)
# --------------------------------------------------------------------------- #
if [ "${1:-}" = "--serve" ] || [ "${2:-}" = "--serve" ]; then
    log "Starting ComfyUI on :${PORT} (--cpu) …"
    exec python3 "${COMFYUI_DIR}/main.py" --cpu --port "${PORT}" --listen 127.0.0.1
fi

log "Done. Start it with:"
log "  bash scripts/setup_comfyui_flux.sh --serve"
log "Then generate with:"
log "  python scripts/generate_phase1_library.py --backend comfyui --comfyui-url http://localhost:${PORT}"
