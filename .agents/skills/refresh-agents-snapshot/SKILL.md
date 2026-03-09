---
name: refresh-agents-snapshot
description: Refresh fixed snapshot sections in the repo root AGENTS.md with current device information for deep-learning work and current repository structure summaries. Use when the user explicitly asks to refresh or sync AGENTS.md project context, device info, GPU topology, repo structure, src/ref module inventory, tests overview, or important root-file summaries.
---

# Refresh Agents Snapshot

## Overview

Refresh the fixed `AGENTS.md` snapshot sections that drift over time: device capabilities relevant to deep learning, and repository structure summaries relevant to onboarding and navigation.

## Workflow

1. Read the repo root `AGENTS.md` and keep all non-snapshot sections untouched.
2. Run `python .agents/skills/refresh-agents-snapshot/scripts/update_agents_snapshot.py` from the repo root.
3. Verify that the numbering remains correct and that only the fixed snapshot sections changed:
   - `## 2. Device Snapshot`
   - `## 3. Repo Structure Snapshot`
4. Rewrite section bodies by heading. Do not use start/end markers in `AGENTS.md`.
5. Render repo structure as a single overall architecture tree.
6. For repo structure, read `notes.md` inside each top-level module directory under `src/` and `ref/`. If a concise summary exists, attach one sentence to that module in the architecture tree.
7. If a module directory has no `notes.md`, omit the description rather than inventing one.
8. Report which device facts were detected and whether topology data was unavailable.

## Snapshot Rules

- Keep invocation explicit. Do not assume this skill should run during normal coding tasks.
- Update only the bodies of `## 2. Device Snapshot` and `## 3. Repo Structure Snapshot`.
- For device info, keep the scope narrow:
  - GPU model
  - GPU count
  - Total GPU memory or unified-memory fallback
  - GPU interconnect topology relevant to multi-GPU training cost
- For repo structure, keep the scope narrow:
  - `src/` and `ref/`: summarize at module-folder level
  - `tests/`: summarize only the top level
  - root directory: summarize only important files such as `AGENTS.md`, `README.md`, `pyproject.toml`, `justfile`, `main.py`, and Docker-related files when present
- Render repo structure as one compact architecture tree, not multiple sub-sections or a flat bullet inventory.
- If a probe command is unavailable, write `unavailable` instead of guessing.

## Device Detection

- Prefer `nvidia-smi` for discrete NVIDIA GPUs. Include the raw `nvidia-smi topo -m` matrix when available.
- On Apple Silicon, fall back to `system_profiler` and report unified memory plus the fact that there is no multi-GPU fabric.
- When neither probe works, keep the section useful by reporting the platform and marking GPU fields unavailable.

## Repo Structure Rules

- Treat folder names as the module boundary.
- Read `notes.md` in each module directory and extract at most one concise line.
- Do not expand `tests/` recursively.
- If `src/` or `ref/` currently contain files but no module folders, keep the fallback file list short.
- Do not summarize unimportant dotfiles in the root snapshot.

## Resources

- `scripts/update_agents_snapshot.py`: refreshes the fixed `AGENTS.md` sections in place.
