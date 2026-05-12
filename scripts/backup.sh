#!/bin/bash
# Reputation Engine Backup Script
# Usage: ./backup.sh
# Requires: N8N_BASE_URL and N8N_API_KEY environment variables

set -e

# Source .env if vars not already set
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$N8N_BASE_URL" ] || [ -z "$N8N_API_KEY" ]; then
  if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
  fi
fi

if [ -z "$N8N_BASE_URL" ] || [ -z "$N8N_API_KEY" ]; then
  echo "Error: N8N_BASE_URL and N8N_API_KEY must be set (or add them to .env)"
  exit 1
fi

BACKUP_DIR="$(dirname "$0")/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR/sites/sinabarimd/articles"
mkdir -p "$BACKUP_DIR/sites/sinabari_net/articles"
mkdir -p "$BACKUP_DIR/sites/sinabariplasticsurgery/articles"
mkdir -p "$BACKUP_DIR/sites/drsinabari/articles"
mkdir -p "$BACKUP_DIR/state"

echo "=== Backing up workflows ==="
# 10 RE workflows + RT Drug Test Check (11 total)
for WF_ID in ACGP2CgEOZFS4ysL luiFMIAgKKxrNreT R6Tw9GAj1NX8EzUN 1l2mzI2FBoMUBCFX eYS8hc6xHbSEDpMu 3RYvkOtuOInfaiuZ PHM1QYKaaGf3X480 knBiNIsXRIOLM8iR 4DpoFWCUglQuM4lz hUwWSMqdcLdFmBBi SZz6xgeJEROPvzgd; do
  curl -s "$N8N_BASE_URL/api/v1/workflows/$WF_ID" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" > "$BACKUP_DIR/workflow_$WF_ID.json"
  # Verify it got a real workflow (not an error)
  if python3 -c "import json; d=json.load(open('$BACKUP_DIR/workflow_$WF_ID.json')); assert 'nodes' in d" 2>/dev/null; then
    NAME=$(python3 -c "import json; print(json.load(open('$BACKUP_DIR/workflow_$WF_ID.json')).get('name','?'))")
    echo "  $WF_ID ($NAME)"
  else
    echo "  $WF_ID (FAILED - no nodes in response)"
  fi
done

echo "=== Backing up live sites (via SSH) ==="
# Map: local_dir:server_path
for SITE in \
  "sinabarimd:/srv/sites/sinabarimd" \
  "sinabari_net:/srv/sites/sinabari-net" \
  "sinabariplasticsurgery:/srv/sites/sinabariplasticsurgery" \
  "drsinabari:/srv/sites/drsinabari"; do
  LOCAL="${SITE%%:*}"
  REMOTE="${SITE#*:}"
  # Copy all files (including articles/) via rsync over SSH
  rsync -az --delete -e ssh "claw:$REMOTE/" "$BACKUP_DIR/sites/$LOCAL/" 2>/dev/null
  COUNT=$(find "$BACKUP_DIR/sites/$LOCAL" -type f | wc -l | tr -d ' ')
  echo "  $LOCAL ($COUNT files)"
done

echo "=== Backing up state ==="
for EP in list-drafts list-research-candidates qa-results seo-intel publish-log serp-results media-items spotlight spotlight-campaign daily-todos; do
  curl -s "$N8N_BASE_URL/webhook/$EP" > "$BACKUP_DIR/state/$EP.json" 2>/dev/null
  echo "  $EP"
done

echo "=== Backup complete: $BACKUP_DIR ==="
