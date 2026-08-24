from app.db import get_order_by_id, get_customer_by_id, get_order_items

def test_get_existing_order(db_conn):
    order = get_order_by_id("ORD-3001", db_conn)
    assert order is not None
    assert order["order_id"] == "ORD-3001"
    assert order["status"] == "delivered"

def test_get_missing_order(db_conn):
    order = get_order_by_id("ORD-9999", db_conn)
    assert order is None

def test_get_customer(db_conn):
    customer = get_customer_by_id("CUST-1001", db_conn)
    assert customer is not None
    assert customer["email"] == "alice@example.com"

def test_get_order_items(db_conn):
    items = get_order_items("ORD-3001", db_conn)
    assert len(items) == 1
    assert items[0]["product_name"] == "Cloud Walk"
