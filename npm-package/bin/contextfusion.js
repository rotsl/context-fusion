#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { delimiter, dirname, join, resolve } from "node:path";
import { existsSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const localSrc = join(repoRoot, "src");
const hasLocalSource = existsSync(
  join(localSrc, "context_portfolio_optimizer", "__init__.py"),
);

const args = process.argv.slice(2);

function printHelp() {
  console.log(`
ContextFusion npm CLI (general users)

Usage:
  contextfusion setup
  contextfusion env [--force]
  contextfusion run <path> [cpo options...]
  contextfusion compile <path> [cpo options...]
  contextfusion ui [cpo options...]
  contextfusion serve-mcp [cpo options...]
  contextfusion <any-cpo-command> [args...]

What this wrapper does:
  - delegates to Python CLI: cpo
  - creates .env template for API keys
  - supports key user commands from README ("What Most Users Need")

Examples:
  contextfusion setup
  contextfusion run ./examples/gui_input --provider anthropic --model claude-sonnet-4-6 --query "Summarize"
  contextfusion compile ./docs --mode qa --provider anthropic --model claude-sonnet-4-6
  contextfusion ui --host 0.0.0.0 --port 8080
  contextfusion serve-mcp --host 0.0.0.0 --port 8765
`);
}

function run(command, commandArgs, options = {}) {
  const result = spawnSync(command, commandArgs, {
    stdio: "inherit",
    ...options,
  });
  return result.status ?? 1;
}

function runSilent(command, commandArgs, options = {}) {
  const result = spawnSync(command, commandArgs, {
    stdio: "ignore",
    ...options,
  });
  return (result.status ?? 1) === 0;
}

function detectPython() {
  const candidates = [];

  const localVenvPython = join(repoRoot, "contextfusionvenv", "bin", "python");
  if (existsSync(localVenvPython)) {
    candidates.push(localVenvPython);
  }

  if (process.env.VIRTUAL_ENV) {
    candidates.push(join(process.env.VIRTUAL_ENV, "bin", "python"));
  }

  if (process.env.PYTHON) {
    candidates.push(process.env.PYTHON);
  }
  candidates.push("python3", "python");

  for (const candidate of candidates) {
    if (runSilent(candidate, ["--version"])) {
      return candidate;
    }
  }
  return null;
}

function pythonEnv() {
  const env = { ...process.env };
  if (hasLocalSource) {
    env.PYTHONPATH = env.PYTHONPATH
      ? `${localSrc}${delimiter}${env.PYTHONPATH}`
      : localSrc;
  }
  return env;
}

function hasContextFusionPython(pythonBin, env) {
  return runSilent(
    pythonBin,
    [
      "-c",
      "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('context_portfolio_optimizer') else 1)",
    ],
    { env },
  );
}

function createEnvTemplate(force = false) {
  const envPath = join(process.cwd(), ".env");
  if (existsSync(envPath) && !force) {
    console.log(".env already exists (use --force to overwrite).");
    return;
  }

  const template = [
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "OPENAI_COMPAT_BASE_URL=",
    "OPENAI_COMPAT_API_KEY=",
    "",
  ].join("\n");

  writeFileSync(envPath, template, "utf-8");
  console.log(`Created .env template at ${envPath}`);
}

function installPythonPackage(pythonBin) {
  if (hasLocalSource) {
    return run(pythonBin, ["-m", "pip", "install", "-e", repoRoot]);
  }
  return run(pythonBin, ["-m", "pip", "install", "context-portfolio-optimizer"]);
}

function runCpoViaPython(pythonBin, forwardedArgs) {
  return run(
    pythonBin,
    ["-m", "context_portfolio_optimizer.cli", ...forwardedArgs],
    { env: pythonEnv() },
  );
}

if (args.length === 0 || ["-h", "--help", "help"].includes(args[0])) {
  printHelp();
  process.exit(0);
}

const command = args[0];

if (command === "env") {
  createEnvTemplate(args.includes("--force"));
  process.exit(0);
}

if (command === "setup") {
  const pythonBin = detectPython();
  if (!pythonBin) {
    console.error("Python 3 is required. Install Python 3.11+ and rerun.");
    process.exit(1);
  }

  const env = pythonEnv();
  if (!hasContextFusionPython(pythonBin, env)) {
    console.log("Installing ContextFusion Python package...");
    const installStatus = installPythonPackage(pythonBin);
    if (installStatus !== 0) {
      process.exit(installStatus);
    }
  } else {
    console.log("ContextFusion Python package is already available.");
  }

  createEnvTemplate(false);
  console.log("Setup complete.");
  console.log("Next: contextfusion run ./data --query \"Summarize\" --provider anthropic");
  process.exit(0);
}

const pythonBin = detectPython();
if (!pythonBin) {
  console.error("Python 3 is required. Install Python 3.11+ and rerun.");
  process.exit(1);
}

const env = pythonEnv();
if (!hasContextFusionPython(pythonBin, env)) {
  console.error(
    "ContextFusion Python package is not available. Run `contextfusion setup` first.",
  );
  process.exit(1);
}

const status = runCpoViaPython(pythonBin, args);
process.exit(status);
