"""Tests for ``src.video_generation`` — video generation engine package.

Covers:
  - VideoInput/VideoOutput data models
  - MockBackend: deterministic MP4 synthesis, submit/poll/download/generate loop
  - get_backend registry: fallback defaults, unknown-name error, env-var override
  - Protocol compliance: ``isinstance(backend, VideoGenerationBackend)``
  - WanVideoBackend: ComfyUI REST contract via injected transport seam
  - CloudVideoBackend: NotConfigured on missing key, fal/replicate stubs
"""

from __future__ import annotations

import json

import pytest
from unittest.mock import patch

from src.video_generation import (
    BackendUnavailable,
    GenerationFailed,
    MockBackend,
    NotConfigured,
    VideoBackendError,
    VideoGenerationBackend,
    VideoInput,
    VideoOutput,
    get_backend,
)
from src.video_generation.base import _sleep, _monotonic


# ======================================================================
# Data models
# ======================================================================

class TestVideoInput:
    def test_defaults(self):
        inp = VideoInput()
        assert inp.prompt == ""
        assert inp.seed == 42
        assert inp.width == 1280
        assert inp.height == 720
        assert inp.frames == 120
        assert inp.fps == 24

    def test_custom_values(self):
        inp = VideoInput(prompt="a cat waves", seed=99, width=640, height=480, frames=48)
        assert inp.prompt == "a cat waves"
        assert inp.frames == 48

    def test_metadata_default(self):
        assert VideoInput().metadata == {}


class TestVideoOutput:
    def test_defaults(self):
        out = VideoOutput()
        assert out.video == b""
        assert out.format == "mp4"
        assert out.job_id == ""
        assert out.backend == ""


# ======================================================================
# MockBackend
# ======================================================================

class TestMockBackend:
    def test_is_configured(self):
        assert MockBackend().is_configured() is True

    def test_synthesize_mp4_deterministic(self):
        from src.video_generation.mock import _synthesize_mp4
        a = _synthesize_mp4(seed=42)
        b = _synthesize_mp4(seed=42)
        c = _synthesize_mp4(seed=99)
        assert a == b
        assert a != c

    def test_mp4_starts_with_ftyp(self):
        from src.video_generation.mock import _synthesize_mp4
        assert _synthesize_mp4(seed=0)[:8] == b"\x00\x00\x00\x18ftyp"

    def test_submit_poll_complete_download_cycle(self):
        backend = MockBackend(states_before_complete=1)
        request = VideoInput(prompt="a bear dances", seed=7, frames=48)
        job_id = backend.submit(request)
        assert isinstance(job_id, str) and job_id.startswith("mock-vid-")

        status = backend.poll(job_id)
        assert status == "running"
        status = backend.poll(job_id)
        assert status == "completed"

        result = backend.download(job_id)
        assert isinstance(result, VideoOutput)
        assert result.video.startswith(b"\x00\x00\x00\x18ftyp")
        assert result.format == "mp4"
        assert result.seed == 7
        assert result.frames == 48

    def test_generate_endpoint(self):
        backend = MockBackend(states_before_complete=0)
        with patch("src.video_generation.base._sleep"):
            result = backend.generate(VideoInput(prompt="test", seed=5))
        assert result.video
        assert result.format == "mp4"

    def test_fail_submit_raises(self):
        backend = MockBackend(fail_submit=True)
        with pytest.raises(GenerationFailed, match="fail_submit"):
            backend.submit(VideoInput())

    def test_unknown_job_poll_raises(self):
        backend = MockBackend()
        with pytest.raises(GenerationFailed, match="Unknown mock video"):
            backend.poll("no-such-id")

    def test_protocol_compliance(self):
        assert isinstance(MockBackend(), VideoGenerationBackend)


# ======================================================================
# get_backend registry
# ======================================================================

