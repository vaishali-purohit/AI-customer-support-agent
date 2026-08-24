import pytest
from unittest.mock import patch
from app.services import OrderService

@pytest.fixture
def service(tmp_path):
    db_path = str(tmp_path / "test.db")
    with patch("app.db.DB_PATH", db_path):
        from app.db import init_db, seed_db
        init_db()
        seed_db()
        yield OrderService()

def test_successful_lookup(service):
    result = service.lookup("ORD-3001", "alice@example.com")
    assert result.order_id == "ORD-3001"
    assert result.status == "delivered"
    assert len(result.items) == 1

def test_order_not_found(service):
    with pytest.raises(ValueError, match="order_not_found"):
        service.lookup("ORD-9999", "alice@example.com")

def test_ownership_mismatch(service):
    with pytest.raises(ValueError, match="ownership_mismatch"):
        service.lookup("ORD-3001", "bob@example.com")
