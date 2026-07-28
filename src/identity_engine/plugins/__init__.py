"""Identity Engine scoring plugins registry.

Each plugin implements the ScoringPlugin protocol:
    - name: str
    - weight: float
    - score(image, reference=None, **kwargs) -> float

All plugins handle missing references gracefully (return documented default)
and handle model load failures gracefully (log warning, return fallback score).
"""

from .dinov2_score import DINOv2ScoringPlugin
from .clip_score import CLIPScoringPlugin
from .color_verification import ColorVerificationPlugin
from .part_verification import PartVerificationPlugin
from .pose_verification import PoseVerificationPlugin
from .expression_verify import ExpressionVerificationPlugin
from .style_verification import StyleVerificationPlugin

ALL_PLUGINS = [
    DINOv2ScoringPlugin,
    CLIPScoringPlugin,
    ColorVerificationPlugin,
    PartVerificationPlugin,
    PoseVerificationPlugin,
    ExpressionVerificationPlugin,
    StyleVerificationPlugin,
]

__all__ = [
    "ALL_PLUGINS",
    "DINOv2ScoringPlugin",
    "CLIPScoringPlugin",
    "ColorVerificationPlugin",
    "PartVerificationPlugin",
    "PoseVerificationPlugin",
    "ExpressionVerificationPlugin",
    "StyleVerificationPlugin",
]
