# PRD: Vibe2Blog Gradio App

## Problem Statement

Sesi "vibe coding" dengan agentic AI sering menghasilkan banyak pengetahuan bernilai: alasan teknis, eksplorasi bug, tradeoff, keputusan arsitektur, potongan kode penting, hasil test, dan pelajaran dari proses implementasi. Namun setelah sesi selesai, konteks tersebut biasanya tersebar di percakapan, diff kode, catatan sementara, dan memori developer.

Akibatnya, developer perlu menulis ulang narasi dari awal jika ingin menjadikannya artikel blog. Banyak insight yang sebenarnya layak dibagikan akhirnya hilang.

Untuk kebutuhan Build Small Hackathon, solusi harus dikemas sebagai aplikasi Gradio yang mudah dicoba langsung di Hugging Face Space, memakai model kecil sesuai constraint hackathon, dan menghasilkan demo yang jelas: dari sesi coding berantakan menjadi draft artikel Markdown yang rapi.

## Solution

Bangun aplikasi Gradio bernama sementara `Vibe2Blog` yang mengubah ringkasan/transkrip sesi vibe coding menjadi artikel Markdown siap edit. Pengguna dapat memasukkan session summary, optional transcript, optional git diff, topic, target audience, tone, dan bahasa output. Aplikasi melakukan redaksi sederhana terhadap secret-like values, membangun prompt terstruktur, memanggil model kecil, lalu menampilkan draft Markdown dengan frontmatter, preview, dan tombol download.

Untuk meningkatkan kualitas tulisan, aplikasi akan memiliki editorial quality pass. Tahap ini mengevaluasi apakah draft terasa spesifik, natural, tidak generik, dan tetap setia pada konteks coding yang diberikan. Tujuannya adalah menghasilkan tulisan yang enak dibaca manusia, bukan untuk mengelabui AI detector.

Produk utama untuk hackathon adalah Gradio app yang di-host sebagai Hugging Face Space. CLI dan slash command tetap dipertahankan sebagai extension path, bukan milestone pertama. Dengan demikian submission selaras dengan requirement hackathon sekaligus tetap menjaga visi jangka panjang: satu generator portable yang bisa dipakai oleh Codex, Claude Code, Cursor, terminal, atau integrasi agentic lainnya.

## Hackathon Alignment

- Target event: Build Small Hackathon by Hugging Face and Gradio.
- Primary track: Backyard AI, because this solves a specific real developer problem.
- Secondary award fit: Best Agent, Field Notes, Sharing is Caring, Off-Brand, and possibly Tiny Titan if a very small model is used.
- Delivery format: Gradio app hosted as a Hugging Face Space.
- Model constraint: total model parameters must be less than or equal to 32B.
- Submission package: Space link, short demo video, and social post.
- Assumption: the builder is already registered or has access to submit under the hackathon organization.

## User Stories

