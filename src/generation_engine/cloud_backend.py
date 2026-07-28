"""CloudAPIBackend — GenerationBackend adapter for cloud ML APIs.

Wraps fal.ai, Replicate, and BFL API behind the GenerationBackend ABC
to enable image generation without local GPU hardware.

API keys are read from environment variables:
  - FAL_API_KEY for fal.ai
  - REPLICATE_API_KEY for Replicate
  - BFL_API_KEY for Black Forest Labs API

Keys are never logged or included in output metadata (T-01-05).
"""

import enum
import logging
import os
import time
import uuid
from typing import Optional

from .base import GenerationBackend, GenerationInput, GenerationOutput

logger = logging.getLogger(__name__)


class Provider(str, enum.Enum):
    """Supported cloud ML API providers."""

    FAL = "fal"
    REPLICATE = "replicate"
    BFL = "bfl"


# Mapping of provider to environment variable name for API key
_PROVIDER_ENV_KEY: dict[Provider, str] = {
    Provider.FAL: "FAL_API_KEY",
    Provider.REPLICATE: "REPLICATE_API_KEY",
    Provider.BFL: "BFL_API_KEY",
}

# Default model per provider
_PROVIDER_DEFAULT_MODEL: dict[Provider, str] = {
    Provider.FAL: "fal-ai/flux/dev",
    Provider.REPLICATE: "black-forest-labs/flux-dev",
    Provider.BFL: "flux-dev",
}


