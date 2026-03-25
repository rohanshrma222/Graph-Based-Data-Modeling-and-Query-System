from __future__ import annotations

import sqlite3
from typing import Any

import networkx as nx

from backend.config import settings


_GRAPH: nx.DiGraph | None = None


NODE_PREFIXES = {
    "customers": "Customer",
    "orders": "Order",
    "order_items": "OrderItem",
    "products": "Product",
    "deliveries": "Delivery",
    "invoices": "Invoice",
    "payments": "Payment",
    "plants": "Plant",
}


def _node_key(node_type: str, raw_id: Any) -> str:
    return f"{node_type}:{raw_id}"


def _fetch_rows(connection: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    cursor = connection.execute(f"SELECT * FROM {table_name}")
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _add_entity_nodes(graph: nx.DiGraph, rows: list[dict[str, Any]], table_name: str) -> None:
    node_type = NODE_PREFIXES[table_name]
    for row in rows:
        raw_id = row.get("id")
        if raw_id is None:
            continue
        node_id = _node_key(node_type, raw_id)
        graph.add_node(
            node_id,
            id=str(raw_id),
            type=node_type,
            label=str(row.get("name") or raw_id),
            metadata=row,
        )


def build_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    db_path = settings.sqlite_path
    if not db_path.exists():
        return graph

    with sqlite3.connect(db_path) as connection:
        tables = {table: _fetch_rows(connection, table) for table in NODE_PREFIXES}

    for table_name, rows in tables.items():
        _add_entity_nodes(graph, rows, table_name)

    for order in tables["orders"]:
        if order.get("customer_id") and order.get("id"):
            graph.add_edge(
                _node_key("Customer", order["customer_id"]),
                _node_key("Order", order["id"]),
                relationship="PLACED",
            )

    for item in tables["order_items"]:
        if item.get("order_id") and item.get("id"):
            graph.add_edge(
                _node_key("Order", item["order_id"]),
                _node_key("OrderItem", item["id"]),
                relationship="CONTAINS",
            )
        if item.get("product_id") and item.get("id"):
            graph.add_edge(
                _node_key("OrderItem", item["id"]),
                _node_key("Product", item["product_id"]),
                relationship="IS_FOR",
            )

    for delivery in tables["deliveries"]:
        if delivery.get("order_id") and delivery.get("id"):
            graph.add_edge(
                _node_key("Order", delivery["order_id"]),
                _node_key("Delivery", delivery["id"]),
                relationship="HAS_DELIVERY",
            )
        if delivery.get("plant") and delivery.get("id"):
            graph.add_edge(
                _node_key("Delivery", delivery["id"]),
                _node_key("Plant", delivery["plant"]),
                relationship="SHIPPED_FROM",
            )

    for invoice in tables["invoices"]:
        if invoice.get("order_id") and invoice.get("id"):
            graph.add_edge(
                _node_key("Order", invoice["order_id"]),
                _node_key("Invoice", invoice["id"]),
                relationship="HAS_INVOICE",
            )

    for payment in tables["payments"]:
        if payment.get("invoice_id") and payment.get("id"):
            graph.add_edge(
                _node_key("Invoice", payment["invoice_id"]),
                _node_key("Payment", payment["id"]),
                relationship="SETTLED_BY",
            )

    return graph


def get_graph(refresh: bool = False) -> nx.DiGraph:
    global _GRAPH
    if refresh or _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


def serialize_graph(graph: nx.DiGraph) -> dict[str, list[dict[str, Any]]]:
    nodes = [
        {
            "id": node_id,
            "type": attrs.get("type"),
            "label": attrs.get("label"),
            "metadata": attrs.get("metadata", {}),
        }
        for node_id, attrs in graph.nodes(data=True)
    ]
    edges = [
        {
            "source": source,
            "target": target,
            "relationship": attrs.get("relationship"),
        }
        for source, target, attrs in graph.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges}


def get_node_neighbors(node_id: str) -> dict[str, Any]:
    graph = get_graph()
    if node_id not in graph:
        return {"node": None, "neighbors": [], "edges": []}

    neighbor_ids = sorted(set(graph.predecessors(node_id)) | set(graph.successors(node_id)))
    neighbors = [{"id": neighbor_id, **graph.nodes[neighbor_id]} for neighbor_id in neighbor_ids]
    edges = []
    for source, target, attrs in graph.in_edges(node_id, data=True):
        edges.append({"source": source, "target": target, **attrs})
    for source, target, attrs in graph.out_edges(node_id, data=True):
        edges.append({"source": source, "target": target, **attrs})

    return {
        "node": {"id": node_id, **graph.nodes[node_id]},
        "neighbors": neighbors,
        "edges": edges,
    }


def get_subgraph(node_ids: list[str]) -> nx.DiGraph:
    graph = get_graph()
    existing_ids = [node_id for node_id in node_ids if node_id in graph]
    return graph.subgraph(existing_ids).copy()
