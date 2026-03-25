from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TableSchema:
    name: str
    columns: dict[str, str]
    primary_key: str
    foreign_keys: dict[str, str]
    source_aliases: tuple[str, ...]


TABLE_SCHEMAS: dict[str, TableSchema] = {
    "customers": TableSchema(
        name="customers",
        columns={"id": "TEXT", "name": "TEXT", "country": "TEXT"},
        primary_key="id",
        foreign_keys={},
        source_aliases=("customers", "customer", "client", "clients"),
    ),
    "products": TableSchema(
        name="products",
        columns={"id": "TEXT", "name": "TEXT", "category": "TEXT"},
        primary_key="id",
        foreign_keys={},
        source_aliases=("products", "product", "materials", "material"),
    ),
    "plants": TableSchema(
        name="plants",
        columns={
            "id": "TEXT",
            "name": "TEXT",
            "country": "TEXT",
            "address": "TEXT",
        },
        primary_key="id",
        foreign_keys={},
        source_aliases=("plants", "plant", "addresses", "address", "locations"),
    ),
    "orders": TableSchema(
        name="orders",
        columns={"id": "TEXT", "customer_id": "TEXT", "date": "TEXT", "status": "TEXT"},
        primary_key="id",
        foreign_keys={"customer_id": "customers.id"},
        source_aliases=("orders", "order", "purchase_orders", "sales_orders"),
    ),
    "order_items": TableSchema(
        name="order_items",
        columns={
            "id": "TEXT",
            "order_id": "TEXT",
            "product_id": "TEXT",
            "quantity": "REAL",
            "amount": "REAL",
        },
        primary_key="id",
        foreign_keys={"order_id": "orders.id", "product_id": "products.id"},
        source_aliases=("order_items", "order_item", "items", "line_items"),
    ),
    "deliveries": TableSchema(
        name="deliveries",
        columns={
            "id": "TEXT",
            "order_id": "TEXT",
            "plant": "TEXT",
            "status": "TEXT",
            "date": "TEXT",
        },
        primary_key="id",
        foreign_keys={"order_id": "orders.id", "plant": "plants.id"},
        source_aliases=("deliveries", "delivery", "shipments", "shipment"),
    ),
    "invoices": TableSchema(
        name="invoices",
        columns={
            "id": "TEXT",
            "order_id": "TEXT",
            "amount": "REAL",
            "date": "TEXT",
            "status": "TEXT",
        },
        primary_key="id",
        foreign_keys={"order_id": "orders.id"},
        source_aliases=(
            "invoices",
            "invoice",
            "billing_documents",
            "billing_document",
            "billing",
        ),
    ),
    "payments": TableSchema(
        name="payments",
        columns={
            "id": "TEXT",
            "invoice_id": "TEXT",
            "amount": "REAL",
            "date": "TEXT",
            "method": "TEXT",
        },
        primary_key="id",
        foreign_keys={"invoice_id": "invoices.id"},
        source_aliases=("payments", "payment", "journal_entries", "journal_entry"),
    ),
}


def build_create_table_sql(schema: TableSchema) -> str:
    column_defs: list[str] = []
    for column_name, column_type in schema.columns.items():
        suffix = " PRIMARY KEY" if column_name == schema.primary_key else ""
        column_defs.append(f"{column_name} {column_type}{suffix}")
    for column_name, reference in schema.foreign_keys.items():
        table_name, ref_column = reference.split(".")
        column_defs.append(
            f"FOREIGN KEY ({column_name}) REFERENCES {table_name} ({ref_column})"
        )
    return f"CREATE TABLE IF NOT EXISTS {schema.name} ({', '.join(column_defs)})"


def schema_summary() -> str:
    lines: list[str] = []
    for table in TABLE_SCHEMAS.values():
        lines.append(f"Table: {table.name}")
        for column, column_type in table.columns.items():
            markers: list[str] = []
            if column == table.primary_key:
                markers.append("PK")
            if column in table.foreign_keys:
                markers.append(f"FK->{table.foreign_keys[column]}")
            suffix = f" ({', '.join(markers)})" if markers else ""
            lines.append(f"  - {column}: {column_type}{suffix}")
    return "\n".join(lines)


def schema_to_dict() -> dict[str, dict[str, Any]]:
    return {
        name: {
            "columns": table.columns,
            "primary_key": table.primary_key,
            "foreign_keys": table.foreign_keys,
            "source_aliases": table.source_aliases,
        }
        for name, table in TABLE_SCHEMAS.items()
    }
