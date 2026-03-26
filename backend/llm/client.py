from __future__ import annotations

from typing import Optional

try:
    from backend.config import settings
except ModuleNotFoundError:
    from config import settings


def _load_genai_module():
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise RuntimeError("google-generativeai is not installed. Install backend requirements first.") from exc
    return genai


def _normalize_model_name(model_name: str) -> str:
    normalized = model_name.strip().strip('"').strip("'").lower().replace(' ', '-')
    if normalized.startswith('models/'):
        return normalized.removeprefix('models/')
    return normalized


def call_llm(prompt: str, model_name: str | None = None, timeout_seconds: int = 20) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai = _load_genai_module()
    genai.configure(api_key=settings.gemini_api_key.strip().strip('"').strip("'"))
    model = genai.GenerativeModel(_normalize_model_name(model_name or settings.gemini_model))
    try:
        response = model.generate_content(prompt, request_options={"timeout": timeout_seconds})
    except Exception as exc:
        raise RuntimeError(f"Gemini request failed: {exc}") from exc

    text: Optional[str] = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()
