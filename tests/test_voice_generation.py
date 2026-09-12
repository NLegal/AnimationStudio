"""Phase 5 Voice tests — Voice Generation Backend + bible wiring.

Covers the provider-agnostic voice layer, mirroring the music generation
tests: request/status/result models, the runtime-checkable backend
protocol, typed exceptions, ``build_voice_request`` bible-aware defaults,
engine-name resolution, the deterministic offline mock, the lazily-loaded
Kokoro surface (never requiring the ``kokoro`` package), the refusing
Piper/XTTS stubs, file persistence, and the AudioProductionSystem wiring
(``synth_voice`` / ``synth_plan_voices`` / ``music_request_for``).
Everything runs fully offline — no engine, no network, no audio hardware.
"""

import importlib.util
import io
import json
import os
import wave

import pytest
from pydantic import ValidationError

from src.audio_bible import AudioProductionSystem
from src.voice_generation import (
    DEFAULT_VOICE_CODE,
    MockBackend,
    NotConfigured,
    VoiceBackendError,
    VoiceRequest,
    VoiceResult,
    backend_for_engine,
    build_voice_request,
    get_backend,
    save_voice_result,
    voice_code_for_brief,
)
from src.voice_generation.backends import CHARACTER_VOICE_CODES
from src.voice_generation.piper import PiperBackend, PIPER_NO_API_MESSAGE
from src.voice_generation.xtts import XttsBackend, XTTS_NO_API_MESSAGE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clean_voice_env(monkeypatch):
    """Env isolation: no TTS_BACKEND so resolution falls back to mock."""
    monkeypatch.delenv("TTS_BACKEND", raising=False)


def _wav_probe(audio: bytes) -> dict:
    """Parse a WAV payload and return header facts (offline, stdlib only)."""
    with wave.open(io.BytesIO(audio), "rb") as wav:
        return {
            "channels": wav.getnchannels(),
            "sampwidth": wav.getsampwidth(),
            "framerate": wav.getframerate(),
            "frames": wav.getnframes(),
        }


class TestVoiceModels:
    """Models: defaults, bounds, and the request/status/result contract."""

    def test_request_defaults(self):
        request = VoiceRequest(text="Hello there")
        assert request.speaker == "unnamed"
        assert request.voice_code == DEFAULT_VOICE_CODE == "af_heart"
        assert request.lang_code == "a"
        assert request.pace == 1.0
        assert request.sample_rate == 24000
        assert request.seed is None

    def test_request_rejects_empty_text(self):
        with pytest.raises(ValidationError):
            VoiceRequest(text="")

    def test_request_bounds(self):
        with pytest.raises(ValidationError):
            VoiceRequest(text="x", pace=3.0)
        with pytest.raises(ValidationError):
            VoiceRequest(text="x", sample_rate=2000)

    def test_result_shape(self):
        request = VoiceRequest(text="hi", seed=7)
        result = VoiceResult(
            request=request, audio=b"RIFF...", format="wav",
            sample_rate=24000, duration_s=1.25, job_id="j-1",
            backend="mock", seed=7,
        )
        assert result.duration_s == 1.25
        assert result.format == "wav"


class TestBuildVoiceRequest:
    """Bible-aware defaults: voice code per character, pace per speed label."""

    def test_explicit_voice_code_wins(self, system):
        request = build_voice_request("Hi", voice_code="am_adam")
        assert request.voice_code == "am_adam"

    def test_character_profile_maps_voice_code(self, system):
        brief = system.resolve_voice("Lily Bunny")
        request = build_voice_request("Hi", brief=brief)
        assert request.speaker == "Lily Bunny"
        assert request.voice_code == "af_sarah"

    def test_slow_speech_maps_slower_pace(self, system):
        brief = system.resolve_voice("Ben Bear")  # speech_speed = "Slow"
        request = build_voice_request("Hi", brief=brief)
        assert request.pace == pytest.approx(0.9)

    def test_unknown_character_falls_back_to_narrator_code(self, system):
        brief = system.bible.build_voice_brief("Stranger")
        request = build_voice_request("Hi", brief=brief)
        assert request.voice_code == DEFAULT_VOICE_CODE

    def test_explicit_seed_and_sample_rate_pass_through(self):
        request = build_voice_request("Hi", seed=42, sample_rate=8000)
        assert request.seed == 42
        assert request.sample_rate == 8000

    def test_voice_code_for_brief_matches_library(self):
        from src.audio_bible.libraries import VOICE_PROFILES

        for profile in VOICE_PROFILES:
            assert voice_code_for_brief(profile) in CHARACTER_VOICE_CODES.values()


