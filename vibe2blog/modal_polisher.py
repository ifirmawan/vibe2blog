from __future__ import annotations

import os
import urllib.error

from .context import SessionContext
from .modal_extractor import (
    DEFAULT_MODAL_MODEL,
    build_chat_completions_url,
    parse_chat_completion_content,
    post_json_with_modal_redirect,
)


STORYTELLING_TONE = "human storytelling technical blog"


def modal_polish_enabled() -> bool:
    """Enable the polish pass only when the user explicitly opts in."""
    enabled = os.getenv("MODAL_POLISH_ENABLED", "false").strip().lower()
    return enabled in {"1", "true", "yes", "on"}


def should_polish_with_modal() -> bool:
    """Check both the feature flag and the shared Modal vLLM endpoint config."""
    return modal_polish_enabled() and bool(os.getenv("MODAL_VLLM_BASE_URL", "").strip())


def polish_markdown_with_modal(markdown: str, context: SessionContext) -> str:
    """Rewrite a Markdown draft through Modal vLLM, returning blank on failure."""
    base_url = os.getenv("MODAL_VLLM_BASE_URL", "").strip()
    if not base_url:
        return ""

    model = os.getenv("MODAL_VLLM_MODEL", DEFAULT_MODAL_MODEL).strip() or DEFAULT_MODAL_MODEL
    timeout = float(os.getenv("MODAL_POLISH_TIMEOUT", "60"))
    endpoint = build_chat_completions_url(base_url)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_polish_system_prompt(context.language)},
            {"role": "user", "content": build_polish_user_prompt(markdown, context)},
        ],
        "temperature": 0.35,
        "top_p": 0.9,
        "max_tokens": 1800,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    api_key = os.getenv("MODAL_VLLM_API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        body = post_json_with_modal_redirect(endpoint, payload, headers, timeout=timeout)
    except (OSError, urllib.error.HTTPError, urllib.error.URLError):
        return ""

    return parse_chat_completion_content(body)


def build_polish_system_prompt(language: str) -> str:
    """Constrain Modal to editorial polish, not new article generation."""
    if language == "id":
        return (
            "Kamu adalah editor teknis untuk Vibe2Blog. "
            "Poles draft Markdown agar terasa lebih natural, spesifik, dan manusiawi. "
            "Pertahankan semua klaim faktual, struktur Markdown, YAML frontmatter, heading, "
            "nama file, command, hasil verifikasi, dan code block. "
            "Jangan membuat YAML frontmatter, tanggal, author, tag, atau metadata baru jika tidak ada di draft. "
            "Jangan mengarang test, file, API, keputusan, hasil, atau detail baru. "
            "Hilangkan frasa AI generik dan perbaiki alur transisi. "
            "Susun ulang draft sebagai cerita teknis yang enak diikuti: masalah, penelusuran, momen temuan, perubahan, verifikasi, dan pelajaran. "
            "Boleh menambahkan transisi atau kalimat penghubung ringan selama tetap berada dalam konteks yang diberikan. "
            "Jika draft pendek, tetap poles draft yang ada tanpa meminta konteks tambahan. "
            "Jangan memberi contoh, template, penjelasan, atau catatan editor. "
            "Kembalikan hanya Markdown final."
        )
    return (
        "You are a technical editor for Vibe2Blog. "
        "Polish the Markdown draft so it reads more natural, specific, and human. "
        "Preserve all factual claims, Markdown structure, YAML frontmatter, headings, "
        "file names, commands, verification results, and code blocks. "
        "Do not create YAML frontmatter, dates, authors, tags, or metadata when the draft does not already include them. "
        "Do not invent tests, files, APIs, decisions, outcomes, or new details. "
        "Remove generic AI phrasing and improve narrative flow. "
        "Shape the draft as a technical story: problem, investigation, discovery moment, change, verification, and lesson. "
        "You may add light transitions or connective sentences as long as they stay inside the supplied context. "
        "If the draft is short, polish only the draft provided without asking for more context. "
        "Do not provide examples, templates, explanations, or editor notes. "
        "Return only the final Markdown."
    )


def build_polish_user_prompt(markdown: str, context: SessionContext) -> str:
    """Provide style context and the bounded draft to rewrite."""
    return f"""Language: {context.language}
Editorial mode: {context.tone}
Audience: {context.audience}

Rewrite this Markdown draft according to the system instructions.
Return the edited version of this exact draft only.

Draft:
{markdown[:16000]}
"""


def maybe_polish_markdown(markdown: str, context: SessionContext) -> str:
    """Apply Modal polish when configured, otherwise return the original draft."""
    if not should_polish_with_modal():
        return markdown
    polished = polish_markdown_with_modal(markdown, context)
    return polished or markdown
