# Changelog

## v2026.07 - July 2026

Auto-synced from live system on 2026-07-01.

### Changes

- Updated profiles/sinabarimd_com.yaml
- Updated profiles/sinabari_net.yaml
- Updated profiles/drsinabari_com.yaml
- Updated profiles/sinabariplasticsurgery_com.yaml
- Synced deploy/deploy_service.py from live
- Synced services/extract_server.py from live

### Stats
- 1 new file(s)
- 7 modified file(s)

---

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

## Week of 2026-06-27

### Added
- **sinabarimd.com hub rewrite -- entity-anchor + funnel** (Jun 27) -- Retired the chronological blog feed on the homepage. Replaced `PIPELINE:INSIGHTS` and `PIPELINE:PUBLICATIONS` auto-feeds with a static, hand-curated Selected Work router that funnels OUT to sinabari.net (Healthcare AI), drsinabari.com (Essays), and sinabariplasticsurgery.com (Surgical Practice) -- 3 representative articles per card. Cornerstone identity essays kept on the hub and listed beneath the router. New "Now / Current Focus" section signals a live entity without a blog cadence. Footer now cross-links to all 4 owned domains plus About and Press (drsinabari.com previously missing). Title now reads "Surgeon, Healthcare-AI Executive, Builder"; entity-anchored meta description replaces the personal-blog framing. Hero rewritten to lead with the whole entity rather than a single specialty.
- **Selected Writing index on sinabarimd.com/articles/** (Jun 27) -- Replaced the chronological list of 13 articles with a curated 4-section index: Identity & Integration (4 cornerstones), Building (2 showcases incl. spotlight), Selected Work Elsewhere (3 satellite cards), Personal (3 lifestyle pieces, fenced and visually subordinate). `CollectionPage` schema added with author/about/isPartOf references into `#sinabari` and `#website`.
- **Now / Current Focus homepage section** (Jun 27) -- New section describing the entity's live state (work at iMerit, Awesome Medical Tools maintenance, writing across the network). Hand-authored, not driven by article cadence.

### Changed
- **JSON-LD `@graph` tightened** (Jun 27) -- Person+Physician `jobTitle` now includes "VP, Healthcare AI"; added `worksFor: { @type: Organization, name: "iMerit" }`; removed the invalid `"image": "#headshot"` fragment URI; tightened `knowsAbout` to entity-relevant topics only (dropped NBA Basketball, Gentle Parenting, Interfaith Families, Oakland Community, etc. that were diluting the entity signal); WebSite description rewritten to the canonical-entity role; `ProfilePage.dateModified` refreshed. Validates in Rich Results Test; 14 sameAs URLs intact (LinkedIn, Scholar, Wikidata Q138774674, TechCrunch, Doximity, Crunchbase, MuckRack, Healthgrades, Instagram, X, Facebook, YouTube channel, ORCID 0009-0001-6594-6177, GitHub).
- **Impact Stats: verifiable claims only** (Jun 27) -- Replaced unsourced "12k+ Clinical Procedures" and "4+ Training & Fellowships" with "344+ Awesome Medical Tools" (the verified GitHub catalog) and "4 Owned Domain Network". Kept "20+ Years in Healthcare" and "75+ Research Contributions" pending Scholar/CV verification.
- **Top nav re-labeled** (Jun 27) -- Profile / Selected Work / Now / Writing / Press / About. Removed `#research` and `#insights` anchors that no longer exist. Contact button replaced with a Bio link.
- **`profiles/sinabarimd_com.yaml`** (Jun 27) -- `allowed_topics` scoped to identity / credentials / integration / builder showcases / curation / fenced personal. `forbidden_topics` now explicitly bans board-certification claims (Dr. Bari is NOT board certified), healthcare-AI deep dives, plastic-surgery procedure writing, longevity/anti-aging, generic AI explainers, and long-form editorial essays -- those route to satellites. The QA `topic_violation` gate now auto-enforces hub coherence. Hub is OFF auto-dispatch as of 2026-06-27 -- cornerstone content is hand-authored, not auto-generated.
- **Portfolio Orchestrator: sinabarimd off auto-dispatch** (Jun 27) -- Removed `sinabarimd` from `PUBLISH_DAYS` and from every `RAMP_SCHEDULE` week. The hub no longer receives auto-generated topical drafts on Mondays. Operator overrides via `requested_sites` still bypass the day-of-week check, so manual hub publishes remain possible. (Live workflow only; the staging tree's `workflows/portfolio-orchestrator.json` is NOT auto-synced per `PUBLISH_MANIFEST.md` -- refresh on a separate operator-controlled push.)

### Migrated
- **4 misplaced topical articles from sinabarimd.com to satellites** (Jun 27) -- Regenerated via Content Generator per-site for proper schema and voice; the originals stayed on disk and now 301 to the new URLs:
  - `clinical-ai-governance-problem-not-chatbot` → `sinabari.net/articles/clinical-ai-governance-problem-not-chatbot-problem.html` (1858 words)
  - `how-high-performing-doctors-are-building-a-personal-ai-stack-for-research-writing-and-practice-management` → `sinabari.net/articles/working-physician-personal-ai-stack.html` (1850 words)
  - `why-value-based-care-is-the-future-of-plastic-and-reconstructive-surgery` → `sinabariplasticsurgery.com/articles/why-value-based-care-is-harder-in-plastic-and-reconstructive-surgery-than-it-looks.html` (2261 words)
  - `longevity-science-clinical-practice-physician-perspective` → `sinabariplasticsurgery.com/articles/what-a-surgeon-actually-tells-patients-about-longevity-medicine.html` (1889 words)
  All 4 generated drafts passed deterministic QA (0 em-dashes, 0 banned AI phrases, 0 board-certification claims about Dr. Bari) before publish. Post-publish domain QA: sinabari.net A+ 100/100 0 fail/warn; sinabariplasticsurgery A+ 100/100 0 fail/warn. Audited and confirmed: Publisher's `Build Deploy Payload` node uses `article_archive` (full history, not the 3-item rotation register) and fetches every existing live satellite article before each deploy, so full-file-sync did not wipe any pre-existing satellite content -- all 11 sinabari.net articles and all 8 sinabariplasticsurgery articles remained live throughout.
- **4x 301 redirects via Traefik `redirectRegex` middlewares** (Jun 27) -- Added to `/etc/traefik/dynamic/sinabarimd.yml` as `sinabarimd-migrate-{clinical-ai-governance,ai-stack,value-based-care,longevity}`, attached to both the http and https routers. Each old hub URL 301s to its specific new satellite article URL so topical equity transfers (not a soft-404 redirect-to-homepage). Hub homepage and all other hub URLs (`/about`, `/press`, `/articles/`, `/articles/physician-builders.html`, `/articles/how-i-built-a-personal-reputation-engine.html`, `/dashboard`, `/sitemap.xml`) still 200.

> Why this rewrite: the May 21 – Jun 2 core update re-ranked source types for `[name] MD` queries and specifically punished topical incoherence. Of four owned domains, only sinabari.net survived page 1 (#5), precisely because it is the deepest, narrowest topical cluster. The hub had been the opposite -- surgery + healthcare AI + family + hobbies on one domain -- sending mixed signals so it ranked for nothing and competed with its own narrower satellites. This rewrite makes the hub a single-purpose entity node and funnels topical authority outward.

### Later same day

#### Added
- **Real headshot wired into the entity schema across all 4 sites** (Jun 27) -- Selected one shot per site from the `Headshots and portraits/` archive to match each site's voice: hub gets the navy-suit office shot (`sina-bari-headshot.jpg`), sinabari.net gets the builder-at-desk-with-laptop shot (`sina-bari-builder.jpg`), sinabariplasticsurgery gets the white-coat-on-tree-lined-street shot (`sina-bari-coat.jpg`), drsinabari gets the half-zip-pullover smile (`sina-bari-portrait.jpg`). Each resized to 1200 + 600 widths via `sips` (JPEG q85). Uploaded to `/srv/assets/{site}/` where the nginx `/assets/` alias exists; for drsinabari, lives at `/srv/sites/drsinabari/assets/` (no alias). Each site got `og:image`, `og:image:width/height/alt`, `twitter:card: summary_large_image`, `twitter:image`, and a new `ImageObject` node in the JSON-LD `@graph` referenced by `WebPage.primaryImageOfPage` (or `MedicalWebPage.primaryImageOfPage` on sips). Visible placement per site: hub hero `<img>` replaces the 108KB inline base64 placeholder; sinabari.net About-the-Author panel rebuilt as a flex layout with 220px portrait + expanded bio; sinabariplasticsurgery hero background swaps the molecular-biology placeholder for the white coat at `opacity-30 grayscale`; drsinabari About column re-laid out so the portrait (cols 2-4, grayscale) sits beside the bio (cols 5-10).
- **YouTube walkthrough embedded on the hub** (Jun 27) -- New `id="watch"` section between Selected Work and Pillars of Expertise. Left column: framing block + "Open on YouTube ↗" CTA. Right column: responsive 16:9 `youtube-nocookie.com/embed/3WV84_8cgA8` iframe with `loading="lazy"`. Top nav got a `Watch` link. Matches the existing `VideoObject @id #video-reputation-engine` already in the `@graph`, with `subjectOf` reciprocal on Person.
- **Instagram carousel format in the spotlight Web 2.0 campaign** (Jun 27) -- Portfolio Orchestrator `campaign-prepare-prompt` rewritten so Day 13 (Instagram) is now a 6-slide carousel instead of a single `story_or_post`. Each slide is `{ slide_number, image_brief, slide_text }` -- on-slide text is the literal text rendered over the image (max 8 words); image_brief is a concrete subject + visual style (1-2 sentences) the operator can hand to Canva or Stitch. Caption (with hashtags) goes in the task's `content` field. Coherent micro-story shape enforced by the prompt: slide 1 hook → slides 2-5 the why/how/what → slide 6 CTA. `campaign-parse-store` preserves the `carousel_slides[]` array into staticData.
- **Dashboard Web 2.0 Content tab renders carousel slides inline** (Jun 27) -- When a spotlight task has `carousel_slides[]`, the dashboard renders the slides in a numbered grid below the caption: green-circle slide badges, per-slide on-slide text (bold, copy button), per-slide image brief (italic, copy button). Standard non-carousel post tasks unchanged.
- **Deploy service binary file support** (`deploy/deploy_service.py`) (Jun 27) -- Added `content_b64` field support alongside the existing `content` (text) field on the `POST /deploy` payload. If a file entry has `content_b64`, the service `base64.b64decode`s it and `write_bytes`. Otherwise text path. Pre-existing `.bak-pre-binary-2026-06-27` saved on the host. Enables binary assets (images) to round-trip through the Publisher's full-file-sync deploys.

#### Changed
- **Dashboard: sinabarimd off the publish schedule UI** (Jun 27) -- Matches this morning's Orchestrator change (hub off auto-dispatch). Dropped `sinabarimd` from `SCHED_MIN_INTERVALS`, `SCHED_CRON_DAYS`, `SCHED_CRON_HOURS`, `SCHED_RAMP_UNLOCK_WEEK`, and `SCHED_ALL_SITES` (Overview "Next Publish", Daily Todos, Content Alerts no longer treat the hub as a cron-publishing site) and from `ALL_SCHED_SITES` in the Publish tab (no more empty-pipeline "Scheduled: Mon" card). Added `SCHED_MANUAL_SITES = new Set(['sinabarimd'])`; approved sinabarimd drafts still render in the Publish list with a "manual route" badge and "Manual publish only" label instead of a predicted cron date; they sort to the bottom of the queue.
- **Hub Person+Physician schema: real `image` ImageObject + `subjectOf` VideoObject** (Jun 27) -- The morning rewrite omitted the schema `image` field because the only candidate was an invalid `#headshot` fragment URI. Now populated as a full `ImageObject` with `@id #headshot`, `contentUrl`, `thumbnailUrl`, `width`, `height`, `caption`. Person now carries `subjectOf: #video-reputation-engine`. Hub `og:image`/`twitter:image` added (was missing before). Domain QA: A+ 100/100 throughout each redeploy.
- **Publisher `Build Deploy Payload`: drsinabari binary asset preservation** (Jun 27) -- Mirrors the existing `sinabarimd` extraPaths preservation block. drsinabari publish now fetches `assets/sina-bari-portrait.jpg` and `assets/sina-bari-portrait-sm.jpg` from the live URL with `encoding: 'arraybuffer'`, base64-encodes the body, and pushes `{path, content_b64}` into the deploy payload. Required because drsinabari's container has no `/srv/assets/drsinabari → /srv/assets` mount or `/assets/` nginx alias like the other two satellites, so the portrait has to live inside the deploy target.
- **Publisher `Render Featured Section`: hub renderer trimmed** (Jun 27) -- sinabarimd renderer now returns `spotlightHtml ? { SPOTLIGHT } : {}` (was `{ INSIGHTS, PUBLICATIONS, SPOTLIGHT }`). The `PIPELINE:INSIGHTS` and `PIPELINE:PUBLICATIONS` markers were retired this morning with the Selected Work router rewrite, so without this fix the next manual hub publish would have thrown `PIPELINE markers not found for section INSIGHTS`.
- **Publisher `Replace PIPELINE Section`: tolerant of missing markers** (Jun 27) -- The replacement loop now `continue`s past a missing marker instead of throwing. Defense-in-depth for future marker retirements.
- **Publisher `Generate Articles Index`: sinabarimd fetch-and-passthrough** (Jun 27) -- The default behaviour regenerates `articles/index.html` from a chronological card template. For sinabarimd that would have wiped this morning's "Selected Writing" curated index (4 cornerstones + 2 builder showcases + 3 satellite cards + fenced personal). New behaviour for sinabarimd only: `httpRequest` the live `articles/index.html`; if 200 with body >500 bytes, return that as `articles_index_html`. Falls back to template only if fetch fails.

#### Fixed
- **Spotlight campaign auth bug (was silent)** (Jun 27) -- `campaign-prepare-prompt` was dropping `openclaw_key` from its return so `campaign-openclaw-gen` sent `Bearer undefined` and 401-ed. Now passes `openclaw_key: $json.openclaw_key` through. The Chief of Staff campaign launched 2026-06-12 had this bug latent -- generic Instagram content with no article context. Today's regen with the fix produced a 14-task campaign with the proper carousel from the Chief of Staff article text.
- **Chief of Staff spotlight 404 on the hub** (Jun 27) -- The hub homepage spotlight card hardcoded `href="https://drsinabari.com/articles/chief-of-staff-personal-operating-system.html"` -- a URL that 404-ed because the article never existed on drsinabari (drsinabari is editorial-only; Chief of Staff is a builder showcase). Cleared `staticData.global.spotlight.canonical_url` to `null` so the Publisher's `spotlightLivesOn()` falls back to sinabarimd.com (where the article actually lives), cleared the same field on the `spotlight_history` entry, and rewrote the live hub `index.html` spotlight card link to `sinabarimd.com/articles/chief-of-staff-personal-operating-system.html` (200).

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
