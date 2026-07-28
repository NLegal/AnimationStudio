from .base import GenerationBackend, GenerationInput, GenerationOutput, ModelLoadError
from .flux_backend import FluxBackend
from .sdxl_backend import SDXLBackend
from .pony_backend import PonyBackend
from .comfy_backend import ComfyUIBackend
from .cloud_backend import CloudAPIBackend

BACKENDS: dict[str, type[GenerationBackend]] = {
    "flux": FluxBackend,
    "sdxl": SDXLBackend,
    "pony": PonyBackend,
    "comfy": ComfyUIBackend,
    "cloud": CloudAPIBackend,
}

__all__ = [
    "GenerationBackend",
    "GenerationInput",
    "GenerationOutput",
    "ModelLoadError",
    "FluxBackend",
    "SDXLBackend",
    "PonyBackend",
    "ComfyUIBackend",
    "CloudAPIBackend",
    "BACKENDS",
]
