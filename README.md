---
title: Vibe2Blog
emoji: 📝
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.50.0
python_version: '3.13'
app_file: app.py
pinned: false
license: gpl-3.0
short_description: Turn agentic coding sessions into editable Markdown notes
---

# Vibe2Blog

Vibe2Blog is a Gradio app that turns vibe coding session context into editable Markdown blog drafts.

It is designed for developers who code with AI agents and want to preserve the useful reasoning that usually disappears after a session: the original problem, implementation path, technical decisions, verification notes, and lessons learned.

This project is being prepared as a Build Small Hackathon submission.

## Links

- Public GitHub repository: https://github.com/ifirmawan/vibe2blog
- Hugging Face Space: https://huggingface.co/spaces/build-small-hackathon/vibe2blog
- Social post proof: `<add-social-post-url>`

For the OpenAI Codex Track, the Hugging Face Space README must include the public GitHub repository link.
For the main hackathon submission, the Space README must include proof of a social media post.

## Project Status

Planning and product definition are complete. The first Gradio MVP implementation is in progress.

Current artifacts:

- Product PRD: [`docs/prd-blog-from-vibe-coding.md`](docs/prd-blog-from-vibe-coding.md)
- Hackathon submission plan: [`docs/hackathon-submission-plan.md`](docs/hackathon-submission-plan.md)
- OpenAI Codex Track plan: [`docs/openai-codex-track-plan.md`](docs/openai-codex-track-plan.md)
- Remotion demo video PRD: [`docs/remotion-demo-video-prd.md`](docs/remotion-demo-video-prd.md)
- GitHub to Hugging Face sync plan: [`docs/github-to-huggingface-sync-plan.md`](docs/github-to-huggingface-sync-plan.md)
- WordPress publishing extension PRD: [`docs/prd-wordpress-publishing.md`](docs/prd-wordpress-publishing.md)
- Featured image generation PRD: [`docs/prd-featured-image-modal.md`](docs/prd-featured-image-modal.md)
- Agent instructions: [`AGENTS.md`](AGENTS.md)

## What It Does

The app lets a user paste:

- A vibe coding session summary or raw Claude Code/Codex-style transcript
- Optional transcript excerpt
- Optional git diff
- Optional verification notes

Then the user can choose:

- Output language: Indonesian (`id`) or English (`en`)
- Tone
- Target audience
- Whether to include frontmatter
- Whether to include code snippets

The app will generate:

- A Markdown article draft
- YAML frontmatter
- A clear engineering story
- Technical decisions
- Verification notes
- Lessons learned
- An editorial quality pass for more natural, specific prose
- A downloadable `.md` file

Raw agent transcripts are normalized into a compact session summary before article generation. This keeps the draft focused on the problem, findings, changes, verification, related files, and outcome instead of copying a long tool log verbatim.

Transcript extraction has two paths:

- Deterministic local extraction for Claude Code/Codex-style tool logs.
- Optional Modal vLLM extraction when `MODAL_VLLM_BASE_URL` is configured.

Editorial polishing also has two paths:

- Lightweight local quality scoring and deterministic cleanup.
- Optional Modal vLLM rewrite when `MODAL_POLISH_ENABLED=true` and `MODAL_VLLM_BASE_URL` is configured.

## Hackathon Fit

Vibe2Blog is planned as a Gradio app hosted on Hugging Face Spaces.

The hackathon MVP should:

- Use a small model within the Build Small Hackathon constraint of <=32B parameters.
- Be usable directly from a Hugging Face Space, preferably under the official hackathon organization when eligible.
- Include sample data so judges can try it quickly.
- Generate both Indonesian and English Markdown output.
- Include a short demo video built with Remotion.
- Link social post proof from the Space README.

For the OpenAI Codex Track:

- Build the Space with Codex as the coding agent.
- Push the code to a public GitHub repository.
- Keep Codex-attributed commits in the repository history.
- Add the public GitHub repository link to the Hugging Face Space README.

## Implementation Roadmap

### 1. Core Generator

- Define the `SessionContext` data shape.
- Normalize user input and extract signal from raw agent transcripts.
- Redact likely secrets.
- Build language-aware prompts.
- Validate generated Markdown.
- Add an editorial quality pass to reduce generic prose.
- Export Markdown with a deterministic filename.

### 2. Gradio App

- Build the main Gradio interface.
- Add sample input.
- Add language, tone, and audience controls.
- Display generated Markdown.
- Add copy and download actions.
- Add clear error states.

