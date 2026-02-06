# AGENTS.md

Guide for coding agents working in this repository.

## Project Overview

- Domain: Computer vision experiments with ArUco / ChArUco and camera calibration
- Language: Python
- Python version: 3.13+ (see `.python-version`, `pyproject.toml`)
- Env/deps manager: `uv`
- Test runner: `pytest`
- Lint/format: `ruff`
- Packaging mode: workspace scripts (`[tool.uv] package = false`)

## High-Signal Files

- `find_aruco_points.py`: live marker detection + frame overlays
- `find_extrinsic_object.py`: pose estimation with known object points
- `cali.py`: charuco calibration and parquet output
- `capture.py`: webcam frame capture helper
- `run_capture.py`: multi-port gstreamer recorder CLI (`click`)
- `scripts/uv_to_object_points.py`: UV -> 3D conversion script
- `test_cam_props.py`: camera property probe test/script
- Shell helpers: `gen.sh`, `cvt_all_pdfs.sh`, `dump_and_play.sh`

## Setup

```bash
uv sync
```

Creates `.venv` and installs dependencies from `pyproject.toml`.

## Build / Lint / Test Commands

No compile step. “Build” usually means running generation/util scripts.

### Lint

```bash
uv run ruff check .
uv run ruff check . --fix
```

### Format

```bash
uv run ruff format .
```

### Tests

Full suite:

```bash
uv run pytest -q
```

Single test file (important):

```bash
uv run pytest test_cam_props.py -q
```

Single test function:

```bash
uv run pytest test_cam_props.py::test_props -q
```

Keyword filter:

```bash
uv run pytest -k "props" -q
```

### Script sanity checks

```bash
uv run python -m py_compile *.py scripts/*.py
uv run python run_capture.py --help
uv run python scripts/uv_to_object_points.py --help
```

## Runtime/Tooling Notes

- Prefer `uv run python <script>.py` for all local execution.
- `scripts/uv_to_object_points.py` also supports script-mode execution directly.
- Shell scripts require system tools:
  - `gen.sh`: expects `MarkerPrinter.py` from OpenCV contrib generator context
  - `cvt_all_pdfs.sh`: needs ImageMagick (`magick`)
  - `dump_and_play.sh`: needs `gst-launch-1.0`

## Code Style (Observed Conventions)

Follow existing style in touched files; keep edits narrow.

### Imports

- Keep imports at top of module.
- Common pattern: stdlib + third-party; ordering is not perfectly strict.
- Do not do broad import reordering unless asked.

### Formatting

- 4-space indentation
- Predominantly double quotes
- Script-oriented functions; avoid unnecessary abstractions

### Types

- Type hints are common in core numeric/geometry scripts.
- Existing usage includes:
  - builtin generics (`list[int]`, `tuple[float, float]`)
  - `TypedDict`
  - `typing.cast`
  - `numpy.typing` and jaxtyping aliases
- Preserve/improve types when touching typed code.

### Naming

- `snake_case`: functions, variables
- `PascalCase`: classes
- `UPPER_SNAKE_CASE`: constants/config

### Error Handling / Logging

- `loguru` is the preferred logger.
- Use `logger.warning(...)` for recoverable detection/runtime issues.
- Raise explicit exceptions for invalid inputs in utility code.

### CLI / Entrypoints

- `click` is used for CLI scripts.
- Use `if __name__ == "__main__":` entrypoints.
- Keep side effects in `main()` when possible.

### CV / Numeric Practices

- Be explicit about array shapes where relevant.
- Normalize/reshape OpenCV outputs before downstream operations.
- Keep calibration/dictionary constants near top-level config.

## Testing Guidance

- Repo is hardware-heavy; avoid adding camera-dependent tests unless requested.
- Prefer extracting pure logic and testing that logic.
- Use pytest naming: `test_*.py`, `test_*`.

## Dependency Management (uv)

```bash
uv add <package>
uv add --dev <package>
uv remove <package>
uv sync
```

Prefer checking in both `pyproject.toml` and `uv.lock` for reproducibility.

## Cursor / Copilot Rules Check

- `.cursor/rules/`: not present
- `.cursorrules`: not present
- `.github/copilot-instructions.md`: not present

No repository-specific Cursor/Copilot rule files currently exist.

## Agent Workflow Checklist

Before coding:
1. Read this file and target scripts.
2. Run `uv sync` if env may be stale.
3. Check whether task depends on camera/hardware.

After coding:
1. Run focused checks first.
2. Run `uv run ruff check .`.
3. Run `uv run pytest -q` (or explain hardware-related skips).
4. Keep edits minimal and task-scoped.
