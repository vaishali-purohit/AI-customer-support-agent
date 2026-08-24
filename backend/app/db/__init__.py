from app.db.connection import _get_connection, DB_PATH
from app.db.repository import (
    get_order_by_id,
    get_customer_by_id,
    get_order_items,
)


def init_db(conn=None) -> None:
    from app.db.connection import _get_connection
    close = False
    if conn is None:
        conn = _get_connection()
        close = True
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT
        );
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price_cents INTEGER NOT NULL,
            description TEXT,
            materials TEXT,
            care_instructions TEXT
        );
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            shipping_method TEXT,
            shipping_carrier TEXT,
            tracking_number TEXT,
            estimated_delivery TEXT,
            subtotal_cents INTEGER NOT NULL,
            shipping_cents INTEGER NOT NULL,
            discount_cents INTEGER DEFAULT 0,
            total_cents INTEGER NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            size TEXT,
            color TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
        CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
    """)
    if close:
        conn.close()


def seed_db(conn=None) -> None:
    from app.db.connection import _get_connection
    close = False
    if conn is None:
        conn = _get_connection()
        close = True
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] > 0:
        if close:
            conn.close()
        return
    customers = [
        ("CUST-1001", "Alice Johnson", "alice@example.com", "+1-555-0101"),
        ("CUST-1002", "Bob Smith", "bob@example.com", "+1-555-0102"),
        ("CUST-1003", "Carol Davis", "carol@example.com", "+1-555-0103"),
    ]
    products = [
        ("PROD-2001", "Cloud Walk", "Footwear", 12999, "Lightweight daily walking shoe with CloudFoam midsole.", "Engineered mesh and synthetic overlay", "Hand wash cold; air dry"),
        ("PROD-2002", "Trail Blazer", "Footwear", 15999, "Rugged hiking boot with Vibram outsole and waterproof membrane.", "Waterproof leather and ripstop nylon", "Wipe clean; condition leather monthly"),
        ("PROD-2003", "City Glide", "Footwear", 10999, "Sleek slip-on for urban commutes with responsive cushioning.", "Knit upper with TPU heel frame", "Machine washable insole; wipe upper"),
        ("PROD-2004", "Recovery Slide", "Footwear", 4999, "Cushioned recovery slide with orthotic-grade footbed.", "EVA foam and rubber outsole", "Wipe with damp cloth"),
    ]
    orders = [
        ("ORD-3001", "CUST-1001", "2026-08-10", "delivered", "Standard", "USPS", "9400129208475930001", "2026-08-17", 12999, 0, 0, 12999),
        ("ORD-3002", "CUST-1001", "2026-08-18", "shipped", "Express", "UPS", "1Z9999WX1234567890", "2026-08-21", 15999, 999, 0, 16998),
        ("ORD-3003", "CUST-1002", "2026-08-19", "processing", "Standard", None, None, "2026-08-26", 10999, 0, 500, 10499),
        ("ORD-3004", "CUST-1003", "2026-08-05", "delivered", "Overnight", "FedEx", "794690000001", "2026-08-06", 4999, 1999, 0, 6998),
        ("ORD-3005", "CUST-1002", "2026-07-20", "returned", "Standard", "USPS", "9400129208475930002", "2026-07-27", 12999, 0, 2000, 10999),
    ]
    order_items = [
        ("OI-4001", "ORD-3001", "PROD-2001", 1, 12999, "10", "White"),
        ("OI-4002", "ORD-3002", "PROD-2002", 1, 15999, "11", "Olive"),
        ("OI-4003", "ORD-3003", "PROD-2003", 1, 10999, "9", "Black"),
        ("OI-4004", "ORD-3004", "PROD-2004", 1, 4999, "M", "Grey"),
        ("OI-4005", "ORD-3005", "PROD-2001", 1, 12999, "10", "White"),
    ]
    conn.executemany("INSERT OR REPLACE INTO customers VALUES (?,?,?,?)", customers)
    conn.executemany("INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?)", products)
    conn.executemany("INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", orders)
    conn.executemany("INSERT OR REPLACE INTO order_items VALUES (?,?,?,?,?,?,?)", order_items)
    conn.commit()
    if close:
        conn.close()


__all__ = [
    "init_db",
    "seed_db",
    "get_order_by_id",
    "get_customer_by_id",
    "get_order_items",
    "DB_PATH",
    "_get_connection",
]
