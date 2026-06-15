# Changelog

## v2026.06 - June 2026

Auto-synced from live system on 2026-06-01.

### Changes

- Updated profiles/sinabarimd_com.yaml
- Updated profiles/sinabari_net.yaml
- Updated profiles/drsinabari_com.yaml
- Updated profiles/sinabariplasticsurgery_com.yaml
- Synced deploy/deploy_service.py from live
- Synced services/extract_server.py from live

### Stats
- 4 modified file(s)

---

<!-- Claude Code appends here during sessions, grouped by week. -->

## Week of 2026-06-13

### Added
- **Narrative-led editorial voice for drsinabari.com** (Jun 13) -- Content Generator now writes long-form essays in the Malcolm Gladwell tradition for `site_id === 'drsinabari'`: open inside a specific scene, withhold the thesis until the reader is invested, build the spine on a counterintuitive reframe, coin one memorable named concept per essay (2-4 words) that recurs, and stack 2-4 cases that converge on the same principle. Rigor guardrails (named studies with quantitative figures, acknowledged counter-evidence, first-person clinical detail) override narrative momentum. Implemented as an `editorial_voice: true` flag in `Build Runtime Config`'s SITE_MAP; `Inject Content Prompt` reads `runtime.editorial_voice` to swap behavior. The AEO answer-block (`<div class="article-summary">`) is suppressed for this site so essays can withhold their thesis; extraction value moves to the coined concept and the end-of-essay FAQ. Other three sites unchanged. Verified end-to-end: first draft in the new voice opened "Last Tuesday, I was halfway through a routine follow-up...", coined "attention tax" (6 recurrences), cited JAMA Network Open with quantitative figure, FAQ at the end with branded Dr. Bari question; control sinabari_net draft still emits the AEO block.

### Changed
- **Pre-push secret scan hardened** (Jun 13) -- `.githooks/pre-push` now also matches OpenAI-style keys (`sk-...`), HuggingFace tokens (`hf_...`), AWS Access Key IDs (`AKIA...`), Google API keys (`AIza...`), generic JWTs (`eyJ...`), and explicit `X-Voice-Key` headers. Added a generalized high-entropy base64-ish blob scanner (36+ char `[A-Za-z0-9_]` runs) with a `# SAFE-B64` allowlist marker for known-safe content hashes / Stitch image IDs. URL/CDN/SRI/data-URI exclusions prevent false positives on legitimate image and font references.
- **measure.py SSL hardening** (Jun 13) -- Removed `ctx.check_hostname = False` / `verify_mode = CERT_NONE` from the BrightData / GSC measurement script. Cert verification now enforced.
- **sync_pending_actions label updates** (Jun 13) -- Reconciler now detects when a tracked Daily Todo's label text has drifted (e.g. "8 syndication tasks pending" → "5 syndication tasks pending" against the same `todo_id`) and updates the line in place rather than leaving stale wording. Surfaces a `label_updates` count in dry-run and live output.
- **backup.sh metrics endpoint name** (Jun 13) -- State backup loop now hits `/webhook/metrics` (the live Measurement Agent endpoint) instead of the deprecated `/webhook/serp-results` path.
- **model-grade-playbook antithetical-pivot guidance** (Jun 13) -- "Remove AI structural tells" section now explicitly names the `"That is not X. It is Y." / "This isn't X. It's Y."` antithetical pivot pattern as a major AI tell to strip during rewrites.

> Note: a portfolio-wide publishing cadence slowdown (sinabari.net biweekly, sinabariplasticsurgery biweekly, drsinabari monthly, sinabarimd unchanged) was prototyped and reverted in the same session after reviewing internal SERP and SEO-brief data. The live cron / min-interval values are unchanged from the prior baseline: sinabarimd 7d (Mon), sinabari_net 3d (Tue+Fri), sinabariplasticsurgery 7d (Wed), drsinabari 14d (Thu).

> Note: `workflows/portfolio-orchestrator.json` and `workflows/content-generator.json` in this tree are NOT auto-synced with the live n8n workflows (operator regenerates from sanitized backups per `PUBLISH_MANIFEST.md`). The live drsinabari editorial-voice changes in Content Generator are not reflected in the staged export yet; refresh on a separate operator-controlled push.

## Week of 2026-05-23

