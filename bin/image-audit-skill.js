#!/usr/bin/env node

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "..");
const sourceSkillDir = path.join(repoRoot, ".claude", "skills", "image-audit");

function printHelp() {
  console.log(`Image Audit installer

Usage:
  image-audit-skill install [--claude|--codex] [--global|--project <path>|--target <path>]
  image-audit-skill help

Examples:
  npx image-audit-skill install --claude
  npx image-audit-skill install --claude --project .
  npx image-audit-skill install --codex
  npx image-audit-skill install --target "C:\\work\\site\\.claude\\skills"
`);
}

function ensureExists(targetPath) {
  fs.mkdirSync(targetPath, { recursive: true });
}

function removeIfExists(targetPath) {
  if (fs.existsSync(targetPath)) {
    fs.rmSync(targetPath, { recursive: true, force: true });
  }
}

function copyDirectory(source, target) {
  fs.cpSync(source, target, { recursive: true, force: true });
}

function resolveProjectSkills(projectPath, product) {
  const resolvedProject = path.resolve(projectPath);
  return product === "codex"
    ? path.join(resolvedProject, ".codex", "skills")
    : path.join(resolvedProject, ".claude", "skills");
}

function defaultGlobalSkills(product) {
  const home = os.homedir();
  return product === "codex"
    ? path.join(home, ".codex", "skills")
    : path.join(home, ".claude", "skills");
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const command = args[0];
  const flags = args.slice(1);
  return { command, flags };
}

function consumeValue(flags, index, label) {
  const value = flags[index + 1];
  if (!value) {
    throw new Error(`Missing value for ${label}`);
  }
  return value;
}

function install(flags) {
  let product = "claude";
  let targetPath = null;
  let projectPath = null;

  for (let i = 0; i < flags.length; i += 1) {
    const flag = flags[i];
    if (flag === "--claude") {
      product = "claude";
    } else if (flag === "--codex") {
      product = "codex";
    } else if (flag === "--global") {
      targetPath = defaultGlobalSkills(product);
    } else if (flag === "--project") {
      projectPath = consumeValue(flags, i, "--project");
      i += 1;
    } else if (flag === "--target") {
      targetPath = consumeValue(flags, i, "--target");
      i += 1;
    } else if (flag === "--help" || flag === "-h") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown flag: ${flag}`);
    }
  }

  if (!targetPath && projectPath) {
    targetPath = resolveProjectSkills(projectPath, product);
  }

  if (!targetPath) {
    targetPath = defaultGlobalSkills(product);
  }

  const resolvedTarget = path.resolve(targetPath);
  const destination = path.join(resolvedTarget, "image-audit");

  ensureExists(resolvedTarget);
  removeIfExists(destination);
  copyDirectory(sourceSkillDir, destination);

  console.log(`Installed image-audit to ${destination}`);
  if (product === "codex") {
    console.log("Restart Codex to pick up the new skill.");
  } else {
    console.log("Restart Claude Code if it is already running.");
  }
}

function main() {
  const { command, flags } = parseArgs(process.argv);

  if (!command || command === "help" || command === "--help" || command === "-h") {
    printHelp();
    return;
  }

  if (command !== "install") {
    throw new Error(`Unknown command: ${command}`);
  }

  install(flags);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
