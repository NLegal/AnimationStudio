"""Phase 7 tests — Music Generation Backend Integration.

Covers the provider-agnostic core layer: request/status/result models,
the runtime-checkable backend protocol, typed exceptions, the category
-> music-parameter mapping anchored on the Phase 5 audio bible, the
stdlib transport seam, generate() orchestration, and the deterministic
mock backend. Everything runs fully offline — no network, no database,
no audio hardware (fake transports and monkeypatched seams only).
"""

import io
import os
import struct
import wave

import pytest
from pydantic import ValidationError

from src.audio_bible import AUDIO_NEGATIVE_BASE, category_negative
from src.audio_bible.prompts import build_music_prompt
from src.music_generation import (
    BackendUnavailable,
    GenerationFailed,
    MockBackend,
    MusicBackendError,
    MusicGenerationBackend,
    MusicRequest,
    MusicResult,
    MusicStatus,
    NotConfigured,
)
from src.music_generation.backends import (
    CATEGORY_MUSIC_PARAMS,
    CategoryMusicParams,
    build_music_request,
    music_negative_prompt,
    resolve_music_params,
)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _riff_header_fields(audio: bytes) -> dict:
    """Unpack the canonical 44-byte RIFF/WAVE header of mock audio bytes."""
    return {
        "magic": audio[0:4],
        "riff_size": struct.unpack("<I", audio[4:8])[0],
        "wave_tag": audio[8:12],
        "fmt_tag": audio[12:16],
        "fmt_chunk_size": struct.unpack("<I", audio[16:20])[0],
        "audio_format": struct.unpack("<H", audio[20:22])[0],
        "channels": struct.unpack("<H", audio[22:24])[0],
        "sample_rate": struct.unpack("<I", audio[24:28])[0],
        "byte_rate": struct.unpack("<I", audio[28:32])[0],
        "block_align": struct.unpack("<H", audio[32:34])[0],
        "bits_per_sample": struct.unpack("<H", audio[34:36])[0],
        "data_tag": audio[36:40],
        "data_size": struct.unpack("<I", audio[40:44])[0],
        "payload_size": len(audio) - 44,
    }


class TestMockBackend:
    """Tracer slice: deterministic end-to-end generation, fully offline."""

    def test_generate_end_to_end_deterministic(self):
        req = MusicRequest(category="Bedtime", topic="sleepy moon",
                           duration_s=120, seed=7)
        backend = MockBackend()

        r1 = backend.generate(req)
        r2 = backend.generate(req)

        assert r1.audio == r2.audio          # same seed => byte-identical
        assert r1.backend == "mock"
        assert r1.seed == 7                  # effective seed echoed back
        assert r1.job_id
        assert r1.format == "wav"
        assert r1.request.category == "Bedtime"

    def test_protocol_conformance_without_inheritance(self):
        backend = MockBackend()
        assert isinstance(backend, MusicGenerationBackend)
        # Structural conformance only — MockBackend must NOT inherit from
        # the protocol (deliberate divergence from generation_engine ABCs).
        # Note: issubclass() against a @runtime_checkable Protocol is itself
        # structural (member presence) on all supported Pythons, so the
        # no-inheritance guarantee is asserted via the MRO instead.
        assert MusicGenerationBackend not in MockBackend.__mro__

    def test_model_defaults_and_validation(self):
        req = MusicRequest(category="Bedtime", topic="sleepy moon", seed=7)
        assert req.duration_s == 60
        assert req.vocals == "female lead vocal, children's choir"
        assert req.lyrics_override is None
        assert req.tags == []

        status = MusicStatus(state="pending")
        assert status.progress == 0.0
        assert status.error is None

        result = MusicResult(request=req, audio=b"\x00\x01", job_id="j1",
                             backend="mock", seed=1)
        assert result.format == "wav"

        with pytest.raises(ValidationError):
            MusicStatus(state="exploded")     # invalid state string

    def test_fail_submit_raises_generation_failed(self):
        req = MusicRequest(category="Bedtime", seed=1)
        with pytest.raises(GenerationFailed):
            MockBackend(fail_submit=True).generate(req)

    def test_state_walk_across_polls(self):
        backend = MockBackend(states_before_complete=2)
        job_id = backend.submit(MusicRequest(category="Bedtime", seed=7))

        assert backend.poll(job_id).state == "pending"
        assert backend.poll(job_id).state == "running"

        final = backend.poll(job_id)
        assert final.state == "completed"
        assert final.progress == 1.0

    def test_exception_taxonomy(self):
        for exc_cls in (NotConfigured, BackendUnavailable, GenerationFailed):
            assert issubclass(exc_cls, MusicBackendError)
            assert issubclass(exc_cls, Exception)

    def test_wav_structure_is_valid(self):
        req = MusicRequest(category="Animals", topic="duck pond", seed=99)
        audio = MockBackend().generate(req).audio

        fields = _riff_header_fields(audio)
        assert fields["magic"] == b"RIFF"
        assert fields["wave_tag"] == b"WAVE"
        assert fields["fmt_tag"] == b"fmt "
        assert fields["fmt_chunk_size"] == 16
        assert fields["audio_format"] == 1           # PCM
        assert fields["channels"] == 1               # mono
        assert fields["sample_rate"] == 8000         # 8 kHz
        assert fields["bits_per_sample"] == 16
        assert fields["byte_rate"] == 8000 * 2
        assert fields["block_align"] == 2
        assert fields["data_tag"] == b"data"
        assert fields["riff_size"] == len(audio) - 8
        assert fields["data_size"] == fields["payload_size"]

        with wave.open(io.BytesIO(audio)) as handle:  # parses as valid WAV
            assert handle.getnchannels() == 1
            assert handle.getsampwidth() == 2
            assert handle.getframerate() == 8000
            assert handle.getnframes() > 0

    def test_different_seeds_produce_different_bytes(self):
        req_a = MusicRequest(category="Colors", seed=1)
        req_b = MusicRequest(category="Colors", seed=2)
        audio_a = MockBackend().generate(req_a).audio
        audio_b = MockBackend().generate(req_b).audio
        assert audio_a != audio_b

    def test_effective_seed_chain(self):
        # request.seed wins, then constructor seed, then 0.
        assert MockBackend(seed=5).generate(
            MusicRequest(category="Numbers")).seed == 5
        assert MockBackend().generate(
            MusicRequest(category="Numbers")).seed == 0


