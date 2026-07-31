from datetime import datetime

from .models import KeywordEntry, TitleVariant


class MetadataEngine:
    def generate(
        self,
        episode_id: str,
        title: str = "",
        series: str = "",
        episode_number: int = 1,
        learning_objective: str = "",
        age_group: str = "2-5",
        language: str = "en",
        duration_seconds: float = 0.0,
        characters: list[str] | None = None,
        curriculum_tags: list[str] | None = None,
        keywords: list[str] | None = None,
    ) -> dict:
        return {
            "episode_id": episode_id,
            "title": title,
            "series": series,
            "episode_number": episode_number,
            "learning_objective": learning_objective,
            "age_group": age_group,
            "language": language,
            "duration_seconds": duration_seconds,
            "characters": characters or [],
            "curriculum_tags": curriculum_tags or [],
            "keywords": keywords or [],
            "hashtags": self._build_hashtags(curriculum_tags, keywords),
            "copyright": f"© {datetime.now().year} AI Nursery Studio",
            "license": "All rights reserved",
            "generated_at": datetime.now().isoformat(),
        }

    def _build_hashtags(self, curriculum_tags: list[str] | None, keywords: list[str] | None) -> list[str]:
        tags = (curriculum_tags or []) + (keywords or [])
        seen: set[str] = set()
        hashtags: list[str] = []
        for tag in tags:
            cleaned = "".join(c for c in tag if c.isalnum()).lower()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                hashtags.append(f"#{cleaned}")
        return hashtags

    def validate_completeness(self, metadata: dict) -> dict:
        checks: dict[str, bool] = {
            "has_episode_id": bool(metadata.get("episode_id")),
            "has_title": bool(metadata.get("title")),
            "has_learning_objective": bool(metadata.get("learning_objective")),
            "has_age_group": bool(metadata.get("age_group")),
            "has_language": bool(metadata.get("language")),
            "has_keywords": len(metadata.get("keywords") or []) > 0,
            "has_copyright": bool(metadata.get("copyright")),
            "has_generated_at": bool(metadata.get("generated_at")),
        }
        errors = [k for k, v in checks.items() if not v]
        score = (sum(1 for v in checks.values() if v) / len(checks)) * 100.0 if checks else 0.0
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
            "score": round(score, 1),
        }


class TitleGenerator:
    TITLE_TEMPLATES = {
        "primary": "Learn {topic} with {character}!",
        "seo": "Learn {topic} for Kids | {age_group} Preschool {format}",
        "short": "{topic} Song!",
        "educational": "Let's Learn {topic} | {objective}",
    }

    def generate_titles(
        self,
        topic: str,
        character: str = "Lily Bunny",
        age_group: str = "2-5",
        objective: str = "",
        format: str = "Learning Video",
    ) -> list[TitleVariant]:
        titles = [
            TitleVariant(
                title=self.TITLE_TEMPLATES["primary"].format(topic=topic, character=character),
                kind="primary",
            ),
            TitleVariant(
                title=self.TITLE_TEMPLATES["seo"].format(
                    topic=topic, age_group=age_group, format=format,
                ),
                kind="seo",
            ),
            TitleVariant(
                title=self.TITLE_TEMPLATES["short"].format(topic=topic),
                kind="short",
            ),
            TitleVariant(
                title=self.TITLE_TEMPLATES["educational"].format(
                    topic=topic, objective=objective or "Preschool Learning",
                ),
                kind="educational",
            ),
        ]
        for variant in titles:
            variant.score = self.score_title(variant.title)
        return titles

    def score_title(self, title: str, target_length: int = 60) -> float:
        score = 0.0
        length = len(title)
        if length <= target_length:
            score += 40
        else:
            score += max(0, 40 - (length - target_length))
        words = title.lower().split()
        educational_terms = ["learn", "kids", "preschool", "song", "colors", "numbers", "alphabet"]
        keyword_matches = sum(1 for w in words if w in educational_terms)
        score += min(30, keyword_matches * 10)
        if words[0][0].isupper():
            score += 10
        if "!" in title:
            score += 10
        if any(c.isdigit() for c in title):
            score += 5
        return round(score, 1)

    def select_best(self, variants: list[TitleVariant]) -> TitleVariant:
        if not variants:
            return TitleVariant()
        return max(variants, key=lambda v: v.score)


