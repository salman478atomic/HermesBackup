#!/bin/bash
# Hermes → GitHub auto-backup
# Rules (learned the hard way):
#   1. NEVER use `git push -f` (it once destroyed ps3 files in this repo)
#   2. NEVER delete pre-existing repo files — only add/update
#   3. Pull --rebase before push if remote moved ahead
# Silent on success (empty stdout = cron sends nothing); prints error on failure.

set -u

HERMES_HOME="${HERMES_HOME:-/data/.hermes}"
REPO_DIR="/data/workspace/HermesBackup"
REPO_URL_HOSTED="github.com/salman478atomic/HermesBackup.git"
PAT="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"
LOG="$HERMES_HOME/logs/backup.log"

fail() { echo "Backup FAILED: $1"; echo "[$(date -u +%FT%TZ)] FAILED: $1" >> "$LOG" 2>/dev/null; exit 1; }
log()  { echo "[$(date -u +%FT%TZ)] $1" >> "$LOG" 2>/dev/null; }

mkdir -p "$HERMES_HOME/logs"

# --- clone if missing ---
if [ ! -d "$REPO_DIR/.git" ]; then
    git clone "https://${PAT}@${REPO_URL_HOSTED}" "$REPO_DIR" >>"$LOG" 2>&1 || fail "clone failed"
fi
cd "$REPO_DIR" || fail "cd $REPO_DIR failed"

# identity + remote (idempotent)
git config user.email "hermes-backup@railway.local"
git config user.name "Hermes Backup"
git remote set-url origin "https://${PAT}@${REPO_URL_HOSTED}"

# --- consistent sqlite snapshots via backup API ---
snap() { # snap <src.db> <dest.db>
    python3 - "$1" "$2" <<'PYEOF'
import sqlite3, sys
src, dst = sys.argv[1], sys.argv[2]
s = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
d = sqlite3.connect(dst)
s.backup(d)
d.close(); s.close()
PYEOF
}

# --- copy everything ---
mkdir -p memories sessions logs
cp -f "$HERMES_HOME/memories/MEMORY.md" memories/ 2>/dev/null
cp -f "$HERMES_HOME/memories/USER.md" memories/ 2>/dev/null
cp -f "$HERMES_HOME/config.yaml" config.yaml
cp -f "$HERMES_HOME/SOUL.md" SOUL.md
cp -f "$HERMES_HOME/.env" .env
cp -f "$HERMES_HOME/channel_directory.json" channel_directory.json 2>/dev/null
cp -rf "$HERMES_HOME/sessions/." sessions/ 2>/dev/null
cp -rf "$HERMES_HOME/skills/." skills/ 2>/dev/null
cp -rf "$HERMES_HOME/logs/." logs/ 2>/dev/null
mkdir -p scripts_backup
cp -rf "$HERMES_HOME/scripts/." scripts_backup/ 2>/dev/null

snap "$HERMES_HOME/state.db" state.db            || fail "state.db snapshot"
snap "$HERMES_HOME/kanban.db" kanban.db          || fail "kanban.db snapshot"
snap "$HERMES_HOME/cron/executions.db" cron_executions.db || fail "executions.db snapshot"

cat > backup_info.json <<JSON
{
  "timestamp": "$(date -u +%FT%TZ)",
  "hostname": "$(hostname)",
  "hermes_version": "unknown",
  "backup_items": [
    "memories", "config.yaml", "SOUL.md", ".env", "channel_directory.json",
    "skills", "sessions", "logs", "state.db", "kanban.db", "cron_executions.db"
  ],
  "notes": "NO force-push policy; pre-existing files preserved."
}
JSON

# --- commit & push (NEVER force) ---
git add -A
if git diff --cached --quiet; then
    log "no changes to commit"
    exit 0
fi
git commit -m "Auto backup: $(date -u +%FT%TZ)" >>"$LOG" 2>&1 || fail "commit failed"

# sync with remote without force
git fetch origin >>"$LOG" 2>&1 || fail "fetch failed"
git pull --rebase origin main >>"$LOG" 2>&1 || fail "rebase against remote failed (remote: $(git log --oneline -1 origin/main 2>/dev/null))"

git push origin main >>"$LOG" 2>&1 || fail "push failed"
log "backup pushed OK"
exit 0
