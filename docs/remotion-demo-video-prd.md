# PRD: Remotion Demo Video for Vibe2Blog

## Objective

Create a short demo video for the Build Small Hackathon submission that clearly shows how `Vibe2Blog` turns messy vibe coding context into a polished Markdown blog draft.

The video should be built with Remotion so the team can generate a repeatable, editable, code-driven demo asset.

## Target Output

- Format: landscape video.
- Resolution: 1920x1080.
- FPS: 30.
- Duration target: 60-75 seconds.
- Primary language: English voiceover with visible Indonesian output demo, or Indonesian voiceover if targeting a local audience.
- Delivery use: hackathon submission video and social post embed.

## Core Message

Agentic coding sessions are full of useful reasoning, but the notes are messy and easy to lose. `Vibe2Blog` uses a small model in a Gradio app to turn that context into Markdown field notes that developers can edit, publish, and share.

## Audience

- Hackathon judges.
- Developers who use coding agents.
- AI builders interested in small-model apps.

## Success Criteria

- Viewers understand the problem within the first 10 seconds.
- Viewers see the Gradio app by the first 20 seconds.
- Viewers see actual input context and generated Markdown output.
- The video explicitly mentions small-model and Gradio/Hugging Face Space fit.
- The video ends with a clear submission-ready value proposition.
- The video can be rendered reproducibly from Remotion code.

## Visual Direction

- Use a clean developer-tool aesthetic.
- Avoid a generic marketing hero.
- Show realistic UI states: messy notes, Gradio controls, generated Markdown, download result.
- Use large readable text for video compression.
- Prefer screen-like panels, terminal/editor surfaces, and Markdown previews.
- Keep motion purposeful: slide, fade, type-on, highlight, and progress states.

## Remotion Implementation Notes

- Use `Sequence` for scene timing.
- Use `useCurrentFrame()`, `useVideoConfig()`, `interpolate()`, and `Easing` for animation.
- Do not use CSS transitions or CSS animations because they do not render reliably in Remotion.
- Place any static screenshots, logos, or audio files in `public/`.
- Use `staticFile()` for local assets.
- Use `<Img>` for images and `<Video>` from `@remotion/media` for screen recordings if needed.
- Keep composition metadata in `src/Root.tsx`.
- Recommended composition id: `Vibe2BlogDemo`.

## Storyboard

### Scene 1: Hook, 0-8s

Visual:

- Fast montage of messy vibe coding artifacts: chat snippets, git diff fragments, test result lines, and TODO notes.
- Text overlay: "Your AI coding session is full of publishable insight."
- Secondary text: "But it usually disappears."

Voiceover:

> Every agentic coding session produces useful decisions, tradeoffs, and lessons. The problem is that most of it disappears when the session ends.

### Scene 2: Product Reveal, 8-16s

Visual:

- Reveal the `Vibe2Blog` name.
- Show a clean Gradio app frame.
- Text overlay: "Vibe2Blog turns coding sessions into Markdown field notes."

Voiceover:

> Vibe2Blog is a Gradio app that turns messy vibe coding context into editable Markdown field notes.

### Scene 3: Inputs, 16-29s

Visual:

- Show the app fields:
  - session summary
  - optional transcript excerpt
  - optional git diff
  - verification notes
  - language: id/en
  - tone
  - audience
- Highlight language set to Indonesian.

Voiceover:

> Paste a session summary, add optional transcript or diff snippets, choose the audience and tone, then pick the output language.

### Scene 4: Small Model Generation, 29-40s

Visual:

- Show "Redacting secrets" step.
- Show "Building prompt" step.
- Show "Generating with small model <=32B" step.
- Use subtle progress animation.

Voiceover:

> Before generation, the app masks likely secrets, builds a structured prompt, and uses a small model that fits the hackathon constraint.

### Scene 5: Markdown Result, 40-58s

Visual:

