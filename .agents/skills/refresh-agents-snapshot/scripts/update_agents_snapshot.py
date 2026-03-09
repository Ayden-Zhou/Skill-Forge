#!/usr/bin/env python3
"""Refresh fixed device and repository snapshot sections in AGENTS.md."""

from __future__ import annotations

import platform
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    output: str


def run_command(*args: str) -> CommandResult:
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return CommandResult(ok=False, output="")
    output = (completed.stdout or completed.stderr or "").strip()
    return CommandResult(ok=completed.returncode == 0, output=output)


def current_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def mib_to_gib(memory_mib: str) -> str:
    gib = int(memory_mib) / 1024
    return f"{int(gib)} GiB" if gib.is_integer() else f"{gib:.1f} GiB"


def detect_nvidia_snapshot() -> str | None:
    gpu_query = run_command(
        "nvidia-smi",
        "--query-gpu=name,memory.total",
        "--format=csv,noheader,nounits",
    )
    if not gpu_query.ok or not gpu_query.output:
        return None

    gpu_rows = []
    for raw_line in gpu_query.output.splitlines():
        parts = [part.strip() for part in raw_line.split(",")]
        if len(parts) == 2:
            gpu_rows.append((parts[0], parts[1]))

    if not gpu_rows:
        return None

    counter = Counter(gpu_rows)
    gpu_summary = ", ".join(
        f"{name} x{count} ({mib_to_gib(memory_mib)} each)"
        for (name, memory_mib), count in sorted(counter.items())
    )
    total_memory_gib = sum(int(memory_mib) for _, memory_mib in gpu_rows) / 1024

    lines = [
        f"- Refreshed at: `{current_timestamp()}`",
        "- Accelerator backend: `nvidia-smi`",
        f"- GPU summary: {gpu_summary}",
        f"- GPU count: `{len(gpu_rows)}`",
        f"- Aggregate GPU memory: `{total_memory_gib:.1f} GiB`",
    ]

    topo = run_command("nvidia-smi", "topo", "-m")
    if topo.ok and topo.output:
        lines.append("- GPU interconnect topology:")
        lines.append("```text")
        lines.append(topo.output)
        lines.append("```")
    else:
        lines.append("- GPU interconnect topology: unavailable")

    return "\n".join(lines)


