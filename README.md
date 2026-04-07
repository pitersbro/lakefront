# Lakefront

Lakehouse Observability Platform

## About

Terminal-first tool for exploring and monitoring Parquet datasets.
Keyboard-driven TUI.
Powered by DuckDB.

## Install

```bash
pip install lakefront
```

## Setup

```bash
lakefront db init       # initialize local database
lakefront db reset      # wipe and reinitialize
```

State is stored in `~/.config/lakefront/` — two files:

```
~/.config/lakefront/
├── .db           # projects + sources (DuckDB)
└── .project      # active project name
```

## Usage

```bash
lakefront ui       # launch TUI
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