class TestGetBackend:
    """Registry: env var default, explicit names, unknown-name errors."""

    def test_defaults_to_mock_without_env(self, monkeypatch):
        _clean_voice_env(monkeypatch)
        backend = get_backend()
        assert isinstance(backend, MockBackend)

    def test_mock_default_when_unset(self, monkeypatch):
        monkeypatch.setenv("TTS_BACKEND", "mock")
        assert isinstance(get_backend(), MockBackend)

    def test_env_var_resolution(self, monkeypatch):
        monkeypatch.setenv("TTS_BACKEND", "xtts")
        assert isinstance(get_backend(), XttsBackend)

    def test_explicit_name_wins_over_env(self, monkeypatch):
        monkeypatch.setenv("TTS_BACKEND", "mock")
        assert isinstance(get_backend("pipER"), PiperBackend)

    def test_unknown_name_raises(self, monkeypatch):
        _clean_voice_env(monkeypatch)
        with pytest.raises(VoiceBackendError) as exc:
            get_backend("satellite")
        assert "Valid backends" in str(exc.value)


class TestBackendForEngine:
    """Bible engine names resolve to the expected adapters."""

    def test_kokoro_engine(self):
        from src.voice_generation.kokoro import KokoroBackend

        assert isinstance(backend_for_engine("Kokoro"), KokoroBackend)

    def test_xtts_v2_engine(self):
        assert isinstance(backend_for_engine("XTTS v2"), XttsBackend)

    def test_xtts_short_alias(self):
        assert isinstance(backend_for_engine("xtts"), XttsBackend)

    def test_piper_engine(self):
        assert isinstance(backend_for_engine("Piper"), PiperBackend)

    def test_unknown_engine_falls_back_to_mock(self, monkeypatch):
        _clean_voice_env(monkeypatch)
        assert isinstance(backend_for_engine("ElevenLabs"), MockBackend)

    def test_piper_stub_refuses_generate(self):
        backend = backend_for_engine("Piper")
        assert backend.is_configured() is False
        with pytest.raises(NotConfigured) as exc:
            backend.generate(VoiceRequest(text="hi"))
        assert "GPL" in str(exc.value)

    def test_xtts_stub_refuses_generate(self):
        backend = backend_for_engine("XTTS v2")
        assert backend.is_configured() is False
        with pytest.raises(NotConfigured) as exc:
            backend.generate(VoiceRequest(text="hi"))
        assert "CPML" in str(exc.value)


class TestRefusingStubs:
    """Piper/XTTS refuse every operation with the locked gate citations."""

    def test_piper_messages_cite_gpl(self):
        assert "GPL" in PIPER_NO_API_MESSAGE

    def test_xtts_messages_cite_cpml(self):
        assert "CPML" in XTTS_NO_API_MESSAGE

    def test_piper_full_surface_refuses(self):
        backend = PiperBackend()
        assert backend.is_configured() is False
        with pytest.raises(NotConfigured):
            backend.submit(VoiceRequest(text="x"))
        with pytest.raises(NotConfigured):
            backend.poll("j")
        with pytest.raises(NotConfigured):
            backend.download("j")
        with pytest.raises(NotConfigured):
            backend.generate(VoiceRequest(text="x"))

    def test_xtts_full_surface_refuses(self):
        backend = XttsBackend()
        with pytest.raises(NotConfigured):
            backend.generate(VoiceRequest(text="x"))


