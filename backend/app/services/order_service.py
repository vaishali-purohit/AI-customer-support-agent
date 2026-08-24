from app.db import get_order_by_id, get_customer_by_id, get_order_items
from app.models.schemas import OrderLookupResponse
from app.core.constants import MASKED_FIELDS


# Service for looking up orders and returning only safe, allowed fields to the customer
class OrderService:
    def lookup(self, order_id: str, email: str) -> OrderLookupResponse:
        order = get_order_by_id(order_id)
        if not order:
            raise ValueError("order_not_found")
        customer = get_customer_by_id(order["customer_id"])
        if not customer:
            raise ValueError("customer_not_found")
        if customer["email"].lower() != email.lower():
            raise ValueError("ownership_mismatch")
        items = get_order_items(order_id)
        safe_customer = {k: v for k, v in customer.items() if k not in MASKED_FIELDS}
        return OrderLookupResponse(
            order_id=order["order_id"],
            status=order["status"],
            order_date=order["order_date"],
            estimated_delivery=order.get("estimated_delivery"),
            shipping_method=order.get("shipping_method"),
            tracking_number=order.get("tracking_number"),
            items=items,
            subtotal_cents=order["subtotal_cents"],
            shipping_cents=order["shipping_cents"],
            discount_cents=order.get("discount_cents", 0),
            total_cents=order["total_cents"],
            customer=safe_customer,
        )
