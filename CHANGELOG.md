# Changelog

## v0.3.3 (2026-04-19)

### Fix

- push and commit automation
- use annotated tag to ensure push with --follow-tags

## v0.3.2 (2026-04-19)

### Fix

- tag still not pushed

## v0.3.1 (2026-04-19)

### Fix

- workflow glitches
- unable to parse pyproject.toml

## v0.3.0 (2026-04-19)

### Feat

- add commitizen for automated changelog and versioning

### Fix

- cz command not found

## v0.2.2 (2026-04-18)

### Feat

- s3 support; added util.fs
- source can be attached to and detached from a project during runtime (#4)
- **tui**: basic source navigation and query execution
- **core**: can attach and query csv, parquet and parquet datasets (#3)
- **tui**: preliminary layout
- **core**: project context registers sources for querying (#2)
- **wip**: project lifecycle management (#1)

### Fix

- unable to connect to s3

### Refactor

- **core,cli**: moving around and renaming things
