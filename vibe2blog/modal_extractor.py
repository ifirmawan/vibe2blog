from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_MODAL_MODEL = "llm"


def modal_extraction_enabled() -> bool:
    """Use Modal only when the deployed vLLM endpoint is explicitly configured."""
    return bool(os.getenv("MODAL_VLLM_BASE_URL", "").strip())


def summarize_with_modal_vllm(raw_text: str, *, language: str) -> str:
    """Call a Modal-hosted OpenAI-compatible vLLM service for transcript extraction."""
    base_url = os.getenv("MODAL_VLLM_BASE_URL", "").strip()
    if not base_url:
        return ""

    model = os.getenv("MODAL_VLLM_MODEL", DEFAULT_MODAL_MODEL).strip() or DEFAULT_MODAL_MODEL
    timeout = float(os.getenv("MODAL_VLLM_TIMEOUT", "45"))
    endpoint = build_chat_completions_url(base_url)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": build_system_prompt(language),
            },
            {
                "role": "user",
                "content": raw_text[:12000],
            },
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 900,
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


class NoPostRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Expose Modal redirects so callers can repeat POST with the same body."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def post_json_with_modal_redirect(
    endpoint: str,
    payload: dict,
    headers: dict[str, str],
    *,
    timeout: float,
    max_redirects: int = 3,
) -> str:
    """POST JSON and manually follow Modal 303 redirects without changing to GET."""
    data = json.dumps(payload).encode("utf-8")
    opener = build_modal_opener()
    url = endpoint
    for _ in range(max_redirects + 1):
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code not in {301, 302, 303, 307, 308}:
                raise
            location = exc.headers.get("Location")
            if not location:
                raise
            url = urllib.parse.urljoin(url, location)
    return ""


def build_modal_opener() -> urllib.request.OpenerDirector:
    """Build an opener that understands Modal redirects and local CA bundles."""
    handlers: list[object] = [NoPostRedirectHandler]
    try:
        import certifi
    except ImportError:
        pass
    else:
        context = ssl.create_default_context(cafile=certifi.where())
        handlers.append(urllib.request.HTTPSHandler(context=context))
    return urllib.request.build_opener(*handlers)


def build_chat_completions_url(base_url: str) -> str:
    """Normalize a Modal web server URL into the OpenAI chat completions route."""
    trimmed = base_url.rstrip("/")
    if trimmed.endswith("/v1"):
        return f"{trimmed}/chat/completions"
    if trimmed.endswith("/v1/chat/completions"):
        return trimmed
    return f"{trimmed}/v1/chat/completions"


def build_system_prompt(language: str) -> str:
    """Constrain the extraction model to factual Markdown fields, not article prose."""
    if language == "id":
        return (
            "Kamu adalah extraction engine untuk Vibe2Blog. "
            "Ringkas transcript agentic coding mentah menjadi Markdown pendek dan faktual. "
            "Gunakan heading: Masalah awal, Temuan utama, Perubahan yang dilakukan, "
            "Verifikasi, File terkait, Hasil akhir. "
            "Jangan menyalin marker tool mentah seperti Read(...), Update(...), Bash(...), atau simbol transcript. "
            "Pertahankan detail teknis konkret seperti nama file, fungsi, command test, dan akar masalah."
        )
    return (
        "You are an extraction engine for Vibe2Blog. "
        "Summarize a raw agentic coding transcript into short factual Markdown. "
        "Use these headings: Initial problem, Key findings, Changes made, Verification, "
        "Related files, Outcome. "
        "Do not copy raw tool markers such as Read(...), Update(...), Bash(...), or transcript symbols. "
        "Preserve concrete technical details such as files, functions, test commands, and root cause."
    )


def parse_chat_completion_content(body: str) -> str:
    """Read the assistant message from a non-streaming chat completion response."""
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return ""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content", "")
    return content.strip() if isinstance(content, str) else ""
