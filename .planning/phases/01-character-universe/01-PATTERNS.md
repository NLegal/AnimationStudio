# Phase 1: Character Universe & Bible — Pattern Map

**Mapped:** 2026-07-28
**Files analyzed:** 51 (all new — greenfield foundation phase)
**Analogs found:** 0 / 51

**Status:** This is the foundation phase of a 100% greenfield project with zero existing source code. All patterns documented below are **to be established**, not copied from existing code. Every pattern originates from architectural decisions D-01 through D-19 (CONTEXT.md) and the recommended project structure from RESEARCH.md.

## File Classification

### Source Code — Generation Engine (D-09: Pluggable Model Adapters)

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/generation_engine/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/generation_engine/base.py` | service | request-response | — | no-analog — establishes ABC for all future backends |
| `src/generation_engine/flux_backend.py` | service | transform (image gen) | — | no-analog — FluxPipeline adapter |
| `src/generation_engine/sdxl_backend.py` | service | transform (image gen) | — | no-analog — SDXL adapter |
| `src/generation_engine/pony_backend.py` | service | transform (image gen) | — | no-analog — Pony adapter |
| `src/generation_engine/comfy_backend.py` | service | transform (image gen) | — | no-analog — ComfyUI API adapter (R&D) |

### Source Code — Identity Engine (D-07: Plugin-based Scoring)

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/identity_engine/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/identity_engine/scorer.py` | service | transform (scoring) | — | no-analog — IdentityScorer factory |
| `src/identity_engine/brand_score.py` | service | transform (scoring) | — | no-analog — weighted composite |
| `src/identity_engine/plugins/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/identity_engine/plugins/dinov2_score.py` | service | transform (embedding) | — | no-analog — DINOv2 scoring plugin |
| `src/identity_engine/plugins/clip_score.py` | service | transform (embedding) | — | no-analog — CLIP scoring plugin |
| `src/identity_engine/plugins/color_verification.py` | service | transform (color analysis) | — | no-analog — brand color adherence |
| `src/identity_engine/plugins/part_verification.py` | service | transform (object detection) | — | no-analog — body part detection |
| `src/identity_engine/plugins/pose_verification.py` | service | transform (pose estimation) | — | no-analog — pose matching |
| `src/identity_engine/plugins/expression_verify.py` | service | transform (expression det.) | — | no-analog — expression matching |
| `src/identity_engine/plugins/style_verification.py` | service | transform (style analysis) | — | no-analog — style consistency |

### Source Code — Asset Repository (D-14: Repository Pattern)

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/asset_repository/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/asset_repository/interfaces.py` | service | CRUD | — | no-analog — AssetRepository ABC |
| `src/asset_repository/sqlite_repo.py` | service | CRUD | — | no-analog — SQLite implementation |
| `src/asset_repository/models.py` | model | CRUD | — | no-analog — Pydantic data models |
| `src/asset_repository/migrations.py` | utility | file-I/O | — | no-analog — schema versioning |

### Source Code — Training Engine (D-18: Training Abstraction)

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/training_engine/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/training_engine/base.py` | service | request-response | — | no-analog — TrainingBackend ABC |
| `src/training_engine/kohya_adapter.py` | service | batch (subprocess) | — | no-analog — Kohya SS adapter |

### Source Code — Prompt Builder (CHAR-08)

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/prompt_builder/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/prompt_builder/templates.py` | service | transform (text) | — | no-analog — prompt templates |
| `src/prompt_builder/negative.py` | service | transform (text) | — | no-analog — negative prompts |
| `src/prompt_builder/builder.py` | service | transform (text) | — | no-analog — prompt composition |

### Source Code — Pipeline Orchestration

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/pipeline/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/pipeline/job_queue.py` | service | CRUD | — | no-analog — generation job management |
| `src/pipeline/generation_job.py` | service | request-response | — | no-analog — full generation flow |
| `src/pipeline/diversity_filter.py` | service | transform (clustering) | — | no-analog — K-Means dedup |

