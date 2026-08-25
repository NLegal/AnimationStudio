"""Pydantic v2 models for the music generation backend contracts.

Mirrors the conventions of ``src/models/schemas.py``: ``Literal`` enums,
``Optional[T] = None``, ``Field(default_factory=...)`` and bounded fields,
one docstring per class.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class MusicRequest(BaseModel):
    """Request for one song generation job.

    Exactly the surface fixed by Phase 7 research §4 — captions are NOT
    part of the request; adapters compose them via
    ``src.audio_bible.prompts.build_music_prompt`` so bible ordering
    rules stay authoritative.
    """

    category: str
    topic: str = ""
    duration_s: int = Field(default=60, ge=10, le=600)
    vocals: str = "female lead vocal, children's choir"
    lyrics_override: Optional[str] = None
    seed: Optional[int] = None
    tags: list[str] = Field(default_factory=list)


class MusicStatus(BaseModel):
    """Poll status of an async music generation job.

    ``state`` vocabulary mirrors the pipeline job state machine
    (``src/pipeline/job_queue.py``): pending | running | completed | failed.
    """

    state: Literal["pending", "running", "completed", "failed"]
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    error: Optional[str] = None


class MusicResult(BaseModel):
    """Result of a completed music generation job.

    Held in memory only — persistence into the asset catalog is
    explicitly out of scope for this phase.
    """

    request: MusicRequest
    audio: bytes
    format: Literal["wav", "mp3"] = "wav"
    job_id: str
    backend: str
    seed: int
