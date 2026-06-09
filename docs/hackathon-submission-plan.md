# Hackathon Submission Plan: Vibe2Blog

## Submission Goal

Submit `Vibe2Blog` as a Gradio app for the Build Small Hackathon.

The app turns messy vibe coding session context into a clean Markdown blog draft. It helps developers preserve field notes from agentic coding: what problem they solved, what changed, why decisions were made, how the result was verified, and what they learned.

## Positioning

Working pitch:

> Vibe2Blog is a small-model Gradio app that turns agentic coding sessions into publishable Markdown field notes.

Primary track:

- Backyard AI
- OpenAI Codex Track

Why:

- The problem is specific and real for developers who code with AI agents.
- The app is directly usable by a person.
- The small-model constraint is honest because the task is structured summarization and drafting, not broad autonomous coding.
- The project is being built with Codex as the coding agent, and the repository can preserve Codex-assisted commits.

Potential bonus/award alignment:

- Best Agent: the workflow is designed around agentic coding sessions.
- Field Notes: the app generates the report/blog artifact from what was built and learned.
- Sharing is Caring: the build can share an agent trace on the Hub.
- Off-Brand: the Gradio UI can be customized beyond the default look.
- Tiny Titan: possible if the final model is meaningfully smaller than the 32B cap.

## OpenAI Codex Track Requirements

Based on the claimed Codex credits and track instructions:

- Build the Space with Codex as the coding agent.
- Push the code to a public GitHub repository.
- Ensure the repository contains Codex-attributed commits.
- Add the public GitHub repository link to the Hugging Face Space README.

Track plan:

- See `docs/openai-codex-track-plan.md`.

## MVP Scope

Build a Hugging Face Space with a Gradio app that supports:

- Session summary input.
- Optional transcript excerpt input.
- Optional git diff input.
- Optional verification notes input.
- Language selection: Indonesian (`id`) and English (`en`).
- Tone selection.
- Audience selection.
- Secret redaction before prompt construction.
- Markdown generation with YAML frontmatter.
- Editorial quality pass to reduce generic AI prose and improve specificity.
- Markdown preview/editor.
- Copy or download `.md`.
- Built-in sample data for judges.

## Non-MVP Scope

Do not spend hackathon time on:

- Full CLI implementation.
- Slash command adapters.
- Automatic private transcript extraction.
- Automatic blog publishing.
- Multi-provider support.
- Image generation.
- Social card generation.
- Complex project import from a git repository.
- Featured image generation with Modal.

## Demo Story

The demo should show:

1. A developer finishes a vibe coding session.
2. The session contains useful but messy notes, decisions, diff snippets, and test results.
3. The developer pastes the context into Vibe2Blog.
4. The developer chooses Indonesian output.
5. Vibe2Blog generates a polished Markdown article with frontmatter.
6. The developer downloads the `.md` file.

Recommended demo topic:

> Building Vibe2Blog itself: turning agentic coding sessions into Markdown field notes.

## Model Plan

The final model must fit the hackathon constraint of less than or equal to 32B parameters.

Selection criteria:

- Can follow structured prompts.
- Can draft coherent Markdown.
- Handles Indonesian reasonably well.
- Runs reliably in the Hugging Face Space environment or through an allowed small-model inference path.
- Has clear model card information for parameter count and licensing.

The implementation should keep the model behind an `ArticleGenerator` boundary so the model can be swapped if runtime constraints require it.

## Build Milestones

### Milestone 1: Core Generator

- Define `SessionContext`.
- Implement secret redaction.
- Implement language-aware prompt building.
- Implement mock article generation path for tests.
- Implement Markdown validation.
- Implement editorial quality rubric and optional rewrite pass.
- Implement Markdown export filename generation.

### Milestone 2: Gradio App

- Build Gradio UI.
- Wire inputs to generation function.
- Add sample data.
- Add Markdown output preview.
- Add download output.
- Add clear error states.

### Milestone 3: Model Integration

- Select small model.
- Integrate model through `ArticleGenerator`.
- Verify Indonesian and English output.
- Verify generation latency is acceptable for a demo.
- Document model name and parameter count.

### Milestone 4: Space and Submission

- Create Hugging Face Space.
- Deploy Gradio app.
- Run sample-data smoke test in the Space.
- Push code to a public GitHub repository with Codex-assisted commit history.
- Add the public GitHub repository link to the Space README.
- Build or render the short demo video with Remotion using `docs/remotion-demo-video-prd.md`.
- Write social post.
- Prepare submission with Space link, video, and post.

## Acceptance Criteria

- A judge can open the Space and generate an article from sample data without local setup.
- The app can generate Indonesian Markdown output.
- The app can generate English Markdown output.
- Generated output includes YAML frontmatter.
- Generated output includes the problem, implementation story, technical decisions, verification, lessons learned, and conclusion.
- Generated output is specific to the provided session context and does not read like a generic AI article.
- Likely secrets in input are masked before the prompt is sent to the model.
- The output can be downloaded as `.md`.
- The model used is documented and fits the 32B parameter cap.
- The submission includes a short demo video that shows the full flow from messy context to downloadable Markdown.
- The GitHub repository is public and linked from the Hugging Face Space README.
- The repository history includes Codex-attributed commits.

## Risks

- Model latency may be too high in the Space.
- The selected small model may produce weak Indonesian prose.
- Free Space resources may not comfortably run the chosen model.
- Prompt output may include too much raw diff unless constrained.
- Generated prose may sound generic if the prompt lacks concrete details or no rewrite pass is used.
- Users may paste secrets accidentally, so redaction needs to be visible and conservative.

## Mitigations

- Keep a mock/demo mode for UI development.
- Test multiple candidate small models early.
- Keep prompt context compact.
- Add an editorial quality pass with a rubric for specificity, narrative flow, concrete detail, and natural transitions.
- Add sample input that demonstrates the intended quality.
- Use clear UI copy that tells users not to paste sensitive data.
- Keep generated articles as drafts and label them as editable output.

## Post-MVP Extensions

- WordPress draft publishing.
- Featured image generation with Modal.
- CLI and slash-command adapters.