### Source Code — Review UI (D-17)

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/review_ui/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/review_ui/app.py` | controller | request-response | — | no-analog — FastAPI app |
| `src/review_ui/templates/` | component | request-response | — | no-analog — Jinja2 templates (directory) |
| `src/review_ui/static/` | component | request-response | — | no-analog — CSS/JS (directory) |

### Source Code — Shared Models

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `src/models/__init__.py` | utility | N/A (package init) | — | no-analog (greenfield) |
| `src/models/schemas.py` | model | CRUD | — | no-analog — Pydantic pipeline schemas |

### Test Files

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `tests/conftest.py` | config | N/A (fixtures) | — | no-analog (greenfield) |
| `tests/test_identity_engine.py` | test | unit | — | no-analog (greenfield) |
| `tests/test_generation_engine.py` | test | unit | — | no-analog (greenfield) |
| `tests/test_asset_repository.py` | test | unit + integration | — | no-analog (greenfield) |
| `tests/test_prompt_builder.py` | test | unit | — | no-analog (greenfield) |
| `tests/test_training_engine.py` | test | unit | — | no-analog (greenfield) |

### Content / Data Files

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `Universe/Characters/Lily Bunny/bio.md` | config | N/A (content) | — | no-analog — character bible entry |
| `Universe/StyleGuide/` | config | N/A (content) | — | no-analog — style reference (directory) |
| `Universe/ColorPalette/` | config | N/A (content) | — | no-analog — color palette (directory) |
| `Universe/PromptTemplates/` | config | N/A (content) | — | no-analog — prompt templates (directory) |

### Config / Root Files

| New File | Role | Data Flow | Analog | Match Quality |
|----------|------|-----------|--------|---------------|
| `pyproject.toml` | config | N/A | — | no-analog — project metadata |
| `.env.example` | config | N/A | — | no-analog — API key template |

## Pattern Assignments

### `src/generation_engine/base.py` (service, request-response)

**Analog:** No existing code. **Establish new pattern.**

**Pattern to establish — Adapter ABC (from RESEARCH.md §Pattern 1):**

```python
# generation_engine/base.py — ESTABLISH THIS PATTERN
from abc import ABC, abstractmethod
from dataclasses import dataclass
from PIL import Image

@dataclass
class GenerationInput:
    prompt: str
    negative_prompt: str
    seed: int
    width: int = 1024
    height: int = 1024
    num_images: int = 1

@dataclass
class GenerationOutput:
    images: list[Image.Image]
    seed: int
    metadata: dict

class GenerationBackend(ABC):
    @abstractmethod
    def generate(self, input: GenerationInput) -> GenerationOutput:
        ...

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        ...
```

**Rationale (D-09):** This adapter interface is the foundational pattern for all backend swapping. Every concrete backend (Flux, SDXL, Pony, CloudAPI) implements this ABC. Downstream phases depend on the interface, never on concrete implementations.

---

### `src/generation_engine/flux_backend.py` (service, transform)

**Analog:** No existing code. **Establish pattern — FluxPipeline adapter (from RESEARCH.md §Code Examples).**

**Pattern to establish:**

```python
# generation_engine/flux_backend.py — FluxPipeline adapter
import torch
from diffusers import FluxPipeline
from .base import GenerationBackend, GenerationInput, GenerationOutput

class FluxBackend(GenerationBackend):
    def __init__(self, model_id: str = "black-forest-labs/FLUX.1-dev"):
        self.pipe = FluxPipeline.from_pretrained(
            model_id, torch_dtype=torch.bfloat16,
        )
        self.pipe.enable_model_cpu_offload()

    def load_model(self, model_path: str) -> None:
        # Load fine-tuned checkpoint or LoRA
        pass

    def generate(self, input: GenerationInput) -> GenerationOutput:
        generator = torch.Generator("cpu").manual_seed(input.seed)
        images = self.pipe(
            prompt=input.prompt,
            negative_prompt=input.negative_prompt,
            height=input.height,
            width=input.width,
            guidance_scale=3.5,
            num_inference_steps=50,
            max_sequence_length=512,
            generator=generator,
            num_images_per_prompt=input.num_images,
        ).images
        return GenerationOutput(
            images=images,
            seed=input.seed,
            metadata={"model": "FLUX.1-dev", "backend": "flux"},
        )
