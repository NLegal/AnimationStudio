"""ComfyUIBackend — R&D generation backend for ComfyUI API.

Designed exclusively for R&D and lab use (D-08). Connects to a running
ComfyUI server (local or remote) via its REST API to submit workflow
jobs and retrieve results.

Never used in the production pipeline — ComfyUI is for prompt discovery,
workflow design, and model testing only.
"""

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Optional

from .base import GenerationBackend, GenerationInput, GenerationOutput, ModelLoadError

logger = logging.getLogger(__name__)

# Path to the workflows directory containing type-specific JSON templates.
_WORKFLOW_DIR = Path(__file__).parent / "workflows"

# Model files the ComfyUI setup scripts install (setup_comfyui_flux.ps1/.sh
# download the Q4 GGUF Flux unet plus its text encoders and VAE under exactly
# these names).  Used to fill in any loader node that would otherwise submit
# an empty file name, which ComfyUI rejects with "Value not in list".
#
# The unet is the city96 GGUF quantization (flux1-dev-Q4_K_S.gguf): it loads
# through the ComfyUI-GGUF node as an int4/bf16 model instead of fp8.  fp8
# weights have no CPU kernel in torch and crash with a Windows access
# violation on CPU-only installs, which is why the fp8 checkpoint is avoided.
_DEFAULT_UNET_NAME = "flux1-dev-Q4_K_S.gguf"
_DEFAULT_CLIP_L_NAME = "clip_l.safetensors"
_DEFAULT_T5_NAME = "t5xxl_fp16.safetensors"
_DEFAULT_VAE_NAME = "ae.safetensors"

# Generation asset types that do not have a dedicated graph reuse the closest
# single-image template instead of falling through to the bare default.
_WORKFLOW_ALIASES: dict[str, str] = {
    "reference": "reference_sheet",
    "lighting": "reference_sheet",
}

# Default minimal workflow JSON template for single-image generation.
# In practice, users should export their own workflow from ComfyUI
# and place it in the configured template path.
_DEFAULT_WORKFLOW_TEMPLATE: dict = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 42,
            "steps": 25,
            "cfg": 3.5,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0],
        },
    },
    "4": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": _DEFAULT_UNET_NAME, "weight_dtype": "default"}},
    "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["10", 0]}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["10", 0]}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["11", 0]}},
    "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "comfy", "images": ["8", 0]}},
    "10": {
        "class_type": "DualCLIPLoader",
        "inputs": {
            "clip_name1": _DEFAULT_CLIP_L_NAME,
            "clip_name2": _DEFAULT_T5_NAME,
            "type": "flux",
        },
    },
    "11": {"class_type": "VAELoader", "inputs": {"vae_name": _DEFAULT_VAE_NAME}},
}