class TestCategoryMapping:
    """Golden-value assertions on the LOCKED RESEARCH §3 table.

    Style mirrors tests/test_audio_bible.py::TestMusicBrief.
    """

    def test_bedtime_golden_values(self):
        params = resolve_music_params("Bedtime")
        assert params.bpm == 66
        assert params.key_scale == "F major"
        assert params.time_signature == "3/4"
        assert params.duration_s == 120
        assert params.lyric_structure.startswith("[instrumental intro]")
        assert params.caption_keyword == "lullaby"

    def test_all_category_rows_match_research_table(self):
        expected = {
            "Alphabet": (110, "C major", "4/4",
                         "[verse][chorus][verse][chorus]", "alphabet", 75),
            "Numbers": (116, "D major", "4/4",
                        "[verse][chorus][verse][chorus]", "counting", 75),
            "Colors": (108, "G major", "4/4",
                       "[verse][chorus][bridge][chorus]", "colors", 60),
            "Animals": (120, "C major", "4/4",
                        "[verse][chorus][verse][chorus]", "animal", 80),
        }
        for category, (bpm, key_scale, time_signature,
                       lyric_structure, caption_keyword, duration_s) in expected.items():
            params = resolve_music_params(category)
            label = f"{category}: "
            assert params.bpm == bpm, label + "bpm"
            assert params.key_scale == key_scale, label + "key"
            assert params.time_signature == time_signature, label + "time signature"
            assert params.lyric_structure == lyric_structure, label + "scaffold"
            assert params.caption_keyword == caption_keyword, label + "keyword"
            assert params.duration_s == duration_s, label + "duration"

    def test_table_holds_exactly_five_named_rows(self):
        assert set(CATEGORY_MUSIC_PARAMS) == {
            "Alphabet", "Numbers", "Colors", "Animals", "Bedtime",
        }

    def test_case_insensitive_lookup(self):
        assert resolve_music_params("bedtime") == resolve_music_params("Bedtime")
        assert resolve_music_params(" BEDTIME ") == resolve_music_params("Bedtime")
        assert isinstance(resolve_music_params("BeDtImE"), CategoryMusicParams)

    def test_unknown_category_falls_back_to_generic_row(self):
        params = resolve_music_params("Spaceship")
        assert params.bpm == 110
        assert params.key_scale == "C major"
        assert params.time_signature == "4/4"
        assert params.duration_s == 60
        assert params.lyric_structure == "[verse][chorus][verse][chorus]"
        assert params.caption_keyword == "spaceship"   # slug-derived

    def test_resolved_rows_are_copies_not_table_cells(self):
        # Mutating a resolved row must never corrupt the shared table.
        params = resolve_music_params("Alphabet")
        params.bpm = 999
        assert resolve_music_params("Alphabet").bpm == 110

    def test_build_music_request_resolves_duration_and_seed(self):
        request = build_music_request(category="Bedtime",
                                      topic="sleepy moon", seed=42)
        assert isinstance(request, MusicRequest)
        assert request.category == "Bedtime"
        assert request.topic == "sleepy moon"
        assert request.duration_s == 120           # Bedtime pinned at 120 s
        assert request.seed == 42
        assert request.vocals == "female lead vocal, children's choir"

    def test_build_music_request_explicit_duration_overrides_category(self):
        request = build_music_request(category="Bedtime", topic="moon",
                                      seed=1, duration_s=90)
        assert request.duration_s == 90            # explicit wins over 120

    def test_build_music_request_generic_duration_for_unknown(self):
        request = build_music_request(category="Spaceship", seed=2)
        assert request.duration_s == 60            # generic fallback default

    def test_caption_property_via_bible_builder(self):
        for category in ("Alphabet", "Numbers", "Colors", "Animals", "Bedtime"):
            params = resolve_music_params(category)
            caption = build_music_prompt(category, topic="test topic")
            assert len(caption) <= 512, category
            assert params.caption_keyword in caption.lower(), category

    def test_music_negative_prompt_delegates_to_bible(self):
        negative = music_negative_prompt("Bedtime")
        assert negative == category_negative("Bedtime", include_base=True)
        assert AUDIO_NEGATIVE_BASE in negative