```

**Same pattern applies to:** `sdxl_backend.py`, `pony_backend.py`, `comfy_backend.py` — each implements `GenerationBackend` with its own pipeline/wrapper.

---

### `src/identity_engine/__init__.py` (utility, package init)

**Analog:** No existing code. **Establish pattern — public SDK export (D-07).**

```python
# identity_engine/__init__.py — D-07: importable as `from identity import IdentityScorer`
from .scorer import IdentityScorer
from .brand_score import BrandScore

__all__ = ["IdentityScorer", "BrandScore"]
```

---

### `src/identity_engine/scorer.py` (service, transform)

**Analog:** No existing code. **Establish pattern — plugin-based scoring factory (D-06, D-07).**

```python
# identity_engine/scorer.py — Plugin-based IdentityScorer
from typing import Protocol
from PIL import Image

class ScoringPlugin(Protocol):
    name: str
    weight: float
    def score(self, image: Image.Image, reference: Image.Image | None = None, **kwargs) -> float: ...

class IdentityScorer:
    def __init__(self, plugins: list[ScoringPlugin] | None = None):
        self.plugins = plugins or self._default_plugins()

    def _default_plugins(self) -> list[ScoringPlugin]:
        # D-06 weights: DINOv2 40%, CLIP 20%, Color 10%, Part 10%, Pose 5%, Expression 5%, Style 10%
        from .plugins.dinov2_score import DINOv2ScoringPlugin
        from .plugins.clip_score import CLIPScoringPlugin
        from .plugins.color_verification import ColorVerificationPlugin
        from .plugins.part_verification import PartVerificationPlugin
        from .plugins.pose_verification import PoseVerificationPlugin
        from .plugins.expression_verify import ExpressionVerificationPlugin
        from .plugins.style_verification import StyleVerificationPlugin
        return [
            DINOv2ScoringPlugin(weight=0.40),
            CLIPScoringPlugin(weight=0.20),
            ColorVerificationPlugin(weight=0.10),
            PartVerificationPlugin(weight=0.10),
            PoseVerificationPlugin(weight=0.05),
            ExpressionVerificationPlugin(weight=0.05),
            StyleVerificationPlugin(weight=0.10),
        ]

    def score_all(self, image: Image.Image, **kwargs) -> dict[str, float]:
        return {p.name: p.score(image, **kwargs) for p in self.plugins}

    def brand_score(self, image: Image.Image, **kwargs) -> dict:
        scores = self.score_all(image, **kwargs)
        return BrandScore.compute(scores)
```

---

### `src/identity_engine/brand_score.py` (service, transform)

**Analog:** No existing code. **Establish pattern — weighted composite (D-05, from RESEARCH.md §Code Examples).**

```python
# identity_engine/brand_score.py — D-05: Weighted composite scoring
class BrandScore:
    WEIGHTS = {
        "prompt_accuracy": 0.20,
        "character_consistency": 0.20,
        "technical_quality": 0.15,
        "facial_appeal": 0.15,
        "child_friendliness": 0.10,
        "color_harmony": 0.10,
        "silhouette_recognizability": 0.05,
        "style_consistency": 0.05,
    }

    @classmethod
    def compute(cls, scores: dict[str, float]) -> dict:
        total = sum(
            scores.get(key, 0.0) * weight
            for key, weight in cls.WEIGHTS.items()
        )
        return {
            "total": round(total, 4),
            "max": 1.0,
            "components": {
                key: {
                    "raw": scores.get(key, 0.0),
                    "weighted": round(scores.get(key, 0.0) * weight, 4),
                    "weight": weight,
                }
                for key, weight in cls.WEIGHTS.items()
            },
        }
