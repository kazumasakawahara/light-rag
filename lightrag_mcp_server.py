#!/usr/bin/env python
"""LightRAG MCP Server — minimal MCP interface for Claude Desktop.

Exposes three tools against a running LightRAG API server:
  - lightrag_query:  Query the knowledge graph (all retrieval modes)
  - lightrag_insert: Insert text into the knowledge graph
  - lightrag_health: Check server health and pipeline status

Environment variables:
  LIGHTRAG_URL      Base URL for the LightRAG API server.
                    Default: http://localhost:9621
  LIGHTRAG_API_KEY  Optional. If set, sent as the X-API-Key header on
                    every request. Required when the LightRAG server
                    is started with LIGHTRAG_API_KEY configured in
                    its own .env file.

Install:
  uv sync --extra mcp

Claude Desktop configuration (~/Library/Application Support/Claude/claude_desktop_config.json):
  {
    "mcpServers": {
      "lightrag": {
        "command": "/absolute/path/to/LightRAG/.venv/bin/python",
        "args": ["/absolute/path/to/LightRAG/lightrag_mcp_server.py"],
        "env": {
          "LIGHTRAG_URL": "http://localhost:9621",
          "LIGHTRAG_API_KEY": "your-api-key-if-configured"
        }
      }
    }
  }
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

LIGHTRAG_BASE_URL = os.environ.get("LIGHTRAG_URL", "http://localhost:9621").rstrip("/")
LIGHTRAG_API_KEY = os.environ.get("LIGHTRAG_API_KEY") or None
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("LIGHTRAG_MCP_TIMEOUT", "180"))

app = Server("lightrag")


def _auth_headers() -> dict[str, str]:
    if LIGHTRAG_API_KEY:
        return {"X-API-Key": LIGHTRAG_API_KEY}
    return {}


async def _api_call(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make an HTTP call to the LightRAG API server.

    Raises:
        httpx.ConnectError: LightRAG server unreachable.
        httpx.HTTPStatusError: Server returned a non-2xx status.
    """
    url = f"{LIGHTRAG_BASE_URL}{path}"
    headers = _auth_headers()
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        if method == "GET":
            resp = await client.get(url, headers=headers)
        else:
            resp = await client.post(url, json=body or {}, headers=headers)
        resp.raise_for_status()
        return resp.json()


# ── Tool definitions ──────────────────────────────────────────────


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="lightrag_query",
            description=(
                "Query the LightRAG knowledge graph. "
                "Modes: local (entity-focused), global (broad), "
                "hybrid (combined), naive (vector only), mix (KG+vector). "
                "Returns an answer synthesized from stored documents."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question to ask the knowledge graph",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["local", "global", "hybrid", "naive", "mix"],
                        "default": "hybrid",
                        "description": "Retrieval mode",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="lightrag_insert",
            description="Insert text content into the LightRAG knowledge graph for indexing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to insert into the knowledge graph",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="lightrag_health",
            description="Check LightRAG server health and pipeline status.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


def _error_text(message: str) -> list[TextContent]:
    return [TextContent(type="text", text=message)]


def _format_http_error(exc: httpx.HTTPStatusError) -> str:
    code = exc.response.status_code
    if code in (401, 403):
        if LIGHTRAG_API_KEY:
            return (
                f"Auth error ({code}): the configured LIGHTRAG_API_KEY was "
                f"rejected by the LightRAG server at {LIGHTRAG_BASE_URL}. "
                "Verify that the key matches the server's LIGHTRAG_API_KEY."
            )
        return (
            f"Auth error ({code}): the LightRAG server at {LIGHTRAG_BASE_URL} "
            "requires authentication, but LIGHTRAG_API_KEY is not set in this "
            "MCP server's environment. Set LIGHTRAG_API_KEY and restart."
        )
    body = exc.response.text
    if len(body) > 500:
        body = body[:500] + "... (truncated)"
    return f"API error {code}: {body}"


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name == "lightrag_query":
            if "query" not in arguments or not arguments["query"]:
                return _error_text("Error: 'query' argument is required and non-empty.")
            result = await _api_call(
                "POST",
                "/query",
                {
                    "query": arguments["query"],
                    "mode": arguments.get("mode", "hybrid"),
                    "stream": False,
                },
            )
            response_text = result.get(
                "response", json.dumps(result, ensure_ascii=False)
            )
            return [TextContent(type="text", text=response_text)]

        elif name == "lightrag_insert":
            if "text" not in arguments or not arguments["text"]:
                return _error_text("Error: 'text' argument is required and non-empty.")
            result = await _api_call(
                "POST", "/documents/text", {"text": arguments["text"]}
            )
            return [
                TextContent(type="text", text=json.dumps(result, ensure_ascii=False))
            ]

        elif name == "lightrag_health":
            health = await _api_call("GET", "/health")
            pipeline = await _api_call("GET", "/documents/pipeline_status")
            summary = {
                "server": "online",
                "base_url": LIGHTRAG_BASE_URL,
                "health": health,
                "pipeline_busy": pipeline.get("busy", False),
                "pipeline_progress": f"{pipeline.get('cur_batch', 0)}/{pipeline.get('batchs', 0)} docs",
                "chunk_progress": (
                    f"{pipeline.get('processed_chunks', 0)}/"
                    f"{pipeline.get('total_chunks', 0)} chunks"
                ),
                "current_phase": pipeline.get("current_phase", "idle"),
            }
            return [
                TextContent(
                    type="text", text=json.dumps(summary, ensure_ascii=False, indent=2)
                )
            ]

        else:
            return _error_text(f"Unknown tool: {name}")

    except httpx.ConnectError:
        return _error_text(
            f"Connection error: LightRAG server at {LIGHTRAG_BASE_URL} is not "
            "reachable. Ensure it is running (e.g. `docker compose up -d` or "
            "`lightrag-server`)."
        )
    except httpx.TimeoutException:
        return _error_text(
            f"Timeout: LightRAG API did not respond within "
            f"{REQUEST_TIMEOUT_SECONDS:.0f}s. The query may be too large or "
            "the server may be overloaded."
        )
    except httpx.HTTPStatusError as exc:
        return _error_text(_format_http_error(exc))
    except Exception as exc:
        return _error_text(f"Unexpected error: {type(exc).__name__}: {exc}")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