class DescriptionEngine:
    TEMPLATE = (
        "{summary}\n\n"
        "🎓 Learning Objective: {objective}\n"
        "👧 Ages: {age_group}\n\n"
        "In this episode of {series}:\n{highlights}\n\n"
        "📚 About {studio}:\n{about}\n\n"
        "👍 Like, subscribe, and hit the bell for more {series} episodes!\n\n"
        "© {year} {studio}. All rights reserved."
    )

    def build_description(
        self,
        summary: str,
        objective: str,
        age_group: str = "2-5",
        series: str = "AI Nursery",
        studio: str = "AI Nursery Studio",
        about: str = "We create fun, safe, educational videos for young children.",
        highlights: list[str] | None = None,
        playlist_links: list[str] | None = None,
        website: str = "",
        social: str = "",
    ) -> str:
        bullet_highlights = "\n".join(f"• {h}" for h in (highlights or ["Join Lily on a fun learning adventure"]))
        description = self.TEMPLATE.format(
            summary=summary,
            objective=objective,
            age_group=age_group,
            series=series,
            highlights=bullet_highlights,
            studio=studio,
            about=about,
            year=datetime.now().year,
        )
        extras: list[str] = []
        if playlist_links:
            extras.append("🎬 Watch More:\n" + "\n".join(f"• {p}" for p in playlist_links))
        if website:
            extras.append(f"🌐 Website: {website}")
        if social:
            extras.append(f"📱 Social: {social}")
        if extras:
            description += "\n\n" + "\n\n".join(extras)
        return description.strip()

    def validate(self, description: str) -> dict:
        checks = {
            "has_content": len(description.strip()) > 0,
            "has_learning_objective": "Learning Objective" in description,
            "has_age_group": "Ages:" in description,
            "has_series": "In this episode of" in description,
            "has_call_to_action": "subscribe" in description.lower(),
            "has_copyright": "©" in description and "All rights reserved" in description,
        }
        errors = [k for k, v in checks.items() if not v]
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }


class KeywordEngine:
    DEFAULT_KEYWORDS: dict[str, list[str]] = {
        "general": ["kids", "toddlers", "preschool", "educational videos"],
        "colors": ["learn colors", "color songs", "primary colors"],
        "numbers": ["learn numbers", "counting songs", "1 to 10"],
        "alphabet": ["alphabet songs", "abc", "letter sounds"],
        "animals": ["animal sounds", "farm animals", "animal songs"],
        "nursery": ["nursery rhymes", "baby songs", "children songs"],
        "bedtime": ["bedtime stories", "lullabies", "good night songs"],
        "science": ["science for kids", "nature videos", "learning science"],
    }

    def __init__(self):
        self._library: dict[str, list[KeywordEntry]] = {
            category: [KeywordEntry(keyword=k, category=category) for k in keywords]
            for category, keywords in self.DEFAULT_KEYWORDS.items()
        }

    def suggest(self, topics: list[str], language: str = "en", limit: int = 10) -> list[str]:
        keywords: list[str] = []
        for topic in topics:
            topic_keywords = self._library.get(topic, [])
            keywords.extend(k.keyword for k in topic_keywords)
        if not keywords:
            keywords.extend(k.keyword for k in self._library["general"])
        seen: list[str] = []
        for k in keywords:
            if k not in seen:
                seen.append(k)
        return seen[:limit]

    def add_keyword(self, keyword: str, category: str = "general", weight: float = 1.0) -> None:
        if category not in self._library:
            self._library[category] = []
        entry = KeywordEntry(keyword=keyword, category=category, weight=weight)
        existing = [k for k in self._library[category] if k.keyword == keyword]
        if not existing:
            self._library[category].append(entry)

    def all_keywords(self) -> list[str]:
        result: list[str] = []
        for entries in self._library.values():
            result.extend(e.keyword for e in entries)
        return result

    def list_categories(self) -> list[str]:
        return list(self._library.keys())

    def keywords_for_category(self, category: str) -> list[str]:
        return [k.keyword for k in self._library.get(category, [])]