### Fixed
- **Orchestrator cron time gate broken (locale format change)** (May 23) -- Node.js `toLocaleString` with `weekday:'short'` produces `"Fri 10:00"` (no comma) in current n8n container, but code split on `", "`. All cron publish windows silently failed for ~2 weeks (May 9-23), causing sinabari.net and sinabariplasticsurgery to miss multiple publish cycles. Fixed with index-based parsing in 3 workflows (Orchestrator, Content Research Agent, RT Drug Test Check). Live-tested with 1-minute cron fire.
- **MG Auto Trigger content type** (May 23) -- Model grade auto-trigger after publish used `rawContentType: "JSON"` instead of `"application/json"`, causing n8n webhook to reject the body. Model grades never fired automatically after publish. Fixed.
- **Article wipeout on deploy** (May 23) -- Deploy service does full file sync; Publisher's article_register capped at 3, so older articles were deleted on every publish. Added `article_archive` (uncapped) to Publisher staticData. Both Publisher and Site Refresh now preserve all existing articles during deploy. Recovered 5 wiped articles from backups and restored to production.
- **Ghost QA entries** (May 23) -- Removed stale QA entries for articles that no longer exist (404), cleaning 6 phantom records from the dashboard.

### Added
- **Article archive system** (May 23) -- Publisher maintains `article_archive` per site (all articles ever published, no cap) alongside the 3-article `article_register` (homepage featured only). Articles index page renders from full archive. Deploy payloads include all archive articles. Site Refresh now fetches and preserves existing articles before deploying.
- **Site-aware model grade rubric** (May 23) -- 6-dimension rubric with per-site context injection. New `site_mandate_fit` dimension scores whether an article serves its domain's purpose. Per-site `INFORMATION_GAIN BENCHMARK`: editorial sites judged by originality of synthesis (not page-1-of-Google competitiveness). Soft gate: `site_mandate_fit < 2` caps grade at C. Portfolio impact: 16/18 GREEN (was 7/18), 3 A-grades, average 83% (was 72%).
- **QA dashboard sort dropdown** (May 23) -- Article Health section has sort-by dropdown: Newest first, Title A-Z, Model score (lowest first). Articles flattened across all sites with site badge on each card.
- **Playbook integration into pipeline** (May 23) -- Content Research Agent now requires `information_gain_prediction`, `clinical_vignette_seeds`, `self_correction_opportunity`, and `opening_hook` fields. Content Generator prompt includes full PLAYBOOK REQUIREMENTS section: mandatory scene opening, callback closing, self-correction arc, quoted dialogue, "what I would NOT do" judgment, 3-5 named citations with quantitative data.

### Changed
- **18 articles rewritten across 4 sites** (May 23) -- Systematic rewrite campaign using playbook tactics + web research. 8 D/F-grade articles rewritten to B/A (avg +35 pts). 9 additional articles given Pass 2 rewrites to push past 75% GREEN threshold. New experimental tactics validated: temporal specificity, self-correction narrative, embedded disagreement, contrarian framing for information_gain.
- **Model grade playbook updated** (May 23) -- information_gain section updated from "open question" to "partially answered" with confirmed findings. Site-aware rubric results documented. Pipeline integration section added.
- **Model grade rubric file** (May 23) -- Full rubric saved to `model-grade-rubric.md` for reference.

## Week of 2026-05-19

### Added
- **AI content exposure check (Layer 1)** (May 21) -- deterministic article-level check in SEO QA Agent scanning for banned AI phrases, em-dashes, missing first-person voice, weak specificity signals, insufficient outbound links, and structural tells. Scores GREEN/AMBER/RED per article. Runs automatically after every publish and on demand.
- **Model-based editorial grade (Layer 2)** (May 21) -- 3-pass LLM-evaluated content quality check using OpenClaw. Grades articles 1-5 on five dimensions: first_hand_expertise, information_gain, specificity_evidence, depth_substance, voice_authenticity. Aggregates with confidence scoring. Advisory only, never gates deploy. Dedicated webhook: POST /webhook/qa-model-grade.
- **QA dashboard dual-grade display** (May 21) -- Article Health cards now show both Rules-Based Grade and Model-Based Grade (with ADVISORY label). Expandable per-dimension scores with bar chart, confidence flag, and merged fix list. "Model Grade" button for on-demand runs.
- **Content quality rewrite playbook** (May 21) -- systematic rewriting of 12 articles across 4 sites using RLAiF loop (rewrite, regrade, measure, refine tactics). Results: 0 RED remaining (was 5), 6 GREEN (was 0), 7 AMBER. Average improvement +20pts. Playbook documented in `model-grade-playbook.md` with ranked tactics for integration into Content Generator prompt.
- **YouTube walkthrough video** (May 21) -- embedded in spotlight article with `VideoObject` schema (duration PT8M6S). Added "Watch the walkthrough" link to README.

