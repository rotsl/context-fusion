# ContextFusion NPM CLI (User Guide)

Use this package if you want a simple npm entrypoint for ContextFusion, without Python dev tooling.

## What You Can Do

- `contextfusion setup`
- `contextfusion env`
- `contextfusion run`
- `contextfusion compile`
- `contextfusion ui`
- `contextfusion serve-mcp`

## Requirements

- Node.js 18+
- Python 3.11+

## Install

If you are using this repository locally:

```bash
npm install -g ./npm-package
```

If installed from npm:

```bash
npx @rotsl/contextfusion setup
```

## First-Time Setup

```bash
contextfusion setup
```

This command:
- installs the ContextFusion Python package (if missing)
- creates a `.env` template in your current folder

Then add your API key(s), for example:

```env
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

## Common Commands

Run pipeline:

```bash
contextfusion run ./examples/gui_input --query "Summarize" --provider anthropic --model claude-sonnet-4-6
```

Compile provider-ready context packet:

```bash
contextfusion compile ./docs --mode qa --provider anthropic --model claude-sonnet-4-6
```

Start Web UI:

```bash
contextfusion ui --host 0.0.0.0 --port 8080
```

Start MCP server:

```bash
contextfusion serve-mcp --host 0.0.0.0 --port 8765
```

Create or refresh `.env` template:

```bash
contextfusion env
```

## Troubleshooting

- If command is not found after install, restart your shell.
- If Python package is missing, run `contextfusion setup` again.
- If model calls fail, verify API keys in `.env`.

## License

Apache-2.0. See [LICENSE](LICENSE).
