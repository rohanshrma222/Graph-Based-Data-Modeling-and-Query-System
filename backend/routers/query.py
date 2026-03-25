from __future__ import annotations

import re
import sqlite3
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.config import settings
from backend.database.models import schema_summary
from backend.graph.builder import get_graph
from backend.llm.client import call_llm
from backend.llm.guardrails import OFF_TOPIC_MESSAGE, is_relevant_query
from backend.llm.prompt import build_answer_prompt, build_sql_prompt


router = APIRouter(prefix="/api/query", tags=["query"])

READ_ONLY_BLOCKLIST = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "attach",
    "detach",
    "pragma",
    "vacuum",
    "begin",
    "commit",
    "rollback",
}

ID_PATTERN = re.compile(r"\b(?:CUST|ORD|ITEM|MAT|PROD|DEL|BIL|INV|PAY|PLANT)-?[A-Z0-9]+\b", re.IGNORECASE)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)


class QueryResponse(BaseModel):
    answer: str
    sql: str
    results: list[dict[str, Any]]
    nodes_referenced: list[str]


def validate_sql(sql: str) -> str:
    cleaned = sql.strip().strip("`")
    lowered = cleaned.lower()
    if not lowered.startswith("select") and not lowered.startswith("with"):
        raise ValueError("Generated SQL must start with SELECT or WITH.")
    if ";" in cleaned[:-1]:
        raise ValueError("Only a single SQL statement is allowed.")
    if any(token in lowered for token in READ_ONLY_BLOCKLIST):
        raise ValueError("Generated SQL is not read-only.")
    return cleaned


def execute_sql(sql: str) -> list[dict[str, Any]]:
    db_path = settings.sqlite_path
    if not db_path.exists():
        raise RuntimeError("SQLite database file does not exist. Run initialization first.")

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(sql)
        columns = [description[0] for description in cursor.description or []]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def generate_sql(question: str, previous_error: str | None = None) -> str:
    prompt = build_sql_prompt(question, schema_summary())
    if previous_error:
        prompt += f"\nPrevious SQL failed with this error: {previous_error}\nRegenerate valid SQLite SQL only."
    sql = call_llm(prompt)
    return validate_sql(sql)


def extract_nodes_referenced(results: list[dict[str, Any]]) -> list[str]:
    graph = get_graph()
    available_nodes = set(graph.nodes)
    referenced: set[str] = set()

    for row in results:
        for value in row.values():
            if value is None:
                continue
            text = str(value)
            for node_id in available_nodes:
                if text == graph.nodes[node_id].get("id"):
                    referenced.add(node_id)
            for match in ID_PATTERN.findall(text):
                for node_id in available_nodes:
                    if graph.nodes[node_id].get("id", "").lower() == match.lower():
                        referenced.add(node_id)

    return sorted(referenced)


@router.post("", response_model=QueryResponse)
def run_query(payload: QueryRequest) -> QueryResponse:
    question = payload.question.strip()
    if not is_relevant_query(question):
        raise HTTPException(status_code=400, detail=OFF_TOPIC_MESSAGE)

    try:
        sql = generate_sql(question)
        results = execute_sql(sql)
    except Exception as first_error:
        try:
            sql = generate_sql(question, previous_error=str(first_error))
            results = execute_sql(sql)
        except ValueError as retry_validation_error:
            raise HTTPException(status_code=400, detail=str(retry_validation_error)) from retry_validation_error
        except Exception as retry_error:
            raise HTTPException(status_code=500, detail=str(retry_error)) from retry_error
    
    try:
        answer = call_llm(build_answer_prompt(question, sql, results))
    except Exception as answer_error:
        raise HTTPException(status_code=500, detail=str(answer_error)) from answer_error

    return QueryResponse(
        answer=answer,
        sql=sql,
        results=results,
        nodes_referenced=extract_nodes_referenced(results),
    )
