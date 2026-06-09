# PRD: WordPress Draft Publishing Extension

## Problem Statement

Vibe2Blog generates editable Markdown drafts from vibe coding sessions. For many users, the next step after generating a draft is publishing it to a blog platform. WordPress is a common target, but copying Markdown manually, converting it to HTML, setting title/tags/categories, and saving a draft takes extra effort.

The problem is to provide a safe, optional path from generated Vibe2Blog Markdown to a WordPress draft without making automatic publishing part of the hackathon MVP.

## Solution

Build a post-hackathon WordPress publishing extension that lets users send a reviewed Vibe2Blog article to WordPress as a draft. The extension converts Markdown to HTML, maps metadata to WordPress post fields, and creates a draft post through the WordPress REST API.

The extension should prioritize safety. It must not publish automatically by default, must not expose WordPress credentials in public logs or generated content, and should be designed primarily for private/self-hosted usage or trusted deployments.

## Scope Positioning

This feature is not part of the Build Small Hackathon MVP.

Hackathon MVP:

- Generate Markdown.
- Preview Markdown.
- Download `.md`.

Post-hackathon extension:

- Connect to WordPress.
- Convert Markdown to HTML.
- Create a WordPress draft.
- Return the draft edit/view URL.

## User Stories

1. As a blogger, I want to send a generated Markdown article to WordPress, so that I do not need to copy and paste content manually.
2. As a blogger, I want the WordPress post to be created as a draft, so that I can review it before publishing.
3. As a blogger, I want the generated title to become the WordPress post title, so that metadata carries over.
4. As a blogger, I want frontmatter tags to become WordPress tags, so that taxonomy setup is faster.
5. As a blogger, I want frontmatter categories to become WordPress categories, so that the draft lands in the right editorial area.
6. As a blogger, I want Markdown content converted to WordPress-friendly HTML, so that the article formatting is preserved.
7. As a blogger, I want code blocks to stay readable, so that technical posts remain useful.
8. As a blogger, I want to see the WordPress draft URL after posting, so that I can continue editing in WordPress.
9. As a blogger, I want to configure my WordPress site URL once, so that repeated posting is easier.
10. As a blogger, I want credentials to be stored outside the generated article, so that secrets do not leak into content.
11. As a maintainer, I want WordPress publishing isolated behind an integration boundary, so that the core generator does not depend on WordPress.
12. As a maintainer, I want the extension to be disabled by default, so that public deployments remain safe.
13. As a maintainer, I want clear errors from WordPress API failures, so that users can fix authentication or permission issues.
14. As a maintainer, I want tests with a mocked WordPress API, so that publishing behavior is reliable without hitting real sites.
15. As a public Space user, I want to avoid entering WordPress credentials into an untrusted public demo, so that my blog remains safe.

## Implementation Decisions

- WordPress publishing will be implemented as an optional extension, not as core generation behavior.
- The first supported action will be `create draft`, not `publish`.
- The integration will use the WordPress REST API.
- Authentication should use WordPress Application Passwords or another standard REST-compatible mechanism.
- Credentials must come from environment variables, encrypted local config, or trusted deployment secrets. They should not be stored in article Markdown.
- The public Hugging Face Space should not enable WordPress publishing unless the deployment is private or the credential flow is explicitly designed for safe per-user authentication.
- Markdown-to-HTML conversion will happen before sending content to WordPress.
- Frontmatter parsing will map supported fields into WordPress post fields.
- The integration boundary should expose a small interface such as `publishDraft(article, config)`.
- The core article generator should remain platform-agnostic.
- WordPress API errors should be normalized into user-friendly messages.
- The extension should return the created post id, edit URL if available, public preview/view URL if available, and post status.

## Proposed Data Mapping

Vibe2Blog article:

```yaml
title: "Mengubah Sesi Vibe Coding Menjadi Catatan Lapangan"
date: "2026-06-06"
tags: ["agentic-ai", "gradio", "markdown"]
categories: ["Engineering"]
language: "id"
excerpt: "Catatan tentang mengubah sesi agentic coding menjadi artikel Markdown."
```

WordPress draft:

- `title`: frontmatter `title`
- `content`: Markdown body converted to HTML
- `status`: `draft`
- `excerpt`: frontmatter `excerpt` if present
- `tags`: resolved or created from frontmatter `tags`
- `categories`: resolved or created from frontmatter `categories`
- `date`: optional; only set when user chooses to preserve date

## UX Requirements

For a private/trusted deployment:

- Add a `Post to WordPress Draft` action after article generation.
- Show a confirmation step before calling WordPress.
- Show the destination site URL.
- Show the post status that will be used: `draft`.
- Show success result with draft link.
- Show actionable error messages.

For the public hackathon Space:

- Keep WordPress publishing disabled.
- Mention WordPress publishing as a planned extension only.
- Do not ask users to enter WordPress credentials into the public app.

## Security Requirements

- Never include credentials in prompts sent to the model.
- Never include credentials in generated Markdown.
- Never log credentials.
- Redact credentials from exception messages where possible.
- Prefer deployment secrets or local environment variables over UI text fields.
- Use `draft` as the only initial status.
- Add clear warnings if a user enables the feature in a public deployment.

## Testing Decisions

- Unit test frontmatter parsing and WordPress field mapping.
- Unit test Markdown-to-HTML conversion for headings, links, lists, and code blocks.
- Unit test credential redaction in logs and error messages.
- Integration test `create draft` against a mocked WordPress REST API.
- Test authentication failure handling.
- Test taxonomy resolution for existing and missing tags/categories.
- Test that the default post status is always `draft`.
- Test that WordPress publishing is disabled when config is missing.

## Out of Scope

- Publishing directly with status `publish` in the first version.
- Editing existing WordPress posts.
- Uploading images/media to WordPress.
- Managing featured images.
- Supporting WordPress.com-specific OAuth flows.
- Supporting every CMS.
- Enabling this feature in the public hackathon Space by default.
- Building a full editorial workflow inside Vibe2Blog.

## Further Notes

- This feature is valuable because it completes the path from generated draft to real publishing workflow.
- It should be implemented after the Gradio hackathon MVP is stable.
- The safest first release is for local/private usage where the user controls the deployment and credentials.
- The extension should preserve Vibe2Blog's core principle: generated articles are drafts, and users remain the final editors.