def parse_system_profiler_value(output: str, key: str) -> str | None:
    pattern = rf"^\s*{re.escape(key)}:\s*(.+)$"
    match = re.search(pattern, output, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def detect_apple_snapshot() -> str | None:
    hardware = run_command("system_profiler", "SPHardwareDataType")
    displays = run_command("system_profiler", "SPDisplaysDataType")
    if not hardware.ok or not displays.ok:
        return None

    chip = parse_system_profiler_value(hardware.output, "Chip")
    system_memory = parse_system_profiler_value(hardware.output, "Memory")
    gpu_name = parse_system_profiler_value(displays.output, "Chipset Model")
    gpu_cores = parse_system_profiler_value(displays.output, "Total Number of Cores")
    metal = parse_system_profiler_value(displays.output, "Metal Support")

    accelerator_name = gpu_name or chip or "Apple integrated GPU"
    lines = [
        f"- Refreshed at: `{current_timestamp()}`",
        "- Accelerator backend: `system_profiler`",
        f"- GPU summary: {accelerator_name} x1",
        "- GPU count: `1`",
    ]
    if gpu_cores:
        lines.append(f"- GPU cores: `{gpu_cores}`")
    if system_memory:
        lines.append(
            f"- Memory model: unified memory shared with the system (`{system_memory}` total)"
        )
    else:
        lines.append("- Memory model: unified/shared memory (exact total unavailable)")
    lines.append("- GPU interconnect topology: integrated single-device GPU; no multi-GPU fabric")
    if metal:
        lines.append(f"- Metal support: `{metal}`")

    return "\n".join(lines)


def detect_device_snapshot() -> str:
    nvidia_snapshot = detect_nvidia_snapshot()
    if nvidia_snapshot:
        return nvidia_snapshot

    apple_snapshot = detect_apple_snapshot()
    if apple_snapshot:
        return apple_snapshot

    return "\n".join(
        [
            f"- Refreshed at: `{current_timestamp()}`",
            f"- Platform: `{platform.platform()}`",
            "- GPU summary: unavailable",
            "- GPU count: unavailable",
            "- Aggregate GPU memory: unavailable",
            "- GPU interconnect topology: unavailable",
        ]
    )


def list_directory_entries(path: Path) -> tuple[list[Path], list[Path]]:
    if not path.exists():
        return [], []
    directories = sorted(
        [entry for entry in path.iterdir() if entry.is_dir() and not entry.name.startswith(".")]
    )
    files = sorted(
        [entry for entry in path.iterdir() if entry.is_file() and not entry.name.startswith(".")]
    )
    return directories, files


def extract_notes_summary(path: Path) -> str | None:
    notes_path = path / "notes.md"
    if not notes_path.exists():
        return None

    for raw_line in notes_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        return line
    return None


def build_source_subtree(path: Path) -> list[str]:
    lines = [f"{path.name}/"]
    if not path.exists():
        lines.append("└── (missing)")
        return lines

    directories, files = list_directory_entries(path)
    children: list[str] = []
    for directory in directories:
        summary = extract_notes_summary(directory)
        child = f"{directory.name}/ - {summary}" if summary else f"{directory.name}/"
        children.append(child)

    if files and not directories:
        children.extend(file_path.name for file_path in files[:5])

    if not children:
        children.append("(no module directories yet)")

    for index, child in enumerate(children):
        branch = "└── " if index == len(children) - 1 else "├── "
        lines.append(f"{branch}{child}")
    return lines


def build_tests_subtree(path: Path) -> list[str]:
    lines = ["tests/"]
    if not path.exists():
        lines.append("└── (missing)")
        return lines

    directories, files = list_directory_entries(path)
    children = [f"{directory.name}/" for directory in directories]
    children.extend(file_path.name for file_path in files)
    if not children:
        children.append("(no top-level test groups)")

    for index, child in enumerate(children):
        branch = "└── " if index == len(children) - 1 else "├── "
        lines.append(f"{branch}{child}")
    return lines


ROOT_FILE_DESCRIPTIONS = {
    "AGENTS.md": "repo-level operating instructions and workflow contracts",
    "README.md": "human-facing project overview and onboarding entrypoint",
    "pyproject.toml": "Python project metadata and dependency declaration",
    "justfile": "standard formatting and verification commands",
    "main.py": "main executable entrypoint",
    "Dockerfile": "container build recipe",
    "docker-compose.yml": "multi-service local container orchestration",
    "docker-compose.yaml": "multi-service local container orchestration",
    ".dockerignore": "container build context exclusions",
    ".env.example": "example environment variable template",
    "CLAUDE.md": "parallel assistant guidance file kept in repo",
}


def build_root_files_subtree(repo_root: Path) -> list[str]:
    lines = ["important-root-files/"]
    present_files = [
        file_name for file_name in ROOT_FILE_DESCRIPTIONS if (repo_root / file_name).exists()
    ]
    if not present_files:
        lines.append("└── (no configured root files found)")
        return lines

    for index, file_name in enumerate(present_files):
        branch = "└── " if index == len(present_files) - 1 else "├── "
        lines.append(f"{branch}{file_name} - {ROOT_FILE_DESCRIPTIONS[file_name]}")
    return lines


def append_subtree(lines: list[str], subtree: list[str], is_last: bool) -> None:
    for index, line in enumerate(subtree):
        if index == 0:
            branch = "└── " if is_last else "├── "
            lines.append(f"{branch}{line}")
        else:
            prefix = "    " if is_last else "│   "
            lines.append(f"{prefix}{line}")


def build_repo_snapshot(repo_root: Path) -> str:
    lines = [
        f"- Refreshed at: `{current_timestamp()}`",
        "",
        "```text",
        ".",
    ]
    subtrees = [
        build_source_subtree(repo_root / "src"),
        build_source_subtree(repo_root / "ref"),
        build_tests_subtree(repo_root / "tests"),
        build_root_files_subtree(repo_root),
    ]
    for index, subtree in enumerate(subtrees):
        append_subtree(lines, subtree, is_last=index == len(subtrees) - 1)
    lines.append("```")
    return "\n".join(lines)


def replace_section_body(content: str, heading: str, replacement: str) -> str:
    pattern = re.compile(rf"({re.escape(heading)}\n\n)(.*?)(?=\n## |\Z)", flags=re.DOTALL)
    if not pattern.search(content):
        raise RuntimeError(f"Could not find heading: {heading}")
    return pattern.sub(rf"\1{replacement}\n", content, count=1)


def main() -> None:
    content = AGENTS_PATH.read_text()
    content = replace_section_body(content, "## 2. Device Snapshot", detect_device_snapshot())
    content = replace_section_body(
        content,
        "## 3. Repo Structure Snapshot",
        build_repo_snapshot(REPO_ROOT),
    )
    AGENTS_PATH.write_text(content)
    print(f"Updated {AGENTS_PATH}")


if __name__ == "__main__":
    main()
