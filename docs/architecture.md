# Architecture

## System Design Principles

Reputation Engine is built on four core principles:

**1. Entity-first SEO** — Instead of optimizing a single site for keywords, we optimize multiple
sites to consolidate a *person entity* in Google's knowledge graph. Each domain targets a different
facet of the entity (professional identity, expertise area, editorial voice, clinical specialty),
and all sites reference a single canonical identity anchor via structured data (`@id`).

**2. Agent isolation** — Every workflow has exactly one responsibility. The Content Generator
doesn't know about SEO scores. The QA Agent doesn't publish. The Measurement Agent doesn't
modify content. This makes the system safe to modify: changing one agent never breaks another,
and each can be tested independently.

**3. Deterministic deploys** — The deploy service uses a full-file-sync model. Every deploy
specifies exactly which files should exist. Files not in the manifest are removed. This eliminates
state drift and makes rollbacks trivial (redeploy the previous manifest).

**4. Human-in-the-loop** — Every piece of content goes through human review before publishing.
The system generates, validates, and prepares content automatically, but a human operator must
approve before anything goes live. Auto-publish only fires for previously approved drafts.

---

## Multi-Site Architecture

```
                    ┌──────────────────────┐
                    │   sinabarimd.com     │
                    │  (Canonical Hub)     │
                    │  Person+Physician    │
                    │  @id: /#sinabari     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼──────┐ ┌──────▼───────┐ ┌──────▼──────────────┐
     │ sinabari.net  │ │drsinabari.com│ │sinabariplasticsurgery│
     │ Healthcare AI │ │ Editorial    │ │ .com — Specialty     │
     │ WebSite+Page  │ │ WebSite+Page │ │ WebSite+MedicalPage  │
     └───────────────┘ └──────────────┘ └──────────────────────┘

     All satellites reference sinabarimd.com/#sinabari as author @id
     All satellites include contextual links back to sinabarimd.com
```

### Why Four Domains?

Each domain competes for its own SERP slot. For a branded query like "Sina Bari MD",
having four separate domains means potentially occupying four of the ten page-one results.
Subdomains of a single domain would consolidate ranking signals but only get one slot.

The entity signal is preserved across domains through:
- Consistent `author.@id` pointing to `sinabarimd.com/#sinabari`
- `sameAs` array on the canonical hub listing all satellite domains
- Consistent author name and attribution across all published content

---

## Agent Architecture

```
                    ┌───────────────────────────────┐
                    │     Portfolio Orchestrator     │
                    │  (scheduling, cadence, dispatch│
                    │   auto-publish, ramp-up)       │
                    └──┬──────┬──────┬──────┬───────┘
                       │      │      │      │
    ┌──────────────────┘      │      │      └──────────────────┐
    │           ┌─────────────┘      └─────────────┐           │
    ▼           ▼                                  ▼           ▼
┌────────┐ ┌────────┐                         ┌────────┐ ┌────────┐
│Content │ │Content │                         │  SEO   │ │  SEO   │
│Research│ │Generat.│                         │Research│ │  QA    │
│ Agent  │ │        │                         │ Agent  │ │ Agent  │
└────────┘ └───┬────┘                         └────────┘ └────────┘
               │
               ▼
          ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
          │Content │     │  Tech  │     │ Media  │     │Measure-│
          │Publish.│     │  SEO   │     │Ingest  │     │ ment   │
          │        │     │Implem. │     │ Agent  │     │ Agent  │
          └────────┘     └────────┘     └────────┘     └────────┘
```

Each agent runs as an independent n8n workflow, communicating via webhooks.
Inter-agent calls use HTTP Request nodes (not Execute Workflow) due to
n8n licensing constraints.

---

## Publishing Pipeline (20 Nodes)

The Content Publisher is the most complex workflow, transforming an approved
draft into a fully deployed article with all SEO metadata:

```
1.  Receive publish webhook (draft_id, site_id)
2.  Fetch full draft from Content Generator
3.  Extract publish fields (title, slug, content_html, etc.)
4.  Fetch current live homepage from the domain
5.  Update article register (max 3 articles per site, newest first)
6.  Render featured section (primary/secondary/tertiary card templates)
7.  Replace PIPELINE markers in homepage HTML
8.  Fetch current styles.css (graceful 404 handling)
9.  Attach styles to build context
10. Generate article page (/articles/slug.html) with full SEO meta + schema
11. Generate articles index (/articles/index.html)
12. Run QA checks (author byline, canonical link, schema)
13. Generate sitemap.xml
14. Build deploy payload (pre-serialize for large payloads)
15. POST deploy payload to deploy service
16. Log publish date to Orchestrator
17. Return success response
18. Trigger SEO QA Agent for post-publish validation
```

The article register maintains a sliding window of 3 articles per site.
When a new article publishes, it becomes primary; the previous primary
becomes secondary; secondary becomes tertiary; and the old tertiary
drops off the homepage (but remains accessible at its direct URL).

---

## Deploy Architecture

The deploy service is a Python HTTP server running on the host machine,
accessible from the n8n Docker container via `host.docker.internal:9911`.

```
n8n (Docker) → host.docker.internal:9911/deploy → /srv/sites/{site}/
```

Key properties:
- **Full file sync**: files not in the manifest are removed
- **Atomic**: all files written before any are removed
- **Deterministic**: same manifest = same deployed state
- **Auditable**: every deploy returns a manifest hash for tracking

Traffic routing:
```
Internet → Traefik (443) → nginx containers → /srv/sites/{site}/
```

Each site has its own nginx container, with Traefik handling TLS termination
and routing based on domain name.