class CloudAPIBackend(GenerationBackend):
    """Generation backend that wraps cloud ML APIs (fal.ai, Replicate, BFL).

    Enables image generation without local GPU by routing requests
    through cloud REST APIs. API keys are read from environment variables
    and validated on load_model().

    Usage:
        backend = CloudAPIBackend(provider="fal")
        result = backend.generate(GenerationInput(prompt="a cat", seed=42))
    """

    def __init__(
        self,
        provider: str = "fal",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = Provider(provider)
        self.api_key = api_key
        self.model = model or _PROVIDER_DEFAULT_MODEL[self.provider]
        self._ready = False

    def load_model(self, model_path: str = "") -> None:
        """Validate API key availability for the configured provider.

        Checks the environment variable for the API key. If no key is
        provided via __init__ or environment, a warning is logged but
        the backend does not crash — generate() will return error metadata.

        Args:
            model_path: Ignored for cloud backends (API manages models).
        """
        env_key = _PROVIDER_ENV_KEY[self.provider]

        # Resolve API key: constructor arg > env var > None
        resolved_key = self.api_key or os.environ.get(env_key)
        if not resolved_key:
            logger.warning(
                "CloudAPIBackend[%s]: No API key found. "
                "Set %s environment variable or pass api_key to constructor. "
                "Generation will return empty results with error metadata.",
                self.provider.value,
                env_key,
            )
            self._ready = False
            return

        self.api_key = resolved_key
        self._ready = True
        logger.info(
            "CloudAPIBackend[%s] ready (model: %s)",
            self.provider.value,
            self.model,
        )

    def generate(self, input: GenerationInput) -> GenerationOutput:
        """Generate images via the configured cloud API provider.

        Args:
            input: GenerationInput with prompt, seed, dimensions, etc.

        Returns:
            GenerationOutput with generated images (empty list on failure
            with error metadata — never crashes).
        """
        # Ensure API key validation has run
        if not self._ready:
            self.load_model()

        if not self._ready or not self.api_key:
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": f"CloudAPIBackend[{self.provider.value}]: "
                    f"No API key configured. "
                    f"Set {_PROVIDER_ENV_KEY[self.provider]} environment variable.",
                    "backend": "CloudAPIBackend",
                    "provider": self.provider.value,
                },
            )

        try:
            if self.provider == Provider.FAL:
                return self._generate_fal(input)
            elif self.provider == Provider.REPLICATE:
                return self._generate_replicate(input)
            elif self.provider == Provider.BFL:
                return self._generate_bfl(input)
            else:
                return GenerationOutput(
                    images=[],
                    seed=input.seed,
                    metadata={
                        "error": f"Unknown provider: {self.provider}",
                        "backend": "CloudAPIBackend",
                        "provider": self.provider.value,
                    },
                )
        except Exception as exc:
            logger.warning(
                "CloudAPIBackend[%s] generation failed: %s",
                self.provider.value,
                exc,
            )
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": str(exc),
                    "backend": "CloudAPIBackend",
                    "provider": self.provider.value,
                    "model": self.model,
                },
            )

    def _generate_fal(self, input: GenerationInput) -> GenerationOutput:
        """Generate via fal.ai REST API."""
        import requests

        endpoint = f"https://fal.run/{self.model}"
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": input.prompt,
            "seed": input.seed,
            "num_images": input.num_images,
            "image_size": {
                "width": input.width,
                "height": input.height,
            },
        }

        resp = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        result = resp.json()

        images = self._download_images(result.get("images", []))
        return GenerationOutput(
            images=images,
            seed=input.seed,
            metadata={
                "backend": "CloudAPIBackend",
                "provider": "fal",
                "model": self.model,
                "num_images": len(images),
                "request_id": result.get("request_id", ""),
            },
        )

    def _generate_replicate(self, input: GenerationInput) -> GenerationOutput:
        """Generate via Replicate REST API."""
        import requests

        # Start prediction
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "wait",
        }
        payload = {
            "input": {
                "prompt": input.prompt,
                "seed": input.seed,
                "num_outputs": input.num_images,
                "width": input.width,
                "height": input.height,
            },
        }

        resp = requests.post(
            f"https://api.replicate.com/v1/models/{self.model}/predictions",
            json=payload,
            headers=headers,
            timeout=120,
        )
        resp.raise_for_status()
        prediction = resp.json()

        # If prediction is still processing, poll for completion
        if prediction.get("status") == "processing":
            prediction_id = prediction["id"]
            for _attempt in range(60):
                time.sleep(5)
                poll_resp = requests.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers=headers,
                    timeout=30,
                )
                poll_resp.raise_for_status()
                prediction = poll_resp.json()
                if prediction.get("status") == "succeeded":
                    break
                elif prediction.get("status") == "failed":
                    raise RuntimeError(
                        f"Replicate prediction failed: {prediction.get('error', 'unknown')}"
                    )

        images = self._download_images(prediction.get("output", []))
        return GenerationOutput(
            images=images,
            seed=input.seed,
            metadata={
                "backend": "CloudAPIBackend",
                "provider": "replicate",
                "model": self.model,
                "num_images": len(images),
                "prediction_id": prediction.get("id", ""),
            },
        )

    def _generate_bfl(self, input: GenerationInput) -> GenerationOutput:
        """Generate via Black Forest Labs (BFL) API."""
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": input.prompt,
            "seed": input.seed,
            "width": input.width,
            "height": input.height,
        }

        # Start generation
        resp = requests.post(
            "https://api.bfl.ml/v1/generation",
            json={"model": self.model, **payload},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        request_id = result.get("id", "")

        # Poll for completion
        for _attempt in range(60):
            time.sleep(3)
            status_resp = requests.get(
                f"https://api.bfl.ml/v1/generation/{request_id}",
                headers=headers,
                timeout=30,
            )
            status_resp.raise_for_status()
            status_data = status_resp.json()
            if status_data.get("status") == "completed":
                result_data = status_data.get("result", {})
                images = self._download_images(result_data.get("images", []))
                return GenerationOutput(
                    images=images,
                    seed=input.seed,
                    metadata={
                        "backend": "CloudAPIBackend",
                        "provider": "bfl",
                        "model": self.model,
                        "num_images": len(images),
                        "request_id": request_id,
                    },
                )
            elif status_data.get("status") == "failed":
                raise RuntimeError(
                    f"BFL generation failed: {status_data.get('error', 'unknown')}"
                )

        raise TimeoutError(f"BFL generation did not complete within timeout ({request_id})")

    def _download_images(self, urls: list) -> list:
        """Download images from URL list.

        Validates content-type is image/* before processing (T-01-06).

        Args:
            urls: List of image URLs (strings) or dicts with 'url' key.

        Returns:
            List of PIL Image objects.
        """
        import requests
        from PIL import Image
        import io

        images = []
        for item in urls:
            url = item if isinstance(item, str) else item.get("url", "")
            if not url:
                continue
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()

                # Validate content-type is image/* (T-01-06)
                content_type = resp.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    logger.warning(
                        "Skipping non-image content-type: %s (%s)",
                        content_type,
                        url,
                    )
                    continue

                img = Image.open(io.BytesIO(resp.content))

                # Validate image dimensions and format (T-01-06)
                img.verify()
                # Re-open after verify() which may have consumed the data
                img = Image.open(io.BytesIO(resp.content))

                images.append(img)
            except Exception as exc:
                logger.warning("Failed to download image from %s: %s", url, exc)
        return images
