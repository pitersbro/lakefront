# Changelog

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