### 3. Small Model Integration

- Select a model that fits the <=32B parameter constraint.
- Integrate the model behind an `ArticleGenerator` boundary.
- Verify Indonesian and English output quality.
- Document model name, parameter count, and runtime assumptions.

### 4. Hugging Face Space

- Deploy the Gradio app as a Space.
- Run a smoke test with sample data.
- Confirm generation latency is acceptable.
- Confirm Markdown download works.
- Sync from GitHub to the Space using the planned GitHub Actions workflow.
- Add the public GitHub repository link to the Space README for the Codex Track.

### 5. Demo Video

- Build the Remotion demo video described in [`docs/remotion-demo-video-prd.md`](docs/remotion-demo-video-prd.md).
- Show the flow from messy coding context to downloadable Markdown.
- Include the Space URL placeholder or final Space URL.

### 6. Future Extensions

- CLI support.
- Slash command adapters for agentic coding tools.
- More languages.
- More model/provider options.
- Blog publishing integrations.
- WordPress draft publishing.
- Featured image generation with Modal.

## Planned Architecture

The implementation should keep product logic reusable outside Gradio.

Recommended modules:

- `SessionContext`: normalized session data.
- `SecretRedactor`: masks token-like values before prompting.
- `PromptBuilder`: creates language-aware prompts.
- `ArticleGenerator`: model/provider boundary.
- `MarkdownValidator`: checks output structure.
- `EditorialQualityPass`: critiques and rewrites drafts for specificity and readability.
- `MarkdownExporter`: creates downloadable Markdown.
- `GradioApp`: UI and event wiring.

Future CLI and slash-command workflows should call the same core modules.

## Example Use Case

Input summary:

```text
We changed the project direction from CLI-first to Gradio-first for the Build Small Hackathon.
The app should turn vibe coding notes into Markdown field notes.
It should support Indonesian and English output.
It should redact likely secrets before generating.
```

Expected output:

```md
---
title: "Mengubah Sesi Vibe Coding Menjadi Catatan Lapangan"
date: "2026-06-06"
tags: ["agentic-ai", "gradio", "markdown"]
language: "id"
---

## Masalah

Sesi coding dengan AI sering menghasilkan keputusan teknis yang penting, tetapi konteksnya mudah hilang setelah percakapan selesai.
```

## Development Notes

This repository now contains the first Gradio MVP and reusable core generator modules. Continue improving the smallest useful Gradio MVP before adding CLI or slash-command support.

Run locally:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Run tests:

```bash
.venv/bin/python -m unittest discover -s tests
```

Optional hosted inference:

```bash
export HF_TOKEN="<your-huggingface-token>"
export VIBE2BLOG_MODEL="<small-instruct-model-under-32b>"
.venv/bin/python app.py
```

Without `HF_TOKEN` and `VIBE2BLOG_MODEL`, the app uses a deterministic template fallback so the demo and tests stay runnable.

Optional Modal transcript extraction:

```bash
export MODAL_VLLM_BASE_URL="https://<workspace>--vibe2blog-backend-serve.modal.run/v1"
export MODAL_VLLM_MODEL="llm"
export MODAL_VLLM_TIMEOUT="45"
.venv/bin/python app.py
```

The Modal endpoint should expose an OpenAI-compatible `/v1/chat/completions` route, such as the vLLM server pattern from Modal's official example.

Optional Modal editorial polishing:

```bash
export MODAL_VLLM_BASE_URL="https://<workspace>--vibe2blog-backend-serve.modal.run/v1"
export MODAL_VLLM_MODEL="llm"
export MODAL_POLISH_ENABLED="true"
export MODAL_POLISH_TIMEOUT="60"
.venv/bin/python app.py
```

When enabled, Vibe2Blog sends the generated Markdown draft to the Modal vLLM endpoint for a final editorial pass. The prompt instructs the model to preserve factual claims, YAML frontmatter, Markdown headings, file names, commands, verification results, and code blocks while improving flow, specificity, and readability. If Modal fails, the original draft is kept.

Modal may return an initial `303` redirect for web server calls. Vibe2Blog follows that redirect while preserving the original POST body.

When implementing:

- Keep the first screen as the working generator.
- Keep tests focused on observable behavior.
- Do not depend on exact model prose in tests.
- Keep model-specific code isolated.
- Keep generated articles as editable drafts.
- Use prompt, examples, and rewrite passes before considering fine-tuning.

## License

This project is licensed under the GNU General Public License v3.0.

See [`LICENSE`](LICENSE).
