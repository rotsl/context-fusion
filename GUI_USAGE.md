# ContextFusion GUI Usage Guide

This document explains how to use the built-in ContextFusion Web UI end-to-end.

## 1. Prerequisites

- You are in the repository root.
- Dependencies are installed.

```bash
make install-dev
```

## 2. Start the GUI

Start the server with CLI:

```bash
cpo ui --host <host> --port 8080
```

Or with Make:

```bash
make ui
```

Then open:

`http://<host>:8080`

### Local GUI on Port 8080 (exact commands)

From repository root:

```bash
cpo ui --host 0.0.0.0 --port 8080
```

In another terminal, verify health:

```bash
curl -fsS http://localhost:8080/api/health
```

Open in browser:

`http://localhost:8080`

Stop local GUI:

- close browser tabs/windows (auto-stop behavior), or
- press `Ctrl+C` in the terminal running `cpo ui`.

### GitHub Pages Public GUI (same layout)

The workflow `.github/workflows/gui-public.yml` deploys a public GUI page under `web/pages/index.html`.

- It mirrors the same section layout used by local GUI:
  1. Run Panel
  2. Run Stats
  3. Representation Usage / Selected Source Types
  4. Selected Blocks + Context Preview
  5. Model Answer
- The public GUI asks users to enter API key directly in the form.
- Because GitHub Pages is static, file input is done via browser file/folder picker (not local path strings).

## 3. UI Layout

The page has five main sections:

1. **Run Panel**
2. **Run Stats**
3. **Representation Usage / Selected Source Types**
4. **Selected Blocks + Context Preview**
5. **Model Answer (CF as middleware)**

## 4. Run Panel Inputs

### Input Mode

- `Directory`: process all supported files in one directory.
- `File list`: process explicit file paths you provide.

### Budget

- Token budget for retrieval/context selection.
- Must be greater than `0`.

### Task Mode

- Choose `chat`, `qa`, `code`, or `agent`.
- This is forwarded to the ContextFusion pipeline so the UI run uses the matching mode.

### Query / Task

- Optional query string to drive two-stage retrieval and scoring.
- Example: `Summarize differences between README and GUI placeholder content`.

### Provider / Model / Model Call

- `Provider`: `anthropic`, `openai`, `ollama`, or compatible aliases.
- `Model`: target model name for selected provider.
- `Call model after CF pipeline`: if enabled, UI runs:
  1. CF pipeline for context selection
  2. provider/model call using selected context packet
  3. model answer rendering in UI
- For this repo’s default API setup, use:
  - `Provider = anthropic`
  - `Model = claude-sonnet-4-6`

### Max Answer Tokens / Temperature

- Controls provider response length and randomness for model-call mode.

### Directory Path (Directory mode)

- Absolute or relative path.
- Accepts both directories and single files.
- Examples:
  - `./docs`
  - `./examples/gui_input/random.csv`
  - `/absolute/path/to/your/data`

### File Paths (File list mode)

- One file path per line.
- Empty lines are ignored.

## 5. Example Runs

### Example A: Directory mode

1. Select `Input Mode = Directory`.
2. Set `Task Mode = qa`.
3. Set `Query / Task = Summarize key facts from these files`.
4. Set `Directory Path = ./examples/gui_input`.
5. Set `Provider = anthropic`, `Model = claude-sonnet-4-6`.
6. Keep `Call model after CF pipeline` enabled.
7. Click `Run Pipeline`.

### Example B: File list mode

1. Select `Input Mode = File list`.
2. Set `Task Mode = chat`.
3. Set `Budget = 1200`.
3. Enter paths, one per line, for example:

```text
./README.md
./docs/architecture.md
./docs/algorithm.md
```

4. Set provider/model if you want model answer.
5. Click `Run Pipeline`.

## 6. Understanding the Output

### Run Stats cards

- `Files`: number of files ingested.
- `Segments`: raw extracted segments.
- `Blocks Created`: normalized context blocks.
- `Blocks Selected`: blocks chosen by optimizer.
- `Total Tokens`: selected context token count.

### Representation Usage

Shows which representations were chosen (for example `full_text`, `bullet_summary`, `citation_pointer`).

### Selected Source Types

Distribution of selected block source types (for example `TEXT`, `DOCUMENT`, `CODE`).

### Context Preview

Shows the assembled context string (truncated preview).

### Selected Blocks (Actual CF Output)

Shows the selected ContextFusion blocks with:
- source URI
- representation type
- token estimate
- score

### Model Answer (CF as Middleware)

- Shows the provider/model response after CF compilation.
- Includes provider, model, task mode, and input message count metadata.
- If `Call model after CF pipeline` is disabled, this panel notes model call was skipped.

## 7. API Behavior (for debugging)

- `GET /` returns the UI page.
- `POST /api/run` executes the pipeline.

`POST /api/run` request payload:

```json
{
  "mode": "directory",
  "budget": 3000,
  "directory": "./docs",
  "task_type": "qa",
  "query": "Summarize this content",
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
  "call_model": true,
  "max_answer_tokens": 256,
  "temperature": 0
}
```

Or:

```json
{
  "mode": "files",
  "budget": 1200,
  "file_paths": ["./README.md", "./docs/cli.md"],
  "task_type": "chat",
  "query": "Give me a short summary",
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
  "call_model": true
}
```

## 8. Common Errors and Fixes

### `directory is required`

You selected `Directory` mode but did not provide a directory.

### `directory path does not exist`

The supplied directory/file path does not exist on the machine where GUI server is running.

### `at least one file path is required`

You selected `File list` mode but did not provide any valid path lines.

### `budget must be greater than zero`

Set budget to a positive integer.

### Model call failed

Common causes:
- missing API key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.)
- invalid model name for selected provider
- provider service unavailable (for `ollama`, check local server is running)

### Port already in use

Start on a different port:

```bash
cpo ui --host <host> --port 8081
```

Then open `http://<host>:8081`.

## 9. Docker Option

You can also run the UI service via Docker Compose:

```bash
docker compose up cpo-ui
```

Then open:

`http://<host>:8080`

## 10. Stop the GUI

Close browser tabs/windows using the UI and the server will auto-stop.

You can also still stop manually with `Ctrl+C` in the terminal where the server is running.
