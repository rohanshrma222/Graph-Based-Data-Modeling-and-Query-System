from __future__ import annotations

NODE_TYPES = {
    "Customer": ["id", "name", "country"],
    "Order": ["id", "customer_id", "date", "status"],
    "OrderItem": ["id", "order_id", "product_id", "quantity", "amount"],
    "Product": ["id", "name", "category"],
    "Delivery": ["id", "order_id", "plant", "status", "date"],
    "Invoice": ["id", "order_id", "amount", "date", "status"],
    "Payment": ["id", "invoice_id", "amount", "date", "method"],
    "Plant": ["id", "name", "country", "address"],
}

EDGE_TYPES = {
    "PLACED": ("Customer", "Order"),
    "CONTAINS": ("Order", "OrderItem"),
    "IS_FOR": ("OrderItem", "Product"),
    "HAS_DELIVERY": ("Order", "Delivery"),
    "HAS_INVOICE": ("Order", "Invoice"),
    "SETTLED_BY": ("Invoice", "Payment"),
    "SHIPPED_FROM": ("Delivery", "Plant"),
}
