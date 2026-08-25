#!/usr/bin/env python3
"""Phase 5 — Audio Bible & Music Production System verification + report.

Verifies the machine-readable audio bible against the `Audio/` markdown docs,
resolves every song category and voice profile into a brief, builds a full
episode AudioPlan, and writes `PHASE5_REPORT.md`.

Generation mode (--generate) batches music requests through the Phase 7
backend layer, writes WAV/MP3 files plus a crash-safe manifest.json, and
resumes interrupted batches by request signature.

Reproduction (report mode — zero network):
    python scripts/generate_phase5.py

Reproduction (generation mode — offline mock):
    python scripts/generate_phase5.py --generate --backend mock --out Audio/Music

Live smoke (requires local ACE-Step service — see Audio/Music/README.md):
    python scripts/generate_phase5.py --generate --backend ace-step --category Bedtime
"""

import argparse
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio_bible import AudioBible, AudioProductionSystem, quality_checklist

# Imported at module level so tests can monkeypatch it (Phase 8 plan requirement).
from src.music_generation import MusicBackendError, build_music_request, get_backend  # noqa: E402


# =================================================================== #
# Generation-mode constants and helpers                                #
# =================================================================== #

BACKEND_ALIASES = {
    "acestep": "ace-step",
    "ace-step": "ace-step",
    "suno": "suno",
    "mock": "mock",
}


def _slug(text: str) -> str:
    """Lowercase slug: non-alphanumeric chars become hyphens; strip edges."""
    slug = "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")
    return slug or "song"


def song_filename(category: str, topic: str, seed, fmt: str = "wav") -> str:
    """Build ``<cat-slug>-<topic-slug-or-song>-<seed>.<fmt>``."""
    cat_slug = _slug(category)
    topic_slug = _slug(topic) or "song"
    effective_seed = seed if seed is not None else 0
    return f"{cat_slug}-{topic_slug}-{effective_seed}.{fmt}"


def parse_categories(value: str) -> list[str]:
    """Split a comma-separated category string, strip whitespace, drop empties."""
    tokens = [t.strip() for t in value.split(",") if t.strip()]
    if not tokens:
        return []
    return tokens


def now_iso() -> str:
    """Return a timezone-aware UTC ISO-8601 timestamp string."""
    return datetime.now(timezone.utc).isoformat()


# =================================================================== #
# Manifest helpers (module-level for plan 08-02 import)                #
# =================================================================== #

_MANIFEST_VERSION = 1
_MANIFEST_KEYS = {
    "file", "category", "topic", "seed", "backend", "format",
    "bytes", "duration_s", "bpm", "key_scale", "time_signature",
    "job_id", "generated_at",
}


def load_manifest(path: str) -> dict:
    """Load manifest.json; missing or malformed → fresh v1 structure.

    A leftover .tmp file is never read. A truncated/corrupt manifest is
    treated as fresh with a one-line warning to stderr (resume survives).
    """
    if not os.path.exists(path):
        return {"version": _MANIFEST_VERSION, "songs": []}
    try:
        data = json.loads(open(path, encoding="utf-8").read())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"WARNING: manifest corrupted at {path}, rebuilding ({exc})",
              file=sys.stderr)
        return {"version": _MANIFEST_VERSION, "songs": []}
    if not isinstance(data, dict):
        print(f"WARNING: manifest at {path} is not an object, rebuilding",
              file=sys.stderr)
        return {"version": _MANIFEST_VERSION, "songs": []}
    data.setdefault("version", _MANIFEST_VERSION)
    data.setdefault("songs", [])
    return data


def find_entry(manifest: dict, fname: str) -> dict | None:
    """Linear scan for an entry whose 'file' matches *fname*."""
    for entry in manifest.get("songs", []):
        if entry.get("file") == fname:
            return entry
    return None


def entry_matches(entry: dict, sig: dict) -> bool:
    """Check backend / topic / duration_s equality (pure dict comparison)."""
    return (
        entry.get("backend") == sig.get("backend")
        and entry.get("topic") == sig.get("topic")
        and entry.get("duration_s") == sig.get("duration_s")
    )


def upsert_entry(manifest: dict, entry: dict) -> None:
    """Replace an existing entry with same 'file' key, or append."""
    songs = manifest.setdefault("songs", [])
    fname = entry.get("file")
    for i, existing in enumerate(songs):
        if existing.get("file") == fname:
            songs[i] = entry
            return
    songs.append(entry)


