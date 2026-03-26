from __future__ import annotations

try:
    from backend.llm.client import call_llm
except ModuleNotFoundError:
    from llm.client import call_llm


ALLOWED_TOPICS = {
    "orders", "order", "deliveries", "delivery", "invoices", "invoice", "payments", "payment", "customers", "customer", "products", "product", "billing", "supply chain", "logistics", "finance", "billing documents", "plants", "plant",
}

OFF_TOPIC_MESSAGE = "This system is designed to answer questions related to the provided dataset only."


def _keyword_match(question: str) -> bool:
    lowered = question.lower()
    return any(topic in lowered for topic in ALLOWED_TOPICS)


def _llm_relevance_check(question: str) -> bool:
    prompt = (
        "Classify whether the user question is relevant to a business dataset about "
        "orders, order items, deliveries, invoices, payments, customers, products, plants, "
        "billing, logistics, finance, and supply chain relationships.\n"
        "Respond with only YES or NO.\n\n"
        f"Question: {question}"
    )
    try:
        response = call_llm(prompt)
    except Exception:
        return False
    return response.strip().upper().startswith("YES")


def is_relevant_query(question: str) -> bool:
    if not question or not question.strip():
        return False
    if _keyword_match(question):
        return True
    return _llm_relevance_check(question)
