from __future__ import annotations

import re
from dataclasses import dataclass

from .modal_extractor import modal_extraction_enabled, summarize_with_modal_vllm


CLAUDE_MARKERS = ("⏺", "⎿", "Read(", "Update(", "Search(", "Bash(", "Edit(", "Write(")


@dataclass(frozen=True)
class ExtractedSession:
    problem: str
    findings: list[str]
    changes: list[str]
    verification: list[str]
    files: list[str]
    outcome: str

    def has_signal(self) -> bool:
        """Return true when the transcript parser found at least one useful field."""
        return any([self.problem, self.findings, self.changes, self.verification, self.files, self.outcome])

    def to_markdown(self, language: str) -> str:
        """Render extracted fields as compact Markdown for the article generator."""
        if language == "id":
            return self._to_indonesian_markdown()
        return self._to_english_markdown()

    def _to_indonesian_markdown(self) -> str:
        return "\n\n".join(
            section
            for section in [
                f"Masalah awal: {self.problem}" if self.problem else "",
                bullet_section("Temuan utama", self.findings),
                bullet_section("Perubahan yang dilakukan", self.changes),
                bullet_section("Verifikasi", self.verification),
                bullet_section("File terkait", self.files),
                f"Hasil akhir: {self.outcome}" if self.outcome else "",
            ]
            if section
        )

    def _to_english_markdown(self) -> str:
        return "\n\n".join(
            section
            for section in [
                f"Initial problem: {self.problem}" if self.problem else "",
                bullet_section("Key findings", self.findings),
                bullet_section("Changes made", self.changes),
                bullet_section("Verification", self.verification),
                bullet_section("Related files", self.files),
                f"Outcome: {self.outcome}" if self.outcome else "",
            ]
            if section
        )


def maybe_extract_session_summary(raw_text: str, *, language: str) -> str:
    """Summarize raw agent transcripts while leaving normal user summaries untouched."""
    if not looks_like_agent_transcript(raw_text):
        return raw_text.strip()

    if modal_extraction_enabled():
        modal_summary = summarize_with_modal_vllm(raw_text, language=language)
        if modal_summary:
            return modal_summary

    extracted = extract_session(raw_text)
    if not extracted.has_signal():
        return raw_text.strip()
    return extracted.to_markdown(language)


def looks_like_agent_transcript(text: str) -> bool:
    """Detect Claude/Codex-style logs using tool markers and user-turn syntax."""
    marker_count = sum(text.count(marker) for marker in CLAUDE_MARKERS)
    command_like = len(re.findall(r"\b(Read|Update|Search|Bash)\(", text))
    user_turns = len(re.findall(r"^>\s+", text, re.MULTILINE))
    return marker_count + command_like + user_turns >= 3


def extract_session(raw_text: str) -> ExtractedSession:
    """Extract a deterministic session summary when no Modal endpoint is configured."""
    cleaned_lines = [normalize_line(line) for line in raw_text.splitlines()]
    cleaned_lines = [line for line in cleaned_lines if line]

    problem = extract_problem(cleaned_lines)
    findings = unique_limited(extract_findings(cleaned_lines), 5)
    changes = unique_limited(extract_changes(cleaned_lines), 6)
    verification = unique_limited(extract_verification(cleaned_lines), 5)
    files = unique_limited(extract_files(raw_text), 8)
    outcome = extract_outcome(cleaned_lines)

    return ExtractedSession(
        problem=problem,
        findings=findings,
        changes=changes,
        verification=verification,
        files=files,
        outcome=outcome,
    )


def extract_problem(lines: list[str]) -> str:
    """Prefer the first explicit user request as the problem statement."""
    user_lines = [line[2:].strip() for line in lines if line.startswith("> ")]
    for line in user_lines:
        lowered = line.lower()
        if line and not lowered.startswith(("commit", "this branch", "its works", "it works")):
            return trim_sentence(line, 220)
    for line in lines:
        lowered = line.lower()
        if any(token in lowered for token in ("issue", "bug", "problem", "overlap", "unable", "preventing")):
            return trim_sentence(strip_tool_prefix(line), 220)
    return ""


