"""Phase 7 tests — Music Generation Backend Integration.

Covers the provider-agnostic core layer: request/status/result models,
the runtime-checkable backend protocol, typed exceptions, the category
-> music-parameter mapping anchored on the Phase 5 audio bible, the
stdlib transport seam, generate() orchestration, and the deterministic
mock backend. Everything runs fully offline — no network, no database,
no audio hardware (fake transports and monkeypatched seams only).
"""

import io
import json
import logging
import os
import socket
import struct
import urllib.error
import urllib.parse
import wave
from dataclasses import dataclass

import pytest
from pydantic import ValidationError

from src.audio_bible import AUDIO_NEGATIVE_BASE, category_negative
from src.audio_bible.prompts import build_music_prompt
from src.music_generation import (
    AceStepBackend,
    BackendUnavailable,
    GenerationFailed,
    MockBackend,
    MusicBackendError,
    MusicGenerationBackend,
    MusicRequest,
    MusicResult,
    MusicStatus,
    NotConfigured,
    SunoBackend,
    SunoWrapperBackend,
    get_backend,
)
from src.music_generation import backends as mg_backends
from src.music_generation.backends import (
    CATEGORY_MUSIC_PARAMS,
    DEFAULT_TRANSPORT,
    CategoryMusicParams,
    _get_bytes,
    _get_json,
    _post_json,
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


class _FakeResponse:
    """Minimal urllib response stand-in (read()/status/headers/context mgr)."""

    def __init__(self, payload=b"", status=200, headers=None):
        self._payload = payload if isinstance(payload, bytes) else payload.encode()
        self.status = status
        self.headers = headers or {}

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def _install_fake_urlopen(monkeypatch, responses, calls):
    """Route every helper call through a recording fake seam."""

    def fake_urlopen(request, timeout=None):
        calls.append({
            "url": request.get_full_url(),
            "method": request.get_method(),
            "headers": {k.lower(): v for k, v in request.header_items()},
            "data": request.data,
            "timeout": timeout,
        })
        if isinstance(responses[0], Exception):
            raise responses.pop(0)
        return responses.pop(0)

    monkeypatch.setattr(mg_backends, "_urlopen", fake_urlopen)


class TestProtocolAndExceptions:
    """Exception taxonomy + runtime-checkable protocol conformance."""

    def test_exception_taxonomy(self):
        for exc_cls in (NotConfigured, BackendUnavailable, GenerationFailed):
            assert issubclass(exc_cls, MusicBackendError)
            assert issubclass(exc_cls, Exception)

    def test_mock_backend_isinstance_without_inheritance(self):
        backend = MockBackend()
        assert isinstance(backend, MusicGenerationBackend)
        # Structural conformance only — MockBackend must NOT inherit from
        # the protocol. issubclass() against a @runtime_checkable Protocol
        # is itself structural (member presence), so the no-inheritance
        # guarantee is asserted via the MRO.
        assert MusicGenerationBackend not in MockBackend.__mro__


class TestTransportSeam:
    """_post_json/_get_json/_get_bytes route through the _urlopen seam.

    Fakes intercept every call — no direct network syscalls possible
    (constraint C3).
    """

    HEADERS = {"Authorization": "Bearer secret-token"}

    def test_post_json_passes_full_request_shape(self, monkeypatch):
        calls: list[dict] = []
        _install_fake_urlopen(
            monkeypatch,
            [_FakeResponse(json.dumps({"job_id": "j-1"}).encode())],
            calls,
        )

        result = _post_json(
            "http://localhost:8001/v1/music/generate",
            {"caption": "song", "bpm": 66},
            headers=self.HEADERS,
        )

        assert result == {"job_id": "j-1"}
        assert len(calls) == 1
        call = calls[0]
        assert call["url"] == "http://localhost:8001/v1/music/generate"
        assert call["method"] == "POST"
        assert call["timeout"] == (5, 30)
        assert call["headers"]["authorization"] == "Bearer secret-token"
        assert call["headers"]["content-type"] == "application/json"
        assert json.loads(call["data"].decode()) == {
            "caption": "song", "bpm": 66,
        }

    def test_get_json_passes_full_request_shape(self, monkeypatch):
        calls: list[dict] = []
        _install_fake_urlopen(
            monkeypatch,
            [_FakeResponse(json.dumps({"state": "running", "progress": 0.5}).encode())],
            calls,
        )

        result = _get_json("http://localhost:8001/v1/jobs/j-1",
                           headers=self.HEADERS)

        assert result == {"state": "running", "progress": 0.5}
        call = calls[0]
        assert call["url"] == "http://localhost:8001/v1/jobs/j-1"
        assert call["method"] == "GET"
        assert call["timeout"] == (5, 30)
        assert call["headers"]["authorization"] == "Bearer secret-token"
        assert call["data"] is None

    def test_get_bytes_returns_binary_passthrough(self, monkeypatch):
        calls: list[dict] = []
        payload = b"RIFF\x24\x00\x00\x00WAVEfmt" + b"\x00" * 16
        _install_fake_urlopen(monkeypatch, [_FakeResponse(payload)], calls)

        result = _get_bytes("http://localhost:8001/v1/audio?path=a.wav",
                            headers=self.HEADERS)

        assert result == payload
        assert calls[0]["method"] == "GET"
        assert calls[0]["timeout"] == (5, 30)

    def test_http_401_maps_to_not_configured(self, monkeypatch):
        _install_fake_urlopen(
            monkeypatch,
            [urllib.error.HTTPError(
                "http://x", 401, "Unauthorized", {}, io.BytesIO(b"{}"))],
            [],
        )
        with pytest.raises(NotConfigured):
            _get_json("http://x/v1/jobs/j-1")

    def test_http_403_maps_to_not_configured(self, monkeypatch):
        _install_fake_urlopen(
            monkeypatch,
            [urllib.error.HTTPError(
                "http://x", 403, "Forbidden", {}, io.BytesIO(b"{}"))],
            [],
        )
        with pytest.raises(NotConfigured):
            _post_json("http://x/v1/music/generate", {})

    def test_http_500_maps_to_generation_failed(self, monkeypatch):
        _install_fake_urlopen(
            monkeypatch,
            [urllib.error.HTTPError(
                "http://x", 500, "Server Error", {}, io.BytesIO(b"{}"))],
            [],
        )
        with pytest.raises(GenerationFailed):
            _get_json("http://x/v1/jobs/j-1")

    def test_connection_errors_map_to_backend_unavailable(self, monkeypatch):
        for exc in (
            urllib.error.URLError("connection refused"),
            socket.timeout("timed out"),
            OSError("network down"),
        ):
            calls: list[dict] = []
            _install_fake_urlopen(monkeypatch, [exc], calls)
            with pytest.raises(BackendUnavailable):
                _get_json("http://down-host/v1/jobs/j-1")

    def test_malformed_json_body_maps_to_generation_failed(self, monkeypatch):
        _install_fake_urlopen(monkeypatch, [_FakeResponse(b"not-json{")], [])
        with pytest.raises(GenerationFailed, match="[Mm]alformed"):
            _get_json("http://x/v1/jobs/j-1")

    def test_non_object_json_body_maps_to_generation_failed(self, monkeypatch):
        _install_fake_urlopen(monkeypatch, [_FakeResponse(b"[1, 2]")], [])
        with pytest.raises(GenerationFailed):
            _get_json("http://x/v1/jobs/j-1")

    def test_default_transport_exposes_pinned_attribute_names(self):
        # Pinned exactly like this: plan 07-02 adapters consume these as
        # self._transport.post_json / get_json / get_bytes.
        assert DEFAULT_TRANSPORT.post_json is mg_backends._post_json
        assert DEFAULT_TRANSPORT.get_json is mg_backends._get_json
        assert DEFAULT_TRANSPORT.get_bytes is mg_backends._get_bytes

    def test_exception_messages_never_embed_header_values(self, monkeypatch):
        # Threat T7-01-I: Authorization values must never leak into errors.
        _install_fake_urlopen(
            monkeypatch,
            [urllib.error.HTTPError(
                "http://x", 401, "Unauthorized", {}, io.BytesIO(b"{}"))],
            [],
        )
        with pytest.raises(NotConfigured) as excinfo:
            _get_json("http://x/v1/jobs/j-1",
                      headers={"Authorization": "Bearer secret-token"})
        assert "secret-token" not in str(excinfo.value)


class TestGenerateOrchestration:
    """generate() backoff/deadline hardening via patched seams only."""

    def test_backoff_sequence_starts_1s_then_2s(self, monkeypatch):
        sleeps: list[float] = []
        monkeypatch.setattr(mg_backends, "_sleep",
                            lambda seconds: sleeps.append(seconds))
        backend = MockBackend(states_before_complete=2)

        result = backend.generate(
            MusicRequest(category="Bedtime", seed=7), poll_interval_s=1.0)

        assert isinstance(result, MusicResult)
        assert result.seed == 7
        # Doubling sequence 1 -> 2 -> 4 -> 8 capped at x8 of the base interval.
        assert sleeps == [1.0, 2.0]

    def test_deadline_expiry_raises_fast_with_job_id_and_elapsed(
            self, monkeypatch):
        monkeypatch.setattr(mg_backends, "_sleep", lambda seconds: None)
        clock_values = iter([100.0, 401.0])   # start, then past deadline
        monkeypatch.setattr(mg_backends, "_monotonic",
                            lambda: next(clock_values))

        backend = MockBackend()
        monkeypatch.setattr(
            backend, "poll",
            lambda job_id: MusicStatus(state="pending", progress=0.1),
        )

        with pytest.raises(GenerationFailed) as excinfo:
            backend.generate(MusicRequest(category="Bedtime", seed=7))
        message = str(excinfo.value)
        assert "mock-" in message                    # job id present
        assert "300.0" in message                    # timeout budget named
        assert "301.0" in message                    # elapsed seconds named

    def test_terminal_failed_poll_carries_server_error_text(self, monkeypatch):
        backend = MockBackend()
        monkeypatch.setattr(
            backend, "poll",
            lambda job_id: MusicStatus(state="failed", progress=0.4,
                                       error="model exploded"),
        )

        with pytest.raises(GenerationFailed, match="model exploded"):
            backend.generate(MusicRequest(category="Bedtime", seed=7))


# ---------------------------------------------------------------------------
# Plan 07-02 — real adapters, registry, and CLI (offline contract tests)     #
# ---------------------------------------------------------------------------


@dataclass
class _TransportCall:
    """One recorded transport invocation (url/method/headers/payload/timeout)."""

    url: str
    method: str
    headers: dict
    payload: object
    timeout: object


class _RecordingTransport:
    """Scripted fake transport — records every call, replays responses.

    Script entries may be: plain values (returned), Exception instances
    (raised), or zero-arg callables (invoked for dynamic responses).
    When the script is exhausted, ``default`` (if provided) is replayed
    forever — useful for never-completing job scripts.
    Mirrors the pinned DEFAULT_TRANSPORT surface exactly:
    post_json(url, payload, headers=..., timeout=...),
    get_json(url, headers=..., timeout=...),
    get_bytes(url, headers=..., timeout=...).
    """

    def __init__(self, *responses, default=None):
        self.calls: list[_TransportCall] = []
        self._script = list(responses)
        self._default = default

    def _replay(self, method, url, headers, payload, timeout):
        self.calls.append(_TransportCall(
            url=url, method=method,
            headers={k.lower(): v for k, v in dict(headers or {}).items()},
            payload=payload, timeout=timeout,
        ))
        if self._script:
            item = self._script.pop(0)
        elif self._default is not None:
            item = self._default
        else:
            raise AssertionError(
                f"scripted transport exhausted; unexpected {method} {url}"
            )
        if isinstance(item, Exception):
            raise item
        if callable(item):
            return item()
        return item

    def post_json(self, url, payload, headers=None, timeout=None):
        return self._replay("POST", url, headers, payload, timeout)

    def get_json(self, url, headers=None, timeout=None):
        return self._replay("GET", url, headers, None, timeout)

    def get_bytes(self, url, headers=None, timeout=None):
        return self._replay("GET", url, headers, None, timeout)

    # -- recording accessors ------------------------------------------------

    def posts(self) -> list[_TransportCall]:
        return [c for c in self.calls if c.method == "POST"]

    def gets(self) -> list[_TransportCall]:
        return [c for c in self.calls if c.method == "GET"]


def _clean_music_env(monkeypatch):
    """Env isolation for every test that builds adapters (ACESTEP_*/MUSIC_BACKEND)."""
    for var in ("ACESTEP_API_KEY", "ACESTEP_BASE_URL", "MUSIC_BACKEND"):
        monkeypatch.delenv(var, raising=False)


class TestAceStepAdapter:
    """Tracer 07-02-01: AceStepBackend happy path over scripted fake transport.

    Targets the REAL ACE-Step 1.5 REST contract (vendor docs/en/API.md):
    GET /health, POST /release_task, POST /query_result, GET /v1/audio?path=,
    with a ``{data, code, error}`` wrapper and integer task status codes.
    """

    BASE = "http://localhost:8001"
    AUDIO = b"RIFF\x24\x00\x00\x00WAVEfmt" + b"\xab" * 40

    def _backend(self, **kwargs):
        transport = kwargs.pop("transport", None) or _RecordingTransport()
        backend = AceStepBackend(transport=transport, **kwargs)
        return backend, transport

    def _submit_script(self, task_id="j-abc"):
        return _RecordingTransport({"data": {"task_id": task_id}})

    def _completed_match(self, task_id, file_url=None, result=None):
        """One /query_result entry in terminal 'completed' state."""
        if result is None:
            result = {"status": 1}
            if file_url is not None:
                result["file"] = file_url
        return {"data": [{"task_id": task_id, "status": 1,
                          "result": json.dumps(result)}]}

    # -- protocol conformance ----------------------------------------------

    def test_isinstance_protocol_without_inheritance(self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend, _ = self._backend(api_key="k")
        assert isinstance(backend, MusicGenerationBackend)
        assert MusicGenerationBackend not in AceStepBackend.__mro__

    # -- end-to-end happy path ----------------------------------------------

    def test_end_to_end_scripted_happy_path(self, monkeypatch):
        _clean_music_env(monkeypatch)
        monkeypatch.setattr(mg_backends, "_sleep", lambda seconds: None)

        # Vendor file URL is itself a /v1/audio?path=... relative endpoint.
        vendor_file = "/v1/audio?path=" + urllib.parse.quote(
            "/generated/song one.wav", safe="")
        transport = _RecordingTransport(
            {"data": {"task_id": "j-abc"}},                          # submit
            {"data": [{"task_id": "j-abc", "status": 0}]},           # poll 1
            {"data": [{"task_id": "j-abc", "status": 0}]},           # poll 2
            self._completed_match("j-abc", file_url=vendor_file),    # completed
            self.AUDIO,                                              # download
        )
        backend = AceStepBackend(api_key="k-test", base_url=self.BASE,
                                 transport=transport)

        seen_states: list[str] = []
        real_poll = backend.poll

        def spy_poll(job_id):
            status = real_poll(job_id)
            seen_states.append(status.state)
            return status

        backend.poll = spy_poll  # type: ignore[method-assign]

        request = MusicRequest(category="Bedtime", topic="sleepy moon", seed=7)
        result = backend.generate(request)

        # Exactly one POST to the submit endpoint.
        submits = [c for c in transport.posts()
                   if c.url == f"{self.BASE}/release_task"]
        assert len(submits) == 1

        # Status polls hit /query_result until completed.
        queries = [c for c in transport.posts()
                   if c.url == f"{self.BASE}/query_result"]
        assert len(queries) >= 2

        # Exactly one download GET to the vendor audio endpoint.
        downloads = [c for c in transport.gets()
                     if c.url == f"{self.BASE}{vendor_file}"]
        assert len(downloads) == 1

        # States surfaced in script order; result carries scripted bytes.
        assert seen_states == ["running", "running", "completed"]
        assert result.audio == self.AUDIO
        assert result.backend == "ace-step"
        assert result.seed == 7          # effective seed echoed back
        assert result.job_id == "j-abc"
        assert result.format == "wav"

    def test_completed_result_is_json_string_array(self, monkeypatch):
        """Real ACE-Step 1.5 result is a JSON string containing an ARRAY of
        record dicts (API.md §5.3), not a single object. Ensure the adapter
        decodes the array and pulls the audio URL out of the first record.
        """
        _clean_music_env(monkeypatch)
        monkeypatch.setattr(mg_backends, "_sleep", lambda seconds: None)

        vendor_file = "/v1/audio?path=" + urllib.parse.quote(
            "/generated/array one.wav", safe="")
        result_json = json.dumps([{
            "file": vendor_file, "wave": "", "status": 1,
            "create_time": 0, "prompt": "p", "lyrics": "",
            "metas": {"bpm": 120, "duration": 30},
            "seed_value": "1", "dit_model": "acestep-v15-turbo",
        }])
        transport = _RecordingTransport(
            {"data": {"task_id": "j-arr"}},                        # submit
            {"data": [{"task_id": "j-arr", "status": 0}]},         # running
            {"data": [{"task_id": "j-arr", "status": 1,
                       "result": result_json}]},                   # completed
            self.AUDIO,                                            # download
        )
        backend = AceStepBackend(api_key="k", base_url=self.BASE,
                                 transport=transport)
        result = backend.generate(
            MusicRequest(category="Bedtime", topic="t", seed=3))
        # Demonstrates the bugfix: no "result is not an object" failure.
        assert result.audio == self.AUDIO
        assert result.backend == "ace-step"

    def test_completed_result_is_bare_dict(self, monkeypatch):
        """Some result variants are a single dict; must still decode."""
        _clean_music_env(monkeypatch)
        monkeypatch.setattr(mg_backends, "_sleep", lambda seconds: None)
        vendor_file = "/v1/audio?path=" + urllib.parse.quote(
            "/generated/bare.wav", safe="")
        transport = _RecordingTransport(
            {"data": {"task_id": "j-d"}},
            {"data": [{"task_id": "j-d", "status": 1,
                       "result": json.dumps({"file": vendor_file})}]},
            self.AUDIO,
        )
        backend = AceStepBackend(api_key="k", base_url=self.BASE,
                                 transport=transport)
        result = backend.generate(MusicRequest(category="Bedtime", topic="t"))
        assert result.audio == self.AUDIO

    def test_bearer_header_from_constructor_arg(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = self._submit_script()
        backend = AceStepBackend(api_key="ctor-key", transport=transport)
        backend.submit(MusicRequest(category="Bedtime", seed=1))
        post = transport.posts()[0]
        assert post.headers["authorization"] == "Bearer ctor-key"
        assert post.headers["content-type"] == "application/json"

    def test_bearer_header_from_env_when_no_constructor_arg(self, monkeypatch):
        _clean_music_env(monkeypatch)
        monkeypatch.setenv("ACESTEP_API_KEY", "env-key")
        transport = self._submit_script()
        backend = AceStepBackend(transport=transport)
        backend.submit(MusicRequest(category="Bedtime", seed=1))
        assert transport.posts()[0].headers["authorization"] == "Bearer env-key"

    def test_no_auth_header_when_key_unset(self, monkeypatch):
        _clean_music_env(monkeypatch)
        # Real ACE-Step 1.5: empty key disables server auth; client omits header.
        transport = self._submit_script()
        backend = AceStepBackend(transport=transport)
        backend.submit(MusicRequest(category="Bedtime", seed=1))
        headers = transport.posts()[0].headers
        assert "authorization" not in headers
        assert headers["content-type"] == "application/json"

    def test_submit_payload_golden_bedtime(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = self._submit_script()
        backend = AceStepBackend(api_key="k", transport=transport)
        # Production composition path: build_music_request resolves the
        # category duration (Bedtime pinned at 120 s).
        request = build_music_request("Bedtime", "sleepy moon", seed=7)
        assert request.duration_s == 120
        backend.submit(request)

        payload = transport.posts()[0].payload
        expected_prompt = build_music_prompt(
            "Bedtime", "sleepy moon",
            vocals="female lead vocal, children's choir")[:512]

        assert payload["prompt"] == expected_prompt
        assert len(payload["prompt"]) <= 512
        assert "lullaby" in payload["prompt"].lower()

        # Bedtime scaffold markers joined with newlines.
        assert payload["lyrics"] == "\n".join([
            "[instrumental intro]", "[verse]", "[chorus]", "[verse]", "[outro]",
        ])
        assert len(payload["lyrics"]) <= 4096

        assert payload["audio_duration"] == 120      # request.duration_s
        assert payload["bpm"] == 66                  # resolve_music_params
        assert payload["key_scale"] == "F major"
        assert payload["time_signature"] == "3/4"
        assert isinstance(payload["seed"], int)
        assert payload["seed"] == 7
        assert payload["use_random_seed"] is False   # honor the explicit seed
        assert payload["thinking"] is False
        assert payload["model"] == "acestep-v15-turbo"

    def test_lyrics_override_used_and_capped_at_4096(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = self._submit_script()
        backend = AceStepBackend(api_key="k", transport=transport)
        request = MusicRequest(category="Bedtime", seed=1,
                               lyrics_override="y" * 5000)
        backend.submit(request)
        payload = transport.posts()[0].payload
        assert payload["lyrics"] == "y" * 4096

    def test_caption_truncated_hard_at_512(self, monkeypatch):
        _clean_music_env(monkeypatch)
        import src.music_generation.ace_step as ace_step_module
        monkeypatch.setattr(ace_step_module, "build_music_prompt",
                            lambda *args, **kwargs: "z" * 700)
        transport = self._submit_script()
        backend = AceStepBackend(api_key="k", transport=transport)
        backend.submit(MusicRequest(category="Bedtime", seed=1))
        assert len(transport.posts()[0].payload["prompt"]) == 512

    def test_seed_defaults_to_zero_when_unset(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = self._submit_script()
        backend = AceStepBackend(api_key="k", transport=transport)
        backend.submit(MusicRequest(category="Numbers"))
        assert transport.posts()[0].payload["seed"] == 0
        assert backend._effective_seed == 0   # echoes into MusicResult via generate()

    # -- configuration resolution -------------------------------------------

    def test_invalid_model_name_rejected(self, monkeypatch):
        _clean_music_env(monkeypatch)
        with pytest.raises(ValueError, match="acestep"):
            AceStepBackend(api_key="k", model="bogus-model")

    def test_sft_model_selected(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = self._submit_script()
        backend = AceStepBackend(api_key="k", model="acestep-v15-sft",
                                 transport=transport)
        backend.submit(MusicRequest(category="Bedtime", seed=1))
        assert transport.posts()[0].payload["model"] == "acestep-v15-sft"

    def test_base_url_resolution_order_and_default(self, monkeypatch):
        _clean_music_env(monkeypatch)
        default_backend, _ = self._backend(api_key="k")
        assert default_backend.base_url == "http://localhost:8001"

        monkeypatch.setenv("ACESTEP_BASE_URL", "http://127.0.0.1:9999/")
        env_backend, _ = self._backend(api_key="k")
        assert env_backend.base_url == "http://127.0.0.1:9999"

        arg_backend, _ = self._backend(
            api_key="k", base_url="http://10.0.0.5:8000//")
        assert arg_backend.base_url == "http://10.0.0.5:8000"

    # -- health probe ---------------------------------------------------------

    def test_is_configured_true_when_health_probe_ok(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = _RecordingTransport({"data": {"status": "ok"}})
        backend = AceStepBackend(api_key="k", transport=transport)
        assert backend.is_configured() is True
        probe = transport.gets()[0]
        assert probe.url == f"{self.BASE}/health"
        assert probe.timeout == (5.0, 5.0)   # short connect budget per RESEARCH §5

    def test_is_configured_falls_back_to_root_on_404(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = _RecordingTransport(
            urllib.error.HTTPError(f"{self.BASE}/health", 404,
                                   "Not Found", {}, io.BytesIO(b"{}")),
            {"data": {"status": "ok"}},
        )
        backend = AceStepBackend(api_key="k", transport=transport)
        assert backend.is_configured() is True
        assert transport.gets()[1].url == f"{self.BASE}/"

    def test_is_configured_false_on_connection_failure(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = _RecordingTransport(urllib.error.URLError("conn refused"))
        backend = AceStepBackend(api_key="k", transport=transport)
        assert backend.is_configured() is False

    def test_is_configured_false_on_auth_rejection(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = _RecordingTransport(
            urllib.error.HTTPError(f"{self.BASE}/health", 401,
                                   "Unauthorized", {}, io.BytesIO(b"{}")),
        )
        backend = AceStepBackend(api_key="k", transport=transport)
        assert backend.is_configured() is False

    def test_is_configured_true_without_key_when_service_up(self, monkeypatch):
        _clean_music_env(monkeypatch)
        # Real ACE-Step 1.5 can run with auth disabled (no key on the server);
        # our client must still report configured and omit the auth header.
        transport = _RecordingTransport({"data": {"status": "ok"}})
        backend = AceStepBackend(transport=transport)
        assert backend.is_configured() is True
        assert "authorization" not in transport.gets()[0].headers

    # -- poll/download semantics ----------------------------------------------

    def test_poll_running_until_terminal(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = _RecordingTransport(
            {"data": [{"task_id": "j-1", "status": 0}]},
            {"data": [{"task_id": "j-1", "status": 1,
                       "result": json.dumps({"status": 1})}]},
        )
        backend = AceStepBackend(api_key="k", transport=transport)
        assert backend.poll("j-1").state == "running"
        assert backend.poll("j-1").state == "completed"
        query = transport.posts()[0]
        assert query.url == f"{self.BASE}/query_result"
        assert query.payload == {"task_id_list": ["j-1"]}

    def test_download_performs_one_poll_if_path_unknown(self, monkeypatch):
        _clean_music_env(monkeypatch)
        vendor_file = "/v1/audio?path=" + urllib.parse.quote(
            "/generated/song.wav", safe="")
        transport = _RecordingTransport(
            self._completed_match("j-1", file_url=vendor_file),
            self.AUDIO,
        )
        backend = AceStepBackend(api_key="k", transport=transport)
        assert backend.download("j-1") == self.AUDIO
        assert transport.posts()[0].url == f"{self.BASE}/query_result"

    def test_download_uses_absolute_audio_url_verbatim(self, monkeypatch):
        _clean_music_env(monkeypatch)
        absolute = "http://127.0.0.1:8001/v1/audio?path=%2Fa.wav"
        transport = _RecordingTransport(
            self._completed_match("j-2", file_url=absolute),
            self.AUDIO,
        )
        backend = AceStepBackend(api_key="k", transport=transport)
        backend.download("j-2")
        assert transport.gets()[0].url == absolute

    def test_download_without_any_audio_url_raises(self, monkeypatch):
        _clean_music_env(monkeypatch)
        transport = _RecordingTransport(
            self._completed_match("j-3"),   # completed but no file field
        )
        backend = AceStepBackend(api_key="k", transport=transport)
        with pytest.raises(GenerationFailed):
            backend.download("j-3")

    def test_registry_resolves_ace_step_and_mock(self, monkeypatch):
        _clean_music_env(monkeypatch)
        ace = get_backend("ace-step", api_key="k")
        assert isinstance(ace, AceStepBackend)
        mock = get_backend("mock")
        assert isinstance(mock, MockBackend)


class TestErrorMapping:
    """07-02-02: the LOCKED RESEARCH §2 error map through the real adapter."""

    def _backend(self, transport):
        return AceStepBackend(api_key="k-error-tests", transport=transport)

    # -- submit-time failures ------------------------------------------------

    def test_url_error_on_submit_maps_to_backend_unavailable(self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(
            urllib.error.URLError("connection refused")))
        with pytest.raises(BackendUnavailable):
            backend.generate(MusicRequest(category="Bedtime", seed=1))

    def test_http_401_on_submit_maps_to_not_configured(self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(
            urllib.error.HTTPError("http://x", 401, "Unauthorized",
                                   {}, io.BytesIO(b"{}"))))
        with pytest.raises(NotConfigured):
            backend.submit(MusicRequest(category="Bedtime", seed=1))

    def test_http_403_on_submit_maps_to_not_configured(self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(
            urllib.error.HTTPError("http://x", 403, "Forbidden",
                                   {}, io.BytesIO(b"{}"))))
        with pytest.raises(NotConfigured):
            backend.submit(MusicRequest(category="Bedtime", seed=1))

    @pytest.mark.parametrize("bad_response", [
        "totally-not-json",                # non-object body
        [],                                # data not an object
        {"nope": 1},                       # JSON object missing task_id
        {"data": {"task_id": ""}},         # empty task_id
        {"data": {"task_id": None}},       # null task_id
    ])
    def test_malformed_submit_response_maps_to_generation_failed(
            self, monkeypatch, bad_response):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(bad_response))
        with pytest.raises(GenerationFailed, match="[Mm]alformed"):
            backend.submit(MusicRequest(category="Bedtime", seed=1))

    # -- poll-time failures ----------------------------------------------------

    def test_failed_status_poll_carries_error_and_generate_raises(
            self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(
            {"data": [{"task_id": "j-fail", "status": 2,
                       "error": "model exploded"}]},
        ))
        status = backend.poll("j-fail")
        assert status.state == "failed"
        assert status.error == "model exploded"

    def test_failed_terminal_via_generate_includes_server_text(self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(
            {"data": {"task_id": "j-f2"}},
            {"data": [{"task_id": "j-f2", "status": 2,
                       "error": "GPU OOM"}]},
        ))
        with pytest.raises(GenerationFailed, match="GPU OOM"):
            backend.generate(MusicRequest(category="Bedtime", seed=1))

    def test_unknown_status_code_maps_to_generation_failed(self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(
            {"data": [{"task_id": "j-x", "status": 99}]},
        ))
        with pytest.raises(GenerationFailed, match="unknown status"):
            backend.poll("j-x")

    def test_non_object_poll_body_maps_to_generation_failed(self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport("not-a-list"))
        with pytest.raises(GenerationFailed, match="[Mm]alformed"):
            backend.poll("j-y")

    def test_connection_drop_mid_poll_maps_to_backend_unavailable(
            self, monkeypatch):
        _clean_music_env(monkeypatch)
        backend = self._backend(_RecordingTransport(
            {"data": {"task_id": "j-drop"}},
            {"data": [{"task_id": "j-drop", "status": 0}]},
            urllib.error.URLError("connection reset mid-poll"),
        ))
        job_id = backend.submit(MusicRequest(category="Bedtime", seed=1))
        assert backend.poll(job_id).state == "running"
        with pytest.raises(BackendUnavailable):
            backend.poll(job_id)

        # Same drop surfacing through the full generate() loop.
        backend = self._backend(_RecordingTransport(
            {"data": {"task_id": "j-drop2"}},
            {"data": [{"task_id": "j-drop2", "status": 0}]},
            urllib.error.URLError("connection reset"),
        ))
        with pytest.raises(BackendUnavailable):
            backend.generate(MusicRequest(category="Bedtime", seed=1))

    def test_deadline_expiry_names_job_id_and_elapsed(self, monkeypatch):
        _clean_music_env(monkeypatch)
        monkeypatch.setattr(mg_backends, "_sleep", lambda seconds: None)
        clock_values = iter([100.0, 999.0])   # start, then past the deadline
        monkeypatch.setattr(mg_backends, "_monotonic",
                            lambda: next(clock_values))

        backend = self._backend(_RecordingTransport(
            {"data": {"task_id": "j-slow"}},
            default={"data": [{"task_id": "j-slow", "status": 0}]}))

        with pytest.raises(GenerationFailed) as excinfo:
            backend.generate(MusicRequest(category="Bedtime", seed=1))
        message = str(excinfo.value)
        assert "j-slow" in message             # job id named
        assert "300.0" in message              # timeout budget named
        assert "899.0" in message              # elapsed time named

    # -- registry environment resolution ---------------------------------------

    def test_get_backend_honors_music_backend_env(self, monkeypatch):
        _clean_music_env(monkeypatch)
        monkeypatch.setenv("MUSIC_BACKEND", "suno")
        assert isinstance(get_backend(None), SunoBackend)

        monkeypatch.setenv("MUSIC_BACKEND", "ace-step")
        assert isinstance(get_backend(), AceStepBackend)

        monkeypatch.setenv("MUSIC_BACKEND", "mock")
        assert isinstance(get_backend(), MockBackend)

    def test_get_backend_defaults_to_mock_without_env(self, monkeypatch):
        _clean_music_env(monkeypatch)
        assert isinstance(get_backend(None), MockBackend)

    def test_unknown_name_raises_listing_valid_choices(self, monkeypatch):
        _clean_music_env(monkeypatch)
        with pytest.raises(MusicBackendError) as excinfo:
            get_backend("nope")
        message = str(excinfo.value)
        for choice in ("ace-step", "suno", "mock"):
            assert choice in message

    # -- secret hygiene (threat T7-02-I) ----------------------------------------

    def test_token_never_leaks(self, monkeypatch, caplog):
        """Run the whole matrix; the dummy key appears nowhere."""
        _clean_music_env(monkeypatch)
        token = "super-secret-token-42"

        unauthorized = urllib.error.HTTPError(
            "http://x", 401, "Unauthorized", {}, io.BytesIO(b"{}"))
        forbidden = urllib.error.HTTPError(
            "http://x", 403, "Forbidden", {}, io.BytesIO(b"{}"))
        server_error = urllib.error.HTTPError(
            "http://x", 500, "Server Error", {}, io.BytesIO(b"{}"))
        failed_body = {"data": [{"task_id": "j", "status": 2,
                                 "error": "boom"}]}

        # Each scenario replays its failure forever (default=) so the same
        # script can serve is_configured() AND generate() without exhausting.
        scenarios = [
            lambda: _RecordingTransport(urllib.error.URLError("down"),
                                        default=urllib.error.URLError("down")),
            lambda: _RecordingTransport(unauthorized, default=unauthorized),
            lambda: _RecordingTransport(forbidden, default=forbidden),
            lambda: _RecordingTransport(server_error, default=server_error),
            lambda: _RecordingTransport("not-a-list", default="not-a-list"),
            lambda: _RecordingTransport({"data": {"missing": "task_id"}},
                                        default={"data": {"missing": "task_id"}}),
            lambda: _RecordingTransport({"data": {"task_id": "j"}},
                                        failed_body, default=failed_body),
            lambda: _RecordingTransport({"data": {"task_id": "j"}},
                                        default=urllib.error.URLError("reset")),
        ]

        with caplog.at_level(logging.DEBUG):
            for make_transport in scenarios:
                request = MusicRequest(category="Bedtime", seed=3)
                backend = AceStepBackend(api_key=token,
                                         transport=make_transport())
                try:
                    backend.is_configured()
                except MusicBackendError as exc:
                    assert token not in repr(exc), "probe leaked token"
                try:
                    backend.generate(request)
                except MusicBackendError as exc:
                    assert token not in repr(exc), \
                        f"{type(exc).__name__} leaked token: {exc}"

        for record in caplog.records:
            assert token not in record.getMessage(), \
                f"log record leaked token: {record.getMessage()}"


class TestSunoStub:
    """07-02-03: Suno refusal stub + experimental wrapper + registry invariant."""

    LOCKED_CITATION = (
        "Suno has no official public API (as of Aug 2026); "
        "see .planning/research/MUSIC-GENERATION.md"
    )
    WRAPPER_SUFFIX = "(experimental third-party relay — disabled by default)"

    def test_suno_is_configured_constant_false(self):
        assert SunoBackend().is_configured() is False
        assert SunoWrapperBackend().is_configured() is False

    def test_every_entry_point_refuses_with_locked_message(self):
        backend = SunoBackend()
        request = MusicRequest(category="Bedtime", seed=1)

        with pytest.raises(NotConfigured) as excinfo:
            backend.submit(request)
        assert self.LOCKED_CITATION in str(excinfo.value)

        with pytest.raises(NotConfigured) as excinfo:
            backend.poll("j-1")
        assert self.LOCKED_CITATION in str(excinfo.value)

        with pytest.raises(NotConfigured) as excinfo:
            backend.download("j-1")
        assert self.LOCKED_CITATION in str(excinfo.value)

        with pytest.raises(NotConfigured) as excinfo:
            backend.generate(request)          # refuses WITHOUT building requests
        assert self.LOCKED_CITATION in str(excinfo.value)

    def test_wrapper_flagged_experimental_with_suffix(self):
        wrapper = SunoWrapperBackend()
        assert SunoWrapperBackend.EXPERIMENTAL is True
        assert "experimental" in SunoWrapperBackend.__doc__.lower()

        request = MusicRequest(category="Bedtime", seed=1)
        for call in (
            lambda: wrapper.submit(request),
            lambda: wrapper.poll("j-1"),
            lambda: wrapper.download("j-1"),
            lambda: wrapper.generate(request),
        ):
            with pytest.raises(NotConfigured) as excinfo:
                call()
            message = str(excinfo.value)
            assert self.LOCKED_CITATION in message
            assert self.WRAPPER_SUFFIX in message

    def test_registry_never_resolves_wrapper(self, monkeypatch):
        _clean_music_env(monkeypatch)
        resolved = get_backend("suno")
        assert isinstance(resolved, SunoBackend)
        assert not isinstance(resolved, SunoWrapperBackend)

        for bad_name in ("sunowrapper", "SunoWrapperBackend", "wrapper"):
            with pytest.raises(MusicBackendError):
                get_backend(bad_name)

        monkeypatch.setenv("MUSIC_BACKEND", "suno")
        resolved = get_backend(None)
        assert isinstance(resolved, SunoBackend)
        assert not isinstance(resolved, SunoWrapperBackend)

    def test_protocol_conformance_without_inheritance_from_protocol(self):
        for cls in (SunoBackend, SunoWrapperBackend):
            assert issubclass(cls, object)      # plain classes
            assert MusicGenerationBackend not in cls.__mro__
            assert isinstance(cls(), MusicGenerationBackend)

    def test_suno_module_contains_no_http_code(self):
        """Constraint C3/C4: nothing to connect to — no HTTP imports at all."""
        import pathlib
        import src.music_generation.suno as suno_module
        source = pathlib.Path(suno_module.__file__).read_text(encoding="utf-8")
        for forbidden in ("import requests", "urllib", "http.client",
                          "socket", "_post_json", "_get_json", "_get_bytes"):
            assert forbidden not in source


class TestPhase7Cli:
    """07-02-04: scripts/generate_phase7.py — dry-run proves zero dials."""

    @pytest.fixture
    def cli(self):
        """Load the script module in-process (bootstrap runs harmlessly)."""
        import importlib.util
        script_path = os.path.join(ROOT, "scripts", "generate_phase7.py")
        spec = importlib.util.spec_from_file_location("generate_phase7",
                                                      script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _install_no_dial_guard(self, monkeypatch):
        """Fail loud if ANY transport seam is touched (constraint C3)."""

        def _boom(*args, **kwargs):
            raise AssertionError(
                f"network seam dial attempted: {args} {kwargs}")

        for name in ("_post_json", "_get_json", "_get_bytes", "_urlopen"):
            monkeypatch.setattr(mg_backends, name, _boom)
        # DEFAULT_TRANSPORT binds the original functions at import time;
        # guard its pinned attributes too so no path can sneak through.
        monkeypatch.setattr(mg_backends.DEFAULT_TRANSPORT, "post_json", _boom)
        monkeypatch.setattr(mg_backends.DEFAULT_TRANSPORT, "get_json", _boom)
        monkeypatch.setattr(mg_backends.DEFAULT_TRANSPORT, "get_bytes", _boom)

    def test_dry_run_prints_request_json_zero_dials(
            self, cli, monkeypatch, capsys):
        _clean_music_env(monkeypatch)
        self._install_no_dial_guard(monkeypatch)

        rc = cli.main(["--dry-run", "--category", "Bedtime",
                       "--topic", "sleepy moon", "--seed", "7"])

        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["category"] == "Bedtime"
        assert payload["duration_s"] == 120
        assert payload["topic"] == "sleepy moon"
        assert payload["seed"] == 7
        assert "choir" in payload["vocals"]

    def test_dry_run_needs_no_credentials(self, cli, monkeypatch, capsys):
        _clean_music_env(monkeypatch)   # ACESTEP_API_KEY deliberately unset
        self._install_no_dial_guard(monkeypatch)

        rc = cli.main(["--dry-run", "--category", "Alphabet"])

        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["category"] == "Alphabet"

    def test_dry_run_unknown_category_still_exits_zero(
            self, cli, monkeypatch, capsys):
        _clean_music_env(monkeypatch)
        self._install_no_dial_guard(monkeypatch)

        rc = cli.main(["--dry-run", "--category", "Spaceship"])

        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["duration_s"] == 60   # generic fallback row

    def test_real_mode_mock_writes_wav_and_summary(
            self, cli, monkeypatch, capsys, tmp_path):
        _clean_music_env(monkeypatch)
        out_dir = tmp_path / "music"
        out_dir_str = str(out_dir)

        rc = cli.main(["--backend", "mock", "--category", "Bedtime",
                       "--topic", "sleepy moon", "--seed", "9",
                       "--out", out_dir_str])

        assert rc == 0
        wav_path = out_dir / "bedtime-sleepy-moon-9.wav"
        assert wav_path.exists()
        audio = wav_path.read_bytes()
        assert audio.startswith(b"RIFF")
        with wave.open(io.BytesIO(audio)) as handle:
            assert handle.getnchannels() == 1

        output = capsys.readouterr().out
        assert "mock" in output
        assert "mock-" in output                 # job id
        assert str(len(audio)) in output         # byte count
        assert str(wav_path) in output           # output path

    def test_backend_default_comes_from_music_backend_env(
            self, cli, monkeypatch, capsys, tmp_path):
        _clean_music_env(monkeypatch)
        monkeypatch.setenv("MUSIC_BACKEND", "mock")

        rc = cli.main(["--category", "Animals", "--topic", "duck pond",
                       "--seed", "3", "--out", str(tmp_path / "x")])

        assert rc == 0
        assert (tmp_path / "x" / "animals-duck-pond-3.wav").exists()

    def test_real_mode_suno_refusal_exits_one_on_stderr(
            self, cli, monkeypatch, capsys):
        _clean_music_env(monkeypatch)

        rc = cli.main(["--backend", "suno", "--category", "Bedtime"])

        captured = capsys.readouterr()
        assert rc == 1
        assert "no official public API" in captured.err
        assert "Traceback" not in captured.err
        assert "Traceback" not in captured.out

    def test_unknown_backend_exits_nonzero_with_choice_list(
            self, cli, monkeypatch, capsys):
        _clean_music_env(monkeypatch)

        rc = cli.main(["--backend", "nope"])

        captured = capsys.readouterr()
        assert rc == 1                            # handled failure, no crash
        for choice in ("ace-step", "suno", "mock"):
            assert choice in captured.err
