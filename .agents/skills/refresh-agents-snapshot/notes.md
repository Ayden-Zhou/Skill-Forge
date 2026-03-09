# refresh-agents-snapshot notes

- Keep this skill explicit-invocation only; do not rely on implicit triggering.
- Update only the fixed snapshot sections in the repo root `AGENTS.md`.
- Treat `src/` and `ref/` as module inventories at folder level; fall back to a tiny key-file note only when no module folders exist.
- Treat `tests/` as a top-level-only inventory.
- Prefer platform-native device probes (`nvidia-smi`, `system_profiler`) and report unavailable fields explicitly.
- Preserve the numbered section structure in `AGENTS.md` during refreshes.
- When a module directory contains `notes.md`, extract one concise line and attach it to that module in the architecture tree.
- Do not use start/end markers in `AGENTS.md`; rewrite section bodies by heading.
