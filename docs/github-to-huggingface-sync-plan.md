# GitHub to Hugging Face Space Sync Plan

## Objective

Use GitHub as the canonical source repository and Hugging Face Space as the deployment target for the Gradio app.

The desired workflow:

```text
push to GitHub main
-> GitHub Actions runs
-> repository contents sync to Hugging Face Space
-> Hugging Face Space rebuilds and restarts the Gradio app
```

## Recommended Repository Roles

- GitHub repository: source of truth for development, docs, tests, issues, PRs, and implementation history.
- Hugging Face Space repository: deployment target for the public Gradio demo.

## Operational Sync Decision

Use token-based Hugging Face CLI sync as the preferred manual deployment path.

Reason:

- SSH push depends on the right key being loaded into `ssh-agent`.
- Passphrase-protected SSH keys can fail across new terminal sessions.
- During implementation, token-based `hf upload` successfully synced the Space without requiring SSH passphrase prompts.
- GitHub remains the canonical code repository; the Space is a deployment target.

Preferred manual sync command:

```bash
hf upload build-small-hackathon/vibe2blog . . \
  --repo-type space \
  --exclude '.git' \
  --exclude '.git/*' \
  --exclude '.venv' \
  --exclude '.venv/*' \
  --exclude '__pycache__' \
  --exclude '__pycache__/*' \
  --exclude '*/__pycache__/*' \
  --exclude '.pytest_cache' \
  --exclude '.pytest_cache/*' \
  --exclude '.DS_Store' \
  --commit-message "chore: sync Vibe2Blog Space"
```

Use SSH only as a fallback/debug path. If SSH is used, first verify:

```bash
ssh -T git@hf.co
git push --dry-run hf main
```

If SSH returns an authentication error, use `hf upload` instead of spending time debugging `ssh-agent`.

## Prerequisites

1. A GitHub repository for this project.
2. A Hugging Face account.
3. A Hugging Face Space created with SDK `Gradio`.
4. A Hugging Face access token with write access to the target Space.
5. The target Hugging Face Space repo id, for example:

```text
<hf-username>/vibe2blog
```

or, for an organization:

```text
<hf-org>/vibe2blog
```

For hackathon submission, prefer the official hackathon Hugging Face organization as the Space owner when eligible/available. Use a personal Space only as a fallback or temporary deployment target.

## Expected App Files

Once implementation starts, the repo should include the standard Space runtime files:

```text
app.py
requirements.txt
README.md
src/
tests/
docs/
```

For a Gradio Space, Hugging Face uses the Space repository `README.md` metadata block to configure the Space. If the GitHub README is also synced to the Space, make sure it includes valid Space metadata once deployment begins.

Example Space metadata:

```yaml
---
title: Vibe2Blog
emoji: 📝
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: gpl-3.0
---
```

Note: update `sdk_version` to the actual Gradio version used by the project.

## GitHub Secret

Create this repository secret in GitHub:

```text
HF_TOKEN
```

The token should come from Hugging Face user settings and must have write permission for the target Space.

## Workflow File

Create this file:

```text
.github/workflows/sync-to-huggingface.yml
```

Planned workflow:

```yaml
name: Sync to Hugging Face Space

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Sync to Hugging Face Hub
        uses: huggingface/hub-sync@v0.1.0
        with:
          github_repo_id: ${{ github.repository }}
          huggingface_repo_id: <hf-username-or-org>/vibe2blog
          repo_type: space
          hf_token: ${{ secrets.HF_TOKEN }}
```

Replace:

```text
<hf-username-or-org>/vibe2blog
```

with the real Space repo id.

## Branch Strategy

Recommended:

- `main`: production branch that syncs to Hugging Face Space.
- feature branches: development branches that do not auto-deploy.

Optional future improvement:

- Add a separate staging Space for preview deployments.
- Sync `main` to production Space and `develop` to staging Space.

## Sync Timing

Recommended setup:

- Enable automatic sync on every push to `main`.
- Enable `workflow_dispatch` so deployment can be triggered manually from GitHub Actions.

