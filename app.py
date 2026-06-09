from __future__ import annotations

import gradio as gr

from vibe2blog.pipeline import generate_article


SAMPLE_SUMMARY = """We planned Vibe2Blog, a Gradio app for the Build Small Hackathon.
The product changed from CLI-first to Gradio-first so judges can try it directly in a Hugging Face Space.
Important decisions:
- Gradio is the hackathon MVP.
- CLI and slash commands are future extensions.
- Output supports Indonesian and English.
- Likely secrets are redacted before generation.
- The generated result is Markdown with frontmatter.
"""

SAMPLE_TRANSCRIPT = """The key product decision was to keep the core generator reusable while making the hackathon demo Gradio-first.
We also added a Codex Track plan, GitHub-to-Hugging Face sync plan, and post-MVP extension PRDs for WordPress and Modal featured images.
"""

SAMPLE_DIFF = """diff --git a/README.md b/README.md
+ Added OpenAI Codex Track requirements.
+ Added Hugging Face Space deployment plan.
+ Added editorial quality pass to the roadmap.
"""

SAMPLE_VERIFICATION = """Documentation baseline was committed with a Codex co-author trailer.
The repo now includes PRDs, AGENTS.md, and Space deployment planning.
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
        "Mengubah Sesi Vibe Coding Menjadi Catatan Lapangan",
        SAMPLE_SUMMARY,
        SAMPLE_TRANSCRIPT,
        SAMPLE_DIFF,
        SAMPLE_VERIFICATION,
        "id",
        "reflective",
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
            topic = gr.Textbox(label="Topic or working title", placeholder="Building Vibe2Blog for the Build Small Hackathon")
            session_summary = gr.Textbox(
                label="Session summary or raw agent transcript",
                lines=8,
                placeholder="Paste a short summary or raw Claude Code/Codex-style session transcript...",
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
                label="Tone",
            )
            audience = gr.Dropdown(
                ["developers", "beginners", "maintainers", "product stakeholders"],
                value="developers",
                label="Audience",
            )
            include_code_snippets = gr.Checkbox(value=True, label="Include selected code snippets")
            include_frontmatter = gr.Checkbox(value=True, label="Include YAML frontmatter")
            editorial_quality_pass = gr.Checkbox(value=True, label="Editorial quality pass")
            sample_button = gr.Button("Load sample data", variant="secondary")
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