class TestGetBackend:
    def test_default_is_mock(self):
        backend = get_backend()
        assert isinstance(backend, MockBackend)

    def test_explicit_mock(self):
        assert isinstance(get_backend("mock"), MockBackend)

    def test_env_var_fallback(self):
        with patch.dict("os.environ", {"VIDEO_BACKEND": "mock"}):
            assert isinstance(get_backend(), MockBackend)

    def test_unknown_raises(self):
        with pytest.raises(VideoBackendError, match="Unknown video backend"):
            get_backend("nonexistent")

    def test_wan_imports(self):
        from src.video_generation.wan import WanVideoBackend
        b = get_backend("wan")
        assert isinstance(b, WanVideoBackend)

    def test_hunyuan_imports(self):
        from src.video_generation.hunyuan import HunyuanVideoBackend
        b = get_backend("hunyuan", provider="fal", api_key="fake")
        assert isinstance(b, HunyuanVideoBackend)

    def test_cloud_requires_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(NotConfigured):
                get_backend("cloud", provider="fal", api_key=None)


# ======================================================================
# WanVideoBackend — ComfyUI transport seam
# ======================================================================

class TestWanVideoBackend:
    def _make_backend(self):
        from src.video_generation.wan import WanVideoBackend
        return WanVideoBackend(server_url="http://mock-comfy:8188")

    def test_is_configured(self):
        b = self._make_backend()
        assert b.is_configured()

    def test_submit_posts_workflow(self):
        b = self._make_backend()
        calls = []

        def fake_transport(method, url, *, payload=None, headers=None):
            calls.append((method, url, payload))
            return b'{"prompt_id": "w-abc"}'

        b.transport = fake_transport
        job_id = b.submit(VideoInput(prompt="a duck hops", seed=42))
        assert job_id == "w-abc"
        assert len(calls) == 1
        method, url, payload = calls[0]
        assert method == "POST"
        assert "/prompt" in url
        assert payload["prompt"]["6"]["inputs"]["text"] == "a duck hops"
        assert payload["prompt"]["5"]["inputs"]["seed"] == 42

    def test_poll_completed(self):
        b = self._make_backend()
        history = json.dumps({"w-abc": {"status": {"status_str": "success"}}}).encode()
        b.transport = lambda *a, **kw: history
        assert b.poll("w-abc") == "completed"

    def test_poll_running(self):
        b = self._make_backend()
        b.transport = lambda *a, **kw: b"{}"
        assert b.poll("w-abc") == "running"

    def test_download_fetches_video(self):
        b = self._make_backend()
        video_bytes = b"\x00\x00\x00\x18ftyp" + b"\xff" * 10
        history_entry = {
            "w-abc": {
                "outputs": {"20": {"videos": [
                    {"filename": "wan_42_00001.mp4", "subfolder": "",
                     "type": "output", "format": "video/h264-mp4"}
                ]}},
                "status": {"status_str": "success"},
            }
        }

        call_count = [0]
        def fake_transport(method, url, *, payload=None, headers=None):
            call_count[0] += 1
            if "/history/" in url:
                return json.dumps(history_entry).encode()
            return video_bytes

        b.transport = fake_transport
        result = b.download("w-abc")
        assert result.video == video_bytes
        assert result.format == "mp4"
        assert result.job_id == "w-abc"
        assert call_count[0] == 2  # history + view


# ======================================================================
# CloudVideoBackend — config and error paths
# ======================================================================

