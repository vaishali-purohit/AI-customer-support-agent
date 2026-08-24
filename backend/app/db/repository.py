import sqlite3
from typing import Optional
from app.db.connection import _get_connection


def get_order_by_id(order_id: str, conn: Optional[sqlite3.Connection] = None) -> Optional[dict]:
    close = False
    if conn is None:
        conn = _get_connection()
        close = True
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = cur.fetchone()
    if close:
        conn.close()
    return dict(row) if row else None


def get_customer_by_id(customer_id: str, conn: Optional[sqlite3.Connection] = None) -> Optional[dict]:
    close = False
    if conn is None:
        conn = _get_connection()
        close = True
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cur.fetchone()
    if close:
        conn.close()
    return dict(row) if row else None


def get_order_items(order_id: str, conn: Optional[sqlite3.Connection] = None) -> list[dict]:
    close = False
    if conn is None:
        conn = _get_connection()
        close = True
    cur = conn.cursor()
    cur.execute("""
        SELECT oi.*, p.name as product_name, p.category as product_category
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    """, (order_id,))
    rows = cur.fetchall()
    if close:
        conn.close()
    return [dict(r) for r in rows]
