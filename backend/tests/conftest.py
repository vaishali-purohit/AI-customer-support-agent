import pytest
import tempfile
import os
from app.db import init_db, seed_db
from app.db import _get_connection

@pytest.fixture
def db_conn():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    conn = _get_connection(path)
    init_db(conn)
    seed_db(conn)
    yield conn
    conn.close()
    os.unlink(path)
