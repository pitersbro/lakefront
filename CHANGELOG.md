# Changelog

## v0.8.0 (2026-05-03)

### Feat

- add navigation screen and demo project setup

### Fix

- **tui**: make profiler on-demand via 'p' keybind
- **core**: skip configure_s3 for projects with no S3 sources
- **tui**: move NavigationScreen I/O off the main thread
- **tui**: use call_from_thread for notify calls inside thread workers

## v0.7.1 (2026-04-27)

### Fix

- toml properties not being overriden by corresponding env vars

## v0.7.0 (2026-04-26)

### Feat

- **tui**: support multiple tabs in editor and result panes

## v0.6.0 (2026-04-26)

### Feat

- **core**: read analyzer row limit setting
- **tui**: read theme setting from core section
- **core**: add core config section

## v0.5.1 (2026-04-26)

### Refactor

- **tui**: consolidate styles in app.tcss

## v0.5.0 (2026-04-24)

### Feat

- **tui**: add explore action to result pane

## v0.4.0 (2026-04-22)

### Feat

- data profile is presented on source selection
- enable ai powered data source exploration
- **cli**: add configuration profile delete and demo commands
- add anthropic section to configuration model

### Fix

- analyzer mishandles bool types
- typo on app title

### Refactor

- move data profiling and llm code to analyzer module
- move data profiling code from tui to core.analyzer
- split core.main responsibilities across submodules
- core

## v0.3.4 (2026-04-20)

### Fix

- **tui**: rebuild source list after attach and detach

## v0.3.3 (2026-04-19)

### Feat

- add commitizen for automated changelog and versioning

### Fix

- Add a timeout for S3 source path existence check
- Project init ignores sources if unable to reach them or their existence check fails

## v0.3.0 (2026-04-19)

### Feat

- Add support for attaching S3 sources to a project

## v0.2.2 (2026-04-18)

### Feat

- Local sources can be attached to and detached from a project during runtime (#4)
- **tui**: basic source navigation and query execution
- **core**: can attach and query csv, parquet and parquet datasets (#3)
- **tui**: preliminary layout
- **core**: project context registers sources for querying (#2)
- **wip**: project lifecycle management (#1)

### Refactor

- **core,cli**: moving around and renaming things