1. As a developer, I want to paste a vibe coding session summary or raw agent transcript, so that I can turn the session into a blog draft.
2. As a developer, I want to paste an optional transcript excerpt, so that the article can preserve important conversation details.
3. As a developer, I want to paste an optional git diff, so that the article can describe concrete code changes.
4. As a developer, I want to provide a topic or working title, so that the article has a clear editorial direction.
5. As a developer, I want the app to infer a title when I do not provide one, so that quick usage stays frictionless.
6. As a developer, I want to choose Indonesian or English output, so that I can write for different audiences.
7. As a developer, I want to choose a tone, so that the article can be tutorial-like, reflective, concise, or narrative.
8. As a developer, I want to choose a target audience, so that the article can be shaped for beginners, peers, maintainers, or product stakeholders.
9. As a developer, I want the generated article to include frontmatter, so that it can be used by static blog engines.
10. As a developer, I want the article to include the original problem, so that readers understand why the work mattered.
11. As a developer, I want the article to explain the implementation journey, so that it feels like an authentic engineering story rather than a changelog.
12. As a developer, I want the article to capture technical decisions, so that tradeoffs and reasoning are preserved.
13. As a developer, I want the article to include selected code snippets, so that readers can understand the technical details.
14. As a developer, I want the app to avoid dumping huge diffs, so that the blog remains readable.
15. As a developer, I want the app to include verification notes when provided, so that the article can describe how the work was tested.
16. As a developer, I want likely secrets to be redacted before generation, so that I can use the app with less risk.
17. As a developer, I want a Markdown preview, so that I can inspect the result immediately.
18. As a developer, I want a copy button, so that I can move the article into my editor quickly.
19. As a developer, I want a download button for `.md`, so that I can save the generated draft.
20. As a developer, I want generated filenames to be slugified from the title and date, so that drafts are organized.
21. As a hackathon judge, I want the app to be usable without local setup, so that I can evaluate it quickly from the Space.
22. As a hackathon judge, I want the UI to make the workflow obvious, so that the demo succeeds even with little explanation.
23. As a hackathon judge, I want the app to show why small models are sufficient, so that the submission fits the event theme.
24. As a maintainer, I want prompt templates separated from application code, so that editorial behavior can evolve safely.
25. As a maintainer, I want language-specific prompt fragments, so that adding a new language does not require rewriting the pipeline.
26. As a maintainer, I want structured intermediate context, so that the same generation core can later power a CLI or slash command.
27. As a maintainer, I want provider/model boundaries isolated, so that model changes do not rewrite the app.
28. As a maintainer, I want Markdown validation, so that broken frontmatter or empty sections are caught early.
29. As a maintainer, I want fixtures for sample vibe coding sessions, so that output behavior can be regression-tested.
30. As a future CLI user, I want to run `npm run blog:from-vibe -- --language="id"`, so that the same generator can be used outside Gradio later.
31. As a developer, I want the generated article to sound natural and specific, so that it feels like a real engineering write-up rather than generic AI prose.
32. As a developer, I want an editorial quality pass, so that the app can improve weak drafts before I download them.
33. As a maintainer, I want a quality rubric for generated writing, so that article quality can be evaluated consistently.

## Implementation Decisions

- The hackathon MVP will be a Gradio app, not a CLI-first tool.
- The app will be designed for Hugging Face Spaces from the start.
- The working product name will be `Vibe2Blog`.
- The primary user flow will be: paste context, configure output, generate Markdown, preview, copy, download.
- The first UI should be a single-page Gradio app with clear input and output panels.
- The app will accept session summary as the most important input.
- Transcript and git diff inputs will be optional, because users may not want to share full raw context.
- The app will include a built-in sample input so judges can try it immediately.
- The app will support `id` and `en` as first-class initial output languages.
- The language option will control article prose, section headings, generated title, generated description, and language-related frontmatter.
- The app will expose tone and audience controls as simple dropdowns.
- The app will produce Markdown with YAML frontmatter by default.
- The default generated structure will include title, date, tags, introduction, problem context, implementation story, key technical decisions, verification, lessons learned, and conclusion.
- The model used for the hackathon must fit the Build Small constraint of less than or equal to 32B parameters.
- The implementation should prefer a Hugging Face-hosted or local small model path that can run reliably in a Space.
- The model integration should be replaceable through a small `ArticleGenerator` boundary.
- The app should not require cloud APIs for the core demo if an appropriate small model can run in the Space.
- If hosted inference is used, the README and app should clearly state the model and parameter count.
- The core pipeline will use four major stages: normalize context, redact sensitive values, build prompt, generate article.
- A `SessionContext` module will represent normalized input. It will include topic, session summary, optional transcript, optional diff, verification notes, language, tone, and audience.
- A `SecretRedactor` module will scan collected context for common secret patterns before prompt construction.
- A transcript extraction layer will compact raw Claude Code/Codex-style logs into problem, findings, changes, verification, files, and outcome before article generation.
- The extraction layer should use deterministic local parsing as the safe fallback and may use a Modal-hosted OpenAI-compatible vLLM endpoint when `MODAL_VLLM_BASE_URL` is configured.
- A `PromptBuilder` module will combine normalized context with language-specific prompt fragments.
- An `ArticleGenerator` module will call the configured small model and return Markdown content.
- A `MarkdownValidator` module will check that generated content has valid frontmatter, a non-empty title, useful body sections, and no obvious placeholder text.
- An `EditorialQualityPass` module will evaluate and optionally rewrite the draft for specificity, narrative flow, concrete technical detail, natural transitions, and reduced generic AI phrasing.
- A `MarkdownExporter` module will produce downloadable Markdown bytes and a deterministic filename.
- The MVP will use prompting, few-shot examples, style guidance, and rewrite passes for humanized writing quality.
- Fine-tuning is not required for the hackathon MVP.
- Fine-tuning may be considered later if the project accumulates enough high-quality example articles and needs a consistent personal/editorial voice.
- CLI and slash-command support are future extensions. They should reuse the same core modules after the Gradio MVP works.
- Direct transcript scraping from proprietary agent tools is out of scope. Users should paste or summarize context manually for the MVP.
- Automatic publishing to a blog platform is out of scope. The app should create editable Markdown drafts.

