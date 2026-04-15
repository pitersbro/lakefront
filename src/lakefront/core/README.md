# Lakefront Core

## Project name

Core library for project and data source management in the Lakehouse Observability Platform.

## About

Lakefront Core provides a centralized configuration and query engine for managing lakehouse projects and their associated data sources. It handles project persistence, data source registration, and enables SQL-based querying over data sources using DuckDB as the underlying query engine. The library serves as the foundation for the Lakehouse Observability Platform, enabling users to define, manage, and interact with their data lake infrastructure.

## Usage

### Initialize and get a project

```python
from lakefront.core import initialize, get_project, list_projects

# Initialize the configuration system
initialize(profile="default")

# List all available projects
projects = list_projects()
print(projects)

# Get a specific project
ctx = get_project("my_project")
print(ctx.name)
print(ctx.list_source_names())
```

### Query data sources

```python
from lakefront.core import get_project

ctx = get_project("my_project")

# Execute SQL queries on registered sources
result = ctx.query("SELECT * FROM my_source LIMIT 10")

# Fetch results as DataFrame
df = result.df()
print(df)

# Fetch results as Arrow Table
arrow_table = result.arrow()
print(arrow_table)
```

### Manage project configuration

```python
from lakefront.core import ProjectConfigurationService, ProfileConfigurationService

# Create a new project
service = ProjectConfigurationService()
service.create("new_project", profile="default")

# Get profile settings
profile_service = ProfileConfigurationService()
settings = profile_service.get("default")
```
