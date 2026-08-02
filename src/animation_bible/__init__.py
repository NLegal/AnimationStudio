"""Phase 4 — Animation Bible & Motion System.

Machine-readable standards for animation at the studio, transcribed from the
`Animation/` markdown bibles: cycle libraries, facial acting, gestures,
interactions, camera language, transitions, physics, cloth motion, timing,
prompt templates, and the quality checklist.
"""

from .models import (
    ActionTiming, BlinkType, CameraShot, ClothElement, DanceLoop,
    DocConsistencyReport, DocFact, EmotionalBeat, ExpressionLevel,
    FacialExpression, Gesture, IdleLayer, Interaction, InteractionPhase,
    JumpCycle, JumpPhase, LocomotionVariant, MotionBrief, MotionCycle,
    MouthAction, PacingStandard, PhysicsRule, ReactionStandard,
    SceneTransition, ShotHold,
)
from .bible import AnimationBible
from .prompts import (
    ANIMATION_NEGATIVE_BASE, build_animation_prompt,
    camera_style_descriptor, category_negative, emotion_word,
    quality_checklist,
)
from .motion_system import MotionSystem, MotionSystemResult

__all__ = [
    "ActionTiming", "BlinkType", "CameraShot", "ClothElement", "DanceLoop",
    "DocConsistencyReport", "DocFact", "EmotionalBeat", "ExpressionLevel",
    "FacialExpression", "Gesture", "IdleLayer", "Interaction",
    "InteractionPhase", "JumpCycle", "JumpPhase", "LocomotionVariant",
    "MotionBrief", "MotionCycle", "MouthAction", "PacingStandard",
    "PhysicsRule", "ReactionStandard", "SceneTransition", "ShotHold",
    "AnimationBible", "ANIMATION_NEGATIVE_BASE", "build_animation_prompt",
    "camera_style_descriptor", "category_negative", "emotion_word",
    "quality_checklist", "MotionSystem", "MotionSystemResult",
]
