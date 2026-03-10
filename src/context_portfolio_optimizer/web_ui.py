# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Local Web UI for pipeline visualization."""

from __future__ import annotations

import json
import os
import threading
import time
from collections import Counter
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .assembly.compiler import compile_packet
from .orchestration.runner import PipelineRunner
from .providers.registry import ProviderRegistry

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-6",
    "openai": "gpt-5-mini",
    "ollama": "llama3.1",
    "openai_compatible": "gpt-4o-mini",
    "grok": "grok-2-latest",
    "kimi": "kimi-k2",
    "deepseek": "deepseek-chat",
    "together": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "groq": "llama-3.1-70b-versatile",
}

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
    .inline-check {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 10px;
    }
    .inline-check input {
      width: auto;
      margin: 0;
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
      <div class="grid grid-3">
        <div>
          <label for="mode">Input Mode</label>
          <select id="mode">
            <option value="directory" selected>Directory</option>
            <option value="files">File list</option>
          </select>
        </div>
        <div>
          <label for="task-type">Task Mode</label>
          <select id="task-type">
            <option value="chat" selected>Chat</option>
            <option value="qa">QA</option>
            <option value="code">Code</option>
            <option value="agent">Agent</option>
          </select>
        </div>
        <div>
          <label for="budget">Budget</label>
          <input id="budget" type="number" min="1" value="3000">
        </div>
      </div>
      <div style="margin-top: 10px;">
        <label for="query">Query / Task</label>
        <input id="query" type="text" placeholder="Summarize key points from this directory">
      </div>
      <div class="grid grid-3" style="margin-top: 10px;">
        <div>
          <label for="provider">Provider</label>
          <select id="provider">
            <option value="anthropic" selected>Anthropic (Claude)</option>
            <option value="openai">OpenAI</option>
            <option value="ollama">Ollama (Local)</option>
            <option value="openai_compatible">OpenAI-Compatible</option>
            <option value="grok">Grok</option>
            <option value="kimi">Kimi</option>
            <option value="deepseek">DeepSeek</option>
            <option value="together">Together</option>
            <option value="groq">Groq</option>
          </select>
        </div>
        <div>
          <label for="model">Model</label>
          <input id="model" type="text" value="claude-sonnet-4-6" placeholder="claude-sonnet-4-6">
        </div>
        <div>
          <label for="max-answer-tokens">Max Answer Tokens</label>
          <input id="max-answer-tokens" type="number" min="1" value="256">
        </div>
      </div>
      <div class="grid grid-2" style="margin-top: 10px;">
        <div>
          <label for="temperature">Temperature</label>
          <input id="temperature" type="number" min="0" max="2" step="0.1" value="0">
        </div>
        <div class="inline-check">
          <input id="call-model" type="checkbox" checked>
          <label for="call-model" style="margin: 0;">Call model after CF pipeline (uses API keys)</label>
        </div>
      </div>

      <div id="dir-input-wrap" style="margin-top: 10px;">
        <label for="directory">Directory or File Path (relative or absolute)</label>
        <input id="directory" type="text" placeholder="./examples/gui_input or /abs/path/to/file.csv">
      </div>
      <div id="files-input-wrap" style="display:none; margin-top: 10px;">
        <label for="files">File Paths (one per line, relative or absolute)</label>
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
      <h3>Selected Blocks (Actual CF Output)</h3>
      <pre id="selected-blocks" class="mono"></pre>
    </div>

    <div class="panel">
      <h3>Context Preview</h3>
      <pre id="context-preview" class="mono"></pre>
    </div>
    <div class="panel">
      <h3>Model Answer (CF as Middleware)</h3>
      <pre id="model-answer" class="mono"></pre>
    </div>
  </div>

  <script>
    const modeEl = document.getElementById("mode");
    const taskTypeEl = document.getElementById("task-type");
    const providerEl = document.getElementById("provider");
    const dirWrap = document.getElementById("dir-input-wrap");
    const filesWrap = document.getElementById("files-input-wrap");
    const runBtn = document.getElementById("run-btn");
    const statusEl = document.getElementById("status");
    const clientId = (window.crypto && window.crypto.randomUUID)
      ? window.crypto.randomUUID()
      : `cf-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    let heartbeatTimer = null;

    modeEl.addEventListener("change", () => {
      const isDir = modeEl.value === "directory";
      dirWrap.style.display = isDir ? "block" : "none";
      filesWrap.style.display = isDir ? "none" : "block";
    });

    const defaultModelByProvider = {
      anthropic: "claude-sonnet-4-6",
      openai: "gpt-5-mini",
      ollama: "llama3.1",
      openai_compatible: "gpt-4o-mini",
      grok: "grok-2-latest",
      kimi: "kimi-k2",
      deepseek: "deepseek-chat",
      together: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
      groq: "llama-3.1-70b-versatile",
    };

    providerEl.addEventListener("change", () => {
      const modelInput = document.getElementById("model");
      const selected = providerEl.value;
      if (!modelInput.value || modelInput.value === defaultModelByProvider[modelInput.dataset.lastProvider || ""]) {
        modelInput.value = defaultModelByProvider[selected] || "";
      }
      modelInput.dataset.lastProvider = selected;
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

    function renderSelectedBlocks(blocks) {
      const root = document.getElementById("selected-blocks");
      if (!blocks || !blocks.length) {
        root.textContent = "No selected blocks.";
        return;
      }

      const lines = blocks.map((block, index) =>
        `${index + 1}. ${block.source_uri} | rep=${block.representation_type} | tokens=${block.tokens_est} | score=${block.score.toFixed(4)}`
      );
      root.textContent = lines.join("\\n");
    }

    function renderModelAnswer(payload) {
      const root = document.getElementById("model-answer");
      if (payload.model_error) {
        root.textContent = `Model call failed: ${payload.model_error}`;
        return;
      }
      if (!payload.model_answer) {
        root.textContent = "Model call skipped. Enable 'Call model after CF pipeline'.";
        return;
      }
      const info = payload.model_info || {};
      const meta = [
        `provider=${info.provider || "n/a"}`,
        `model=${info.model || "n/a"}`,
        `task_mode=${info.task_type || "n/a"}`,
        `input_messages=${info.input_messages ?? "n/a"}`,
      ].join(" | ");
      root.textContent = `${payload.model_answer}\\n\\n---\\n${meta}`;
    }

    async function postLifecycle(path, useBeacon = false) {
      const payload = JSON.stringify({ client_id: clientId });
      if (useBeacon && navigator.sendBeacon) {
        const blob = new Blob([payload], { type: "application/json" });
        navigator.sendBeacon(path, blob);
        return;
      }
      await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload,
        keepalive: true,
      });
    }

    async function startSession() {
      try {
        await postLifecycle("/api/connect");
      } catch (_) {
        // Lifecycle transport should not block UI usage.
      }
      heartbeatTimer = window.setInterval(async () => {
        try {
          await postLifecycle("/api/heartbeat");
        } catch (_) {
          // Ignore transient failures.
        }
      }, 4000);
    }

    function endSession() {
      if (heartbeatTimer) {
        window.clearInterval(heartbeatTimer);
      }
      postLifecycle("/api/disconnect", true);
    }

    runBtn.addEventListener("click", async () => {
      setStatus("Running...", false);
      runBtn.disabled = true;
      try {
        const mode = modeEl.value;
        const taskType = taskTypeEl.value;
        const query = document.getElementById("query").value.trim();
        const budget = Number(document.getElementById("budget").value || 3000);
        const payload = {
          mode,
          budget,
          task_type: taskType,
          query,
          provider: document.getElementById("provider").value,
          model: document.getElementById("model").value.trim(),
          call_model: document.getElementById("call-model").checked,
          max_answer_tokens: Number(document.getElementById("max-answer-tokens").value || 256),
          temperature: Number(document.getElementById("temperature").value || 0),
        };
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
        renderSelectedBlocks(data.selected_blocks || []);
        document.getElementById("context-preview").textContent = data.context_preview || "";
        renderModelAnswer(data);
        if (data.model_error) {
          setStatus("Pipeline complete (model call failed)", true);
        } else {
          setStatus("Run complete", false);
        }
      } catch (err) {
        setStatus(err.message || String(err), true);
      } finally {
        runBtn.disabled = false;
      }
    });

    window.addEventListener("beforeunload", endSession);
    window.addEventListener("pagehide", endSession);
    startSession();
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


def _load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE entries from a local .env file into process env."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_key = key.strip()
        env_value = value.strip().strip("'").strip('"')
        if env_key and env_key not in os.environ:
            os.environ[env_key] = env_value


def _provider_chat_kwargs(provider: str, max_tokens: int, temperature: float) -> dict[str, Any]:
    """Map generic UI model options to provider-specific chat kwargs."""
    p = provider.lower().strip()
    safe_max_tokens = max(1, max_tokens)
    safe_temperature = max(0.0, min(2.0, temperature))

    if p == "anthropic":
        return {"max_tokens": safe_max_tokens, "temperature": safe_temperature}
    if p == "openai":
        return {"max_output_tokens": safe_max_tokens, "temperature": safe_temperature}
    if p == "ollama":
        return {"options": {"temperature": safe_temperature, "num_predict": safe_max_tokens}}
    if p in {"openai_compatible", "grok", "kimi", "deepseek", "together", "groq"}:
        return {"max_tokens": safe_max_tokens, "temperature": safe_temperature}
    return {"temperature": safe_temperature}


def _call_model_with_cf(
    *,
    context_packet: Any,
    provider_name: str,
    model_name: str,
    task_type: str,
    query: str | None,
    max_answer_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    """Run provider call using compiled ContextFusion packet as middleware."""
    provider_key = provider_name.lower().strip()
    if not provider_key:
        raise ValueError("provider is required when call_model is enabled")

    model = model_name.strip() or DEFAULT_MODELS.get(provider_key, "")
    if not model:
        raise ValueError("model is required when call_model is enabled")

    compiled = compile_packet(
        packet=context_packet,
        provider=provider_key,
        model=model,
        mode=task_type,
    )

    # Ensure at least one user turn exists for providers that require a user message.
    messages = list(compiled.get("messages", []))
    user_prompt = (query or context_packet.task or "Answer using only provided context.").strip()
    messages.append({"role": "user", "content": user_prompt})

    provider = ProviderRegistry.get(provider_key)
    kwargs = _provider_chat_kwargs(provider_key, max_answer_tokens, temperature)
    response = provider.chat(messages=messages, model=model, **kwargs)

    return {
        "answer": str(response.get("content", "") or "").strip(),
        "info": {
            "provider": provider_key,
            "model": model,
            "task_type": task_type,
            "input_messages": len(messages),
        },
    }


def _build_response(result: dict) -> dict:
    portfolio = result["portfolio"]
    representation_counts = Counter(rep.value for rep in portfolio.representations_used.values())
    source_type_counts = Counter(block.source_type.name for block in portfolio.blocks)
    context = result.get("context", "")
    packet = result.get("context_packet")
    selected_blocks: list[dict[str, object]] = []
    if packet is not None:
        selected_blocks = [
            {
                "block_id": block.block_id,
                "source_uri": block.source_uri,
                "representation_type": block.representation_type,
                "tokens_est": block.tokens_est,
                "score": block.score,
            }
            for block in packet.selected_blocks
        ]

    return {
        "stats": result.get("stats", {}),
        "representation_counts": dict(representation_counts),
        "source_type_counts": dict(source_type_counts),
        "selected_blocks": selected_blocks,
        "context_preview": context[:6000],
    }


class _UIHandler(BaseHTTPRequestHandler):
    runner = PipelineRunner()
    clients: dict[str, float] = {}
    clients_lock = threading.Lock()
    saw_client = False
    last_client_event = time.monotonic()
    shutdown_requested = False
    client_timeout_seconds = 12.0
    shutdown_grace_seconds = 3.0

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep terminal output concise.
        return

    @classmethod
    def _prune_stale_clients(cls, now: float) -> None:
        stale = [
            client_id
            for client_id, ts in cls.clients.items()
            if now - ts > cls.client_timeout_seconds
        ]
        for client_id in stale:
            cls.clients.pop(client_id, None)

    @classmethod
    def _touch_client(cls, client_id: str) -> int:
        now = time.monotonic()
        with cls.clients_lock:
            cls._prune_stale_clients(now)
            cls.clients[client_id] = now
            cls.saw_client = True
            cls.last_client_event = now
            cls.shutdown_requested = False
            return len(cls.clients)

    @classmethod
    def _disconnect_client(cls, client_id: str) -> int:
        now = time.monotonic()
        with cls.clients_lock:
            cls.clients.pop(client_id, None)
            cls._prune_stale_clients(now)
            cls.last_client_event = now
            return len(cls.clients)

    @classmethod
    def shutdown_if_idle(cls, server: ThreadingHTTPServer) -> bool:
        now = time.monotonic()
        with cls.clients_lock:
            cls._prune_stale_clients(now)
            no_clients = len(cls.clients) == 0
            should_shutdown = (
                cls.saw_client
                and no_clients
                and not cls.shutdown_requested
                and (now - cls.last_client_event) >= cls.shutdown_grace_seconds
            )
            if not should_shutdown:
                return False
            cls.shutdown_requested = True

        server.shutdown()
        return True

    def do_GET(self) -> None:
        if self.path == "/":
            _html_response(self, HTML_PAGE)
            return
        if self.path == "/api/health":
            _json_response(self, HTTPStatus.OK, {"status": "ok"})
            return
        _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:
        if self.path not in {"/api/run", "/api/connect", "/api/heartbeat", "/api/disconnect"}:
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
            payload = json.loads(raw.decode("utf-8"))

            if self.path in {"/api/connect", "/api/heartbeat", "/api/disconnect"}:
                client_id = str(payload.get("client_id", "")).strip()
                if not client_id:
                    raise ValueError("client_id is required")

                if self.path == "/api/disconnect":
                    active_clients = self._disconnect_client(client_id)
                else:
                    active_clients = self._touch_client(client_id)

                _json_response(
                    self,
                    HTTPStatus.OK,
                    {"ok": True, "active_clients": active_clients},
                )
                return

            mode = payload.get("mode", "directory")
            budget = int(payload.get("budget", 3000))
            task_type = str(payload.get("task_type", "chat")).strip().lower() or "chat"
            if task_type not in {"chat", "qa", "code", "agent"}:
                raise ValueError("task_type must be one of: chat, qa, code, agent")
            query = str(payload.get("query", "")).strip() or None
            provider_name = str(payload.get("provider", "anthropic")).strip().lower() or "anthropic"
            model_name = str(payload.get("model", "")).strip() or DEFAULT_MODELS.get(
                provider_name, ""
            )
            call_model = bool(payload.get("call_model", True))
            max_answer_tokens = int(payload.get("max_answer_tokens", 256))
            if max_answer_tokens <= 0:
                raise ValueError("max_answer_tokens must be greater than zero")
            temperature = float(payload.get("temperature", 0.0))
            if budget <= 0:
                raise ValueError("budget must be greater than zero")

            if mode == "directory":
                directory = (payload.get("directory") or "").strip()
                if not directory:
                    raise ValueError("directory is required")
                input_path = Path(directory)
                if not input_path.exists():
                    raise ValueError("directory path does not exist")

                if input_path.is_file():
                    # Be forgiving in UI: if a file is entered in Directory mode,
                    # run a single-file pipeline instead of returning empty output.
                    result = self.runner.run(
                        file_paths=[str(input_path)],
                        budget=budget,
                        query=query,
                        task=query or f"{task_type}_ui_run",
                        task_type=task_type,
                    )
                else:
                    result = self.runner.run_on_directory(
                        directory=directory,
                        budget=budget,
                        query=query,
                        task=query or f"{task_type}_ui_run",
                        task_type=task_type,
                    )
            elif mode == "files":
                file_paths = payload.get("file_paths") or []
                if not isinstance(file_paths, list):
                    raise ValueError("file_paths must be a list")
                cleaned_paths = [str(path).strip() for path in file_paths if str(path).strip()]
                if not cleaned_paths:
                    raise ValueError("at least one file path is required")
                result = self.runner.run(
                    file_paths=cleaned_paths,
                    budget=budget,
                    query=query,
                    task=query or f"{task_type}_ui_run",
                    task_type=task_type,
                )
            else:
                raise ValueError("mode must be 'directory' or 'files'")

            response_payload = _build_response(result)
            if call_model:
                try:
                    model_result = _call_model_with_cf(
                        context_packet=result["context_packet"],
                        provider_name=provider_name,
                        model_name=model_name,
                        task_type=task_type,
                        query=query,
                        max_answer_tokens=max_answer_tokens,
                        temperature=temperature,
                    )
                    response_payload["model_answer"] = model_result["answer"]
                    response_payload["model_info"] = model_result["info"]
                except Exception as model_exc:
                    response_payload["model_error"] = str(model_exc)

            _json_response(self, HTTPStatus.OK, response_payload)
        except Exception as exc:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})


def run_web_ui(host: str = "localhost", port: int = 8080) -> None:
    """Run local web UI server.

    Args:
        host: Host interface to bind.
        port: Port to listen on.
    """
    _load_env_file(Path(".env"))
    server = ThreadingHTTPServer((host, port), _UIHandler)
    stop_event = threading.Event()

    def _idle_watchdog() -> None:
        while not stop_event.is_set():
            time.sleep(1.0)
            if _UIHandler.shutdown_if_idle(server):
                break

    watchdog_thread = threading.Thread(target=_idle_watchdog, daemon=True)
    watchdog_thread.start()

    print(f"ContextFusion Web UI running at http://{host}:{port}")
    print("Close browser to auto-stop or press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        server.server_close()
