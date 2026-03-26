from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.database.init_db import init_db
    from backend.graph.builder import get_graph
    from backend.routers.graph import router as graph_router
    from backend.routers.query import router as query_router
except ModuleNotFoundError:
    from database.init_db import init_db
    from graph.builder import get_graph
    from routers.graph import router as graph_router
    from routers.query import router as query_router


app = FastAPI(title="Graph-Based Data Modeling and Query System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph_router)
app.include_router(query_router)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    get_graph(refresh=True)


@app.get("/health")
def health_check() -> dict[str, int | str]:
    graph = get_graph()
    return {
        "status": "ok",
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
    }
