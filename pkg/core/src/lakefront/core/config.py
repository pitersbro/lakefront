from pathlib import Path

import duckdb

CONFIG_DIR = Path("~/.config/lakefront").expanduser()
DB_PATH = CONFIG_DIR / ".db"
ACTIVE_PATH = CONFIG_DIR / ".project"
PROJECTS_DIR = Path("~/.local/share/lakefront/projects").expanduser()


def metadb():
    return duckdb.connect(str(DB_PATH))


def make_project_path(name: str) -> Path:
    path = PROJECTS_DIR / name
    path.mkdir(parents=True, exist_ok=True)
    return path
