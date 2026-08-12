"""Shared ComfyUI server helpers for the AnimationStudio Colab notebooks.

``ensure_comfyui_up()`` reuses or starts the local ComfyUI server and waits
until the API actually answers.  It is imported by several cells so that any
server-dependent step can auto-restart ComfyUI after a Colab VM recycle
(instead of failing with ``ConnectionRefusedError``).

Colab keeps variables in memory per kernel, so after a VM restart the
notebook's earlier cells are wiped.  Importing this module (part of the repo)
keeps the server-management logic available regardless of which cell ran first.
"""

import os
import subprocess
import sys
import time

import requests

COMFY_PROC: subprocess.Popen | None = None


def comfy_alive(port: int = 8188, timeout: float = 5) -> bool:
    """True when the ComfyUI API answers on ``port``."""
    try:
        return requests.get(
            f"http://127.0.0.1:{port}/system_stats", timeout=timeout
        ).ok
    except Exception:
        return False


def ensure_comfyui_up(
    port: int = 8188,
    work: str = "/content",
    comfy_dir: str = "/content/comfyui",
    wait: int = 120,
) -> subprocess.Popen:
    """Return a running ComfyUI server, starting one if needed.

    Args:
        port: ComfyUI HTTP port.
        work: Working directory (used for the ``comfyui.log`` file).
        comfy_dir: Directory containing ComfyUI's ``main.py``.
        wait: Max seconds to wait for the API to come up.

    Raises:
        SystemExit: when the server process dies or the API never answers.
    """
    global COMFY_PROC
    if comfy_alive(port):
        return COMFY_PROC

    print(f"Starting ComfyUI on :{port} (first boot loads nodes, may take 1-2 min) ...")
    log_path = os.path.join(work, "comfyui.log")
    logf = open(log_path, "a")
    COMFY_PROC = subprocess.Popen(
        [sys.executable, "main.py", "--port", str(port), "--listen", "127.0.0.1"],
        cwd=comfy_dir,
        stdout=logf,
        stderr=subprocess.STDOUT,
    )
    for _ in range(wait):
        if comfy_alive(port):
            print(f"PASS: ComfyUI up on :{port}")
            return COMFY_PROC
        if COMFY_PROC.poll() is not None:
            break
        time.sleep(1)

    print("--- comfyui.log tail ---")
    try:
        print(open(log_path).read()[-2000:])
    except Exception:
        pass
    print("--- end log ---")
    raise SystemExit("ComfyUI failed to start (see log above)")


def server_url(port: int = 8188) -> str:
    """Base URL for API calls against the local server."""
    return f"http://127.0.0.1:{port}"