class TestCloudVideoBackend:
    def test_not_configured_without_key(self):
        from src.video_generation.cloud import CloudVideoBackend
        with pytest.raises(NotConfigured):
            CloudVideoBackend(provider="fal", api_key=None)

    def test_not_configured_wrong_env(self):
        with patch.dict("os.environ", {}, clear=True):
            from src.video_generation.cloud import CloudVideoBackend
            with pytest.raises(NotConfigured):
                CloudVideoBackend(provider="fal")

    def test_unknown_provider_submit_raises(self):
        from src.video_generation.cloud import CloudVideoBackend
        backend = CloudVideoBackend(provider="fal", api_key="fake-key")
        # Override the provider to an unknown name after construction
        backend.provider = "nonexistent"
        with pytest.raises(GenerationFailed, match="Unknown cloud provider"):
            backend.submit(VideoInput())

    def test_hunyuan_defaults_fal(self):
        from src.video_generation.hunyuan import HunyuanVideoBackend
        b = HunyuanVideoBackend(api_key="fake-key")
        assert "hunyuan" in b.model.lower() or "hunyuan" in b.model

    def test_download_echoes_request_seed_and_frames(self):
        """A-06 regression: cloud downloads must echo the submitted request's
        seed/frames instead of hardcoded seed=0, frames=0."""
        from src.video_generation.cloud import CloudVideoBackend

        backend = CloudVideoBackend(provider="fal", api_key="fake-key")
        backend._post_json = lambda url, payload, extra_headers=None: {"request_id": "JOB1"}
        backend._get_json = lambda url: {"output": {"video": {"url": "https://x/v.mp4"}}}
        backend._download_url = lambda url: b"VIDEO"
        request = VideoInput(prompt="duck hops", seed=99, frames=148)
        job_id = backend.submit(request)
        result = backend.download(job_id)
        assert result.seed == 99
        assert result.frames == 148

    # ---- A-06: transient vs terminal poll semantics --------------------- #

    def test_poll_fal_transient_network_error_returns_running(self):
        """BackendUnavailable (timeout/reset) is retryable — stay running."""
        from src.video_generation.cloud import CloudVideoBackend

        backend = CloudVideoBackend(provider="fal", api_key="fake-key")
        backend._get_json = lambda url: (_ for _ in ()).throw(
            BackendUnavailable("network down")
        )
        assert backend.poll("JOB1") == "running"

    def test_poll_fal_persistent_api_error_propagates(self):
        """A-06 regression: a persistent API HttpError (GenerationFailed) must
        surface immediately, not be masked as 'running' until the deadline."""
        from src.video_generation.cloud import CloudVideoBackend

        backend = CloudVideoBackend(provider="fal", api_key="fake-key")
        backend._get_json = lambda url: (_ for _ in ()).throw(
            GenerationFailed("Cloud backend returned HTTP 500")
        )
        with pytest.raises(GenerationFailed, match="HTTP 500"):
            backend.poll("JOB1")

    def test_poll_replicate_transient_network_error_returns_running(self):
        from src.video_generation.cloud import CloudVideoBackend

        backend = CloudVideoBackend(provider="replicate", api_key="fake-key")
        backend._get_json = lambda url: (_ for _ in ()).throw(
            BackendUnavailable("connection reset")
        )
        assert backend.poll("JOB1") == "running"

    def test_poll_replicate_persistent_api_error_propagates(self):
        from src.video_generation.cloud import CloudVideoBackend

        backend = CloudVideoBackend(provider="replicate", api_key="fake-key")
        backend._get_json = lambda url: (_ for _ in ()).throw(
            GenerationFailed("Cloud backend returned HTTP 402")
        )
        with pytest.raises(GenerationFailed, match="HTTP 402"):
            backend.poll("JOB1")

    def test_generate_surfaces_persistent_api_error_without_waiting(self, monkeypatch):
        """A-06 regression: the submit->poll loop must not keep polling for the
        full 900s timeout when the status endpoint reports a terminal error."""
        import src.video_generation.base as base_mod
        from src.video_generation.cloud import CloudVideoBackend

        backend = CloudVideoBackend(provider="fal", api_key="fake-key")
        backend._post_json = lambda url, payload, extra_headers=None: {"request_id": "JOB1"}
        poll_calls = []
        def failing_poll(job_id):
            poll_calls.append(job_id)
            raise GenerationFailed("Cloud backend returned HTTP 500")
        monkeypatch.setattr(backend, "poll", failing_poll)
        monkeypatch.setattr(base_mod, "_sleep", lambda s: None)
        monkeypatch.setattr(base_mod, "_monotonic", lambda: 0.0)

        with pytest.raises(GenerationFailed, match="HTTP 500"):
            backend.generate(VideoInput(prompt="duck hops"), timeout_s=900.0)
        assert len(poll_calls) == 1
