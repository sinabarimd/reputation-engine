# Publishing Pipeline

## Overview

The publishing pipeline is a 20-node n8n workflow that transforms an approved draft
into a fully deployed article with SEO metadata, structured data, and updated homepage.

## Trigger

```
POST /webhook/publish-draft
Body: { "draft_id": "...", "site_id": "..." }
```

The pipeline can be triggered by:
- **Auto-publish**: Portfolio Orchestrator fires when an approved draft exists and cadence requirements are met
- **Manual publish**: Operator clicks "Publish Now" on the dashboard
- **API**: Direct webhook call

## Pipeline Stages

### Stage 1: Fetch & Extract

The pipeline fetches the full draft from the Content Generator's storage, extracts
all fields needed for rendering (title, slug, excerpt, content_html, site_id, word_count),
and loads the site profile to determine domain-specific settings.

### Stage 2: Homepage Update

The pipeline fetches the current live homepage, updates the article register
(a sliding window of max 3 articles per site), renders the featured section
using site-specific card templates (primary/secondary/tertiary), and injects
the rendered HTML between the PIPELINE markers.

Each site has a named pipeline section:

| Site | Section | Markers |
|------|---------|---------|
| sinabarimd.com | PUBLICATIONS | `<!-- PIPELINE:START:PUBLICATIONS -->` |
| sinabari.net | ANALYSIS | `<!-- PIPELINE:START:ANALYSIS -->` |
| drsinabari.com | ESSAYS | `<!-- PIPELINE:START:ESSAYS -->` |
| sinabariplasticsurgery.com | ARTICLES | `<!-- PIPELINE:START:ARTICLES -->` |

### Stage 3: Article Rendering

Generates the full article page at `/articles/{slug}.html` with:

- Complete HTML document with site-specific styling
- SEO meta tags (title, description, canonical, robots)
- Open Graph tags (og:type article, og:title, og:description, article:published_time)
- Twitter Card meta
- JSON-LD structured data (@type Article or MedicalWebPage depending on site)
- FAQPage schema auto-extracted from H3/P patterns in content
- Author byline with link to sinabarimd.com/about
- Contextual link to canonical hub (sinabarimd.com)

### Stage 4: Index & Sitemap

Generates the articles index page (`/articles/index.html`) listing all articles
in the register, and generates `sitemap.xml` with all site URLs.

### Stage 5: QA Gate

Before deploying, the pipeline runs inline QA checks:
- Author byline present
- Canonical hub link present
- Structured data valid
- No forbidden topic content

If QA fails, the pipeline halts and reports the failure.

### Stage 6: Deploy

Assembles the deploy payload with all files that should exist on the site:

```json
{
  "domain": "sinabari.net",
  "deployPath": "/srv/sites/sinabari-net",
  "verifyUrl": "https://sinabari.net",
  "files": [
    { "path": "index.html", "content": "..." },
    { "path": "styles.css", "content": "..." },
    { "path": "articles/index.html", "content": "..." },
    { "path": "articles/my-article.html", "content": "..." },
    { "path": "sitemap.xml", "content": "..." }
  ]
}
```

**Important**: The deploy service does a full file sync. Files not in the manifest
are deleted. The pipeline always includes all known files for the site.

### Stage 7: Post-Deploy

After successful deploy:
1. Logs the publish date to the Orchestrator (`POST /webhook/log-publish`)
2. Triggers the SEO QA Agent for comprehensive post-publish validation
3. Returns success response with article URL and publish timestamp

## Cadence Enforcement

The Orchestrator enforces minimum intervals between publishes:

| Site | Minimum Interval |
|------|-----------------|
| sinabarimd.com | 7 days |
| sinabari.net | 3 days |
| drsinabari.com | 14 days |
| sinabariplasticsurgery.com | 7 days |

Auto-publish respects these intervals. Manual "Publish Now" overrides them.
