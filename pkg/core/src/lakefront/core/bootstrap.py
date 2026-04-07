# polon/core/manager.py

from .config import CONFIG_DIR, DB_PATH, PROJECTS_DIR, metadb


def bootstrap():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    with metadb() as db:
        db.execute("""
            CREATE SEQUENCE IF NOT EXISTS projects_id_seq;
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY DEFAULT nextval('projects_id_seq'),
                name        TEXT NOT NULL UNIQUE,
                path        TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT now()
            );
            CREATE SEQUENCE IF NOT EXISTS conf_id_seq;
            CREATE TABLE IF NOT EXISTS conf (
                id          INTEGER PRIMARY KEY DEFAULT nextval('conf_id_seq'),
                key         TEXT NOT NULL UNIQUE,
                value       TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT now()
            );
        """)


def teardown():
    if not DB_PATH.exists():
        return
    with metadb() as db:
        db.execute("DROP TABLE IF EXISTS projects")
        db.execute("DROP SEQUENCE IF EXISTS projects_id_seq")
    DB_PATH.unlink(missing_ok=True)
