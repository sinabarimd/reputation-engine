#!/bin/bash
# Monthly GitHub sync script for Reputation Engine
# Runs on the 1st of each month at 06:00 PST via cron
# Pulls live system state, updates repo, commits with changelog, pushes
set -e

REPO_DIR="/opt/reputation-engine-repo"
N8N_BASE="https://n8n.sinabarimd.com"
PROFILES_BASE="http://localhost:9911/profiles"
LOG_FILE="/var/log/repo-sync.log"
export GIT_SSH_COMMAND="ssh -i /root/.ssh/github_deploy -o StrictHostKeyChecking=accept-new"

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1" | tee -a "$LOG_FILE"; }

log "=== Monthly repo sync starting ==="

cd "$REPO_DIR"

# Pull latest from remote first
git pull --rebase origin main 2>/dev/null || true

CHANGES_LOG=""
track() { CHANGES_LOG="${CHANGES_LOG}\n- $1"; log "  $1"; }

# 1. Sync site profiles from deploy service
for profile in sinabarimd_com sinabari_net drsinabari_com sinabariplasticsurgery_com; do
  if curl -sf "$PROFILES_BASE/${profile}.yaml" -o "profiles/${profile}.yaml" 2>/dev/null; then
    track "Updated profiles/${profile}.yaml"
  fi
done

# 2. Sync deploy service
if [ -f /opt/openclaw-deployer/deploy_service.py ]; then
  cp /opt/openclaw-deployer/deploy_service.py deploy/deploy_service.py
  track "Synced deploy/deploy_service.py from live"
fi

# 3. Sync measurement script
if [ -f /opt/n8n-data/measure.py ]; then
  cp /opt/n8n-data/measure.py measurement/measure.py
  track "Synced measurement/measure.py from live"
fi

# 4. Sync text extraction service
if [ -f /usr/local/bin/extract_server.py ]; then
  mkdir -p services
  cp /usr/local/bin/extract_server.py services/extract_server.py
  track "Synced services/extract_server.py from live"
fi

# 5. Sync QA checks - extract from all three QA levels
curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE/api/v1/workflows/HL9utsXpnzmqxvkL" 2>/dev/null | \
  python3 -c "
import json, sys
wf = json.load(sys.stdin)
for n in wf['nodes']:
    name = n.get('name','')
    code = n.get('parameters',{}).get('jsCode','')
    if 'Run Article Checks' in name and code:
        with open('qa/article_checks.js','w') as f: f.write(code)
    elif 'Run Domain Checks' in name and code:
        with open('qa/domain_checks.js','w') as f: f.write(code)
    elif 'Run Portfolio Checks' in name and code:
        with open('qa/portfolio_checks.js','w') as f: f.write(code)
" 2>/dev/null && track "Synced QA check code (article/domain/portfolio)" || true

# 6. Sync spotlight article
curl -sf "$N8N_BASE/webhook/spotlight" 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
sp = d.get('spotlight')
if sp and sp.get('article_html'):
    slug = sp.get('slug','spotlight')
    with open(f'article/{slug}.html','w') as f: f.write(sp['article_html'])
    sys.stderr.write(f'Synced spotlight: {slug}\n')
# Also sync historical spotlight articles
for h in d.get('history', []):
    if h.get('article_html') and h.get('slug'):
        with open(f'article/{h[\"slug\"]}.html','w') as f: f.write(h['article_html'])
        sys.stderr.write(f'Synced historical spotlight: {h[\"slug\"]}\n')
" 2>&1 | while read line; do track "$line"; done || true

# 7. Sync schema files from live sites
for domain in sinabarimd.com sinabari.net drsinabari.com sinabariplasticsurgery.com; do
  curl -sf "https://$domain/" 2>/dev/null | python3 -c "
import sys, re, json
html = sys.stdin.read()
m = re.search(r'type=\"application/ld\+json\"[^>]*>([\s\S]*?)</script>', html)
if m:
    parsed = json.loads(m.group(1))
    fname = '${domain}'.replace('.','_')
    with open(f'schema/live_{fname}.json','w') as f:
        json.dump(parsed, f, indent=2)
    print(f'Synced schema/live_{fname}.json')
" 2>/dev/null | while read line; do track "$line"; done || true
done

# 8. Generate version and changelog
VERSION=$(date +%Y.%m)
MONTH_LABEL=$(date +"%B %Y")
ADDED=$(git status --porcelain | grep '^?' | wc -l | tr -d ' ')
MODIFIED=$(git status --porcelain | grep '^ M\|^M' | wc -l | tr -d ' ')
DELETED=$(git status --porcelain | grep '^ D\|^D' | wc -l | tr -d ' ')

# Only proceed if there are actual changes
if [ -z "$(git status --porcelain)" ]; then
  log "  no changes detected, skipping push"
  log "=== Monthly repo sync complete (no changes) ==="
  exit 0
fi

# Build detailed changelog entry
ENTRY="## v${VERSION} - ${MONTH_LABEL}\n\n"
ENTRY+="Auto-synced from live system on $(date -u +%Y-%m-%d).\n\n"
ENTRY+="### Changes\n"
if [ -n "$CHANGES_LOG" ]; then
  ENTRY+="$CHANGES_LOG\n"
fi
ENTRY+="\n### Stats\n"
if [ "$ADDED" -gt 0 ]; then ENTRY+="- ${ADDED} new file(s)\n"; fi
if [ "$MODIFIED" -gt 0 ]; then ENTRY+="- ${MODIFIED} modified file(s)\n"; fi
if [ "$DELETED" -gt 0 ]; then ENTRY+="- ${DELETED} removed file(s)\n"; fi
ENTRY+="\n---\n\n"

# Initialize CHANGELOG.md if needed
if [ ! -f CHANGELOG.md ]; then
  echo "# Changelog" > CHANGELOG.md
  echo "" >> CHANGELOG.md
fi

# Prepend entry to changelog (after header)
python3 -c "
entry = '''$ENTRY'''
with open('CHANGELOG.md') as f: content = f.read()
header = '# Changelog\n\n'
rest = content[len(header):] if content.startswith(header) else content
with open('CHANGELOG.md','w') as f: f.write(header + entry + rest)
"

# Commit and push
git add -A
git commit -m "v${VERSION}: monthly sync from live system

Auto-generated on $(date -u +%Y-%m-%d) by monthly-sync.sh
${ADDED} new, ${MODIFIED} modified, ${DELETED} removed files"

git push origin main
log "  pushed v${VERSION} to GitHub"
log "=== Monthly repo sync complete ==="
