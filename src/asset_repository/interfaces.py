"""Repository abstractions for character and asset storage.

Defines the ABCs that all storage backends must implement (D-14).
SQLite is the initial implementation; PostgreSQL migration is supported
by the interface.
"""

from abc import ABC, abstractmethod
from typing import Optional


class CharacterRepository(ABC):
    """Abstract repository for character records."""

    @abstractmethod
    async def save_character(self, char: "CharacterModel") -> str:
        ...

    @abstractmethod
    async def get_character(self, character_id: str) -> Optional["CharacterModel"]:
        ...

    @abstractmethod
    async def find_character_by_name(self, name: str) -> Optional["CharacterModel"]:
        ...

    @abstractmethod
    async def list_characters(self) -> list["CharacterModel"]:
        ...


class AssetRepository(ABC):
    """Abstract repository for asset (image) records."""

    @abstractmethod
    async def save(self, record: "AssetModel") -> str:
        ...

    @abstractmethod
    async def get(self, asset_id: str) -> Optional["AssetModel"]:
        ...

    @abstractmethod
    async def update_state(self, asset_id: str, new_state: str) -> None:
        ...

    @abstractmethod
    async def find_by_character(
        self, character_id: str, asset_type: Optional[str] = None
    ) -> list["AssetModel"]:
        ...

    @abstractmethod
    async def find_approved(
        self, character_id: str, asset_type: str
    ) -> list["AssetModel"]:
        ...