def atomic_write_manifest(path: str, manifest: dict) -> None:
    """Write manifest.json atomically (temp file + os.replace).

    The temp file lives in the SAME directory as the target so that
    os.replace works across devices (Pitfall 6).
    """
    dir_name = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(suffix=".tmp", dir=dir_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(manifest, indent=2) + "\n")
        os.replace(tmp_path, path)
    except BaseException:
        # Clean up temp on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# =================================================================== #
# Song generation orchestrator                                         #
# =================================================================== #

def generate_songs(
    backend_name: str | None,
    categories: list[str],
    topic_fn,
    out_dir: str,
    *,
    seed=None,
    duration_s=None,
    force=False,
) -> list[tuple[str, str]]:
    """Batch-generate songs across *categories* through the named backend.

    Returns a list of ``(category, error_message)`` failures.  Empty list
    means all songs succeeded.
    """
    name = BACKEND_ALIASES.get((backend_name or "").lower(), backend_name or "mock")
    backend = get_backend(name)

    os.makedirs(out_dir, exist_ok=True)

    manifest_path = os.path.join(out_dir, "manifest.json")
    manifest = load_manifest(manifest_path)

    failures: list[tuple[str, str]] = []

    for category in categories:
        topic = topic_fn(category)
        request = build_music_request(
            category, topic, seed=seed, duration_s=duration_s,
        )
        fname = song_filename(
            category, topic, request.seed or 0,
            "wav",
        )

        # Resume-skip logic: skip when signature matches AND file exists
        if not force:
            existing = find_entry(manifest, fname)
            if existing is not None and entry_matches(
                existing,
                {"backend": name, "topic": request.topic,
                 "duration_s": request.duration_s},
            ):
                fpath = os.path.join(out_dir, fname)
                if (
                    os.path.exists(fpath)
                    and os.path.getsize(fpath) == existing.get("bytes", 0)
                    and existing.get("bytes", 0) > 0
                ):
                    continue  # skipped — already done

        try:
            result = backend.generate(request)
        except MusicBackendError as exc:
            failures.append((category, str(exc)))
            continue

        fpath = os.path.join(out_dir, fname)
        with open(fpath, "wb") as fh:
            fh.write(result.audio)

        entry = {
            "file": fname,
            "category": category,
            "topic": request.topic,
            "seed": result.seed,
            "backend": result.backend,
            "format": result.format,
            "bytes": len(result.audio),
            "duration_s": request.duration_s,
            "bpm": 0,
            "key_scale": "",
            "time_signature": "",
            "job_id": result.job_id,
            "generated_at": now_iso(),
        }

        # Fill in the music params from the resolved request
        from src.music_generation.backends import resolve_music_params
        params = resolve_music_params(category)
        entry["bpm"] = params.bpm
        entry["key_scale"] = params.key_scale
        entry["time_signature"] = params.time_signature

        upsert_entry(manifest, entry)
        atomic_write_manifest(manifest_path, manifest)

    return failures


# =================================================================== #
# Report mode (unchanged)                                              #
# =================================================================== #

def _sample_episode(system: AudioProductionSystem):
    return system.plan_episode(
        episode_id="S01E01",
        title="The Alphabet Garden",
        dialogue_lines=[
            ("Lily Bunny", "A is for apple! B is for ball!", "happy"),
            ("Ben Bear", "Yum yum, apples!", "excited"),
            ("Daisy Duck", "Quack quack, let's learn!", "cheerful"),
        ],
        songs=[
            ("Alphabet", "letter sounds", "Short"),
            ("Dance Songs", "moving and dancing", "Standard"),
            ("Bedtime", "sleepy time", "Short"),
        ],
        scene="Sunny Garden Playground",
    )


