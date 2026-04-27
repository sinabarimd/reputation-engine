# Changes for Next Release

<!-- Claude Code appends here during sessions. Monthly sync moves these into CHANGELOG.md. -->

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
