# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Minimal MCP-style HTTP server exposing ContextFusion tools."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .resources import list_resources
from .tools import context_ablate, context_compile, context_memory, context_plan, context_search


class _MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _json_response(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/resources":
            self._json_response(HTTPStatus.OK, {"resources": list_resources()})
            return
        self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        payload = json.loads(raw.decode("utf-8"))

        try:
            if self.path == "/tools/context.search":
                result = context_search(payload.get("query", ""), int(payload.get("limit", 10)))
            elif self.path == "/tools/context.compile":
                result = context_compile(
                    payload.get("file_paths", []),
                    int(payload.get("budget", 3000)),
                    str(payload.get("provider", "openai")),
                    str(payload.get("model", "gpt-4o-mini")),
                    str(payload.get("mode", "chat")),
                )
            elif self.path == "/tools/context.plan":
                result = context_plan(payload.get("task", ""), int(payload.get("budget", 8000)))
            elif self.path == "/tools/context.memory":
                result = context_memory(payload.get("query"), int(payload.get("limit", 10)))
            elif self.path == "/tools/context.ablate":
                result = context_ablate(
                    payload.get("file_paths", []), int(payload.get("budget", 3000))
                )
            else:
                self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})
                return

            self._json_response(HTTPStatus.OK, result)
        except Exception as exc:
            self._json_response(HTTPStatus.BAD_REQUEST, {"error": str(exc)})


def run_mcp_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run MCP-style HTTP server."""
    server = ThreadingHTTPServer((host, port), _MCPHandler)
    print(f"ContextFusion MCP server running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
