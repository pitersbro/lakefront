# Lakefront Cli

Command-line interface for Lakehouse Observability Platform providing access to core features for project management, configuration, and data exploration.

## About

The CLI package exposes the core library features through a command-line interface built with Typer. It provides commands for managing configuration profiles, projects, and data sources. Users can create and configure projects, attach data sources, initialize the system, and launch the interactive terminal UI for data exploration.

## Usage

### Installation

The CLI is installed as part of the lakefront-cli package and provides two command entry points: `lakefront` and `lf`.

### Commands

#### System

```bash
# Initialize the lakefront database (run once before using other commands)
lakefront init

# Display version information
lakefront version

# Launch the interactive UI for a specific project
lakefront ui --project <project-name>
```

#### Configuration

Configuration commands manage profile settings stored in `${LAKEFRONT_HOME}/config` (defaults to `~/.lakefront/config`).

```bash
# List all configuration profiles
lakefront config list

# Show configuration service info
lakefront config info

# Create a new configuration profile
lakefront config create --profile <profile-name>

# Inspect a configuration profile (defaults to active profile)
lakefront config inspect [--profile <profile-name>]

# Get the currently active profile
lakefront config get-active

# Set a profile as active
lakefront config set-active --profile <profile-name>
```

#### Projects

Project commands manage Lakefront projects. Each project has a configuration file at `${LAKEFRONT_HOME}/projects/<project-name>/project.toml` and is pinned to a configuration profile.

```bash
# List all projects
lakefront projects list

# Create a new project
lakefront projects create <project-name> [--description <text>] [--profile <profile-name>]

# Inspect a project's configuration
lakefront projects inspect <project-name>

# Delete a project
lakefront projects delete <project-name> [--yes]
```

#### Data Sources

Data source commands manage individual data sources within a project. A source can be a parquet file, CSV file, parquet dataset, or delta table.

```bash
# Add a data source to a project
lakefront projects source add \
  --project <project-name> \
  --name <source-name> \
  --kind <local|s3> \
  --path <path-to-data> \
  [--description <text>]

# Remove a data source from a project
lakefront projects source remove \
  --project <project-name> \
  --name <source-name>
```

### Configuration

No additional configuration is required beyond running `lakefront init` once. The system manages configuration profiles and project settings automatically in the `${LAKEFRONT_HOME}` directory.
