# AGENTS.md

## Project Purpose

Build `Vibe2Blog`, a Gradio app that turns vibe coding session context into editable Markdown blog drafts for the Build Small Hackathon.

The core product should help developers preserve useful engineering reasoning from agentic coding sessions: the original problem, exploration path, implementation decisions, verification, and lessons learned.

## Important Docs

- PRD: `docs/prd-blog-from-vibe-coding.md`
- Hackathon plan: `docs/hackathon-submission-plan.md`
- OpenAI Codex Track plan: `docs/openai-codex-track-plan.md`
- Demo video PRD: `docs/remotion-demo-video-prd.md`
- GitHub to Hugging Face sync plan: `docs/github-to-huggingface-sync-plan.md`
- WordPress publishing extension PRD: `docs/prd-wordpress-publishing.md`
- Featured image generation PRD: `docs/prd-featured-image-modal.md`

Read the PRD before implementing product behavior or changing scope.

## Current Product Direction

The hackathon submission is Gradio-first.

Build the Hugging Face Space experience before CLI or slash-command workflows. The CLI idea remains valuable, but it is a follow-up surface that should reuse the same core modules after the Gradio MVP works.

Use GitHub as the canonical source repository and Hugging Face Space as the deployment target. Follow `docs/github-to-huggingface-sync-plan.md` when setting up deployment automation.

For the OpenAI Codex Track, keep the public GitHub repository and Space README aligned with `docs/openai-codex-track-plan.md`.

## Core Principles

- Build a usable Gradio app as the primary product.
- Keep the first screen focused on the generator workflow, not a landing page.
- Host the app as a Hugging Face Space for hackathon submission.
- Preserve clear Codex-assisted work history in the public GitHub repository.
- Add the public GitHub repository link to the Hugging Face Space README.
- Use a small model that fits the hackathon constraint of less than or equal to 32B parameters.
- Produce Markdown drafts, not automatic publication, in the first version.
- Support i18n through explicit UI language options for Indonesian (`id`) and English (`en`).
- Never depend on direct scraping of private agent transcripts in v1.
- Ask the user to paste or summarize session context instead.
- Redact likely secrets before sending context to a model.
- Prefer concise diff excerpts over full raw diffs.
- Keep provider/model-specific code behind a small interface.
- Improve prose quality through an editorial quality pass, not by trying to bypass AI detectors.
- Treat fine-tuning as a future option only after prompt, examples, and rewrite passes are insufficient.

## Expected Architecture

The implementation should favor deep, testable modules with small public interfaces:

- `SessionContext`: normalized context shared across the pipeline.
- `SecretRedactor`: masking for token-like or secret-like values.
- `PromptBuilder`: prompt assembly from context and language-specific fragments.
- `ArticleGenerator`: model/provider boundary.
- `MarkdownValidator`: structural checks for generated Markdown.
- `EditorialQualityPass`: rubric-based critique and optional rewrite for natural, specific writing.
- `MarkdownExporter`: deterministic filename and downloadable Markdown output.
- `GradioApp`: UI composition and event wiring.

Do not put product logic inside Gradio callbacks if it can live in a reusable core module. Future CLI and slash-command workflows should call the same core generator.

## Gradio Expectations

The app should be immediately usable by judges.

Required input:

- Session summary

Optional inputs:

- Transcript excerpt
- Git diff
- Verification notes

Controls:

- Language: `id` or `en`
- Tone
- Audience
- Include code snippets
- Include frontmatter

Outputs:

- Markdown article preview/editor
- Detected or generated title
- Basic article metadata such as word count or section count
- Downloadable `.md` file

Include sample data so a judge can generate an article without preparing their own transcript.

## Future CLI Expectations

After the Gradio MVP works, the same core generator may be exposed through CLI.

The npm invocation should eventually support argument forwarding:

```bash
npm run blog:from-vibe -- --language="id"
```

Configuration precedence for the future CLI should be:

1. CLI flags
2. Config file
3. Project defaults

## Testing Guidance

Prefer tests around observable behavior:

- Gradio generation function with sample input.
- Language selection and language fallback.
- Context normalization.
- Secret redaction before prompt construction.
- Prompt construction for Indonesian and English output.
- Markdown validation.
- Editorial quality pass behavior using generic draft fixtures.
- Markdown export and filename generation.
- End-to-end generation flow with a mock model provider.

Do not make tests depend on exact model prose. Check structure, metadata, and important constraints instead.

For writing quality, prefer rubric checks such as specificity, concrete technical detail, narrative flow, natural transitions, and absence of generic AI phrasing.

## Out of Scope for Hackathon MVP

- Direct private transcript extraction from Codex, Claude Code, Cursor, or similar tools.
- Automatic publishing to a CMS or static site.
- Building the CLI before the Gradio app.
- GUI frameworks other than Gradio.
- Multi-provider support before the first small-model path works well.
- Image, diagram, or social preview generation.
- WordPress publishing in the public hackathon Space.
- Featured image generation with Modal before the core Gradio app works.
- Fine-tuning for writing style before the Gradio MVP works.

## Demo Video Guidance

Use Remotion for the hackathon demo video. Follow `docs/remotion-demo-video-prd.md`.

When implementing Remotion scenes:

- Use `Sequence` for timing.
- Use `useCurrentFrame()`, `useVideoConfig()`, `interpolate()`, and `Easing` for animation.
- Do not use CSS transitions or CSS animations.
- Keep text readable at 1920x1080.
- Render still frames at key timestamps to verify layout.

## Writing Style for This Repo

- Keep docs concise and implementation-oriented.
- Use English for code, identifiers, and durable technical contracts.
- Indonesian is welcome in product examples and user-facing article output.
- Document decisions when they affect hackathon fit, portability, privacy, i18n, or model boundaries.
