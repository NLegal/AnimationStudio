"""Failure-path tests for ``src.generation_engine.comfy_backend`` (audit A-05).

Every network-capable path (connectivity check, workflow submit, history
poll, image view) is exercised with a fake ``requests`` module so ComfyUI
server errors produce structured ``GenerationOutput`` error metadata instead
of uncaught exceptions (``KeyError: 'prompt_id'`` pre-fix) or silent hangs.
"""

from __future__ import annotations

import sys
import types

import pytest

from src.generation_engine.comfy_backend import ComfyUIBackend
from src.generation_engine.base import GenerationInput


def _png_bytes():
    """Tiny valid PNG for /view responses."""
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color=(200, 0, 0)).save(buf, format="PNG")
    return buf.getvalue()


class _FakeResponse:
    def __init__(self, status=200, body=None, text="", content=b""):
        self.status_code = status
        self._body = body
        self.text = text
        self.content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        if isinstance(self._body, dict) or isinstance(self._body, list):
            return self._body
        raise ValueError("no json body")


def _install_fake_requests(monkeypatch, post_handler, get_handler):
    """Point the backend's ``requests`` module at scripted handlers.

    Returns a ''module-like'' with ``post``/``get`` routed through
    ``post_handler(url, json=..., timeout=...)`` and
    ``get_handler(url, params=..., timeout=...)``.
    """
    fake = types.ModuleType("requests")

    def post(url, json=None, timeout=10, **kw):
        return post_handler(url, json=json, timeout=timeout)

    def get(url, params=None, timeout=10, **kw):
        return get_handler(url, params=params, timeout=timeout)

    fake.post = post
    fake.get = get
    monkeypatch.setitem(sys.modules, "requests", fake)


def _err_metadata(output):
    return output.metadata.get("error", "")


class TestRESTFailurePaths:
    def test_post_refused_returns_error_metadata(self, monkeypatch):
        def post(url, **kw):
            raise ConnectionError("refused")

        def get(url, **kw):
            raise ConnectionError("refused")

        _install_fake_requests(monkeypatch, post, get)
        out = ComfyUIBackend().generate(GenerationInput(prompt="hi"))
        assert out.images == []
        assert "refused" in _err_metadata(out)

    def test_post_http_500_returns_error_metadata(self, monkeypatch):
        def post(url, **kw):
            return _FakeResponse(500, body=None, text="boom")

        def get(url, **kw):
            return _FakeResponse(200, body={})

        _install_fake_requests(monkeypatch, post, get)
        out = ComfyUIBackend().generate(GenerationInput(prompt="hi"))
        assert out.images == []
        assert "HTTP 500" in _err_metadata(out)
        assert "boom" in _err_metadata(out)

    def test_post_validation_error_no_prompt_id(self, monkeypatch):
        """ComfyUI can return HTTP 200 with an ``error`` body (no prompt_id).
        Regression for the pre-fix ``KeyError: 'prompt_id'``."""
        def post(url, **kw):
            return _FakeResponse(200, body={"error": {"message": "bad node"}})

        def get(url, **kw):
            return _FakeResponse(200, body={})

        _install_fake_requests(monkeypatch, post, get)
        out = ComfyUIBackend().generate(GenerationInput(prompt="hi"))
        assert out.images == []
        assert "prompt_id" in _err_metadata(out)
        assert "bad node" in _err_metadata(out)

    def test_post_non_dict_body_returns_error_metadata(self, monkeypatch):
        def post(url, **kw):
            return _FakeResponse(200, body=[])

        def get(url, **kw):
            return _FakeResponse(200, body={})

        _install_fake_requests(monkeypatch, post, get)
        out = ComfyUIBackend().generate(GenerationInput(prompt="hi"))
        assert out.images == []
        assert "prompt_id" in _err_metadata(out)

    def test_job_failed_in_history_returns_error_metadata(self, monkeypatch):
        def post(url, **kw):
            return _FakeResponse(200, body={"prompt_id": "P1"})

        def get(url, params=None, **kw):
            if url.endswith("/history/P1"):
                return _FakeResponse(
                    200,
                    body={"P1": {"outputs": {}, "status": {"status_str": "error"}}},
                )
            return _FakeResponse(200, body={})

        _install_fake_requests(monkeypatch, post, get)
        out = ComfyUIBackend().generate(GenerationInput(prompt="hi"))
        assert out.images == []
        assert "P1" in _err_metadata(out)
        assert "error" in _err_metadata(out).lower()

    def test_view_failure_skips_image_not_crash(self, monkeypatch):
        def post(url, **kw):
            return _FakeResponse(200, body={"prompt_id": "P1"})

        seen = {"view_calls": 0}

        def get(url, params=None, **kw):
            if url.endswith("/history/P1"):
                return _FakeResponse(
                    200,
                    body={"P1": {"outputs": {"9": {"images": [
                        {"filename": "x.png", "subfolder": "", "type": "output"},
                    ]}}}},
                )
            if url.endswith("/view"):
                seen["view_calls"] += 1
                if seen["view_calls"] == 1:
                    raise ConnectionError("view down")
                return _FakeResponse(200, body=None, content=_png_bytes())
            return _FakeResponse(200, body={})

        _install_fake_requests(monkeypatch, post, get)
        out = ComfyUIBackend().generate(GenerationInput(prompt="hi"))
        assert out.images == []
        assert "P1" in out.metadata.get("prompt_id", "")

    def test_successful_run_returns_image(self, monkeypatch):
        def post(url, **kw):
            return _FakeResponse(200, body={"prompt_id": "P1"})

        def get(url, params=None, **kw):
            if url.endswith("/history/P1"):
                return _FakeResponse(
                    200,
                    body={"P1": {
                        "outputs": {"9": {"images": [
                            {"filename": "x.png", "subfolder": "", "type": "output"},
                        ]}},
                        "status": {"status_str": "success"},
                    }},
                )
            if url.endswith("/view"):
                return _FakeResponse(200, body=None, content=_png_bytes())
            return _FakeResponse(200, body={})

        _install_fake_requests(monkeypatch, post, get)
        out = ComfyUIBackend().generate(GenerationInput(prompt="hi"), asset_type="expression")
        assert len(out.images) == 1
        assert out.images[0].size == (8, 8)


class TestErrorPathsNoServer:
    def test_load_model_unreachable_is_nonfatal(self, monkeypatch):
        def get(url, **kw):
            raise ConnectionError("refused")

        _install_fake_requests(monkeypatch, lambda u, **kw: None, get)
        backend = ComfyUIBackend()
        backend.load_model()  # must not raise

    def test_load_model_missing_requests_is_nonfatal(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "requests", None)
        backend = ComfyUIBackend()
        backend.load_model()  # must not raise