"""Shared Pydantic v2 models for all pipeline contracts."""

import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class CharacterModel(BaseModel):
    """A character identity record in the studio universe."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: Literal["main", "family", "friend", "community", "fantasy"]
    species: str
    bio_data: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    locked_at: Optional[datetime] = None


class AssetModel(BaseModel):
    """An asset (image) in the studio asset repository.

    Follows D-15 lifecycle: draft → generated → scored → shortlisted
    → approved → production → archived.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    asset_type: Literal["reference", "expression", "pose", "outfit"]
    variant: Optional[str] = None
    state: str = "draft"
    file_path: str
    prompt: Optional[str] = None
    seed: Optional[int] = None
    model_id: Optional[str] = None
    scores: Optional[dict] = None
    brand_score: Optional[float] = None
    lineage: Optional[dict] = Field(
        default=None,
        description="Lineage metadata per D-18: generation_batch, candidate_pool, version_history, episode_usage",
    )
    created_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None


class GenerationJobRequest(BaseModel):
    """Request to generate assets for a character."""

    character_id: str
    job_type: Literal["reference", "expression", "pose", "outfit"]
    prompt: str
    negative_prompt: str = ""
    seed: Optional[int] = None
    count: int = Field(default=4, ge=1, le=100)
    model_backend: str = "flux"


class ScoringResult(BaseModel):
    """Result of identity scoring on a generated asset."""

    asset_id: str
    scores: dict[str, float]
    brand_score: dict
    scored_at: datetime = Field(default_factory=datetime.now)
