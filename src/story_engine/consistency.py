from __future__ import annotations
import os
import re
from typing import List

from src.story_engine.models import DocFact, DocConsistencyReport


STORY_QUALITY_CHECKS: List[str] = [
    "One clear educational objective",
    "One primary theme",
    "Appropriate character count",
    "Correct locations",
    "Correct assets",
    "Positive emotional arc",
    "Audience participation included",
    "Vocabulary matches target age",
    "Safe conflict",
    "Positive resolution",
    "Song opportunity identified",
    "Continuity maintained",
    "Variety maintained across recent episodes",
    "Validation passed",
]


def quality_checklist() -> List[str]:
    """Return the Phase 6 story quality checklist."""
    return list(STORY_QUALITY_CHECKS)


def check_docs(docs_dir: str) -> DocConsistencyReport:
    """Verify the StoryEngine/ markdown guides still contain the standards we encode.

    Each fact pairs a file with a token that must appear in that file.
    This keeps the code in sync with the human-readable story engine guides.
    """
    facts = [
        DocFact("StoryEngine/STORY_ENGINE_GUIDE.md", "Studio brand", "Little Learning Town"),
        DocFact("StoryEngine/Curriculum/CURRICULUM_GUIDE.md", "Balanced coverage",
                "Balanced Educational Coverage"),
        DocFact("StoryEngine/Curriculum/CURRICULUM_GUIDE.md", "Geography area", "Geography"),
        DocFact("StoryEngine/Themes/THEMES_GUIDE.md", "Theme library", "All Themes"),
        DocFact("StoryEngine/LearningObjectives/OBJECTIVES_GUIDE.md", "One lesson rule",
                "one primary concept"),
        DocFact("StoryEngine/StoryGrammar/GRAMMAR_GUIDE.md", "Grammar count",
                "14 Grammar Patterns"),
        DocFact("StoryEngine/StoryGrammar/GRAMMAR_GUIDE.md", "Solve a Puzzle", "Solve a Puzzle"),
        DocFact("StoryEngine/NarrativeTemplates/NARRATIVE_TEMPLATES.md", "Standard framework",
                "Standard Story Framework"),
        DocFact("StoryEngine/Dialogue/DIALOGUE_GUIDE.md", "Sentence rule", "Short sentences"),
        DocFact("StoryEngine/Dialogue/DIALOGUE_GUIDE.md", "No sarcasm", "No sarcasm"),
        DocFact("StoryEngine/Interaction/INTERACTION_GUIDE.md", "Count Along", "Count Along"),
        DocFact("StoryEngine/Emotions/EMOTIONS_GUIDE.md", "Positive arc",
                "ends happier than it began"),
        DocFact("StoryEngine/Humor/HUMOR_GUIDE.md", "Never mock", "Never mock"),
        DocFact("StoryEngine/Songs/SONG_GUIDE.md", "Placement options",
                "Song Placement Options"),
        DocFact("StoryEngine/Continuity/CONTINUITY_GUIDE.md", "Engine memory",
                "What the Engine Remembers"),
        DocFact("StoryEngine/Validation/VALIDATION_GUIDE.md", "Quality gate", "quality gate"),
        DocFact("StoryEngine/Series/SERIES_PLANNER.md", "Season episodes", "26 episodes"),
        DocFact("StoryEngine/Seasons/SEASONS_GUIDE.md", "Annual calendar", "Annual Calendar"),
        DocFact("StoryEngine/Episodes/EXAMPLE_EPISODE.md", "Example episode",
                "Lily Bunny Learns to Share"),
        DocFact("StoryEngine/Metadata/METADATA_GUIDE.md", "Episode id", "S01E014"),
        DocFact("StoryEngine/PromptTemplates/prompt-templates.md", "Planning prompt",
                "Planning Prompt Template"),
    ]

    report = DocConsistencyReport()
    base = os.path.abspath(docs_dir)
    strip_story_prefix = os.path.basename(base) == "StoryEngine"

    for fact in facts:
        rel = fact.file
        if strip_story_prefix and rel.startswith("StoryEngine/"):
            rel = rel[len("StoryEngine/"):]
        path = os.path.join(base, rel)
        if not os.path.exists(path):
            report.missing_files.append(fact.file)
            continue
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        norm_content = re.sub(r"\s+", " ", content)
        if fact.expected in norm_content:
            fact.found = True
            fact.detail = f"'{fact.expected}' present in {fact.file}"
        else:
            fact.detail = f"'{fact.expected}' NOT found in {fact.file}"
        report.facts.append(fact)

    return report
