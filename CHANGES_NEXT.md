# Changes for Next Release

<!-- Claude Code appends here during sessions. Monthly sync moves these into CHANGELOG.md. -->

### Added
- **Full workflow source** -- all 10 n8n workflow JSONs (sanitized) in `workflows/`
- **Dashboard source** -- operator dashboard HTML (3,350 lines) with password gate, 8 tabs, inline actions
- **Deep Researcher API** -- async academic paper research service with n8n callback
- **Upgraded research pipeline** -- Tavily advanced search, deep-researcher breadth 3/depth 1, OpenClaw synthesis pass for richer briefs
- **Web 2.0 no-repeat logic** -- syndication tracks posted articles per platform, skips duplicates
- **Monthly YouTube video tasks** -- video walkthrough suggestions for demo-friendly topics, once per month
- **Suggest with seed text** -- typing in the topic field before hitting Suggest makes the AI riff on your idea
- **Full suggestion copy** -- clicking a suggested topic copies title + rationale + angle into the text field

### Fixed
- **Content Generator YAML parser** -- strips model reasoning preamble that was causing "missing title field" errors
- **Spotlight article preservation** -- fixed full-sync deploy wipe; spotlight article now included in all sinabarimd deploys
- **SEO Actions tab** -- graceful fallback when Technical SEO Implementer is inactive (shows empty state + brief toggle)
- **SEO brief dismiss** -- date-based localStorage comparison, reliable element removal on click
- **Daily todos** -- review draft only shows when publish deadline approaching (not for every pending draft)

### Changed
- Spotlight campaign: repeat platform posts (LinkedIn follow-up, Twitter insight, Medium follow-up) can now be skipped
- Syndication article list updated to current live articles across all sites
- Em-dashes replaced with double-hyphens throughout syndication templates
