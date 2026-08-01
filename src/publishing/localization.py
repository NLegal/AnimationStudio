from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class LocalizedPublication:
    language: str = ""
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    thumbnail: str = ""
    subtitle_file: str = ""
    audio_track: str = ""
    end_screen: str = ""


class PublishingLocalizationEngine:
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

    def create_package(
        self,
        episode_id: str,
        language: str,
        title: str = "",
        description: str = "",
        tags: list[str] | None = None,
        thumbnail: str = "",
    ) -> LocalizedPublication | None:
        if not self.is_supported(language):
            return None
        return LocalizedPublication(
            language=language,
            title=title or f"[{language}] {episode_id}",
            description=description,
            tags=tags or [],
            thumbnail=thumbnail,
            subtitle_file=f"{episode_id}.{language}.srt",
            audio_track=f"{episode_id}.{language}.m4a",
            end_screen=f"end_screen_{language}",
        )

    def localize_title(self, title: str, language: str) -> str:
        if not self.is_supported(language):
            return title
        return f"[{language}] {title}"

    def localize_description(self, description: str, language: str) -> str:
        if not self.is_supported(language):
            return description
        return f"{description}\n\n(Translated to {self.SUPPORTED_LANGUAGES[language]})"
