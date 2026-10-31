"""LLM factory for Groq-hosted models."""

import os

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
DEFAULT_GUARD_MODEL = os.getenv("GROQ_GUARD_MODEL", "meta-llama/llama-guard-4-12b")


def get_llm(temperature: float = 0.0, model: str = DEFAULT_MODEL):
    """Return a ChatGroq model. Groq accepts temperature in the range 0-2."""
    from langchain_groq import ChatGroq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Create one at https://console.groq.com/keys")
    if not 0 <= temperature <= 2:
        raise ValueError("temperature must be between 0 and 2")
    return ChatGroq(model=model, temperature=temperature, groq_api_key=api_key)