class ComfyUIBackend(GenerationBackend):
    """R&D backend that submits workflows to a ComfyUI server.

    Connects to a ComfyUI server (default: http://localhost:8188) and
    uses its REST API to queue generation jobs, poll for completion,
    and retrieve result images.

    .. note::
        This backend is for R&D/lab use only (D-08). Never use in the
        production pipeline. The production pipeline uses diffusers
        backends (FluxBackend, SDXLBackend, PonyBackend).

    If PyComfyAPI is available, it is preferred for workflow management.
    Otherwise falls back to raw requests to the ComfyUI REST API.
    """

    def __init__(self, server_url: str = "http://localhost:8188"):
        self.server_url = server_url.rstrip("/")
        self._client: Optional[object] = None

    def load_model(self, model_path: str = "") -> None:
        """Validate connectivity to the ComfyUI server.

        For R&D use, a missing or unreachable server is non-fatal.
        A warning is logged and the backend remains operational —
        generate() will return empty results with error metadata.

        Args:
            model_path: Ignored for ComfyUI backend (server manages models).
        """
        try:
            import requests
            resp = requests.get(f"{self.server_url}/", timeout=5)
            resp.raise_for_status()
            logger.info("ComfyUI server reachable at %s", self.server_url)
        except ImportError:
            logger.warning(
                "requests not installed — cannot verify ComfyUI connectivity"
            )
        except Exception as exc:
            logger.warning(
                "ComfyUI server at %s unreachable (%s). "
                "Generation will return empty results with error metadata. "
                "This is expected for R&D workflows.",
                self.server_url,
                exc,
            )

    def generate(self, input: GenerationInput, asset_type: str = "") -> GenerationOutput:
        """Submit a generation job to ComfyUI and poll for results.

        Uses PyComfyAPI if available, otherwise raw requests to the
        ComfyUI REST API.

        Args:
            input: GenerationInput with prompt and generation params.
            asset_type: Optional asset type key for loading a specific
                workflow template (e.g. "expression", "pose", "outfit").

        Returns:
            GenerationOutput with generated images (empty list if ComfyUI
            is unreachable or generation fails).
        """
        try:
            return self._generate_pycomfy(input, asset_type)
        except ImportError:
            logger.debug("PyComfyAPI not available, falling back to raw REST API")
        except Exception as exc:
            logger.warning("PyComfyAPI generation failed: %s", exc)

        try:
            return self._generate_rest(input, asset_type)
        except Exception as exc:
            logger.warning("ComfyUI REST generation failed: %s", exc)
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": str(exc),
                    "backend": "ComfyUIBackend",
                    "server_url": self.server_url,
                },
            )

    def _generate_pycomfy(self, input: GenerationInput, asset_type: str = "") -> GenerationOutput:
        """Generate using PyComfyAPI client if available."""
        from pycomfyapi import PyComfyClient  # type: ignore[import-untyped]

        client = PyComfyClient(server_url=self.server_url)

        workflow = self._build_workflow(input, asset_type)
        job_id = client.queue_workflow(workflow)

        # Poll for completion
        result = None
        for _attempt in range(60):  # 5 min timeout at 5s intervals
            status = client.get_job_status(job_id)
            if status.get("status") in ("completed", "success"):
                result = client.get_job_result(job_id)
                break
            time.sleep(5)

        if result is None:
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": "ComfyUI job did not complete within timeout",
                    "backend": "ComfyUIBackend",
                    "server_url": self.server_url,
                    "job_id": job_id,
                },
            )

        # Extract images from result
        from PIL import Image
        import io

        images = []
        for img_data in result.get("images", []):
            img_bytes = img_data if isinstance(img_data, bytes) else img_data.get("data", b"")
            if img_bytes:
                images.append(Image.open(io.BytesIO(img_bytes)))

        return GenerationOutput(
            images=images,
            seed=input.seed,
            metadata={
                "backend": "ComfyUIBackend",
                "server_url": self.server_url,
                "job_id": job_id,
                "num_images": len(images),
            },
        )

    def _generate_rest(self, input: GenerationInput, asset_type: str = "") -> GenerationOutput:
        """Fallback generation using raw ComfyUI REST API.

        POSTs a workflow JSON to /prompt, then polls /history for results.
        """
        import requests

        workflow = self._build_workflow(input, asset_type)
        payload = {"prompt": workflow, "client_id": f"character-studio-{uuid.uuid4().hex[:8]}"}

        resp = requests.post(f"{self.server_url}/prompt", json=payload, timeout=10)
        resp.raise_for_status()
        prompt_result = resp.json()
        prompt_id = prompt_result["prompt_id"]

        # Poll /history for completion
        images = []
        for _attempt in range(60):
            hist_resp = requests.get(
                f"{self.server_url}/history/{prompt_id}", timeout=10
            )
            if hist_resp.status_code == 200:
                history = hist_resp.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    # Extract images from node outputs
                    for _node_id, node_output in outputs.items():
                        for img_info in node_output.get("images", []):
                            img_filename = img_info.get("filename", "")
                            img_subfolder = img_info.get("subfolder", "")
                            img_resp = requests.get(
                                f"{self.server_url}/view",
                                params={"filename": img_filename, "subfolder": img_subfolder, "type": "output"},
                                timeout=10,
                            )
                            if img_resp.status_code == 200:
                                from PIL import Image
                                import io
                                images.append(Image.open(io.BytesIO(img_resp.content)))
                    break
            time.sleep(5)

        return GenerationOutput(
            images=images,
            seed=input.seed,
            metadata={
                "backend": "ComfyUIBackend",
                "server_url": self.server_url,
                "prompt_id": prompt_id,
                "num_images": len(images),
            },
        )

    def _build_workflow(self, input: GenerationInput, asset_type: str = "") -> dict:
        """Build a ComfyUI workflow JSON from the generation input.

        Starts from the type-specific template (if available) and injects
        prompt, seed, and dimensions.

        Args:
            input: GenerationInput with prompt and generation params.
            asset_type: Optional asset type key to load a specific workflow
                template (e.g. "expression", "pose", "outfit", "reference_sheet").

        Returns:
            A dict suitable for the ComfyUI /prompt API.
        """
        workflow = self._load_workflow_template(asset_type)

        # Ensure every model loader names a file that exists on the server.
        # ComfyUI rejects an empty name ("Value not in list") — templates that
        # fall back to the default graph must not submit blank loaders.
        for node in workflow.values():
            cls = node.get("class_type", "")
            inputs = node.get("inputs", {})
            if cls == "CheckpointLoaderSimple" and not inputs.get("ckpt_name"):
                inputs["ckpt_name"] = _DEFAULT_UNET_NAME
            elif cls == "UnetLoaderGGUF" and not inputs.get("unet_name"):
                inputs["unet_name"] = _DEFAULT_UNET_NAME
            elif cls == "DualCLIPLoader":
                if not inputs.get("clip_name1"):
                    inputs["clip_name1"] = _DEFAULT_CLIP_L_NAME
                if not inputs.get("clip_name2"):
                    inputs["clip_name2"] = _DEFAULT_T5_NAME
            elif cls == "VAELoader" and not inputs.get("vae_name"):
                inputs["vae_name"] = _DEFAULT_VAE_NAME

        # Inject positive prompt into CLIPTextEncode node (node 6)
        if "6" in workflow and workflow["6"].get("class_type") == "CLIPTextEncode":
            workflow["6"]["inputs"]["text"] = input.prompt

        # Inject negative prompt into CLIPTextEncode node (node 7)
        if "7" in workflow and workflow["7"].get("class_type") == "CLIPTextEncode":
            workflow["7"]["inputs"]["text"] = input.negative_prompt

        # Inject seed into KSampler node (node 3)
        if "3" in workflow and workflow["3"].get("class_type") == "KSampler":
            workflow["3"]["inputs"]["seed"] = input.seed

        # Inject dimensions into EmptyLatentImage node (node 5)
        if "5" in workflow and workflow["5"].get("class_type") == "EmptyLatentImage":
            workflow["5"]["inputs"]["width"] = input.width
            workflow["5"]["inputs"]["height"] = input.height

        return workflow

    def _load_workflow_template(self, asset_type: str = "") -> dict:
        """Load the workflow template JSON for the given asset type.

        Looks for ``{asset_type}.json`` in the ``workflows/`` directory.
        Falls back to ``comfy_workflow.json`` in the same directory as this file,
        then to the built-in default template.

        Args:
            asset_type: The asset type key (e.g. "expression", "pose", "outfit",
                "reference_sheet"). If empty or not found, falls through to
                the file-based fallback, then the built-in default.

        Returns:
            A dict representing the ComfyUI workflow graph.
        """
        import copy

        # Asset types without a dedicated graph reuse the closest template.
        asset_type = _WORKFLOW_ALIASES.get(asset_type or "", asset_type or "")

        # 1. Try type-specific template from workflows/ directory
        if asset_type:
            template_path = _WORKFLOW_DIR / f"{asset_type}.json"
            if template_path.exists():
                with open(template_path) as f:
                    return json.load(f)
            logger.warning(
                "Workflow template '%s' not found at %s. "
                "Falling back to default template.",
                asset_type, template_path,
            )

        # 2. Try the single template file (backward compatibility)
        template_path = Path(__file__).parent / "comfy_workflow.json"
        if template_path.exists():
            with open(template_path) as f:
                return json.load(f)

        # 3. Fall back to built-in template
        return copy.deepcopy(_DEFAULT_WORKFLOW_TEMPLATE)