# =================================================================== #
# CLI + main                                                           #
# =================================================================== #

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", default="Audio",
                        help="Directory containing the Audio/ markdown bibles")
    parser.add_argument("--out", default=None,
                        help="Report path (report mode) or music output "
                             "directory (generation mode, default Audio/Music)")

    # Generation-mode flags
    parser.add_argument("--generate", action="store_true",
                        help="Generate songs (default: verify + write report)")
    parser.add_argument("--backend", default=None,
                        help="Music backend: acestep | ace-step | suno | mock "
                             "(default: MUSIC_BACKEND env, else mock)")
    parser.add_argument("--category", action="append", default=None,
                        help="Song category to generate (repeatable or "
                             "comma-separated; default: all 24 categories)")
    parser.add_argument("--topic", default="",
                        help="Song topic (default: '<category> fun')")
    parser.add_argument("--seed", type=int, default=None,
                        help="Determinism seed (optional)")
    parser.add_argument("--duration-s", type=int, default=None,
                        help="Override duration in seconds (10-600; "
                             "default: LOCKED category params)")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate even when manifest entry matches")

    args = parser.parse_args(argv)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ----- Generation mode ----- #
    if args.generate:
        if args.duration_s is not None and not (10 <= args.duration_s <= 600):
            parser.error("--duration-s must be between 10 and 600")

        bible = AudioBible()
        all_categories = bible.list_song_categories()

        # Resolve --category
        if args.category is None or args.category == ["all"]:
            categories = list(all_categories)
        else:
            # Flatten comma-separated + repeatable forms
            raw: list[str] = []
            for cat_str in args.category:
                raw.extend(parse_categories(cat_str))

            # Validate each category case-insensitively
            valid_map = {c.lower(): c for c in all_categories}
            categories = []
            for token in raw:
                canonical = valid_map.get(token.lower())
                if canonical is None:
                    parser.error(
                        f"Unknown category {token!r}. "
                        f"Valid categories: {', '.join(all_categories)}"
                    )
                categories.append(canonical)

        # Resolve backend name and validate
        raw_backend = args.backend or os.environ.get("MUSIC_BACKEND", "mock")
        resolved_backend = BACKEND_ALIASES.get(raw_backend.lower(), raw_backend)
        valid_backends = set(BACKEND_ALIASES.values())
        if resolved_backend not in valid_backends:
            parser.error(
                f"Unknown backend {raw_backend!r}. "
                f"Valid backends: {', '.join(sorted(valid_backends))}"
            )

        # Topic function
        if args.topic:
            topic_fn = lambda c: args.topic
        else:
            topic_fn = lambda c: f"{c.lower()} fun"

        # Output directory
        out_dir = args.out
        if out_dir is None:
            out_dir = os.path.join(root, "Audio", "Music")
        elif not os.path.isabs(out_dir):
            out_dir = os.path.join(root, out_dir)

        failures = generate_songs(
            resolved_backend, categories, topic_fn, out_dir,
            seed=args.seed, duration_s=args.duration_s, force=args.force,
        )

        # Count from manifest
        manifest_path = os.path.join(out_dir, "manifest.json")
        manifest = load_manifest(manifest_path)
        total = len(manifest.get("songs", []))
        failed_count = len(failures)
        skipped = max(0, total - (len(categories) - failed_count))

        # Summary
        print(f"Generated: {total - skipped - failed_count}")
        print(f"Skipped:   {skipped}")
        print(f"Failed:    {failed_count}")

        for cat, reason in failures:
            print(f"FAILED {cat}: {reason}", file=sys.stderr)

        return 0 if not failures else 1

    # ----- Report mode (unchanged — C4) ----- #
    out_path = args.out
    if out_path is None:
        out_path = "PHASE5_REPORT.md"

    docs_dir = args.docs_dir
    if not os.path.isabs(docs_dir):
        docs_dir = os.path.join(root, docs_dir)

    bible = AudioBible()
    system = AudioProductionSystem()

    doc_report = bible.check_docs(docs_dir)

    music_briefs = [
        bible.build_music_brief(category=c, topic=f"{c.lower()} fun",
                                duration_label="Standard")
        for c in bible.list_song_categories()
    ]
    voice_briefs = [
        bible.build_voice_brief(name) for name in bible.list_voice_profiles()
    ]

    plan = _sample_episode(system)
    episode_validation = system.validate_episode(plan)

    lines = [
        "# Phase 5 Report — Audio Bible & Music Production System",
        "",
        f"> Generated by `scripts/generate_phase5.py` on docs at `{docs_dir}`.",
        "",
        "## Doc <-> Code Consistency",
        "",
        f"- **Facts checked:** {doc_report.to_dict()['facts_checked']}",
        f"- **Facts passed:** {doc_report.to_dict()['facts_passed']}",
        f"- **Overall:** {'PASS' if doc_report.passed else 'FAIL'}",
        f"- **Missing files:** {', '.join(doc_report.missing_files) or 'none'}",
        f"- **Failed facts:** {', '.join(doc_report.to_dict()['facts_failed']) or 'none'}",
        "",
        "## Song Library (all 24 categories, Standard duration)",
        "",
        "| Category | Tempo | Duration | Structure |",
        "|----------|-------|----------|-----------|",
    ]
    for brief in music_briefs:
        lines.append(
            f"| {brief.category} | {brief.tempo} BPM | {brief.duration_label} "
            f"({brief.duration_seconds}s) | {len(brief.structure)} sections |"
        )

    lines += [
        "",
        "## Voice Profiles (11)",
        "",
        "| Character | Role | Pitch | Energy | TTS Engine |",
        "|-----------|------|-------|--------|------------|",
    ]
    for brief in voice_briefs:
        lines.append(
            f"| {brief.character} | {brief.role} | {brief.pitch} | "
            f"{brief.energy} | {brief.tts_engine} |"
        )

    lines += [
        "",
        "## Episode Audio Plan (sample: S01E01 — The Alphabet Garden)",
        "",
        f"- **Passed:** {'yes' if plan.passed else 'no'}",
        f"- **Narration:** {plan.narration.character if plan.narration else 'none'}",
        f"- **Dialogue clips:** {len(plan.dialogue)} ({plan.total_dialogue_seconds:.1f}s total)",
        f"- **Songs:** {len(plan.songs)} ({plan.total_song_seconds}s total)",
        f"- **SFX:** {', '.join(plan.sfx)}",
        f"- **Foley:** {', '.join(plan.foley)}",
        f"- **Ambience:** {', '.join(plan.ambience)}",
        f"- **Mix rules:** {len(plan.mix_rules)} applied",
        f"- **Master rules:** {len(plan.master_rules)} applied",
        f"- **Localization:** {', '.join(plan.localization)}",
        "",
        "| # | Speaker / Song | Type | Validation |",
        "|---|----------------|------|-----------|",
    ]
    for i, clip in enumerate(plan.dialogue, start=1):
        passed = "PASS" if clip.validation.get("passed") else "FAIL"
        phonemes = clip.lip_sync.total_phonemes() if clip.lip_sync else 0
        lines.append(
            f"| {i} | {clip.speaker}: \"{clip.text[:40]}\" | dialogue "
            f"({phonemes} phonemes) | {passed} |"
        )
    for i, entry in enumerate(plan.songs, start=1):
        passed = "PASS" if entry.validation.get("passed") else "FAIL"
        lines.append(
            f"| {i + len(plan.dialogue)} | {entry.category}: {entry.topic[:40]} "
            f"| song ({entry.brief.duration_seconds}s) | {passed} |"
        )
    lines += [
        "",
        f"- **Episode validation:** {episode_validation['violations'] or 'no violations'}; "
        f"{episode_validation['warnings'] or 'no warnings'}",
        "",
        "## Library Inventory",
        "",
        f"- Song categories: {len(bible.list_song_categories())} | "
        f"Sections: {len(bible.list_song_sections())} | Durations: {len(bible.list_durations())}",
        f"- Voice profiles: {len(bible.list_voice_profiles())} | "
        f"Pronunciations: {len(bible.list_pronunciations())}",
        f"- Sound effects: {len(bible.list_sound_effects())} | "
        f"Foley: {len(bible.list_foley_sounds())} | Ambience: {len(bible.list_ambience())}",
        f"- Mixing rules: {len(bible.mixing_rules())} | "
        f"Mastering rules: {len(bible.mastering_rules())} | "
        f"Lip-sync standards: {len(bible.lipsync_standards())} | "
        f"Localization standards: {len(bible.localization_standards())}",
        "",
        "## Quality Checklist",
        "",
    ]
    lines += [f"- [ ] {check}" for check in quality_checklist()]
    lines += ["", "## Summary", ""]
    lines.append(
        f"- **Audio standards encoded:** {len(bible.list_song_categories())} song "
        f"categories, {len(bible.list_voice_profiles())} voice profiles, "
        f"{len(bible.list_sound_effects())} SFX, {len(bible.list_foley_sounds())} foley, "
        f"{len(bible.list_ambience())} ambient beds, {len(bible.list_pronunciations())} pronunciations."
    )
    lines.append(
        f"- **Doc consistency:** {doc_report.to_dict()['facts_passed']}/"
        f"{doc_report.to_dict()['facts_checked']} facts verified against the markdown bibles."
    )
    lines.append(
        f"- **Production system:** episode '{plan.episode_id}' assembled with "
        f"{len(plan.dialogue)} dialogue clips (phoneme lip-sync at 24 fps) and "
        f"{len(plan.songs)} songs; {'passes' if plan.passed else 'fails'} validation."
    )

    if not os.path.isabs(out_path):
        out_path = os.path.join(root, out_path)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Doc consistency: {doc_report.to_dict()['facts_passed']}/"
          f"{doc_report.to_dict()['facts_checked']} facts passed")
    print(f"Episode plan:    {plan.episode_id} -> "
          f"{len(plan.dialogue)} dialogue clips, {len(plan.songs)} songs, "
          f"passed={plan.passed}")
    print(f"Report written:  {out_path}")
    return 0 if doc_report.passed and plan.passed else 1


if __name__ == "__main__":
    sys.exit(main())
