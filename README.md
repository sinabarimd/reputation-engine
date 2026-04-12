# Reputation Engine

**A multi-site automated publishing system for entity-first SEO, built by [Dr. Sina Bari, MD](https://sinabarimd.com/about).**

Reputation Engine is the system I built to take control of my professional online presence. It coordinates AI-powered content generation, multi-site publishing, structured data optimization, and SERP monitoring across four owned domains — all orchestrated by autonomous agents running on [n8n](https://n8n.io).

📖 **[Read the full article: How I Built a Personal Reputation Engine with AI Agents](https://sinabarimd.com/articles/how-i-built-a-personal-reputation-engine.html)**

---

## Why This Exists

Physicians and professionals often discover that Google results for their name include outdated, inaccurate, or context-free information. You can't remove those results, but you can build enough high-quality, authoritative content to occupy the visible SERP yourself.

That's what Reputation Engine does — systematically.

Instead of a single website competing for one slot, I run four purpose-built domains, each targeting a different facet of my professional identity. An autonomous agent pipeline researches topics, generates content, validates SEO quality, publishes articles, and measures the impact — on a weekly schedule, with human oversight at every stage.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Portfolio Orchestrator                   │
│          (scheduling, cadence, dispatch, auto-publish)   │
└──────────┬──────────┬──────────┬──────────┬─────────────┘
           │          │          │          │
     ┌─────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌───▼────────┐
     │ Research │ │Content │ │  QA  │ │ Publisher  │
     │  Agent   │ │ Agent  │ │Agent │ │   Agent    │
     └─────────┘ └────────┘ └──────┘ └────────────┘
           │          │          │          │
     ┌─────▼───┐ ┌───▼────┐ ┌──▼───┐ ┌───▼────────┐
     │  SEO    │ │ Media  │ │Meas. │ │ Technical  │
     │Research │ │Ingest  │ │Agent │ │ SEO Agent  │
     └─────────┘ └────────┘ └──────┘ └────────────┘
```

### The Four Domains

| Domain | Role | Content Focus |
|--------|------|---------------|
| [sinabarimd.com](https://sinabarimd.com) | Canonical identity hub | Bio, work, media, selected writing |
| [sinabari.net](https://sinabari.net) | Healthcare AI authority | Healthcare AI analysis, health tech, digital health |
| [drsinabari.com](https://drsinabari.com) | Editorial node | Medicine & technology essays, clinical ethics, healthcare policy |
| [sinabariplasticsurgery.com](https://sinabariplasticsurgery.com) | Specialty node | Aesthetics, aging, rejuvenation, surgery |

### The Agent System (10 Workflows)

Every agent is a standalone n8n workflow with a single responsibility:

1. **Portfolio Orchestrator** — The scheduling brain. Runs per-site cron jobs, checks publishing cadence, auto-publishes approved drafts, and dispatches content generation when the queue is empty.

2. **Content Research Agent** — Runs weekly topic scouting (Phase 1) using web search APIs, then deep research (Phase 2) when an operator selects a topic. Supports file attachments (PDFs, papers) for research context.

3. **Content Generator** — Takes a research brief and site profile, generates a structured draft via LLM, and stores it for human review. Enforces per-site word counts, tone, and forbidden topics.

4. **Content Publisher** — A 20-node pipeline that fetches the approved draft, renders the article page with full SEO metadata and structured data, updates the homepage, generates sitemaps, deploys via a deterministic file-sync service, and triggers QA.

5. **SEO QA Agent** — Three-level validation (article, domain, portfolio). Checks structured data, meta tags, internal linking, content quality. Runs automatically after every publish.

6. **SEO Research Agent** — Weekly intelligence brief analyzing SERP trends, competitor movements, and keyword opportunities across all four domains.

7. **Technical SEO Implementer** — Converts SEO research briefs into actionable tasks with an approve/dismiss/execute workflow.

8. **Media Ingestion Agent** — Monitors the web for mentions of my name, classifies them, and queues relevant items for the press page.

9. **Measurement Agent** — Tracks SERP positions using residential proxy searches and Google Search Console data. Monitors for negative results and generates alerts.

10. **Site Refresh** — Operator-triggered full page regeneration for design updates (used carefully — it's a destructive operation).

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Orchestration | [n8n](https://n8n.io) (self-hosted) | Visual workflow builder, webhook-native, good API |
| Content Generation | [OpenClaw](https://github.com/open-claw/open-claw) (self-hosted LLM gateway) | Full control over prompts, model swapping, no vendor lock-in, all data stays on-prem |
| Web Research | [Tavily API](https://tavily.com) | Purpose-built for AI research, good relevance |
| SERP Monitoring | [BrightData](https://brightdata.com) residential SERP API | Accurate residential-IP search results |
| Search Analytics | Google Search Console API | First-party click/impression data |
| Hosting | Static HTML + nginx + Traefik | Fast, simple, deterministic deploys |
| Deploy | Custom Python deploy service (port 9911) | Full-file-sync model, atomic deploys |
| Text Extraction | Custom Python service (port 9913) | PDF/DOCX/TXT → plain text for research attachments |
| Site Design | [Google Stitch](https://stitch.withgoogle.com) (planned) | AI-generated site designs, template layer separation |
| Development — Design | [Claude Cowork](https://claude.ai) | Architecture planning, spec writing, brainstorming |
| Development — Build | [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) | Live API calls, coding, deployment, debugging |
| Infrastructure | Single VPS + Docker | n8n in container, host services via Docker bridge |

### The "Open Server" Pattern

n8n runs inside Docker and can't execute host commands directly. The solution: lightweight Python HTTP services on the host, managed by systemd, firewalled to only accept connections from the Docker bridge subnet. Each is a single Python file using `http.server`. When n8n needs host-level capabilities (file deploy, text extraction, etc.), it makes an HTTP call to `host.docker.internal:{port}`.

### Claude as Development Partner

This entire system was designed in [Claude Cowork](https://claude.ai) and built with [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview). Cowork handles the thinking — architecture, specs, strategy, brainstorming. Claude Code handles the doing — live n8n API calls, writing code, deploying changes, debugging production issues. They share the same project folder, so a spec file drafted in Cowork is immediately available for Code to implement.

A 500-line `CLAUDE.md` file in the project root acts as institutional memory — complete API reference, workflow IDs, webhook endpoints, architectural rules, and deployment procedures. Every Claude Code session reads it automatically, starting with full system context.

**Example: Scrolling News Ticker.** The sinabarimd.com homepage has a scrolling news ticker showing recent media mentions. It went from idea → design spec (Cowork) → working component deployed to production (Claude Code) in a single session. That's the kind of iteration speed this workflow enables for a non-engineer.

---

## Key Design Decisions

### Why Static HTML Instead of WordPress/CMS

The deploy service does a **full file sync** — every deploy lists exactly which files should exist, and anything not in the list is removed. This makes deploys completely deterministic: you always know exactly what's live. No database, no plugins, no security surface. The tradeoff is that you need a rendering pipeline, which the Content Publisher handles.

### Why Separate Domains Instead of Subdomains

Each domain builds its own authority and competes for its own SERP slot. Subdomains of a single domain would consolidate ranking power but only occupy one result. The goal is to own as many page-one results as possible for branded queries.

### Why Human-in-the-Loop

Every draft goes through human review before publishing. The operator can edit titles, excerpts, full content, and even reroute articles to a different site. Auto-publish only fires for drafts that have been explicitly approved. This is a reputation system — accuracy matters more than speed.

### Why Per-Agent Isolation

Each agent has exactly one job. The Content Generator doesn't know about SEO scores. The QA Agent doesn't generate content. The Measurement Agent doesn't publish anything. This makes the system debuggable, testable, and safe to modify — changing one agent never breaks another.

---

## Repository Structure

```
reputation-engine/
├── README.md                    # You are here
├── LICENSE                      # MIT
├── deploy/
│   └── deploy_service.py        # Deterministic file-sync deploy service
├── profiles/
│   ├── sinabarimd_com.yaml      # Site profile — canonical hub
│   ├── sinabari_net.yaml        # Site profile — healthcare AI
│   ├── drsinabari_com.yaml      # Site profile — editorial
│   └── sinabariplasticsurgery_com.yaml  # Site profile — specialty
├── qa/
│   └── qa_checks.js             # SEO QA validation logic (n8n Code node)
├── schema/
│   ├── homepage_person.json     # Person+Physician structured data
│   ├── article_schema.json      # Article page structured data template
│   └── faq_extractor.js         # Auto-extracts FAQPage schema from HTML
├── templates/
│   └── article_meta.html        # Article page SEO meta template
├── measurement/
│   └── measure.py               # GSC data collection via service account
└── docs/
    ├── architecture.md          # Detailed architecture documentation
    └── publishing-pipeline.md   # The 20-node publish flow
```

---

## Example: Site Profile

Each domain has a YAML profile that controls content generation, publishing cadence, and SEO settings:

```yaml
site_id: sinabari_net
domain: sinabari.net
name: "Sina Bari, MD — Healthcare AI Analysis"
role: "Healthcare AI authority site"
author:
  name: "Dr. Sina Bari, MD"
  url: "https://sinabarimd.com/about"
content:
  allowed_topics:
    - healthcare AI
    - medical technology
    - digital health
    - precision medicine
  forbidden_topics:
    - plastic surgery
    - reconstructive surgery
    - generic AI
  default_word_count: 1200
  tone: "analytical, evidence-based, first-person clinical perspective"
publishing:
  min_days_between_publishes: 3
  pipeline_section: "ANALYSIS"
  cron_days: [tuesday, friday]
seo:
  schema_type: "WebSite"
  canonical_hub_link: true
  author_id: "https://sinabarimd.com/#sinabari"
```

---

## Example: Deploy Service

The deploy service is a simple Python HTTP server that receives a file manifest and atomically syncs a site directory:

```python
# Simplified — see deploy/deploy_service.py for the full implementation
def handle_deploy(request):
    payload = request.json
    domain = payload['domain']
    deploy_path = payload['deployPath']
    files = payload['files']
    
    # Write all files from the manifest
    for file_entry in files:
        path = os.path.join(deploy_path, file_entry['path'])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(file_entry['content'])
    
    # Remove any files NOT in the manifest (full sync)
    manifest_paths = {f['path'] for f in files}
    for existing in walk_directory(deploy_path):
        if existing not in manifest_paths:
            os.remove(os.path.join(deploy_path, existing))
    
    return {"success": True, "files_written": len(files)}
```

---

## Results

After 3 weeks of operation (as of April 2026):

- **4 owned domains** ranking on page 1 for branded queries
- **6+ articles** published across all sites with automated QA (all scoring A+)
- **Structured data** (Person, Physician, Article, FAQPage) deployed on every page
- **42 media mentions** tracked and classified
- **Zero manual deploys** — everything goes through the pipeline
- **100% QA pass rate** across the portfolio

---

## Running Your Own

This repository is a reference implementation. To adapt it for your own use:

1. **Set up n8n** — self-hosted instance with API access
2. **Define your domains** — what facets of your identity do you want to represent?
3. **Create site profiles** — YAML configs that control content and publishing rules
4. **Set up the deploy service** — or adapt to your hosting (Netlify, Vercel, S3, etc.)
5. **Connect an LLM** — OpenClaw, OpenAI, Anthropic, or any compatible API
6. **Build incrementally** — start with one site, add agents as you go

---

## Author

**Dr. Sina Bari, MD**
Physician · Healthcare AI · Medical Technology

- 🌐 [sinabarimd.com](https://sinabarimd.com)
- 🏥 [sinabari.net](https://sinabari.net) — Healthcare AI Analysis
- ✍️ [drsinabari.com](https://drsinabari.com) — Essays on Medicine & Technology
- 💼 [LinkedIn](https://linkedin.com/in/sinabari)

---

## License

MIT — see [LICENSE](LICENSE) for details.

This is a reference implementation of the system described in [How I Built a Personal Reputation Engine with AI Agents](https://sinabarimd.com/articles/how-i-built-a-personal-reputation-engine.html).