## Gradio UX Requirements

- The first screen should be the usable generator, not a marketing landing page.
- The UI should include a sample-data button or prefilled example for fast judging.
- Required input: session summary.
- Optional inputs: transcript excerpt, git diff, verification notes.
- Controls: language, tone, audience, include code snippets, include frontmatter.
- Optional control: editorial quality pass enabled by default.
- Primary action: generate article.
- Outputs: Markdown editor/preview, detected title, word count or section count, download `.md`.
- Error states should be plain and actionable, especially for missing required input or model failure.
- The app should feel polished beyond default Gradio where feasible, but functionality is more important than visual novelty.

## Testing Decisions

- Tests should verify external behavior rather than internal implementation details.
- `SessionContext` normalization should be tested with minimal input, full input, missing optional fields, Indonesian output, and English output.
- `SecretRedactor` should be tested with common API key and token-like patterns.
- `PromptBuilder` should be tested to ensure Indonesian generation uses Indonesian section labels and English generation uses English section labels.
- `MarkdownValidator` should be tested with valid Markdown, missing frontmatter, missing title, empty body, and placeholder-heavy content.
- `EditorialQualityPass` should be tested with generic draft fixtures to ensure it asks for more specificity, stronger narrative flow, and fewer generic AI phrases.
- `MarkdownExporter` should be tested for slug generation, date prefixing, and `.md` content generation.
- The Gradio generation function should have integration tests using a mock model provider.
- LLM/model calls should be mocked in automated tests. Real model generation should be covered by manual smoke tests in the Space.
- Generated content tests should check structure and constraints, not exact prose.
- Quality tests should use a rubric-based approach rather than exact wording.
- A hackathon smoke test should verify that a judge can open the Space, use sample data, generate an article, and download Markdown.

## Out of Scope

- Automatically scraping full private transcripts from Codex, Claude Code, Cursor, or other agentic coding tools.
- Automatically publishing to a CMS, newsletter, or static site repository.
- Building the CLI before the Gradio hackathon MVP.
- Supporting every LLM provider in the first version.
- Creating a full blog platform.
- Guaranteeing that generated articles need no human editing.
- Reconstructing context from long-running sessions when no summary, diff, or notes are available.
- Handling legal, compliance, or enterprise data governance workflows beyond basic redaction and exclude patterns.
- Generating images, diagrams, or social preview cards for the first hackathon MVP.
- Training or fine-tuning a model for voice/style in the first hackathon MVP.

## Further Notes

- The submission should be framed as "field notes for agentic coding": preserving what happened, why it mattered, what changed, and what was learned.
- The demo should show a messy vibe coding summary becoming a clean Indonesian Markdown article.
- The app should include a clear example that matches this project itself: building Vibe2Blog from a PRD and agent session.
- A strong submission story is that the tool can produce the Field Notes artifact for its own hackathon build.
- After the hackathon MVP, the same core generator can be exposed through CLI and slash commands.
