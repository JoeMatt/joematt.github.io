# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Part of `personal-os`

This repo is a satellite of [`personal-os`](file:///Users/jmattiello/Workspace/personal-os) at `~/Workspace/personal-os`. A fresh agent session here should read `personal-os/AGENTS.md` first for shared conventions:

- **`VOICE.md`** — voice rules. **Mandatory** for blog posts. There's also a `VOICE.md` at the root of this repo that mirrors the central one — keep them in sync; the central copy in `personal-os` is the source of truth.
- **`decisions/`** — cross-repo MADR-numbered ADRs.
- **`journal/`** — daily orchestration log; touch entries when shipping a blog post.
- **`INBOX.md`** — things-to-act-on across all projects.
- **`wiki/projects-index.md`** — registry of every active repo.

Don't edit `personal-os/raw/` from a satellite — that's the central drop-zone, one-way.

## Project Overview

Hugo source for **joemattiello.dev** — Joe's personal blog and portfolio. Static site, deployed to GitHub Pages.

## Build commands

```bash
hugo server                      # local dev at http://localhost:1313/
hugo server --buildDrafts        # include draft posts
hugo --minify                    # production build (output to static-site/)
make                             # see Makefile for the full build pipeline
```

## Architecture

- **Hugo**: theme chain configured in `config.yaml`. Theme submodules live under `themes/`.
- **Build output**: `static-site/`. This is what GitHub Pages serves.
- **Content sources**: blog posts at `static-site/blog/<slug>/index.html` are authored **directly as HTML**, not Hugo Markdown — this is the authoritative location for editing existing posts (e.g. `static-site/blog/virtual-jaguar-v2-2-0/index.html`). Other content under `content/` is standard Hugo Markdown.
- **OG images**: 1200x630 cards live under `static-site/blog/<slug>/`; `og:image` and `twitter:image` both reference the same file.
- **Cloudflare**: `cloudflare-transform-rules.json` and `MIGRATION.md` document the Mozilla Observatory C → A migration path that's pending.

## Hard rules

- **Voice-lint every blog post before commit.** Joe's commit messages reference voice-lint stats (`5 em-dashes / 2786 words, stddev 11.3, 0 violations`) — that's the standard. Use the `voice-check` skill in `personal-os/.claude/skills/voice-check/`.
- **Verify facts before drafting.** Pull actual release data, PR numbers, line counts, and game names from the source repos. Don't invent.
- **Diagnostic before fix.** When writing about a bug fix in a post, the broken behavior gets a paragraph and the fix gets a sentence — see `personal-os/VOICE.md` Sample 2.
- **Never publish hashtag spam.** Tweet drafts in `content/<slug>/x.md` should have at most 1–2 highly relevant tags or none.

## Common edits

- Adding a new blog post: usually a new dir under `static-site/blog/<slug>/index.html` for the body and `<slug>/og.png` for the card. Update `static-site/blog/index.html` (the index page) to list it.
- Tweaking voice rules: edit `personal-os/VOICE.md` (canonical) and copy to this repo's `VOICE.md` to keep them aligned.
