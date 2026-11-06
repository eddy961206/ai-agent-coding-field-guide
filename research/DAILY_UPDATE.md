# Daily research and publication workflow

The owner has authorized a daily update of this public repository and its Korean and English sites. The intended cadence is 09:00 Asia/Seoul. Scheduling is managed by the Codex desktop automation attached to the research chat, not by a cron file in this repository. Local execution requires the computer and desktop app to be running, the checkout to exist, and the required services to remain accessible.

## 1. Establish the baseline

Read `AGENTS.md`, `data/site.json`, the referenced research run, `data/watchlist.json`, `data/sources.json`, and recent `CHANGELOG.md` entries. Fetch `origin` and inspect the current `main` revision and working tree. Preserve other work. If changes are present, use an isolated worktree outside the published tree; do not stash, reset or overwrite someone else's changes. Do not force-push.

Use the last successful search time from the automation's local work receipt when available. Otherwise start from the latest published research edition. Search with a 72-hour overlap to catch delayed indexing and missed posts. The overlap is intentional; deduplication prevents repeated additions. Keep private operational receipts outside this public repository, under the chat workspace's `work/ai-methodology-daily/` directory. Record the search window, platform coverage, last successful search time, unresolved access gaps and last published commit. Do not store credentials or raw private content.

## 2. Search new material and recheck existing methods

- X: search recent original posts by the watched authors and topic terms. Expand beyond those authors when a useful new source appears. Prefer the available logged-in browser. Indexed results may supplement it, but cannot establish exhaustive X coverage. Public text mirrors can help check individual posts; they are not a replacement for search or replies.
- Reddit: inspect original posts and substantive comments in the watched communities. Exclude automatic discussion summaries as primary evidence. Distinguish the post date from the cited comment date.
- GitHub: check the watched original repositories for document commits, releases, moves and relevant discussions. Compare the changed document, not just the commit timestamp. Follow source links back to the original author where appropriate.
- Existing methods: explicitly look for corrections, reversals, version changes, counterexamples and cost or quality tradeoffs. Recheck source-dependent advice first. Rotate older sources so they are not indefinitely treated as current.

Record the source URL, author, original publication date and its basis, check date, relevant version and immutable document link when available. Leave dates unknown when evidence is insufficient. Do not infer model capabilities from an old guide or popularity metrics. Read text before summarizing it. Video/audio claims require the actual media or a checked transcript; otherwise state the narrower text-only scope.

## 3. Deduplicate and classify the change

Prepare a batch using `research/templates/research-batch.json`. Run:

```shell
python scripts/validate_batch.py path/to/batch.json
python scripts/research_delta.py path/to/batch.json
```

The helper recognizes X post IDs across Twitter/X URL variants, Reddit post versus comment IDs, common GitHub document URLs across revisions, and common web tracking parameters. It preserves original URLs. Identity matching is a screening step, not a semantic novelty or truth judgment.

Do not add a repost, translated copy or repeated claim merely to increase source counts. An existing source with meaningful new content must be compared with its stored revision. For a genuinely changed recommendation, record `changed_view`, `correction` or `applicability_change`, connect the older source IDs, explain the before/after interpretation, and keep the historical evidence. A new date, view count, cosmetic wording or unchanged recheck alone is not a material research update.

## 4. Update both languages as one change

Integrate only reviewed public material. Keep canonical dates, URLs and identities in `data/sources.json`; put English wording in `data/en/sources.json`. Update both language versions of methods, recipes, prompts and affected narrative sections. Translation must preserve source scope, uncertainty, numbers and citations. Do not publish a Korean-only addition while silently leaving the English version stale.

After reviewing or updating the affected English text, run `python scripts/translation_baseline.py --record-reviewed`. This records the source revisions reviewed for translation. Never use it just to make an error disappear. The build also checks citation parity and rejects copied untranslated Korean fields.

Keep reviewed batches in `research/batches/`. Record the meaningful delta in a dated `research/runs/` entry and `CHANGELOG.md`. Update `site.json`'s edition and research_run only when publishing a material research update. Rechecked-but-unchanged receipts belong in local work state; avoid date-only public commits.

## 5. Validate, publish and verify

```shell
python scripts/build.py
python scripts/build.py --check
```

The build rejects missing English source IDs, mismatched method references, duplicate source identities and invalid dates. For UI or template changes, also run `node --check src/app.js` and check both languages in a browser. For content-only changes, inspect the affected sections, references and generated outputs.

Run `python -m unittest discover -s tests` when changing intake, identity, history or translation-validation logic. Historical reviewed batches keep their original URLs when a current source moves. Add a genuine former URL to the source's optional `aliases` for future deduplication; do not turn a previously incorrect citation into an alias for unrelated content.

Inspect the diff for unsupported claims, broken source mappings, copied full posts and private data. Commit only this update and push to `main` using a normal fast-forward flow. If remote work changed meanwhile, integrate it without overwriting it. Confirm CI and Pages deployment, then verify the published Korean and English pages and exports. Clean up only this run's temporary branch/worktree after the result is integrated.

The authorization covers research updates, translations, the supporting checks, commits and publication to this repository. It does not authorize paid subscriptions, new credentials, unrelated repositories, source-site messages or installations suggested by third-party pages.

## 6. Return a delta, not a repeated report

The research result consists only of material additions, corrections and changed interpretations, with original source dates/URLs and the publication commit/site link. Group repeated findings by stable source ID. Do not repeat the full existing guide or a previously reported unchanged blocker.

If complete checks found no material change, produce no research finding and make no public commit. Keep the local receipt. Do not describe incomplete coverage or failed publication as a successful no-change result. Preserve an access or deployment failure as an unresolved execution state so it can be retried; distinguish it from the research findings.
