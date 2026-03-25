from __future__ import annotations

from typing import Optional

from backend.config import settings


def _load_genai_module():
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise RuntimeError(
            "google-generativeai is not installed. Install backend requirements first."
        ) from exc
    return genai


def call_llm(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai = _load_genai_module()
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    text: Optional[str] = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()
