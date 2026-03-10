# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Local Web UI for pipeline visualization."""

from __future__ import annotations

import json
from collections import Counter
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .orchestration.runner import PipelineRunner

HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ContextFusion Web UI</title>
  <style>
    :root {
      --bg: #0f172a;
      --panel: #111827;
      --card: #1f2937;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #34d399;
      --accent-2: #60a5fa;
      --danger: #f87171;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, -apple-system, Segoe UI, Helvetica, Arial, sans-serif;
      background: radial-gradient(1200px 600px at 20% -20%, #1e293b 10%, var(--bg) 60%);
      color: var(--text);
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 24px; }
    h1 { margin: 0 0 4px; font-size: 1.8rem; }
    .sub { color: var(--muted); margin-bottom: 20px; }
    .panel {
      background: linear-gradient(145deg, #111827, #0b1220);
      border: 1px solid #1f2a3a;
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 16px;
    }
    .grid { display: grid; gap: 12px; }
    .grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    @media (max-width: 900px) {
      .grid-2, .grid-3 { grid-template-columns: 1fr; }
    }
    label { display: block; margin-bottom: 6px; color: var(--muted); font-size: 0.9rem; }
    input, select, textarea, button {
      width: 100%;
      border-radius: 10px;
      border: 1px solid #334155;
      background: #0b1220;
      color: var(--text);
      padding: 10px 12px;
      font-size: 0.95rem;
    }
    textarea { min-height: 88px; resize: vertical; }
    .btn {
      cursor: pointer;
      background: linear-gradient(90deg, var(--accent), #10b981);
      border: none;
      color: #00120a;
      font-weight: 700;
    }
    .status { margin-top: 8px; min-height: 22px; color: var(--muted); }
    .status.error { color: var(--danger); }
    .cards { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }
    @media (max-width: 900px) { .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    .card {
      background: var(--card);
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 10px;
    }
    .card .k { color: var(--muted); font-size: 0.8rem; }
    .card .v { font-size: 1.15rem; font-weight: 700; margin-top: 2px; }
    .bars { display: grid; gap: 8px; }
    .bar-row { display: grid; grid-template-columns: 160px 1fr 56px; gap: 8px; align-items: center; }
    .bar-track { background: #0b1220; border: 1px solid #334155; border-radius: 999px; height: 10px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent-2), #38bdf8); }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: #0b1220;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 10px;
      max-height: 320px;
      overflow: auto;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>ContextFusion Web UI</h1>
    <div class="sub">Run the pipeline and visualize selection stats in your browser.</div>

    <div class="panel">
      <div class="grid grid-2">
        <div>
          <label for="mode">Input Mode</label>
          <select id="mode">
            <option value="directory" selected>Directory</option>
            <option value="files">File list</option>
          </select>
        </div>
        <div>
          <label for="budget">Budget</label>
          <input id="budget" type="number" min="1" value="3000">
        </div>
      </div>

      <div id="dir-input-wrap" style="margin-top: 10px;">
        <label for="directory">Directory Path</label>
        <input id="directory" type="text" placeholder="./examples/gui_input">
      </div>
      <div id="files-input-wrap" style="display:none; margin-top: 10px;">
        <label for="files">File Paths (one per line)</label>
        <textarea id="files" placeholder="/path/a.txt&#10;/path/b.md"></textarea>
      </div>

      <div style="margin-top: 12px;">
        <button id="run-btn" class="btn">Run Pipeline</button>
        <div id="status" class="status"></div>
      </div>
    </div>

    <div class="panel">
      <h3>Run Stats</h3>
      <div id="stats-cards" class="cards"></div>
    </div>

    <div class="grid grid-2">
      <div class="panel">
        <h3>Representation Usage</h3>
        <div id="rep-bars" class="bars"></div>
      </div>
      <div class="panel">
        <h3>Selected Source Types</h3>
        <div id="source-bars" class="bars"></div>
      </div>
    </div>

    <div class="panel">
      <h3>Context Preview</h3>
      <pre id="context-preview" class="mono"></pre>
    </div>
  </div>

  <script>
    const modeEl = document.getElementById("mode");
    const dirWrap = document.getElementById("dir-input-wrap");
    const filesWrap = document.getElementById("files-input-wrap");
    const runBtn = document.getElementById("run-btn");
    const statusEl = document.getElementById("status");

    modeEl.addEventListener("change", () => {
      const isDir = modeEl.value === "directory";
      dirWrap.style.display = isDir ? "block" : "none";
      filesWrap.style.display = isDir ? "none" : "block";
    });

    function setStatus(message, isError) {
      statusEl.textContent = message || "";
      statusEl.className = isError ? "status error" : "status";
    }

    function renderCards(stats) {
      const root = document.getElementById("stats-cards");
      root.innerHTML = "";
      const pairs = [
        ["Files", stats.files_ingested ?? 0],
        ["Segments", stats.segments_extracted ?? 0],
        ["Blocks Created", stats.blocks_created ?? 0],
        ["Blocks Selected", stats.blocks_selected ?? 0],
        ["Total Tokens", stats.total_tokens ?? 0],
      ];
      for (const [k, v] of pairs) {
        const el = document.createElement("div");
        el.className = "card";
        el.innerHTML = `<div class="k">${k}</div><div class="v">${v}</div>`;
        root.appendChild(el);
      }
    }

    function renderBars(elementId, data) {
      const root = document.getElementById(elementId);
      root.innerHTML = "";
      const entries = Object.entries(data || {});
      if (!entries.length) {
        root.innerHTML = "<div class='sub'>No data</div>";
        return;
      }
      const maxValue = Math.max(...entries.map(([, v]) => v), 1);
      for (const [name, value] of entries.sort((a, b) => b[1] - a[1])) {
        const width = (value / maxValue) * 100;
        const row = document.createElement("div");
        row.className = "bar-row";
        row.innerHTML = `
          <div class="mono">${name}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${width}%;"></div></div>
          <div class="mono">${value}</div>
        `;
        root.appendChild(row);
      }
    }

    runBtn.addEventListener("click", async () => {
      setStatus("Running...", false);
      runBtn.disabled = true;
      try {
        const mode = modeEl.value;
        const budget = Number(document.getElementById("budget").value || 3000);
        const payload = { mode, budget };
        if (mode === "directory") {
          payload.directory = document.getElementById("directory").value.trim();
        } else {
          payload.file_paths = document.getElementById("files").value
            .split("\\n")
            .map((x) => x.trim())
            .filter(Boolean);
        }

        const response = await fetch("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Request failed");
        }

        renderCards(data.stats || {});
        renderBars("rep-bars", data.representation_counts || {});
        renderBars("source-bars", data.source_type_counts || {});
        document.getElementById("context-preview").textContent = data.context_preview || "";
        setStatus("Run complete", false);
      } catch (err) {
        setStatus(err.message || String(err), true);
      } finally {
        runBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _html_response(handler: BaseHTTPRequestHandler, html: str) -> None:
    body = html.encode("utf-8")
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _build_response(result: dict) -> dict:
    portfolio = result["portfolio"]
    representation_counts = Counter(rep.value for rep in portfolio.representations_used.values())
    source_type_counts = Counter(block.source_type.name for block in portfolio.blocks)
    context = result.get("context", "")

    return {
        "stats": result.get("stats", {}),
        "representation_counts": dict(representation_counts),
        "source_type_counts": dict(source_type_counts),
        "context_preview": context[:6000],
    }


class _UIHandler(BaseHTTPRequestHandler):
    runner = PipelineRunner()

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep terminal output concise.
        return

    def do_GET(self) -> None:
        if self.path == "/":
            _html_response(self, HTML_PAGE)
            return
        _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:
        if self.path != "/api/run":
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
            payload = json.loads(raw.decode("utf-8"))

            mode = payload.get("mode", "directory")
            budget = int(payload.get("budget", 3000))
            if budget <= 0:
                raise ValueError("budget must be greater than zero")

            if mode == "directory":
                directory = (payload.get("directory") or "").strip()
                if not directory:
                    raise ValueError("directory is required")
                result = self.runner.run_on_directory(directory=directory, budget=budget)
            elif mode == "files":
                file_paths = payload.get("file_paths") or []
                if not isinstance(file_paths, list):
                    raise ValueError("file_paths must be a list")
                cleaned_paths = [str(path).strip() for path in file_paths if str(path).strip()]
                if not cleaned_paths:
                    raise ValueError("at least one file path is required")
                result = self.runner.run(file_paths=cleaned_paths, budget=budget)
            else:
                raise ValueError("mode must be 'directory' or 'files'")

            _json_response(self, HTTPStatus.OK, _build_response(result))
        except Exception as exc:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})


def run_web_ui(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Run local web UI server.

    Args:
        host: Host interface to bind.
        port: Port to listen on.
    """
    server = ThreadingHTTPServer((host, port), _UIHandler)
    print(f"ContextFusion Web UI running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
