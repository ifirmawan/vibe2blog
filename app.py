from __future__ import annotations

import gradio as gr

from vibe2blog.modal_polisher import should_polish_with_modal
from vibe2blog.pipeline import generate_article


MODAL_STORYTELLING_ENABLED = should_polish_with_modal()

SAMPLE_TITLE = "Fixing a Login Button That Stayed Disabled"

SAMPLE_SUMMARY = """> The login button stays disabled even after users enter a valid email and password.

⏺ I'll inspect the login form state and validation logic.
⏺ Read(src/screens/LoginScreen.tsx)
⎿ Read 120 lines
⏺ I found the issue. The form validates email and password correctly, but the disabled state reads from an old `isValid` flag that is never updated after typing.
⏺ Search(pattern: "isValid", path: "src/screens")
⎿ Found 3 matches
⏺ Update(src/screens/LoginScreen.tsx)
⎿ Updated src/screens/LoginScreen.tsx with 4 additions and 2 removals

The fix removes the stale `isValid` state and derives `canSubmit` directly from the current email, password, loading state, and validation errors.

> It works now. The button enables after valid input and disables while the login request is running.
"""

SAMPLE_TRANSCRIPT = """The session focused on a common UI bug: the visual form looked valid, but the submit button stayed disabled.
The useful debugging step was comparing what the UI displayed with which state variable actually controlled the button.
"""

SAMPLE_DIFF = """diff --git a/src/screens/LoginScreen.tsx b/src/screens/LoginScreen.tsx
- const [isValid, setIsValid] = useState(false)
- const disabled = !isValid || isLoading
+ const canSubmit = emailError === "" && passwordError === "" && email !== "" && password !== ""
+ const disabled = !canSubmit || isLoading
"""

SAMPLE_VERIFICATION = """Manual test:
- Empty form keeps the login button disabled.
- Invalid email keeps the button disabled and shows an error.
- Valid email and password enable the button.
- Clicking login disables the button while the request is pending.
"""


def generate(
    topic: str,
    session_summary: str,
    transcript_excerpt: str,
    git_diff: str,
    verification_notes: str,
    language: str,
    tone: str,
    audience: str,
    include_code_snippets: bool,
    include_frontmatter: bool,
    editorial_quality_pass: bool,
) -> tuple[str, str, str, str]:
    try:
        result = generate_article(
            topic=topic,
            session_summary=session_summary,
            transcript_excerpt=transcript_excerpt,
            git_diff=git_diff,
            verification_notes=verification_notes,
            language=language,
            tone=tone,
            audience=audience,
            include_code_snippets=include_code_snippets,
            include_frontmatter=include_frontmatter,
            editorial_quality_pass=editorial_quality_pass,
        )
    except Exception as exc:
        return "", "Generation failed", f"Error: {exc}", ""

    validation_message = (
        "Validation passed"
        if result.validation.valid
        else "Validation issues: " + "; ".join(result.validation.issues)
    )
    metadata = (
        f"Title: {result.generation.title}\n"
        f"Provider: {result.generation.provider}\n"
        f"Quality: {result.generation.quality_notes}\n"
        f"{validation_message}"
    )
    return (
        result.generation.markdown,
        result.generation.title,
        metadata,
        result.download_path,
    )


def load_sample() -> tuple[str, str, str, str, str, str, str, str, bool, bool, bool]:
    return (
        SAMPLE_TITLE,
        SAMPLE_SUMMARY,
        SAMPLE_TRANSCRIPT,
        SAMPLE_DIFF,
        SAMPLE_VERIFICATION,
        "en",
        "narrative",
        "developers",
        True,
        True,
        True,
    )


with gr.Blocks(
    title="Vibe2Blog",
    theme=gr.themes.Soft(primary_hue="emerald", neutral_hue="slate"),
    css="""
    .vibe2blog-title {max-width: 960px}
    .vibe2blog-note {font-size: 0.92rem; opacity: 0.82}
    textarea {font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace}
    """,
) as demo:
    gr.Markdown(
        """
        # Vibe2Blog

        Turn messy agentic coding context into editable Markdown field notes.

        Built for the Build Small Hackathon with Codex-assisted development.

        Space: https://huggingface.co/spaces/build-small-hackathon/vibe2blog

        Public GitHub repository: https://github.com/ifirmawan/vibe2blog
        """,
        elem_classes=["vibe2blog-title"],
    )

    with gr.Row():
        with gr.Column(scale=5):
            topic = gr.Textbox(
                label="Topic or working title",
                placeholder="Example: Fixing a Login Button That Stayed Disabled",
            )
            session_summary = gr.Textbox(
                label="Session summary or raw agent transcript",
                lines=8,
                placeholder=(
                    "Paste a summary or raw agent transcript. Example: the problem, what the agent inspected, "
                    "what changed, how it was verified, and the final outcome."
                ),
            )
            with gr.Accordion("Optional context", open=False):
                transcript_excerpt = gr.Textbox(label="Transcript excerpt", lines=5)
                git_diff = gr.Textbox(label="Git diff excerpt", lines=5)
                verification_notes = gr.Textbox(label="Verification notes", lines=4)
        with gr.Column(scale=3):
            language = gr.Radio(["id", "en"], value="id", label="Language")
            tone = gr.Dropdown(
                ["reflective", "tutorial", "concise", "narrative"],
                value="reflective",
                label="Tone (fallback mode only)",
                visible=not MODAL_STORYTELLING_ENABLED,
            )
            gr.Markdown(
                (
                    "Modal storytelling mode is active. Tone presets are disabled so the model can shape a more natural engineering story from the supplied context."
                    if MODAL_STORYTELLING_ENABLED
                    else "Tone presets are used by the deterministic fallback when Modal storytelling mode is not enabled."
                ),
                elem_classes=["vibe2blog-note"],
            )
            audience = gr.Dropdown(
                ["developers", "beginners", "maintainers", "product stakeholders"],
                value="developers",
                label="Audience",
            )
            include_code_snippets = gr.Checkbox(value=True, label="Include selected code snippets")
            include_frontmatter = gr.Checkbox(value=True, label="Include YAML frontmatter")
            editorial_quality_pass = gr.Checkbox(value=True, label="Editorial quality pass")
            sample_button = gr.Button("Load demo template", variant="secondary")
            generate_button = gr.Button("Generate Markdown", variant="primary")
            gr.Markdown(
                "Do not paste secrets. Vibe2Blog redacts common token patterns and can summarize raw agent transcripts before building the prompt.",
                elem_classes=["vibe2blog-note"],
            )

    with gr.Row():
        with gr.Column(scale=5):
            markdown_output = gr.Textbox(label="Markdown draft", lines=22, show_copy_button=True)
        with gr.Column(scale=3):
            title_output = gr.Textbox(label="Generated title")
            metadata_output = gr.Textbox(label="Generation metadata", lines=8)
            download_output = gr.File(label="Download .md")

    sample_button.click(
        load_sample,
        outputs=[
            topic,
            session_summary,
            transcript_excerpt,
            git_diff,
            verification_notes,
            language,
            tone,
            audience,
            include_code_snippets,
            include_frontmatter,
            editorial_quality_pass,
        ],
    )

    generate_button.click(
        generate,
        inputs=[
            topic,
            session_summary,
            transcript_excerpt,
            git_diff,
            verification_notes,
            language,
            tone,
            audience,
            include_code_snippets,
            include_frontmatter,
            editorial_quality_pass,
        ],
        outputs=[markdown_output, title_output, metadata_output, download_output],
    )


if __name__ == "__main__":
    demo.launch()
