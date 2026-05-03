# Project Overview

A terminal-based lakehouse observability platform for exploring
and managing data sources from your command line.
It serves a double purpose as it is a library and a TUI for data related work.

- **Library**: importable API for querying various data sources using SQL
- **TUI**: interactive terminal interface built on top of the library

## Commands

```bash
uv run pytest                          # all tests
uv run pytest tests/core/test_main.py  # single file
uv run ruff check . && ruff format .   # lint + format
uv run lakefront <command>             # CLI (alias: lf)
uv build                               # build distribution
```

## Architecture

- `src/lakefront/core/` — library core (no TUI imports)
- `src/lakefront/tui/` — Textual app and screens, imports from core
- `src/lakefront/models` - Pydantic models used within the library
- `tests/` — mirrors src structure
- Never import TUI code from library core — the library must be usable standalone
- Core exposes `ProjectContext` class via `core.get_context`
  encapsulating all main project related features for both a TUI as well as
  an interactive terminal session

## Code Conventions

- Type hints on all public API
- Docstrings on all public API (Google format)
- No mutable default arguments
- Prefer SQL (duckdb) over arrow or pandas for analytical features
- Pure functions in core where possible — side effects only at edges
- TUI components: one Screen per file
- Prefer PEP604 annotation style

## Testing

- Unit tests for all library functions
- Do not mock core logic — test real behavior
- TUI tests use Textual's `App.run_test()`
- Aim for 80%+ coverage on `src/lakefront/core/` (not TUI)
- `conftest.py` wipes and re-initializes `LAKEFRONT_HOME` before each session.
  `test.env` redirects it to `tests/core/runtime/` for isolation.

## Rules

- Never push directly to main
- Keep library and TUI as separate concerns — new features go in core first, TUI second
- Ask before deleting any file
- Keep the friction between core and tui minimal
- All work should be based on an existing gh issue
- `src/lakefront/util` should not reference any external libraries if possible
  as well as other libary modules (apart from logging)