```

---

### `src/identity_engine/plugins/dinov2_score.py` (service, transform)

**Analog:** No existing code. **Establish pattern — DINOv2 scoring plugin (from RESEARCH.md §Code Examples).**

```python
# identity_engine/plugins/dinov2_score.py — DINOv2 embedding similarity (40% weight)
import torch
from PIL import Image
from torchvision import transforms

class DINOv2ScoringPlugin:
    name = "character_consistency"
    weight: float = 0.40

    def __init__(self, weight: float = 0.40, model_name: str = "dinov2_vits14", device: str = "cpu"):
        self.weight = weight
        self.device = device
        self.model = torch.hub.load("facebookresearch/dinov2", model_name).to(device)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def embed(self, image: Image.Image) -> torch.Tensor:
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model(tensor)
        return embedding.squeeze().cpu()

    def score(self, image: Image.Image, reference: Image.Image | None = None, **kwargs) -> float:
        if reference is None:
            return 0.0
        emb_a = self.embed(image)
        emb_b = self.embed(reference)
        cos = torch.nn.functional.cosine_similarity(emb_a.unsqueeze(0), emb_b.unsqueeze(0))
        return float(cos.item())
```

**Same plugin pattern applies to:** `clip_score.py`, `color_verification.py`, `part_verification.py`, `pose_verification.py`, `expression_verify.py`, `style_verification.py` — each implements `score(image, **kwargs) -> float` following the `ScoringPlugin` protocol.

---

### `src/asset_repository/interfaces.py` (service, CRUD)

**Analog:** No existing code. **Establish pattern — Repository ABC (D-14, from RESEARCH.md §Pattern 2).**

```python
# asset_repository/interfaces.py — D-14: Repository pattern
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

class AssetRecord:
    id: str
    character_id: str
    asset_type: str  # 'reference', 'expression', 'pose', 'outfit'
    state: str       # D-15: draft→generated→scored→shortlisted→approved→production→archived
    file_path: str
    scores: dict
    prompt: str
    seed: int
    model_id: str
    created_at: datetime
    approved_at: Optional[datetime] = None

class AssetRepository(ABC):
    @abstractmethod
    async def save(self, record: AssetRecord) -> str: ...
    @abstractmethod
    async def get(self, asset_id: str) -> Optional[AssetRecord]: ...
    @abstractmethod
    async def update_state(self, asset_id: str, new_state: str) -> None: ...
    @abstractmethod
    async def find_by_character(self, character_id: str, asset_type: Optional[str] = None) -> list[AssetRecord]: ...
    @abstractmethod
    async def find_approved(self, character_id: str, asset_type: str) -> list[AssetRecord]: ...
```

---

### `src/asset_repository/sqlite_repo.py` (service, CRUD)

**Analog:** No existing code. **Establish pattern — SQLite implementation (D-13, from RESEARCH.md §Code Examples).**

```python
# asset_repository/sqlite_repo.py — SQLite3 implementation
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from .interfaces import AssetRepository, AssetRecord