### Changed
- **12 articles rewritten for content quality** (May 21) -- added anonymized clinical anecdotes, named citations with quantitative findings, quoted patient dialogue, first-person procedural detail, and clinical vulnerability moments across all 4 sites. Removed banned AI phrases and em-dashes. All articles now score A+ 100% on SEO checks and GREEN on deterministic AI exposure.

## Week of 2026-05-09

### Fixed
- **Cron time gate locale parsing broken on all 5 workflows** (May 11) -- n8n Docker container's Node.js outputs `"Mon 09:37"` (no comma) from `toLocaleString`, but code split on `', '`. All cron-scheduled runs silently failed, returning `[]` every tick. Root cause of the multi-week cron-miss pattern. Fixed with regex `match(/^([A-Za-z]{3})[, ]+(\d{2}):(\d{2})$/)` that handles both formats.
- **Content Generator `openclaw_key` not passed** (May 11) -- `Build OpenClaw Request` node spread `$json` but never included `openclaw_key`, causing OpenClaw auth failures on every draft generation since the last workflow edit.
- **Syntax errors in 3 workflows** (May 11) -- `Build OpenClaw Request` nodes in SEO Research Agent and Media Ingestion Agent had `{ openclaw_key: _openclaw_key, {` (extra brace). `Build Rewrite Prompt` in Content Generator had same pattern on 2 error-return lines.
- **Dashboard password gate broken** (May 11) -- `dashboard-config.js` was deployed empty (1 byte), making `PW_HASH` undefined; no password could match. Restored config with correct SHA-256 hash.
- **Backup script using wrong workflow IDs** (May 11) -- All 11 workflow IDs were stale (from a previous n8n instance); every workflow backup was `{"message":"..."}`. Updated to current IDs, added validation, switched site backups from HTTP to SSH/rsync.
- **SEO Actions tab brief hidden** (May 11) -- "View Latest Brief" toggle only appeared if `seo-implementations.json` had entries; empty file caused early return. Fixed to always show the brief toggle.

### Added
- **Auto-publish on approve when overdue** (May 11) -- When a draft is approved and the site is past its minimum publish interval, the Content Generator now immediately triggers `POST /webhook/publish-draft` instead of waiting for next cron. Flow: Set Draft Approved -> Check Overdue -> IF true -> HTTP Auto-Publish -> Respond.
- **Empty pipeline daily todo alert** (May 11) -- Daily Todos endpoint now surfaces sites with no pending or approved drafts regardless of publish deadline distance (previously only alerted within 72h of cron).
- **Dismiss research candidate endpoint** (May 11) -- `POST /webhook/dismiss-candidate` with `{ site_id, candidate_index }`. Marks candidate as dismissed (filtered from list), moves topic to `topic_seeds` for informing future suggestions.
- **Dashboard candidate edit/dismiss buttons** (May 11) -- Research tab candidate cards now have Edit (inline title/rationale editing) and Dismiss buttons alongside Research.
- **sinabarimd personal site directive** (May 11) -- Content Generator prompt now includes a conditional block for sinabarimd that explicitly directs personal essay voice over professional identity framing. Site role changed from `identity_hub` to `personal_site`.
- **Expanded sinabarimd topic scope** (May 11) -- Content Research Agent scout queries, Content Generator allowed topics, and suggest-topic prompt updated: interfaith/interracial family, gentle parenting, clinical/corporate balance, Oakland, cars, NBA, home automation, local AI, food, reading.
- **Hub-spoke schema architecture** (May 11) -- Added `WebSite` node to sinabarimd.com with `hasPart` linking all 3 satellites. Added `isPartOf: sinabarimd.com/#website` on all satellite WebSite schemas. Added `homeLocation`, expanded `knowsAbout` to 16 items, fixed geo coordinates (LA -> Oakland), added `CollectionPage` schema to all article index pages, added `dateModified` to satellite homepage schemas.

