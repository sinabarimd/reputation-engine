#!/bin/bash
# Monthly GitHub sync script for Reputation Engine
# Runs on the 1st of each month via cron
# Pulls live system state, updates repo, commits with changelog, pushes
set -e

REPO_DIR="/opt/reputation-engine-repo"
N8N_BASE="https://n8n.sinabarimd.com"
PROFILES_BASE="http://localhost:9911/profiles"
LOG_FILE="/var/log/repo-sync.log"

log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1" | tee -a "$LOG_FILE"; }

log "=== Monthly repo sync starting ==="

cd "$REPO_DIR"

# Pull latest from remote first
git pull --rebase origin main 2>/dev/null || true

# 1. Sync site profiles from deploy service
for profile in sinabarimd_com sinabari_net drsinabari_com sinabariplasticsurgery_com; do
  curl -sf "$PROFILES_BASE/${profile}.yaml" -o "profiles/${profile}.yaml" 2>/dev/null && log "  synced profiles/${profile}.yaml" || true
done

# 2. Sync deploy service
cp /usr/local/bin/rt_service.py deploy/ 2>/dev/null || true
if [ -f /opt/openclaw-deployer/deploy_service.py ]; then
  cp /opt/openclaw-deployer/deploy_service.py deploy/deploy_service.py
  log "  synced deploy/deploy_service.py"
fi

# 3. Sync measurement script
if [ -f /opt/n8n-data/measure.py ]; then
  cp /opt/n8n-data/measure.py measurement/measure.py
  log "  synced measurement/measure.py"
fi

# 4. Sync QA checks from SEO QA Agent workflow
curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE/api/v1/workflows/HL9utsXpnzmqxvkL" 2>/dev/null | \
  python3 -c "
import json, sys
wf = json.load(sys.stdin)
for n in wf['nodes']:
    code = n.get('parameters',{}).get('jsCode','')
    if 'article-level checks' in code.lower() or 'articleChecks' in code:
        with open('qa/qa_checks.js','w') as f: f.write(code)
        break
" 2>/dev/null && log "  synced qa/qa_checks.js" || true

# 5. Sync spotlight article if it exists
curl -sf "$N8N_BASE/webhook/spotlight" 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
sp = d.get('spotlight')
if sp and sp.get('article_html'):
    slug = sp.get('slug','spotlight')
    with open(f'article/{slug}.html','w') as f: f.write(sp['article_html'])
    print(f'  synced article/{slug}.html')
" 2>/dev/null || true

# 6. Generate version/changelog entry
VERSION=$(date +%Y.%m)
MONTH_LABEL=$(date +"%B %Y")
CHANGES=$(git diff --stat HEAD 2>/dev/null || echo "initial sync")
ADDED=$(git status --porcelain | grep '^?' | wc -l | tr -d ' ')
MODIFIED=$(git status --porcelain | grep '^ M\|^M' | wc -l | tr -d ' ')

# Append to CHANGELOG.md
if [ ! -f CHANGELOG.md ]; then
  echo "# Changelog" > CHANGELOG.md
  echo "" >> CHANGELOG.md
fi

# Only add entry if there are changes
if [ -n "$(git status --porcelain)" ]; then
  ENTRY="## v${VERSION} - ${MONTH_LABEL}\n\n"
  ENTRY+="Auto-synced from live system on $(date -u +%Y-%m-%d).\n\n"
  if [ "$ADDED" -gt 0 ]; then ENTRY+="- ${ADDED} new file(s)\n"; fi
  if [ "$MODIFIED" -gt 0 ]; then ENTRY+="- ${MODIFIED} modified file(s)\n"; fi
  ENTRY+="\n---\n\n"

  # Prepend to changelog (after header)
  python3 -c "
import sys
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
${ADDED} new, ${MODIFIED} modified files"

  git push origin main
  log "  pushed v${VERSION} to GitHub"
else
  log "  no changes detected, skipping push"
fi

log "=== Monthly repo sync complete ==="
