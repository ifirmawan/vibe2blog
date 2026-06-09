# OpenAI Codex Track Plan

## Objective

Enter the OpenAI Codex Track for the Build Small Hackathon.

The track requirements provided by the organizer:

1. Build the Space with Codex as the coding agent.
2. Push the code to a public GitHub repository.
3. The repository must contain Codex-attributed commits.
4. Add the GitHub repository link to the Hugging Face Space README.

## Working Strategy

Use Codex as the primary coding agent for implementation, documentation updates, tests, and deployment workflow setup.

Use GitHub as the canonical source repository. Use Hugging Face Space as the deployment target.

The Space README must include a visible link back to the public GitHub repository.

## Required Artifacts

- Public GitHub repository.
- Hugging Face Space, preferably under the official hackathon organization when eligible.
- GitHub repository link in the Space README.
- Commit history that clearly shows Codex participation.
- Working Gradio app.
- Demo video.
- Social post.
- Social post proof/link in the Space README for the main hackathon requirements.

## Commit Guidance

The repository should include commits created during Codex-assisted work.

Recommended Codex config:

```toml
commit_attribution = "Codex <noreply@openai.com>"

[features]
codex_git_commit = true
```

Important: `commit_attribution` is a top-level key. It should not be placed inside `[features]`.

Incorrect config:

```toml
[features]
codex_git_commit = true
commit_attribution = "Codex <noreply@openai.com>"
```

That incorrect form can produce an error like:

```text
invalid configuration: invalid type: string "Codex <noreply@openai.com>", expected a boolean
in `features`
```

Recommended commit style:

```text
docs: define Vibe2Blog hackathon plan
feat: add core generation pipeline
feat: add Gradio app
test: cover Markdown validation
ci: sync GitHub repo to Hugging Face Space
```

When useful, commit bodies can mention Codex assistance:

```text
Implemented with Codex as the coding agent for the OpenAI Codex Track.
```

Do not fake work history. Keep commits tied to real implementation or documentation changes.

## README Requirements

The GitHub README should include:

- Project name and pitch.
- Space link once available.
- Hackathon context.
- Implementation status.
- Local run instructions once the app exists.
- Documentation links.

The Hugging Face Space README should include:

- Project name and pitch.
- GitHub repository link.
- Social post proof/link.
- Model name and parameter count.
- Basic usage instructions.
- Hackathon/Codex Track note.

## Suggested Space README Block

Use this block once the GitHub repository URL is known:

```md
## OpenAI Codex Track

This Space was built with Codex as the coding agent for the Build Small Hackathon OpenAI Codex Track.

Public GitHub repository: <github-repo-url>

Social post proof: <social-post-url>
```

Replace `<github-repo-url>` with the final public repo URL.

## Workflow Checklist

1. Initialize git locally.
2. Commit the current documentation baseline.
3. Create a public GitHub repository.
4. Push `main` to GitHub.
5. Continue implementation with Codex-assisted commits.
6. Build the Gradio app.
7. Create the Hugging Face Space under the official hackathon organization if available.
8. Add the GitHub repo link to the Space README.
9. Add social post proof/link to the Space README.
10. Set up GitHub-to-Hugging Face sync.
11. Verify the Space runs.
12. Record demo video.
13. Submit Space link and required materials.

## Acceptance Criteria

- The GitHub repository is public.
- The GitHub repository has a clear commit history for Codex-assisted work.
- The Space README links to the GitHub repository.
- The Space README links to social post proof.
- The Space runs the Gradio app.
- The final submission can be evaluated by Codex and human judges without private context.

## Open Decisions

- Final GitHub repository URL.
- Final Hugging Face Space URL.
- Whether the Space README will be the same root `README.md` or generated from a Space-specific README template.
- Whether to include a short "Built with Codex" note in the app UI footer.
