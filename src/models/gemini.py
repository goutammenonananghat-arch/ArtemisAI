from __future__ import annotations

import asyncio

import google.generativeai as genai

from security.secrets_manager import SecretsManager

_api_key = SecretsManager().retrieve("GEMINI_API_KEY")
if not _api_key:
    raise RuntimeError("GEMINI_API_KEY not found in secrets manager.")

genai.configure(api_key=_api_key)


async def generate(prompt: str, **kwargs) -> str:
    """Generate a response from Google's Gemini model.

    Parameters
    ----------
    prompt: str
        Prompt to send to the model.
    **kwargs:
        Additional parameters passed to ``GenerativeModel`` and
        ``generate_content``. ``model_name`` defaults to ``\"gemini-pro\"``.

    Returns
    -------
    str
        The text output from the model.
    """
    model_name = kwargs.pop("model_name", "gemini-pro")
    model = genai.GenerativeModel(model_name)
    response = await asyncio.to_thread(model.generate_content, prompt, **kwargs)
    return response.text