class SQLiteAssetRepository(AssetRepository):
    def __init__(self, db_path: str = "catalog.db"):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    bio_data TEXT NOT NULL,  -- JSON blob
                    created_at TEXT NOT NULL,
                    locked_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    variant TEXT,
                    state TEXT NOT NULL DEFAULT 'draft',
                    file_path TEXT NOT NULL,
                    prompt TEXT,
                    seed INTEGER,
                    model_id TEXT,
                    scores TEXT,  -- JSON blob
                    brand_score REAL,
                    created_at TEXT NOT NULL,
                    approved_at TEXT,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    config TEXT NOT NULL,  -- JSON blob
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lora_models (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    training_config TEXT,  -- JSON blob
                    benchmark_scores TEXT,  -- JSON blob
                    trained_at TEXT NOT NULL,
                    promoted BOOLEAN DEFAULT 0
                )
            """)
```

---

### `src/asset_repository/models.py` (model, CRUD)

**Analog:** No existing code. **Establish pattern — Pydantic data models.**

```python
# asset_repository/models.py — Pydantic data models
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CharacterModel(BaseModel):
    id: str
    name: str
    category: str  # 'main', 'family', 'friend', 'community', 'fantasy'
    bio_data: dict
    created_at: datetime = Field(default_factory=datetime.now)
    locked_at: Optional[datetime] = None

class AssetModel(BaseModel):
    id: str
    character_id: str
    asset_type: str
    variant: Optional[str] = None
    state: str = "draft"
    file_path: str
    prompt: Optional[str] = None
    seed: Optional[int] = None
    model_id: Optional[str] = None
    scores: Optional[dict] = None
    brand_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
```

---

### `src/training_engine/base.py` (service, request-response)

**Analog:** No existing code. **Establish pattern — Training Engine ABC (D-18).**

```python
# training_engine/base.py — D-18: Training abstraction
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TrainingConfig:
    character_id: str
    dataset_path: Path
    output_path: Path
    base_model: str = "black-forest-labs/FLUX.1-dev"
    learning_rate: float = 1e-4
    num_epochs: int = 10
    batch_size: int = 4
    resolution: int = 1024

@dataclass
class TrainingResult:
    lora_path: Path
    version: str
    metrics: dict

class TrainingBackend(ABC):
    @abstractmethod
    def train(self, config: TrainingConfig) -> TrainingResult: ...
    @abstractmethod
    def validate_environment(self) -> bool: ...
```

---

### `src/prompt_builder/templates.py` (service, transform)

**Analog:** No existing code. **Establish pattern — character-specific prompt templates (CHAR-08).**

```python
# prompt_builder/templates.py — Character-specific prompt templates
from dataclasses import dataclass

@dataclass
class CharacterPrompt:
    name: str
    species: str
    appearance: str
    outfit: str
    style: str = "Pixar-quality, Cocomelon-inspired, bright colorful nursery world"

class PromptTemplates:
    @staticmethod
    def reference_sheet(character: CharacterPrompt, angle: str = "front") -> str:
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {angle} view, "
            f"{character.style}, highly detailed, cinematic lighting, "
            f"consistent character, masterpiece, 8k, child-friendly"
        )

    @staticmethod
    def expression(character: CharacterPrompt, expression: str) -> str:
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {expression} expression, "
            f"{character.style}, portrait, highly detailed"
        )

    @staticmethod
    def pose(character: CharacterPrompt, pose: str) -> str:
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {pose} pose, "
            f"{character.style}, full body, highly detailed"
        )

    @staticmethod
    def outfit(character: CharacterPrompt, outfit: str) -> str:
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {outfit}, standing, front view, "
            f"{character.style}, highly detailed, full body"
        )
```

---

### `src/prompt_builder/negative.py` (service, transform)

**Analog:** No existing code. **Establish pattern — common negative prompt standards (from PHASE1.md).**

```python
# prompt_builder/negative.py — Standardized negative prompts (CHAR-08, PHASE1.md)
COMMON_NEGATIVE = (
    "low quality, blurry, deformed, mutated, duplicate, extra arms, extra legs, "
    "extra fingers, missing fingers, cross eyed, cropped, watermark, text, logo, "
    "dark, scary, horror, realistic skin, adult, violence, blood, ugly, noise"
)

STYLE_NEGATIVE = (
    "anime, watercolor, 3D render, photorealistic, sketch, line art, "
    "black and white, grayscale, sepia, low contrast, oversaturated"
)

def build_negative_prompt(*, custom: str = "") -> str:
    parts = [COMMON_NEGATIVE, STYLE_NEGATIVE]
    if custom:
        parts.append(custom)
    return ", ".join(parts)
```

---

### `src/review_ui/app.py` (controller, request-response)

**Analog:** No existing code. **Establish pattern — FastAPI + Jinja2 review UI (D-17).**

```python
# review_ui/app.py — D-17: Simple web UI for human review
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="Character Review UI")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def review_dashboard(request: Request):
    return templates.TemplateResponse(
        "review.html",
        {"request": request, "characters": [], "candidates": []},
    )

@app.post("/approve/{asset_id}")
async def approve_asset(asset_id: str):
    # Transition asset state: scored → shortlisted → approved
    ...

@app.post("/reject/{asset_id}")
async def reject_asset(asset_id: str):
    # Transition asset state: scored → draft (for regeneration)
    ...

@app.post("/regenerate/{asset_id}")
async def regenerate_similar(asset_id: str):
    # Queue regeneration job with similar seeds
    ...
```

---

### `src/models/schemas.py` (model, CRUD)

**Analog:** No existing code. **Establish pattern — Pydantic pipeline contract schemas.**

```python
# models/schemas.py — Pydantic models for pipeline contracts
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class GenerationJobRequest(BaseModel):
    character_id: str
    job_type: Literal["reference", "expression", "pose", "outfit"]
    prompt: str
    negative_prompt: str = ""
    seed: Optional[int] = None
    count: int = Field(default=4, ge=1, le=100)
    model_backend: str = "flux"

class ScoringResult(BaseModel):
    asset_id: str
    scores: dict[str, float]
    brand_score: dict
    scored_at: datetime = Field(default_factory=datetime.now)
```

---

### `tests/conftest.py` (config, fixtures)

**Analog:** No existing code. **Establish pattern — shared test fixtures.**

```python
# tests/conftest.py — Shared pytest fixtures
import pytest
from pathlib import Path
from PIL import Image
import io

@pytest.fixture
def test_image():
    """Return a small RGB test image."""
    return Image.new("RGB", (224, 224), color=(255, 192, 203))

@pytest.fixture
def in_memory_db():
    """Provide an in-memory SQLite repository for testing."""
    from src.asset_repository.sqlite_repo import SQLiteAssetRepository
    repo = SQLiteAssetRepository(db_path=":memory:")
    return repo

@pytest.fixture
def mock_generation_backend():
    """Mock backend returning pre-stored test images."""
    from src.generation_engine.base import GenerationBackend, GenerationInput, GenerationOutput

    class MockBackend(GenerationBackend):
        def load_model(self, model_path: str) -> None:
            pass
        def generate(self, input: GenerationInput) -> GenerationOutput:
            return GenerationOutput(
                images=[Image.new("RGB", (1024, 1024), color=(255, 255, 255)) for _ in range(input.num_images)],
                seed=input.seed,
                metadata={"backend": "mock"},
            )
    return MockBackend()
```

---

### `pyproject.toml` (config, N/A)

**Analog:** No existing code. **Establish pattern — project metadata and dependency management.**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "character-studio"
version = "0.1.0"
description = "AI Nursery Character Universe — Generation Engine, Identity Scoring, Asset Repository"
requires-python = ">=3.11"

dependencies = [
    "diffusers>=0.39.0",
    "torch>=2.13.0",
    "transformers>=5.14.0",
    "Pillow>=11.0.0",
    "numpy>=2.0.0",
    "scikit-learn>=1.6.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]",
    "jinja2>=3.1.0",
    "aiosqlite>=0.20.0",
    "pydantic>=2.0.0",
    "timm>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-timeout>=2.3.0",
]
scoring = [
    "simple-aesthetics-predictor>=0.0.0",
    "opencv-python>=4.10.0",
]
comfyui = [
    "pycomfyapi>=0.1.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
timeout = 30
```

---

## Shared Patterns

### Pattern: Adapter ABC + Concrete Implementation
**Applies to:** Generation Engine (`generation_engine/base.py` + backends), Training Engine (`training_engine/base.py` + `kohya_adapter.py`), Asset Repository (`asset_repository/interfaces.py` + `sqlite_repo.py`)
**Establishes (per D-09, D-14, D-18):** Every external dependency gets an abstract base class; concrete implementations swap without changing orchestration code. This is the foundational architecture for the entire studio and must be followed by all downstream phases.

### Pattern: Plugin-Based Scoring
**Applies to:** Identity Engine (`identity_engine/scorer.py` + `plugins/*.py`)
**Establishes (per D-06, D-07):** Each scoring dimension is a plugin following a `ScoringPlugin` protocol (`name`, `weight`, `score()`). The `IdentityScorer` discovers and weights them. New scoring dimensions can be added by creating new plugin files.

### Pattern: Repository Pattern with SQLite Implementation
**Applies to:** `asset_repository/interfaces.py`, `asset_repository/sqlite_repo.py`
**Establishes (per D-14):** `AssetRepository` ABC with `SQLiteAssetRepository` implementation. Enables future migration to PostgreSQL without changing pipeline code. All database operations go through the interface.

### Pattern: Pydantic Pipeline Contracts
**Applies to:** `asset_repository/models.py`, `models/schemas.py`
**Establishes:** Every data structure crossing a pipeline boundary is a Pydantic `BaseModel`. Provides validation, serialization, and documentation for all pipeline contracts.

### Pattern: Package as SDK Export
**Applies to:** `identity_engine/__init__.py`, `generation_engine/__init__.py`, `asset_repository/__init__.py`
**Establishes (per D-07):** Each engine package exposes its primary class at package level (e.g., `from identity import IdentityScorer`). Subpackages are implementation details.

### Pattern: Dependency Injection via `__init__`
**Applies to:** All service classes
**Establishes:** All dependencies are injected through `__init__` constructors with sensible defaults. Enables testing with mock implementations and backend swapping.

### Pattern: Structured Error Handling
**Applies to:** All service and controller files
**Establishes:** Errors use custom exception hierarchy with `AppError` base class. API endpoints wrap handler logic in try/except blocks. Never expose raw stack traces in API responses.

```python
# Recommended error pattern (to establish in the first service file)
class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(f"{entity} '{entity_id}' not found", status_code=404)

class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
```

### Pattern: Asset Lifecycle State Machine
**Applies to:** `asset_repository/` — all state transitions
**Establishes (per D-15):** Assets progress through: `draft → generated → scored → shortlisted → approved → production → archived`. State transitions are validated. Only approved assets enter the Universe Library.

### Pattern: Testing with Mock Backends
**Applies to:** `tests/conftest.py` + all test files
**Establishes:** Test fixtures provide mock implementations (e.g., `MockBackend` for generation) so the pipeline can be tested without GPU. Image scoring tests use pre-generated test images.

### Pattern: Prompt Composition
**Applies to:** `prompt_builder/builder.py` + `templates.py`
**Establishes:** Prompt templates are parameterized strings composed per character, expression, pose, outfit, etc. The builder assembles the full prompt from template + character-specific data + negative prompt. Never hand-write prompts.

---

## No Analog Found — All Files

Since this is the foundation phase of a 100% greenfield project with zero existing source code, **all 51 files have no analog**. Every file listed in the classification table establishes new patterns.

The planner should use the RESEARCH.md code examples as reference implementations for:
- DINOv2 scoring plugin → RESEARCH.md lines 481-512
- CLIP scoring → RESEARCH.md lines 516-538
- Brand Score composite → RESEARCH.md lines 542-574
- FluxPipeline generation → RESEARCH.md lines 578-602
- SQLite schema → RESEARCH.md lines 606-673
- Repository ABC pattern → RESEARCH.md lines 376-407
- GenerationBackend ABC pattern → RESEARCH.md lines 338-368

## Metadata

**Analog search scope:** `/workspace/AnimationStudio/` (full repository)
**Files scanned:** 0 source files found (planning documents only)
**Pattern extraction date:** 2026-07-28
**Analogs found:** 0 / 51 (greenfield foundation phase — all patterns are new)

**Note for downstream consumers:** The patterns established in this phase become the canonical patterns that all downstream phases (2-6) must follow. The adapter ABC pattern, repository pattern, plugin-based scoring, Pydantic contracts, and testing patterns documented here are the templates for future work.
