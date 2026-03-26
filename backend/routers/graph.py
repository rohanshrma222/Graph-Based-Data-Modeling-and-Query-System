from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

try:
    from backend.graph.builder import get_graph, get_node_neighbors, get_subgraph, serialize_graph
except ModuleNotFoundError:
    from graph.builder import get_graph, get_node_neighbors, get_subgraph, serialize_graph


router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("")
def read_graph() -> dict:
    return serialize_graph(get_graph())


@router.get("/node/{node_id}")
def read_node(node_id: str) -> dict:
    data = get_node_neighbors(node_id)
    if data["node"] is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return data


@router.get("/subgraph")
def read_subgraph(node_ids: str = Query(..., description="Comma-separated node IDs")) -> dict:
    parsed_node_ids = [node_id.strip() for node_id in node_ids.split(",") if node_id.strip()]
    if not parsed_node_ids:
        raise HTTPException(status_code=400, detail="At least one node_id is required")
    return serialize_graph(get_subgraph(parsed_node_ids))
