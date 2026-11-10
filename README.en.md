# AI Agent Coding Field Guide

[한국어](README.md) · [Read in English](https://eddy961206.github.io/ai-agent-coding-field-guide/en/) · [Korean site](https://eddy961206.github.io/ai-agent-coding-field-guide/)

A bilingual research guide to AI-assisted software development, built from original X posts, Reddit discussions, GitHub documents and first-party articles. Publication dates, document revisions and review dates are distinct. Opinions, self-reports, studies and editorial recommendations remain distinct too.

The current research edition is **2026-11-10 (Asia/Seoul)**. The first edition contained 78 sources, including 40 X posts, 16 practical methods and eight original prompt templates. It is a curated investigation, not an exhaustive survey or an independent reproduction of every claimed effect.

## Read or hand off

- Open `en/index.html` locally for the standalone English guide.
- Give another agent [exports/agent-brief.en.md](exports/agent-brief.en.md) and [exports/research.en.json](exports/research.en.json).
- Read [AGENTS.md](AGENTS.md) and the [daily workflow](research/DAILY_UPDATE.md) before updating the repository.

Canonical provenance is in `data/sources.json`. English source wording is an overlay in `data/en/sources.json`; it does not duplicate dates or URLs. Methods, recipes, prompts and chapter files have explicit English counterparts. The build rejects missing translation IDs or mismatched source references. It does not silently substitute Korean text.

## Build and validate

Python 3.10+ and the standard library are sufficient. No API key, external CDN or package installation is required to build or read the guide.

```shell
python scripts/build.py
python scripts/build.py --check
python scripts/validate_batch.py path/to/research-batch.json
python scripts/research_delta.py path/to/research-batch.json
```

Edit `data/` and `src/`, then regenerate. Do not edit the generated HTML or exports directly. `research_delta.py` flags duplicate source identities; it does not decide whether a claim is new or true. Preserve original URLs and keep changed views connected to their earlier evidence.

After reviewing the English changes, run `python scripts/translation_baseline.py --record-reviewed`. The build detects Korean changes that have not received a corresponding English review. This records a human/agent review decision; it is not an automatic guarantee of translation quality. Do not refresh the baseline without doing that review.

## Daily updates

The authorized workflow runs at 09:00 Asia/Seoul through the Codex desktop automation for the research chat. Local execution requires the computer and app to be running. Each run searches X, Reddit and GitHub, checks changes to existing guidance, deduplicates sources, updates both languages, validates and publishes material changes to `main` and GitHub Pages. Runs with no material research change do not create date-only public commits.

The schedule is managed in the desktop app, not by a repository cron job. Research receipts and credentials do not belong in this public repository. Archived reviewed batches preserve their original language; the current narrative and recommendations are exported in both languages.

## Attribution

Source content remains the property of its original authors. This repository links to sources and provides short editorial summaries rather than republishing full posts or media. A separate license for this repository's original code and writing has not been assigned.
