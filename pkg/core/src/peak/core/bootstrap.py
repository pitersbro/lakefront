# polon/core/manager.py

from .config import CONFIG_DIR, DB_PATH, metadb


def bootstrap():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with metadb() as db:
        db.execute("""
            CREATE SEQUENCE IF NOT EXISTS projects_id_seq;
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY DEFAULT nextval('projects_id_seq'),
                name        TEXT NOT NULL UNIQUE,
                created_at  TIMESTAMP DEFAULT now()
            );
        """)


def teardown():
    if not DB_PATH.exists():
        return
    with metadb() as db:
        db.execute("DROP TABLE IF EXISTS projects")
    DB_PATH.unlink(missing_ok=True)
