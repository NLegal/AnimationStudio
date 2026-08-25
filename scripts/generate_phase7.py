#!/usr/bin/env python3
"""Phase 7 — Music Generation Backend Integration single-song CLI.

Assembles a bible-conformant music request for one song category/topic,
prints it (--dry-run, provably zero network), or generates the song
through the selected src.music_generation backend (ace-step | suno |
mock) writing the WAV under --out.

Reproduction (offline dry-run — assembles the request with zero network):
    python scripts/generate_phase7.py --dry-run --category Bedtime --topic "sleepy moon"

Reproduction (LIVE single-song manual smoke — requires a local ACE-Step
service; CI and the pytest suite NEVER require it):
    python scripts/generate_phase7.py --backend ace-step --category Bedtime --topic "sleepy moon"
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.music_generation import MusicBackendError, build_music_request, get_backend


def _slugify(text: str) -> str:
    """Lowercase slug: non-alphanumeric runs collapse to single hyphens."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "song"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        default=os.environ.get("MUSIC_BACKEND", "mock"),
        help="Music backend to use: ace-step, suno, or mock "
             "(default: MUSIC_BACKEND env var, falling back to 'mock')",
    )
    parser.add_argument(
        "--category", default="Bedtime",
        help="Song category (Alphabet, Numbers, Colors, Animals, Bedtime)",
    )
    parser.add_argument("--topic", default="", help="Song topic phrase")
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Determinism seed; omit to let the backend choose its default",
    )
    parser.add_argument(
        "--out", default="Audio/Music",
        help="Output directory for the generated audio file",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the resolved request JSON and exit — zero network, "
             "no backend construction",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.dry_run:
        # Constraint C3: request assembly ONLY — no backend construction,
        # no transport touch. TestPhase7Cli enforces this with fail-loud
        # guards installed on every transport seam.
        request = build_music_request(args.category, args.topic,
                                      seed=args.seed)
        print(json.dumps(request.model_dump(), indent=2))
        return 0

    try:
        backend = get_backend(args.backend)
        request = build_music_request(args.category, args.topic,
                                      seed=args.seed)
        result = backend.generate(request)
    except MusicBackendError as exc:
        print(f"Music generation failed: {exc}", file=sys.stderr)
        return 1

    out_dir = args.out
    if not os.path.isabs(out_dir):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_dir = os.path.join(root, out_dir)
    os.makedirs(out_dir, exist_ok=True)

    topic_slug = _slugify(request.topic) if request.topic else "song"
    filename = (f"{request.category.lower()}-{topic_slug}-"
                f"{result.seed}.{result.format}")
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "wb") as fh:
        fh.write(result.audio)

    print(f"Backend:     {result.backend}")
    print(f"Job id:      {result.job_id}")
    print(f"Bytes:       {len(result.audio)}")
    print(f"Written:     {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
