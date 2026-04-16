"""Unit tests for lightrag_mcp_server helper functions.

Covers only the pure helpers that do not depend on an MCP runtime or
network. End-to-end testing (the MCP protocol handshake + live LightRAG
server) is out of scope for this file.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import httpx
import pytest


@pytest.fixture
def mcp_module(monkeypatch):
    """Load lightrag_mcp_server.py fresh each test with clean env.

    The module reads env vars at import time, so tests that need specific
    LIGHTRAG_* values must set them via monkeypatch *before* invoking this
    fixture.
    """
    repo_root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "lightrag_mcp_server_under_test",
        repo_root / "lightrag_mcp_server.py",
    )
    mod = importlib.util.module_from_spec(spec)
    # Keep a reference so garbage collection doesn't close the module mid-test.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    yield mod
    sys.modules.pop(spec.name, None)


@pytest.mark.offline
def test_auth_headers_empty_when_no_key(monkeypatch, mcp_module):
    """No LIGHTRAG_API_KEY → no X-API-Key header is attached."""
    monkeypatch.delenv("LIGHTRAG_API_KEY", raising=False)
    # Reset the module-level constant to reflect current env
    mcp_module.LIGHTRAG_API_KEY = None
    assert mcp_module._auth_headers() == {}


@pytest.mark.offline
def test_auth_headers_includes_api_key(mcp_module):
    """With LIGHTRAG_API_KEY set, the X-API-Key header is populated."""
    mcp_module.LIGHTRAG_API_KEY = "sk-test-key"
    assert mcp_module._auth_headers() == {"X-API-Key": "sk-test-key"}


@pytest.mark.offline
def test_error_text_wraps_message(mcp_module):
    """_error_text returns a single TextContent with the given message."""
    result = mcp_module._error_text("boom")
    assert len(result) == 1
    assert result[0].type == "text"
    assert result[0].text == "boom"


def _make_status_error(code: int, body: str = "") -> httpx.HTTPStatusError:
    """Build an httpx.HTTPStatusError with a real response object."""
    request = httpx.Request("GET", "http://test/api")
    response = httpx.Response(status_code=code, text=body, request=request)
    return httpx.HTTPStatusError("status", request=request, response=response)


@pytest.mark.offline
def test_format_http_error_401_without_api_key_tells_user_to_set_it(mcp_module):
    """401 without a configured key produces a hint to set LIGHTRAG_API_KEY."""
    mcp_module.LIGHTRAG_API_KEY = None
    msg = mcp_module._format_http_error(_make_status_error(401))
    assert "401" in msg
    assert "LIGHTRAG_API_KEY is not set" in msg


@pytest.mark.offline
def test_format_http_error_403_with_api_key_flags_rejection(mcp_module):
    """403 with a configured key hints the key was rejected by the server."""
    mcp_module.LIGHTRAG_API_KEY = "sk-wrong"
    msg = mcp_module._format_http_error(_make_status_error(403))
    assert "403" in msg
    assert "rejected" in msg


@pytest.mark.offline
def test_format_http_error_other_code_includes_body(mcp_module):
    """Non-auth errors include the response body (truncated if long)."""
    msg = mcp_module._format_http_error(_make_status_error(500, "internal fail"))
    assert "500" in msg
    assert "internal fail" in msg


@pytest.mark.offline
def test_format_http_error_truncates_long_body(mcp_module):
    """Bodies over 500 chars are truncated with a marker."""
    long_body = "x" * 800
    msg = mcp_module._format_http_error(_make_status_error(502, long_body))
    assert "... (truncated)" in msg
    # Truncation keeps first 500 chars of the body
    assert "x" * 500 in msg
    assert "x" * 800 not in msg


@pytest.mark.offline
def test_list_tools_exposes_three_tools(mcp_module):
    """list_tools must advertise exactly the three documented tools."""
    # list_tools is decorated by MCP; the underlying coroutine is stored
    # on the decorator. Call it via the module-level accessor when possible.
    # Simpler: check the Server's registered tool names via the app.
    import asyncio

    # Find the underlying coroutine function that MCP registered.
    # The @app.list_tools() decorator wraps but preserves the callable at
    # module scope under its original name.
    tools = asyncio.run(mcp_module.list_tools())
    names = {t.name for t in tools}
    assert names == {"lightrag_query", "lightrag_insert", "lightrag_health"}


@pytest.mark.offline
def test_query_tool_schema_requires_query(mcp_module):
    """lightrag_query schema marks 'query' as required."""
    import asyncio

    tools = asyncio.run(mcp_module.list_tools())
    query_tool = next(t for t in tools if t.name == "lightrag_query")
    assert "query" in query_tool.inputSchema["required"]
    # mode is optional with an enum
    assert query_tool.inputSchema["properties"]["mode"]["enum"] == [
        "local",
        "global",
        "hybrid",
        "naive",
        "mix",
    ]


@pytest.mark.offline
def test_api_call_attaches_auth_header(mcp_module, monkeypatch):
    """_api_call passes auth headers to the underlying httpx client."""
    import asyncio

    mcp_module.LIGHTRAG_API_KEY = "sk-test"

    captured = {}

    class FakeResponse:
        def __init__(self):
            self.status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, url, headers=None):
            captured["method"] = "GET"
            captured["url"] = url
            captured["headers"] = headers
            return FakeResponse()

        async def post(self, url, json=None, headers=None):
            captured["method"] = "POST"
            captured["url"] = url
            captured["body"] = json
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr(mcp_module.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(mcp_module._api_call("GET", "/health"))
    assert result == {"ok": True}
    assert captured["method"] == "GET"
    assert captured["url"] == f"{mcp_module.LIGHTRAG_BASE_URL}/health"
    assert captured["headers"] == {"X-API-Key": "sk-test"}


@pytest.mark.offline
def test_api_call_no_auth_header_when_key_missing(mcp_module, monkeypatch):
    """_api_call omits X-API-Key when no key is configured."""
    import asyncio

    mcp_module.LIGHTRAG_API_KEY = None
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, json=None, headers=None):
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr(mcp_module.httpx, "AsyncClient", FakeClient)
    asyncio.run(mcp_module._api_call("POST", "/query", {"query": "hi"}))
    # No X-API-Key key present in headers
    assert "X-API-Key" not in (captured["headers"] or {})


@pytest.mark.offline
def test_base_url_strips_trailing_slash(mcp_module):
    """Trailing slashes in LIGHTRAG_URL must be stripped to avoid // in paths."""
    assert not mcp_module.LIGHTRAG_BASE_URL.endswith("/")