def extract_findings(lines: list[str]) -> list[str]:
    """Collect likely root-cause observations from assistant narration."""
    findings: list[str] = []
    for line in lines:
        lowered = line.lower()
        if any(phrase in lowered for phrase in ("i found the issue", "i can see the issue", "the issue", "root cause", "because", "doesn't account", "passes")):
            findings.append(trim_sentence(strip_tool_prefix(line), 260))
    return findings


def extract_changes(lines: list[str]) -> list[str]:
    """Collect compact change hints from update logs and diff-like lines."""
    changes: list[str] = []
    for line in lines:
        lowered = line.lower()
        if "updated " in lowered and " with " in lowered:
            changes.append(trim_sentence(strip_tool_prefix(line), 220))
        elif lowered.startswith(("+ ", "- ")) and len(line) > 6:
            changes.append(trim_sentence(line, 220))
        elif any(phrase in lowered for phrase in ("added ", "imported ", "changed ", "updated the", "reset ", "created 2 commits")):
            changes.append(trim_sentence(strip_tool_prefix(line), 220))
    return changes


def extract_verification(lines: list[str]) -> list[str]:
    """Collect test commands and verification outcomes mentioned in the session."""
    verification: list[str] = []
    for line in lines:
        lowered = line.lower()
        if any(token in lowered for token in ("type-check", "eslint", "test", "verify", "verified", "works", "worked", "git status")):
            verification.append(trim_sentence(strip_tool_prefix(line), 240))
    return verification


def extract_outcome(lines: list[str]) -> str:
    """Use the last completion-like line as the session outcome."""
    for line in reversed(lines):
        lowered = line.lower()
        if any(phrase in lowered for phrase in ("done.", "the fix is complete", "fix worked", "has been reset", "branch is now focused", "final branch commits")):
            return trim_sentence(strip_tool_prefix(line), 260)
    return ""


def extract_files(raw_text: str) -> list[str]:
    """Find repo-relative file paths that help anchor the generated article."""
    matches = re.findall(r"(?:src|includes|app|tests|vibe2blog|docs)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+", raw_text)
    return [match.rstrip(").,") for match in matches]


def normalize_line(line: str) -> str:
    """Strip transcript glyphs and collapse spacing before pattern matching."""
    stripped = line.strip()
    stripped = stripped.removeprefix("⏺").strip()
    stripped = stripped.removeprefix("⎿").strip()
    return re.sub(r"\s+", " ", stripped)


def strip_tool_prefix(line: str) -> str:
    """Make tool-call lines readable enough to appear in a compact summary."""
    match = re.match(r"^(Read|Update|Search|Bash|Edit|Write)\((.*)\)$", line.strip())
    if not match:
        return line.strip()

    tool, payload = match.groups()
    payload = payload.strip()
    labels = {
        "Bash": "Command",
        "Read": "Read file",
        "Update": "Updated file",
        "Search": "Search",
        "Edit": "Edited file",
        "Write": "Wrote file",
    }
    return f"{labels[tool]}: {payload}"


def bullet_section(title: str, values: list[str]) -> str:
    """Render a titled bullet section only when it has values."""
    if not values:
        return ""
    bullets = "\n".join(f"- {value}" for value in values)
    return f"{title}:\n{bullets}"


def trim_sentence(value: str, limit: int) -> str:
    """Keep extracted snippets short so prompts do not become transcript dumps."""
    stripped = value.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3].rstrip() + "..."


def unique_limited(values: list[str], limit: int) -> list[str]:
    """Deduplicate extracted facts while preserving their original order."""
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        normalized = value.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append(value)
        if len(unique) >= limit:
            break
    return unique
