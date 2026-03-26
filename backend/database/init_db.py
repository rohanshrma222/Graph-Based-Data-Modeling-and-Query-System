from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from backend.config import settings
from backend.database.models import TABLE_SCHEMAS, build_create_table_sql


RAW_DIRECTORIES = {
    "business_partners",
    "business_partner_addresses",
    "products",
    "product_descriptions",
    "plants",
    "sales_order_headers",
    "sales_order_items",
    "outbound_delivery_headers",
    "outbound_delivery_items",
    "billing_document_headers",
    "billing_document_items",
    "journal_entry_items_accounts_receivable",
}


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_number(value: Any) -> float | None:
    text = _normalize_text(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _normalize_item_number(value: Any) -> str | None:
    text = _normalize_text(value)
    if text is None:
        return None
    stripped = text.lstrip("0")
    return stripped or "0"


def iter_jsonl_records(directory: Path) -> Iterable[dict[str, Any]]:
    if not directory.exists():
        return []
    def _generator() -> Iterable[dict[str, Any]]:
        for file_path in sorted(directory.glob("*.jsonl")):
            with file_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
    return _generator()


def load_raw_dataset(data_dir: Path) -> dict[str, list[dict[str, Any]]]:
    raw: dict[str, list[dict[str, Any]]] = {}
    for directory_name in RAW_DIRECTORIES:
        raw[directory_name] = list(iter_jsonl_records(data_dir / directory_name))
    return raw


def build_customers(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    addresses_by_partner: dict[str, dict[str, Any]] = {}
    for row in raw["business_partner_addresses"]:
        partner_id = _normalize_text(row.get("businessPartner"))
        if partner_id and partner_id not in addresses_by_partner:
            addresses_by_partner[partner_id] = row

    customers: list[dict[str, Any]] = []
    for row in raw["business_partners"]:
        customer_id = _normalize_text(row.get("customer") or row.get("businessPartner"))
        if not customer_id:
            continue
        address = addresses_by_partner.get(customer_id) or addresses_by_partner.get(
            _normalize_text(row.get("businessPartner")) or ""
        )
        customers.append(
            {
                "id": customer_id,
                "name": _normalize_text(
                    row.get("businessPartnerFullName")
                    or row.get("businessPartnerName")
                    or row.get("organizationBpName1")
                ),
                "country": _normalize_text(address.get("country")) if address else None,
            }
        )
    return customers


def build_products(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    descriptions: dict[str, str] = {}
    for row in raw["product_descriptions"]:
        product_id = _normalize_text(row.get("product"))
        if not product_id:
            continue
        if product_id not in descriptions or _normalize_text(row.get("language")) == "EN":
            descriptions[product_id] = _normalize_text(row.get("productDescription")) or product_id

    products: list[dict[str, Any]] = []
    for row in raw["products"]:
        product_id = _normalize_text(row.get("product"))
        if not product_id:
            continue
        products.append(
            {
                "id": product_id,
                "name": descriptions.get(product_id) or _normalize_text(row.get("productOldId")) or product_id,
                "category": _normalize_text(row.get("productGroup") or row.get("productType")),
            }
        )
    return products


def build_plants(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    plants: list[dict[str, Any]] = []
    for row in raw["plants"]:
        plant_id = _normalize_text(row.get("plant"))
        if not plant_id:
            continue
        plants.append(
            {
                "id": plant_id,
                "name": _normalize_text(row.get("plantName")) or plant_id,
                "country": None,
                "address": _normalize_text(row.get("addressId")),
            }
        )
    return plants


def build_orders(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    orders: list[dict[str, Any]] = []
    for row in raw["sales_order_headers"]:
        order_id = _normalize_text(row.get("salesOrder"))
        if not order_id:
            continue
        status_parts = [
            _normalize_text(row.get("overallDeliveryStatus")),
            _normalize_text(row.get("overallOrdReltdBillgStatus")),
            _normalize_text(row.get("overallSdDocReferenceStatus")),
        ]
        status = " | ".join(part for part in status_parts if part) or None
        orders.append(
            {
                "id": order_id,
                "customer_id": _normalize_text(row.get("soldToParty")),
                "date": _normalize_text(row.get("creationDate")),
                "status": status,
            }
        )
    return orders


def build_order_items(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in raw["sales_order_items"]:
        order_id = _normalize_text(row.get("salesOrder"))
        item_no = _normalize_item_number(row.get("salesOrderItem"))
        if not order_id or item_no is None:
            continue
        items.append(
            {
                "id": f"{order_id}-{item_no}",
                "order_id": order_id,
                "product_id": _normalize_text(row.get("material")),
                "quantity": _normalize_number(row.get("requestedQuantity")),
                "amount": _normalize_number(row.get("netAmount")),
            }
        )
    return items


def _delivery_to_order_lookup(raw: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, str], dict[tuple[str, str], str], dict[str, str]]:
    delivery_to_order: dict[str, str] = {}
    delivery_item_to_order: dict[tuple[str, str], str] = {}
    delivery_to_plant: dict[str, str] = {}
    for row in raw["outbound_delivery_items"]:
        delivery_id = _normalize_text(row.get("deliveryDocument"))
        order_id = _normalize_text(row.get("referenceSdDocument"))
        item_no = _normalize_item_number(row.get("deliveryDocumentItem"))
        plant_id = _normalize_text(row.get("plant"))
        if delivery_id and order_id and delivery_id not in delivery_to_order:
            delivery_to_order[delivery_id] = order_id
        if delivery_id and order_id and item_no is not None:
            delivery_item_to_order[(delivery_id, item_no)] = order_id
        if delivery_id and plant_id and delivery_id not in delivery_to_plant:
            delivery_to_plant[delivery_id] = plant_id
    return delivery_to_order, delivery_item_to_order, delivery_to_plant


def build_deliveries(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    delivery_to_order, _, delivery_to_plant = _delivery_to_order_lookup(raw)
    deliveries: list[dict[str, Any]] = []
    for row in raw["outbound_delivery_headers"]:
        delivery_id = _normalize_text(row.get("deliveryDocument"))
        if not delivery_id:
            continue
        status_parts = [
            _normalize_text(row.get("overallGoodsMovementStatus")),
            _normalize_text(row.get("overallPickingStatus")),
            _normalize_text(row.get("overallProofOfDeliveryStatus")),
        ]
        status = " | ".join(part for part in status_parts if part) or None
        deliveries.append(
            {
                "id": delivery_id,
                "order_id": delivery_to_order.get(delivery_id),
                "plant": delivery_to_plant.get(delivery_id) or _normalize_text(row.get("shippingPoint")),
                "status": status,
                "date": _normalize_text(row.get("actualGoodsMovementDate") or row.get("creationDate")),
            }
        )
    return deliveries


def build_invoices(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    delivery_to_order, delivery_item_to_order, _ = _delivery_to_order_lookup(raw)
    invoice_to_order: dict[str, str] = {}
    for row in raw["billing_document_items"]:
        invoice_id = _normalize_text(row.get("billingDocument"))
        ref_doc = _normalize_text(row.get("referenceSdDocument"))
        ref_item = _normalize_item_number(row.get("referenceSdDocumentItem"))
        if not invoice_id or not ref_doc:
            continue
        order_id = None
        if ref_doc.startswith("74"):
            order_id = ref_doc
        elif ref_item is not None:
            order_id = delivery_item_to_order.get((ref_doc, ref_item))
        if order_id is None:
            order_id = delivery_to_order.get(ref_doc)
        if order_id and invoice_id not in invoice_to_order:
            invoice_to_order[invoice_id] = order_id

    invoices: list[dict[str, Any]] = []
    for row in raw["billing_document_headers"]:
        invoice_id = _normalize_text(row.get("billingDocument"))
        if not invoice_id:
            continue
        status = "cancelled" if row.get("billingDocumentIsCancelled") else "active"
        invoices.append(
            {
                "id": invoice_id,
                "order_id": invoice_to_order.get(invoice_id),
                "amount": _normalize_number(row.get("totalNetAmount")),
                "date": _normalize_text(row.get("billingDocumentDate") or row.get("creationDate")),
                "status": status,
            }
        )
    return invoices


def build_payments(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    payments: list[dict[str, Any]] = []
    for row in raw["journal_entry_items_accounts_receivable"]:
        invoice_id = _normalize_text(row.get("referenceDocument"))
        payment_doc = _normalize_text(row.get("clearingAccountingDocument") or row.get("accountingDocument"))
        item_no = _normalize_item_number(row.get("accountingDocumentItem")) or "0"
        if not invoice_id or not payment_doc:
            continue
        payments.append(
            {
                "id": f"{payment_doc}-{invoice_id}-{item_no}",
                "invoice_id": invoice_id,
                "amount": _normalize_number(row.get("amountInTransactionCurrency")),
                "date": _normalize_text(row.get("clearingDate") or row.get("postingDate") or row.get("documentDate")),
                "method": _normalize_text(row.get("accountingDocumentType") or row.get("financialAccountType")),
            }
        )
    return payments


def build_canonical_tables(raw: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    return {
        "customers": build_customers(raw),
        "products": build_products(raw),
        "plants": build_plants(raw),
        "orders": build_orders(raw),
        "order_items": build_order_items(raw),
        "deliveries": build_deliveries(raw),
        "invoices": build_invoices(raw),
        "payments": build_payments(raw),
    }


def create_empty_tables(connection: sqlite3.Connection) -> None:
    for schema in TABLE_SCHEMAS.values():
        connection.execute(build_create_table_sql(schema))
    connection.commit()


def replace_table_rows(connection: sqlite3.Connection, table_name: str, rows: list[dict[str, Any]]) -> int:
    schema = TABLE_SCHEMAS[table_name]
    ordered_columns = list(schema.columns.keys())
    connection.execute(f"DELETE FROM {table_name}")
    if rows:
        placeholders = ", ".join("?" for _ in ordered_columns)
        sql = f"INSERT INTO {table_name} ({', '.join(ordered_columns)}) VALUES ({placeholders})"
        values = [tuple(row.get(column) for column in ordered_columns) for row in rows]
        connection.executemany(sql, values)
    count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"Table {table_name}: {count} rows")
    return count


def init_db() -> dict[str, int]:
    db_path = settings.sqlite_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    data_dir = settings.data_dir

    with sqlite3.connect(db_path) as connection:
        create_empty_tables(connection)
        if not data_dir.exists():
            row_counts = {
                table_name: connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                for table_name in TABLE_SCHEMAS
            }
            print(f"Data directory not found: {data_dir}")
            print(f"Existing row counts: {row_counts}")
            return row_counts

        raw = load_raw_dataset(data_dir)
        canonical_tables = build_canonical_tables(raw)
        row_counts = {}
        for table_name in TABLE_SCHEMAS:
            row_counts[table_name] = replace_table_rows(
                connection,
                table_name,
                canonical_tables.get(table_name, []),
            )
        connection.commit()
        return row_counts


if __name__ == "__main__":
    init_db()