class TestMockBackend:
    """Determinism, seed chain, sample-rate honor, and job lifecycle."""

    def test_generate_returns_valid_wav(self):
        backend = MockBackend()
        request = VoiceRequest(text="Hello!", speaker="Lily Bunny", seed=7)
        result = backend.generate(request)
        assert isinstance(result, VoiceResult)
        assert result.backend == "mock"
        assert result.seed == 7
        assert result.audio.startswith(b"RIFF")
        probe = _wav_probe(result.audio)
        assert probe["channels"] == 1
        assert probe["sampwidth"] == 2
        assert probe["framerate"] == 24000
        assert result.duration_s == pytest.approx(1.5, rel=0.05)

    def test_same_seed_byte_identical(self):
        backend = MockBackend()
        a = backend.generate(VoiceRequest(text="Hello", seed=3))
        b = backend.generate(VoiceRequest(text="Hello", seed=3))
        assert a.audio == b.audio

    def test_content_seed_distinguishes_lines(self):
        backend = MockBackend()
        a = backend.generate(VoiceRequest(text="One", speaker="Lily Bunny"))
        b = backend.generate(VoiceRequest(text="Two", speaker="Lily Bunny"))
        assert a.audio != b.audio

    def test_content_seed_is_reproducible(self):
        backend = MockBackend()
        a = backend.generate(VoiceRequest(text="Hello", speaker="Daisy Duck"))
        b = backend.generate(VoiceRequest(text="Hello", speaker="Daisy Duck"))
        assert a.audio == b.audio

    def test_request_seed_beats_constructor_seed(self):
        backend = MockBackend(seed=99)
        with_request = backend.generate(VoiceRequest(text="H", seed=1))
        without_request = backend.generate(VoiceRequest(text="H"))
        assert with_request.seed == 1
        assert without_request.seed == 99

    def test_sample_rate_honored(self):
        backend = MockBackend()
        result = backend.generate(
            VoiceRequest(text="H", sample_rate=8000, seed=5)
        )
        assert _wav_probe(result.audio)["framerate"] == 8000
        assert result.sample_rate == 8000

    def test_fail_submit_injection(self):
        backend = MockBackend(fail_submit=True)
        with pytest.raises(VoiceBackendError):
            backend.generate(VoiceRequest(text="H"))

    def test_unknown_job_poll_and_download(self):
        backend = MockBackend()
        with pytest.raises(VoiceBackendError):
            backend.poll("nope")
        with pytest.raises(VoiceBackendError):
            backend.download("nope")

    def test_poll_progression(self):
        backend = MockBackend(states_before_complete=2)
        job_id = backend.submit(VoiceRequest(text="H"))
        first = backend.poll(job_id)
        assert first.state == "pending"
        second = backend.poll(job_id)
        assert second.state == "running"
        third = backend.poll(job_id)
        assert third.state == "completed"

    def test_is_configured_always_true(self):
        assert MockBackend().is_configured() is True


