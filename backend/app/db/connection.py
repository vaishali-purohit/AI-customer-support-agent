import os
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = os.getenv("DATABASE_PATH", "./data/app.db")
DB_CHECK_SAME_THREAD = False
DB_JOURNAL_MODE = "WAL"


# Returns a configured SQLite connection, creating parent directories if needed
def _get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=DB_CHECK_SAME_THREAD)
    conn.row_factory = sqlite3.Row
    conn.execute(f"PRAGMA journal_mode={DB_JOURNAL_MODE}")
    return conn
