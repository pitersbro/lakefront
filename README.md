# Lakefront

A terminal-based lakehouse observability platform for exploring and managing data sources from your command line.

---

## About

Working with lakehouse data — Parquet files on local disk or S3, DuckDB queries, materialized views — usually means jumping between tools, writing throwaway scripts, or wrestling with heavyweight UIs. Lakefront puts it all in one place: a fast TUI and CLI for data engineers who live in the terminal.

**Problems it solves:**

- **No single tool for lakehouse exploration** — Lakefront combines DuckDB-powered SQL querying, S3 source management, and dataset browsing in one cohesive interface.
- **Configuration sprawl** — profiles let you switch between environments (local dev, staging, production S3) with a single command, keeping credentials out of your scripts.
- **Context switching** — instead of firing up a Jupyter notebook or a GUI just to peek at a Parquet file, you stay in the terminal.

---

## Examples

### Initialise Lakefront

Bootstrap the `~/.lakefront` directory structure and create a default profile:

```bash
uv run lakefront init
```

### Config Management

```bash
# List all profiles
uv run lakefront config list

# Show config directories and paths
uv run lakefront config info

# Create a new profile
uv run lakefront config create --profile staging

# Inspect a profile's current settings
uv run lakefront config inspect --profile staging

# See which profile is active
uv run lakefront config get-active

# Switch to a different profile
uv run lakefront config set-active --profile staging
```

Secrets (S3 access keys etc.) can be written to the TOML profile or
set via environment variables instead:

```bash
export LAKEFRONT_S3__ACCESS_KEY=...
export LAKEFRONT_S3__SECRET_KEY=...
```

### Project Management

Projects are the top-level organisational unit in Lakefront. Each project lives in its own directory under `~/.lakefront/projects/` and can be pinned to a config profile.

```
~/.lakefront/projects/
└── my-project/
    ├── project.toml      ← metadata + pinned profile
    └── results/          ← analysis outputs
```

```bash
# List all projects
uv run lakefront projects list

# Create a new project
uv run lakefront projects create my-project -d "EDA on S3 parquet" -p staging

# Inspect a project
uv run lakefront projects inspect my-project

# Delete a project (prompts for confirmation)
uv run lakefront projects delete my-project
uv run lakefront projects delete my-project --yes
```

### Source Management

Data sources are attached to a project and point to a local path or S3 prefix.

```bash
# Add a source
uv run lakefront projects source add -p my-project -n raw -k s3 --path s3://bucket/raw/
uv run lakefront projects source add -p my-project -n local -k local --path /data/parquet/

# Remove a source
uv run lakefront projects source remove -p my-project -n raw
```

---

## Project Structure

```
src/
├── core/   # config models, settings, project & source service
├── cli/    # Typer entrypoint and sub-commands
└── tui/    # Textual TUI app (in progress)
```
