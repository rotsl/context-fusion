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

## 3. UI Layout

The page has four main sections:

1. **Run Panel**
2. **Run Stats**
3. **Representation Usage / Selected Source Types**
4. **Context Preview**

## 4. Run Panel Inputs

### Input Mode

- `Directory`: process all supported files in one directory.
- `File list`: process explicit file paths you provide.

### Budget

- Token budget for retrieval/context selection.
- Must be greater than `0`.

### Directory Path (Directory mode)

- Absolute or relative path.
- Example: `./docs`

### File Paths (File list mode)

- One file path per line.
- Empty lines are ignored.

## 5. Example Runs

### Example A: Directory mode

1. Select `Input Mode = Directory`.
2. Set `Budget = 3000`.
3. Set `Directory Path = ./docs`.
4. Click `Run Pipeline`.

### Example B: File list mode

1. Select `Input Mode = File list`.
2. Set `Budget = 1200`.
3. Enter paths, one per line, for example:

```text
./README.md
./docs/architecture.md
./docs/algorithm.md
```

4. Click `Run Pipeline`.

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

## 7. API Behavior (for debugging)

- `GET /` returns the UI page.
- `POST /api/run` executes the pipeline.

`POST /api/run` request payload:

```json
{
  "mode": "directory",
  "budget": 3000,
  "directory": "./docs"
}
```

Or:

```json
{
  "mode": "files",
  "budget": 1200,
  "file_paths": ["./README.md", "./docs/cli.md"]
}
```

## 8. Common Errors and Fixes

### `directory is required`

You selected `Directory` mode but did not provide a directory.

### `at least one file path is required`

You selected `File list` mode but did not provide any valid path lines.

### `budget must be greater than zero`

Set budget to a positive integer.

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

Press `Ctrl+C` in the terminal where the server is running.
