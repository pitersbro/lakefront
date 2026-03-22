from pathlib import Path

import duckdb

CONFIG_DIR = Path("~/.config/peak").expanduser()
DB_PATH = CONFIG_DIR / ".db"
ACTIVE_PATH = CONFIG_DIR / ".project"


def metadb():
    return duckdb.connect(str(DB_PATH))