### Changed
- **Backup script overhaul** (May 11) -- Sites backed up via SSH/rsync instead of HTTP (catches dashboard-config.js, seo-implementations.json, all article files). Added spotlight, spotlight-campaign, daily-todos to state endpoints. Workflow backups now verified for `nodes` key presence.



### Fixed
- **Orchestrator cron crash -- duplicate `const body`** (May 9) -- Time gate added in May 4 session introduced a duplicate `const body` declaration in Initialize State; every cron trigger threw `SyntaxError` and silently failed. System was 10 days dark. Removed duplicate declaration.
- **sinabari_net PUBLISH_DAYS missing Friday** (May 9) -- `PUBLISH_DAYS` mapped sinabari_net to Tuesday only; changed to array-based `[2, 5]` with `.includes()` checks to match the Tue/Fri cron schedule.
- **Auto Publish Draft HTTP body format** (May 9) -- Switched Auto Publish Draft and Execute Content Agent nodes from `specifyBody: "json"` to `contentType: "raw"` + `rawContentType: "application/json"` per n8n webhook requirements.
- **sinabari.net missing PIPELINE markers** (May 9) -- Homepage had no `PIPELINE:START:ANALYSIS` / `PIPELINE:END:ANALYSIS` markers; Publisher could not inject featured section. Added markers.
- **Publisher sinabari_net template wrong design system** (May 9) -- Template used Tailwind/Material Design 3 classes that don't exist in sinabari.net's CSS; rewrote to use site's editorial CSS (`--serif`, `--accent`, `.wrap`, `.kicker`).
- **Broken `/topics/healthcare-ai` link on sinabari.net** (May 9) -- Hero CTA pointed to nonexistent path; changed to `/articles/`.

### Improved
- **SEO QA broken link check broadened** (May 9) -- Domain-level QA now crawls all internal links (`/anything`) on homepages, not just `/articles/*.html`. Catches 404s from nav, CTAs, and hero links.

### Published
- **sinabari.net first article** (May 9) -- "Clinical AI in Healthcare: What Hospital Leaders Should Actually Watch" deployed to sinabari.net/articles/

## Week of 2026-05-02

### Added
- **Dashboard SEO brief todo** (May 4) -- Overview tab now shows "New SEO brief" todo with View Brief button when a brief hasn't been actioned; clears when `seo-implementations.json` records the brief date
- **Quill WYSIWYG draft editor** (May 1) -- Quill 2.0.3 rich text editor replaces raw HTML textarea in Drafts tab; toolbar with H2/H3, bold, italic, underline, link, lists, blockquote, clean; "View HTML source" toggle for raw edits
- **SEO implementation log** (May 2) -- SEO Actions tab now shows Claude Code implementation history from `/seo-implementations.json`; overview card shows last run date with stale warning after 14 days

### Fixed
- **All RE crons were dead** (May 4) -- n8n 2.12.3 bug: `scheduleTrigger` with specific-time `cronExpression` silently fails to register; only `*/N` interval patterns work. Converted all 5 RE workflows to `*/30 * * * *` with time gates in the first Code node that check PT day/hour. Webhook/manual triggers bypass the gate.
- **RT Drug Test ack logic** (May 4) -- Escalation ack at 9am+ now suppresses redundant "schedule your test" notification (clinic is open, ack doubles as scheduling ack). Direct 7am ack still allows schedule reminder. Fixed 44ms timing drift on escalation intervals.
- **OpenClaw gateway crash loop** (May 4) -- Gateway was crash-looping (545K restarts) due to missing TELEGRAM_BOT_TOKEN env var. Fixed by disabling Telegram channel in `/root/.openclaw-default/openclaw.json`. Gateway now serves `/v1/responses` on port 18789.
- **OpenClaw proxy port conflict** (May 4) -- Zombie python process held port 18790; proxy couldn't bind. Killed zombie, proxy restored on 18790, gateway runs on 18789.
- **drsinabari publish_log** (May 2) -- Orchestrator `publish_log.drsinabari` was stuck at 2026-03-31 after Apr 29 grey-market-peptides publish; fixed via `/webhook/log-publish`

