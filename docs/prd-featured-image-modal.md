# PRD: Featured Image Generation with Modal

## Problem Statement

Vibe2Blog generates Markdown blog drafts from vibe coding sessions. For many publishing workflows, a blog post also needs a thumbnail or featured image. Creating that image manually adds friction, especially when the post is meant to be published quickly after a coding session.

The problem is to provide an optional way to generate relevant blog thumbnails or featured images from the article content without overloading the Gradio app or making image generation part of the hackathon MVP.

## Solution

Build a post-MVP extension that generates featured images through a Modal-hosted image generation service. Vibe2Blog will create an image prompt from the article title, excerpt, tags, language, and selected visual style. The Gradio app will call a Modal endpoint that runs a text-to-image model on GPU and returns one or more image candidates.

The user can preview, download, and later attach the image to a WordPress draft or other publishing workflow.

## Scope Positioning

This feature is not part of the core Build Small Hackathon MVP.

Hackathon MVP:

- Generate Markdown.
- Preview Markdown.
- Download `.md`.

Post-MVP extension:

- Generate a featured image prompt.
- Call Modal for image generation.
- Return image candidates.
- Let the user download a selected image.
- Optionally integrate with WordPress featured media later.

## User Stories

1. As a blogger, I want to generate a featured image from my article draft, so that my post is more publishable.
2. As a blogger, I want the image prompt to be derived from the article title and summary, so that the image fits the content.
3. As a blogger, I want to choose a visual style, so that the thumbnail matches my blog identity.
4. As a blogger, I want to generate multiple image candidates, so that I can choose the best one.
5. As a blogger, I want to download the selected image, so that I can use it in my publishing workflow.
6. As a blogger, I want image generation to be optional, so that I do not spend compute when I only need Markdown.
7. As a blogger, I want image generation to avoid text-heavy images, so that the result looks better as a thumbnail.
8. As a blogger, I want image generation to respect language and topic, so that Indonesian and English posts can have context-appropriate visuals.
9. As a maintainer, I want Modal integration isolated behind an image-generation boundary, so that the core app does not depend on Modal.
10. As a maintainer, I want the Gradio app to remain lightweight, so that text generation and image generation can scale independently.
11. As a maintainer, I want image generation to require an explicit user action, so that cost and latency stay controlled.
12. As a maintainer, I want generated images cached when possible, so that repeated requests do not waste compute.
13. As a maintainer, I want clear error handling for Modal failures, so that users understand when image generation is unavailable.
14. As a WordPress user, I want the selected image to be usable as featured media later, so that the publishing flow can become end-to-end.

## Implementation Decisions

- Featured image generation will be implemented as an optional extension, not as core article generation behavior.
- The integration will use Modal as a serverless GPU backend.
- The Gradio app will call a Modal endpoint or function through a small `FeaturedImageGenerator` boundary.
- Image generation should happen only when the user clicks `Generate featured image`.
- The extension will first generate an image prompt from the article metadata and content summary.
- The image prompt should avoid requesting large readable text inside the image, because text rendering in image models can be unreliable.
- The app will support visual style presets such as:
  - developer editorial
  - clean abstract
  - technical diagram-inspired
  - warm blog illustration
  - dark code workspace
- The output should return 1-4 candidate images.
- Candidate images should be downloadable as PNG or WebP.
- Generated images should include metadata such as prompt, seed, style, model name, and generation time.
- The Modal model and GPU type should be documented.
- Modal credentials and endpoint configuration should come from environment variables or deployment secrets.
- The public hackathon Space should not require Modal to run the core text generation flow.
- If Modal is not configured, the UI should hide or disable featured image generation.
- WordPress featured media integration is a follow-up after WordPress draft publishing works.

## Proposed Flow

```text
Generated article
-> extract title, excerpt, tags, language, audience
-> build image prompt
-> user selects visual style and image count
-> user clicks Generate featured image
-> Gradio calls Modal endpoint
-> Modal runs image generation model on GPU
-> Modal returns image bytes or URLs
-> Gradio displays candidates
-> user downloads selected image
```

## Proposed Data Shape

Input:

```json
{
  "title": "Mengubah Sesi Vibe Coding Menjadi Catatan Lapangan",
  "excerpt": "Catatan tentang mengubah sesi agentic coding menjadi artikel Markdown.",
  "tags": ["agentic-ai", "gradio", "markdown"],
  "language": "id",
  "style": "developer editorial",
  "count": 2
}
```

Output:

```json
{
  "images": [
    {
      "url": "https://...",
      "format": "png",
      "prompt": "...",
      "seed": 12345,
      "model": "selected-image-model",
      "width": 1024,
      "height": 576
    }
  ]
}
```

## UX Requirements

- Featured image generation should appear after the Markdown draft exists.
- The section should be visually secondary to the Markdown generation flow.
- The user must click an explicit action to generate images.
- The UI should show selected style, candidate count, and expected latency note.
- The UI should show clear loading state while Modal runs.
- The UI should show all candidate images in a gallery.
- The UI should provide a download action for each candidate.
- If Modal is not configured, show a disabled state or hide the section.

## Safety and Cost Requirements

- Do not run image generation automatically after every article generation.
- Limit maximum candidate count.
- Add timeout handling.
- Add basic rate limiting if the deployment becomes public.
- Cache repeated requests based on article title, image prompt, style, and seed.
- Avoid sending secrets or raw diffs to Modal. Send only the generated image prompt and safe article metadata.
- Avoid prompts that request logos, copyrighted characters, public figures, or sensitive imagery unless the user explicitly provides allowed context.

## Testing Decisions

- Unit test image prompt generation from article metadata.
- Unit test style preset mapping.
- Unit test that raw transcript and git diff are not sent to Modal.
- Unit test disabled state when Modal configuration is missing.
- Integration test Modal client behavior with mocked endpoint responses.
- Test failure handling for timeout, authentication error, and malformed image response.
- Test candidate download metadata.
- Test that image generation requires explicit user action.

## Out of Scope

- Making image generation part of the hackathon MVP acceptance criteria.
- Automatically generating images for every article.
- Uploading generated images to WordPress in the first image extension version.
- Training or fine-tuning an image model.
- Supporting arbitrary image editing.
- Guaranteeing perfect text rendering inside images.
- Building a full design editor.

## Further Notes

- Modal is a good fit because image generation can be isolated on serverless GPU while the Hugging Face Space remains focused on the Gradio UI.
- This feature becomes more valuable after WordPress draft publishing exists, because selected images can later be uploaded as WordPress featured media.
- The first implementation should optimize for a reliable, tasteful thumbnail rather than maximum image-model flexibility.
- Keep the hackathon submission focused: mention featured image generation as an extension, but do not block the core demo on it.