- Show generated Markdown with YAML frontmatter.
- Highlight sections:
  - Masalah
  - Proses Implementasi
  - Keputusan Teknis
  - Verifikasi
  - Pelajaran
- Show copy/download button.

Voiceover:

> The result is a blog draft with frontmatter, a clear story, selected technical decisions, verification notes, and lessons learned.

### Scene 6: Why It Matters, 58-68s

Visual:

- Side-by-side before/after:
  - left: messy context
  - right: publishable Markdown
- Text overlay: "From session trace to shareable knowledge."

Voiceover:

> Instead of losing the reasoning behind a build, developers can turn it into something they can edit, publish, and share.

### Scene 7: Closing, 68-75s

Visual:

- Show Hugging Face Space URL placeholder.
- Show tagline: "Vibe2Blog: Field notes for agentic coding."

Voiceover:

> Vibe2Blog: field notes for agentic coding, built small with Gradio.

## On-Screen Copy

- "Messy coding context"
- "Structured field notes"
- "Language: Indonesian"
- "Secret redaction"
- "Small model <=32B"
- "Markdown with frontmatter"
- "Copy or download .md"
- "Built with Gradio for Hugging Face Spaces"

## Sample Demo Input

Use this as the visible example in the video:

```text
We planned a tool that converts vibe coding sessions into blog articles.
We changed the product direction from CLI-first to Gradio-first for the Build Small Hackathon.
Important decisions:
- Gradio app is the hackathon MVP.
- CLI and slash commands are future extensions.
- Output supports Indonesian and English.
- The app redacts secrets before prompting the model.
- The generated result is Markdown with frontmatter.
Verification:
- PRD and AGENTS.md were updated.
- Hackathon submission plan was created.
```

## Sample Generated Markdown Excerpt

Use this as readable output in the video:

```md
---
title: "Mengubah Sesi Vibe Coding Menjadi Catatan Lapangan"
date: "2026-06-06"
tags: ["agentic-ai", "gradio", "markdown"]
language: "id"
---

## Masalah

Sesi coding dengan AI sering menghasilkan keputusan teknis yang penting, tetapi konteksnya mudah hilang setelah percakapan selesai.

## Proses Implementasi

Kami mengubah arah produk dari CLI-first menjadi Gradio-first agar cocok untuk submission Build Small Hackathon.

## Keputusan Teknis

- Gradio menjadi antarmuka utama.
- Markdown tetap menjadi output utama.
- Bahasa Indonesia dan Inggris didukung sejak awal.
```

## Remotion Build Prompt

Use this prompt for an implementation agent:

```text
Build a Remotion video project for the Vibe2Blog hackathon demo.

Create a 1920x1080, 30fps composition named Vibe2BlogDemo with a duration of 75 seconds. The video should follow docs/remotion-demo-video-prd.md exactly.

Use React components for scenes:
- HookScene
- ProductRevealScene
- InputWorkflowScene
- GenerationPipelineScene
- MarkdownResultScene
- BeforeAfterScene
- ClosingScene

Use Remotion Sequence for timing. Animate with useCurrentFrame(), useVideoConfig(), interpolate(), and Easing. Do not use CSS transitions or CSS animations.

Use a clean developer-tool visual style: dark editor panels, readable Markdown, Gradio-like controls, small-model badge, and subtle highlight animations.

Include readable on-screen text and the sample Indonesian Markdown excerpt from the PRD. Make the UI legible at 1920x1080 and avoid tiny text.

No external assets are required for the first version. If assets are added later, place them in public/ and reference them with staticFile().

Add a package script for preview and render. Include a README section explaining how to run Remotion Studio and render the video.
```

## Render Checks

- Open Remotion Studio and review the full timeline.
- Render still frames around 5s, 18s, 35s, 50s, and 70s to verify readability.
- Confirm no text overlaps at 1920x1080.
- Confirm no CSS transitions or CSS animations are used.
- Confirm the final frame includes the product name and Space URL placeholder.