This keeps normal deployment simple while still allowing manual retry when Hugging Face build behavior needs a nudge.

## Manual Sync Procedure

For day-to-day hackathon work:

1. Commit locally with a Codex co-author trailer.
2. Push to GitHub `origin/main`.
3. Sync to the Space using token-based `hf upload`.
4. Verify the Space rebuilds.

Commands:

```bash
git status --short
git push origin main
hf upload build-small-hackathon/vibe2blog . . \
  --repo-type space \
  --exclude '.git' \
  --exclude '.git/*' \
  --exclude '.venv' \
  --exclude '.venv/*' \
  --exclude '__pycache__' \
  --exclude '__pycache__/*' \
  --exclude '*/__pycache__/*' \
  --exclude '.pytest_cache' \
  --exclude '.pytest_cache/*' \
  --exclude '.DS_Store' \
  --commit-message "chore: sync Vibe2Blog Space"
```

If it is important for `hf/main` to share the exact same Git commit history as GitHub, push by Git HTTPS only after confirming credentials are available:

```bash
git push --force-with-lease https://huggingface.co/spaces/build-small-hackathon/vibe2blog main
```

This is optional for normal Space deployment. Content sync is enough for the Space to rebuild.

## Validation Steps

After adding the workflow:

1. Push a commit to `main`.
2. Open GitHub Actions.
3. Confirm `Sync to Hugging Face Space` starts.
4. Confirm the job finishes successfully.
5. Open the Hugging Face Space repository.
6. Confirm the latest commit or files appear in the Space.
7. Open the Space App tab.
8. Confirm the Gradio app rebuilds and launches.
9. Run the sample-data smoke test.
10. Confirm Markdown generation and download work.

## Failure Modes

### Missing or Invalid HF Token

Symptom:

- GitHub Action fails during sync.
- Manual `hf upload` fails with authentication or permission errors.

Fix:

- Regenerate `HF_TOKEN`.
- Ensure token has write access.
- Ensure the secret name is exactly `HF_TOKEN`.
- Run `hf auth whoami` to confirm the local CLI is authenticated.

### SSH Agent or Passphrase Problems

Symptom:

- `git push hf main` fails with an authentication error.
- `ssh-add` must be rerun in each session.
- `ssh -T git@hf.co` connects as anonymous or the push is rejected.

Fix:

- Prefer token-based `hf upload`.
- Only debug SSH if exact Git history on the Space remote is required.
- Ensure the SSH public key is registered in Hugging Face settings.
- Ensure `~/.ssh/config` has a host entry for `hf.co` pointing to the correct identity file.

### Wrong Space Repo ID

Symptom:

- Sync fails or pushes to the wrong target.

Fix:

- Verify the Hugging Face Space URL.
- Use the repo id in the form `<owner>/<space-name>`.

### Space Builds but App Does Not Start

Symptom:

- Sync succeeds, but the Space shows an app/runtime error.

Fix:

- Check Space logs.
- Verify `app.py` exists.
- Verify `requirements.txt` includes required dependencies.
- Verify README metadata has `sdk: gradio` and `app_file: app.py`.

### README Metadata Conflict

Symptom:

- GitHub README looks fine, but Space config is wrong or missing.

Fix:

- Add the Hugging Face metadata block to the top of `README.md` once deployment begins.
- Keep public project documentation below the metadata block.

## Acceptance Criteria

- GitHub is the canonical development repository.
- Pushing to `main` updates GitHub, and token-based sync updates the Hugging Face Space.
- The Space rebuilds after sync.
- The deployed app can run the sample Vibe2Blog flow.
- The workflow can also be triggered manually.

## Open Decisions

- Final Hugging Face Space repo id.
- Whether the Space must be created under the official hackathon organization or can start as a personal Space.
- Whether to use a personal account or hackathon organization Space.
- Final Gradio SDK version.
- Whether to add a staging Space.
- Whether the GitHub README should include Hugging Face Space metadata from day one or only after app implementation starts.
