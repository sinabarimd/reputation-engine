#!/bin/bash
# Reputation Engine Backup Script
# Usage: ./backup.sh
# Requires: N8N_BASE_URL and N8N_API_KEY environment variables

set -e

if [ -z "$N8N_BASE_URL" ] || [ -z "$N8N_API_KEY" ]; then
  echo "Error: N8N_BASE_URL and N8N_API_KEY must be set"
  exit 1
fi

BACKUP_DIR="$(dirname "$0")/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR/sites/sinabarimd/articles"
mkdir -p "$BACKUP_DIR/sites/sinabari_net/articles"
mkdir -p "$BACKUP_DIR/sites/sinabariplasticsurgery/articles"
mkdir -p "$BACKUP_DIR/sites/drsinabari/articles"
mkdir -p "$BACKUP_DIR/state"

echo "=== Backing up workflows ==="
for WF_ID in 1m5QjQ2KsF9Q6s6U 8sibaEgEYW106llR HL9utsXpnzmqxvkL K4uSeWNA29Bu84MO PaZGnhoW9T9JXiG1 S2Bmeg8gXM8NQPo2 SbGN3pzCdy0asKxY orzgeCjPL81pIqar sVqzAcBYugDPkReZ GrUFalRTkkQjqEgT sLLZMHxZCxYRGL81; do
  curl -s "$N8N_BASE_URL/api/v1/workflows/$WF_ID" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" > "$BACKUP_DIR/workflow_$WF_ID.json"
  echo "  $WF_ID"
done

echo "=== Backing up live sites ==="
for URL in \
  "sinabarimd/index.html:https://sinabarimd.com/" \
  "sinabarimd/styles.css:https://sinabarimd.com/styles.css" \
  "sinabarimd/dashboard.html:https://sinabarimd.com/dashboard.html" \
  "sinabarimd/about.html:https://sinabarimd.com/about.html" \
  "sinabarimd/articles/index.html:https://sinabarimd.com/articles/index.html" \
  "sinabarimd/press.html:https://sinabarimd.com/press.html" \
  "sinabarimd/sitemap.xml:https://sinabarimd.com/sitemap.xml" \
  "sinabarimd/robots.txt:https://sinabarimd.com/robots.txt" \
  "sinabari_net/index.html:https://sinabari.net/" \
  "sinabari_net/styles.css:https://sinabari.net/styles.css" \
  "sinabari_net/articles/index.html:https://sinabari.net/articles/index.html" \
  "sinabariplasticsurgery/index.html:https://sinabariplasticsurgery.com/" \
  "sinabariplasticsurgery/styles.css:https://sinabariplasticsurgery.com/styles.css" \
  "sinabariplasticsurgery/articles/index.html:https://sinabariplasticsurgery.com/articles/index.html" \
  "drsinabari/index.html:https://drsinabari.com/" \
  "drsinabari/styles.css:https://drsinabari.com/styles.css" \
  "drsinabari/articles/index.html:https://drsinabari.com/articles/index.html" \
  "drsinabari/sitemap.xml:https://drsinabari.com/sitemap.xml" \
  "drsinabari/robots.txt:https://drsinabari.com/robots.txt"; do
  FILE="${URL%%:*}"
  SRC="${URL#*:}"
  curl -s -f "$SRC" -o "$BACKUP_DIR/sites/$FILE" 2>/dev/null && echo "  $FILE" || echo "  $FILE (failed)"
done

echo "=== Backing up state ==="
for EP in list-drafts list-research-candidates qa-results seo-actions seo-intel publish-log serp-results media-items; do
  curl -s "https://n8n.sinabarimd.com/webhook/$EP" > "$BACKUP_DIR/state/$EP.json" 2>/dev/null
  echo "  $EP"
done

echo "=== Backup complete: $BACKUP_DIR ==="