### Changed
- **Dashboard secrets fully externalized** (May 2) -- PW_HASH and GH_TOKEN loaded from `dashboard-config.js` via `<script>` tag; zero secrets in committed HTML
- **Removed dead SEO workflow UI** (May 2) -- generateSEOTasks, approveSEO, dismissSEO, exportToClaudeCode functions removed; Technical SEO Implementer webhooks no longer called

## Week of 2026-04-27

### Added
- **AEO direct-answer summary** (Apr 27) -- Content Generator prompt now requires a `<div class="article-summary">` block after the opening paragraph, optimized for AI Overview extraction
- **SEO Research Agent upgrade** (Apr 27) -- 4 targeted Tavily queries with date filtering (was 1 kitchen-sink query), source citations required in every claim, 30 sources per brief (was 15)
- **Daily Todos API endpoint** (Apr 27) -- `GET /webhook/daily-todos` mirrors dashboard Overview strip as structured JSON; added to Portfolio Orchestrator
- **sync_pending_actions.py** (Apr 27) -- reconciles daily-todos endpoint against pending_actions.md with marker-based diffing
- **Docker env var TAVILY_KEY** (Apr 27) -- Tavily API key externalized from workflow Code nodes into container env + staticData

### Fixed
- **Content Research Agent Tavily scout** (Apr 27) -- refactored from Code node `$http.request` (broken in n8n 2.12.3 task runner) to HTTP Request node pattern
- **Docker host.docker.internal** (Apr 27) -- added `extra_hosts` to docker-compose.yml; was missing after container recreation
- **UFW rules for compose network** (Apr 27) -- added 172.18.0.0/16 rules for OpenClaw, deploy, text-extract, rt-check services

### Changed
- All workflow IDs changed after container recreation and restore from backup (documented in CLAUDE.md)
- n8n activation now uses `POST /api/v1/workflows/{id}/activate` (active is read-only on PUT in n8n 2.12.3)

## Week of 2026-04-22

### Added
- **Full workflow source** (Apr 26) -- all 10 n8n workflow JSONs (sanitized) in `workflows/`
- **Dashboard source** (Apr 26) -- operator dashboard HTML (3,350 lines) with password gate, 8 tabs, inline actions
- **Deep Researcher API** (Apr 26) -- async academic paper research service with n8n callback
- **Upgraded research pipeline** (Apr 22) -- Tavily advanced search, deep-researcher breadth 3/depth 1, OpenClaw synthesis pass for richer briefs
- **Web 2.0 no-repeat logic** (Apr 22) -- syndication tracks posted articles per platform, skips duplicates
- **Monthly YouTube video tasks** (Apr 26) -- video walkthrough suggestions for demo-friendly topics, once per month
- **Suggest with seed text** (Apr 25) -- typing in the topic field before hitting Suggest makes the AI riff on your idea
- **Full suggestion copy** (Apr 25) -- clicking a suggested topic copies title + rationale + angle into the text field
- **Pre-push secret scanning hook** (Apr 26) -- automatically blocks pushes containing API keys, tokens, or personal data
- **Dashboard secrets externalized** (Apr 26) -- all secrets moved to dashboard-config.js (gitignored)
- **GitHub repo topics** (Apr 26) -- 15 discovery topics added (seo, n8n, ai-agents, etc.)
- **HN + Reddit campaign tasks** (Apr 26) -- Show HN and r/n8n posts added to spotlight campaign
- **Slash commands** (Apr 26) -- /deploy-dashboard, /system-check, /backup, /push-repo

### Fixed
- **Content Generator YAML parser** (Apr 25) -- strips model reasoning preamble that was causing "missing title field" errors
- **Spotlight article preservation** (Apr 22) -- fixed full-sync deploy wipe; spotlight article now included in all sinabarimd deploys
- **SEO Actions tab** (Apr 23) -- graceful fallback when Technical SEO Implementer is inactive (shows empty state + brief toggle)
- **SEO brief dismiss** (Apr 23, Apr 26) -- moved to named function to avoid quote-escaping issues in onclick handlers
- **Daily todos** (Apr 23) -- review draft only shows when publish deadline approaching (not for every pending draft)

### Changed
- Spotlight campaign: repeat platform posts (LinkedIn follow-up, Twitter insight, Medium follow-up) can now be skipped
- Syndication article list updated to current live articles across all sites
- Em-dashes replaced with double-hyphens throughout syndication templates
