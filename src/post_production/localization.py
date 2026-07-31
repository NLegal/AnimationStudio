from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LocalizationPackage:
    language: str = ""
    audio_track: str = ""
    subtitle_file: str = ""
    title: str = ""
    description: str = ""
    thumbnail: str = ""
    graphics: dict[str, str] = field(default_factory=dict)


class LocalizationEngine:
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "pt": "Portuguese",
        "hi": "Hindi",
        "ar": "Arabic",
    }

    def list_languages(self) -> dict[str, str]:
        return dict(self.SUPPORTED_LANGUAGES)

    def is_supported(self, language_code: str) -> bool:
        return language_code in self.SUPPORTED_LANGUAGES

    def create_package(self, language: str, title: str = "") -> Optional[LocalizationPackage]:
        if not self.is_supported(language):
            return None
        return LocalizationPackage(
            language=language,
            title=title,
            audio_track=f"audio_{language}",
            subtitle_file=f"subtitles_{language}",
        )

    def localize_text(self, text: str, language: str) -> str:
        if not self.is_supported(language):
            return text
        return f"[{language}] {text}"
