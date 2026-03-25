from __future__ import annotations

import json


def build_sql_prompt(user_question: str, schema: str) -> str:
    examples = [
        {
            "question": "Which customer has the most pending payments?",
            "sql": (
                "SELECT c.id, c.name, COUNT(p.id) AS pending_payment_count "
                "FROM customers c "
                "JOIN orders o ON o.customer_id = c.id "
                "JOIN invoices i ON i.order_id = o.id "
                "LEFT JOIN payments p ON p.invoice_id = i.id "
                "WHERE i.status = 'pending' OR p.id IS NULL "
                "GROUP BY c.id, c.name "
                "ORDER BY pending_payment_count DESC LIMIT 1;"
            ),
        },
        {
            "question": "Show me all sales orders that were delivered but never billed",
            "sql": (
                "SELECT DISTINCT o.id, o.status, d.id AS delivery_id "
                "FROM orders o "
                "JOIN deliveries d ON d.order_id = o.id "
                "LEFT JOIN invoices i ON i.order_id = o.id "
                "WHERE d.id IS NOT NULL AND i.id IS NULL;"
            ),
        },
    ]
    return (
        "You are generating SQLite SQL for a read-only analytics system.\n"
        "Return ONLY valid SQLite SQL.\n"
        "Do not include markdown, comments, or explanation.\n"
        "Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH, PRAGMA, REPLACE, or transaction statements.\n\n"
        f"Database schema:\n{schema}\n\n"
        f"Examples:\n{json.dumps(examples, indent=2)}\n\n"
        f"User question:\n{user_question}\n"
    )


def build_answer_prompt(question: str, sql: str, results: list[dict]) -> str:
    return (
        "You are answering a question strictly from query results.\n"
        "Ground every statement in the provided data.\n"
        "If the results are empty, say that the data returned no matching records.\n"
        "Do not invent fields, causes, or external context.\n\n"
        f"Original question:\n{question}\n\n"
        f"SQL executed:\n{sql}\n\n"
        f"Raw results JSON:\n{json.dumps(results, indent=2, default=str)}\n"
    )