class TestKokoroBackend:
    """Full surface offline: presence gate, validation, and fake-pipeline path."""

    @pytest.fixture
    def backend(self):
        from src.voice_generation.kokoro import KokoroBackend

        return KokoroBackend()

    def test_is_configured_only_with_package(self, backend):
        installed = importlib.util.find_spec("kokoro") is not None
        assert backend.is_configured() is installed

    def test_missing_engine_raises_install_instructions(self, backend, monkeypatch):
        monkeypatch.setattr(backend, "is_configured", lambda: False)
        with pytest.raises(NotConfigured) as exc:
            backend.generate(VoiceRequest(text="Hello"))
        assert "pip install kokoro" in str(exc.value)

    def test_unknown_voice_family_rejected(self, backend):
        with pytest.raises(NotConfigured) as exc:
            backend.submit(VoiceRequest(text="H", voice_code="zz_fake"))
        assert "voice family" in str(exc.value)

    def test_unknown_lang_code_rejected(self, backend):
        with pytest.raises(NotConfigured) as exc:
            backend.submit(VoiceRequest(text="H", lang_code="q"))
        assert "lang_code" in str(exc.value)

    def test_generate_with_fake_pipeline_result(self, backend, monkeypatch, tmp_path):
        # Without the engine, exercise download via a scripted synthesis
        # producing a canonical WAV, exactly like the real path's contract.
        import struct

        def _fake_synth(request):
            pcm = struct.pack("<h", 500) * (request.sample_rate // 2)
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(request.sample_rate)
                wav.writeframes(pcm)
            return buffer.getvalue()

        monkeypatch.setattr(backend, "is_configured", lambda: True)
        monkeypatch.setattr(backend, "_synth", _fake_synth)
        request = VoiceRequest(text="Hello", speaker="Teddy", seed=11)
        result = backend.generate(request)
        assert result.backend == "kokoro"
        assert result.seed == 11
        assert _wav_probe(result.audio)["framerate"] == 24000
        assert result.duration_s == pytest.approx(0.5, rel=0.05)


class TestSaveVoiceResult:
    """Deterministic file persistence under out_dir."""

    def test_writes_deterministic_path(self, tmp_path):
        backend = MockBackend()
        result = backend.generate(VoiceRequest(text="Hi", speaker="Lily Bunny", seed=7))
        path = save_voice_result(result, str(tmp_path))
        assert path.endswith(".wav")
        assert os.path.isfile(path)
        with open(path, "rb") as fh:
            assert fh.read() == result.audio
        again = save_voice_result(result, str(tmp_path))
        assert again == path


@pytest.fixture
def system():
    return AudioProductionSystem()


class TestProductionWiring:
    """AudioProductionSystem + voice_generation / music_generation bridges."""

    def test_synth_voice_uses_mock_by_default(self, monkeypatch, system):
        _clean_voice_env(monkeypatch)
        result = system.synth_voice("Hello there!", "Lily Bunny")
        assert result.request.voice_code == "af_sarah"
        assert result.audio.startswith(b"RIFF")
        assert result.duration_s > 0

    def test_synth_voice_honors_explicit_backend(self, system):
        with pytest.raises(NotConfigured) as exc:
            system.synth_voice("Hi", "Narrator", backend_name="xtts")
        assert "CPML" in str(exc.value)

    def test_synth_plan_voices_covers_dialogue(self, monkeypatch, system):
        _clean_voice_env(monkeypatch)
        plan = system.plan_episode(
            "ep-1", "Garden Day",
            dialogue_lines=[
                ("Lily Bunny", "Look at the flowers!", "excited"),
                ("Ben Bear", "Yummy honey!", "happy"),
            ],
        )
        entries = system.synth_plan_voices(plan, seed=5)
        assert [e["speaker"] for e in entries] == ["Lily Bunny", "Ben Bear"]
        assert entries[0]["voice_code"] == "af_sarah"
        assert entries[1]["voice_code"] == "am_michael"
        assert all(e["duration_s"] > 0 for e in entries)
        assert all(e["result"].audio.startswith(b"RIFF") for e in entries)

    def test_music_request_for_bridges_lyrics(self, system):
        plan = system.plan_episode(
            "ep-1", "Garden Day",
            songs=[("Bedtime", "sleepy moon", "Standard")],
        )
        song = plan.songs[0]
        assert song.lyrics and "[verse]" in song.lyrics
        request = system.music_request_for(song, seed=9)
        assert request.lyrics_override == song.lyrics
        assert request.category == "Bedtime"
        assert request.topic == "sleepy moon"
        assert request.seed == 9

    def test_music_request_for_is_deterministic(self, system):
        plan = system.plan_episode(
            "ep-1", "Garden Day",
            songs=[("Alphabet", "abc", "Standard")],
        )
        first = system.music_request_for(plan.songs[0], seed=3)
        second = system.music_request_for(plan.songs[0], seed=3)
        assert first.lyrics_override == second.lyrics_override


class TestPhase7LyricsCli:
    """scripts/generate_phase7.py — lyrics_override wiring in the shipped CLI."""

    @pytest.fixture
    def cli(self):
        spec = importlib.util.spec_from_file_location(
            "generate_phase7", os.path.join(ROOT, "scripts", "generate_phase7.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _install_no_dial_guard(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise AssertionError(
                f"network seam dial attempted: {args} {kwargs}")

        from src.music_generation import backends as mg_backends

        for name in ("_post_json", "_get_json", "_get_bytes", "_urlopen"):
            monkeypatch.setattr(mg_backends, name, _boom)
        monkeypatch.setattr(mg_backends.DEFAULT_TRANSPORT, "post_json", _boom)
        monkeypatch.setattr(mg_backends.DEFAULT_TRANSPORT, "get_json", _boom)
        monkeypatch.setattr(mg_backends.DEFAULT_TRANSPORT, "get_bytes", _boom)

    def test_dry_run_carries_inline_lyrics(self, cli, monkeypatch, capsys):
        for var in ("ACESTEP_API_KEY", "ACESTEP_BASE_URL", "MUSIC_BACKEND"):
            monkeypatch.delenv(var, raising=False)
        self._install_no_dial_guard(monkeypatch)

        lyrics = "[verse]\nSleepy moon up high\n[chorus]\nGoodnight!"
        rc = cli.main(["--dry-run", "--category", "Bedtime",
                       "--topic", "sleepy moon", "--lyrics", lyrics])
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["lyrics_override"] == lyrics

    def test_dry_run_reads_lyrics_file(self, cli, monkeypatch, capsys, tmp_path):
        for var in ("ACESTEP_API_KEY", "ACESTEP_BASE_URL", "MUSIC_BACKEND"):
            monkeypatch.delenv(var, raising=False)
        self._install_no_dial_guard(monkeypatch)

        lyrics_file = tmp_path / "lyrics.txt"
        lyrics_file.write_text("[verse]\nTwinkle little star", encoding="utf-8")
        rc = cli.main(["--dry-run", "--category", "Alphabet",
                       "--lyrics-file", str(lyrics_file)])
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["lyrics_override"] == "[verse]\nTwinkle little star"

    def test_dry_run_omits_lyrics_override_when_unset(
            self, cli, monkeypatch, capsys):
        for var in ("ACESTEP_API_KEY", "ACESTEP_BASE_URL", "MUSIC_BACKEND"):
            monkeypatch.delenv(var, raising=False)
        self._install_no_dial_guard(monkeypatch)

        rc = cli.main(["--dry-run", "--category", "Alphabet"])
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload.get("lyrics_override") is None