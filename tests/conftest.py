"""Shared pytest fixtures for the character-studio test suite.

Provides fixtures for in-memory SQLite repositories, mock generation
backends, test images, and sample character/asset data.
"""

import pytest
from PIL import Image

from src.models.schemas import CharacterModel, AssetModel
from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from src.generation_engine.base import GenerationBackend, GenerationInput, GenerationOutput
from src.identity_engine.scorer import IdentityScorer, MockScorerPlugin


class MockBackend(GenerationBackend):
    """Mock generation backend that returns solid-color test images."""

    def __init__(self, color: tuple[int, int, int] = (255, 255, 255)):
        self.color = color

    def load_model(self, model_path: str) -> None:
        pass

    def generate(self, input: GenerationInput) -> GenerationOutput:
        return GenerationOutput(
            images=[
                Image.new("RGB", (1024, 1024), color=self.color)
                for _ in range(input.num_images)
            ],
            seed=input.seed,
            metadata={"backend": "mock", "model": "MockBackend"},
        )


@pytest.fixture
def test_image():
    """Return a small RGB test image (224x224)."""
    return Image.new("RGB", (224, 224), color=(255, 192, 203))


@pytest.fixture
def rgb_image():
    """Return a medium RGB test image (640x480)."""
    return Image.new("RGB", (640, 480), color=(100, 150, 200))


@pytest.fixture
def in_memory_db():
    """Return an SQLiteAssetRepository connected to :memory:."""
    repo = SQLiteAssetRepository(db_path=":memory:")
    return repo


@pytest.fixture
def in_memory_char_db():
    """Return an SQLiteCharacterRepository connected to :memory:."""
    repo = SQLiteCharacterRepository(db_path=":memory:")
    return repo


@pytest.fixture
def mock_generation_backend():
    """Return a MockBackend instance returning white 1024x1024 images."""
    return MockBackend()


@pytest.fixture
def lily_character():
    """Return a sample CharacterModel for Lily Bunny."""
    return CharacterModel(
        name="Lily Bunny",
        category="main",
        species="rabbit",
        bio_data={
            "personality": ["curious", "kind", "brave"],
            "catchphrases": ["Let's learn together!", "Hi, I'm Lily!"],
        },
    )


@pytest.fixture
def sample_asset(lily_character):
    """Return a sample AssetModel linked to the lily_character fixture."""
    return AssetModel(
        character_id=lily_character.id,
        asset_type="reference",
        file_path="/tmp/test.png",
        scores={"character_consistency": 0.85},
        brand_score=0.85,
    )
