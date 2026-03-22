# Peak

Lakehouse Observability Platform

## About

Terminal-first tool for exploring and monitoring Parquet datasets.
Keyboard-driven TUI.
Powered by DuckDB.

## Install

```bash
git clone https://github.com/you/peak
cd peak
uv sync
```

## Setup

```bash
peak db init       # initialize local database
peak db reset      # wipe and reinitialize
```

State is stored in `~/.config/peak/` — two files:

```
~/.config/peak/
├── .db           # projects + sources (DuckDB)
└── .project      # active project name
```

## Usage

```bash
peak explore       # launch TUI
```

### TUI keybindings

| key         | action         |
| ----------- | -------------- |
| `n`         | new project    |
| `d`         | delete project |
| `enter`     | open project   |
| `backspace` | go back        |
| `q`         | quit           |

## Structure

```
pkg/
├── core/     # ProjectManager, Explorer, models
├── tui/      # Textual screens and widgets
└── cli/      # Typer entrypoint
```
