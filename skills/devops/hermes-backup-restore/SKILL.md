---
name: hermes-backup-restore
description: "Use when a fresh Hermes deploy needs restoring from backup."
version: 1.0.0
---

# Restore Hermes from GitHub HermesBackup

Repo: https://github.com/salman478atomic/HermesBackup (private). PAT is in memory under "GitHub Hermes Backup PAT".

## 1. Clone

```bash
git clone https://<PAT>@github.com/salman478atomic/HermesBackup.git /data/workspace/HermesBackup
```

Repo root contains: `memories/`, `skills/`, `sessions/`, `logs/`, `scripts_backup/`, `config.yaml`, `SOUL.md`, `.env`, `channel_directory.json`, `state.db`, `kanban.db`, `cron_executions.db`, `backup_info.json`, plus user files that must NEVER be deleted: `ps3_games.json` (1932 records), `ps3-game-library.html`.

## 2. Restore order

1. **Memories** — copy `memories/MEMORY.md` + `USER.md` into `$HERMES_HOME/memories/`. WARNING: if the live session already wrote memory entries, copying overwrites them — re-add live-session entries to the memory tool afterwards (merge, don't lose).
2. **Skills** — `diff <(ls repo/skills) <(ls $HERMES_HOME/skills)`; only copy if different.
3. **Old chat history** — do NOT swap state.db (live session is in it). Import instead:
   - Open old repo `state.db` + live `$HERMES_HOME/state.db` with two sqlite3 connections.
   - Insert old `sessions` row under id `restored_<old_id>` (set `ended_at`).
   - Insert old `messages` rows WITHOUT the `id` column (auto-assign; explicit ids collide with live rows → UNIQUE error). Change `session_id` to the new restored id.
   - FTS triggers fill automatically. Verify: `SELECT COUNT(*) FROM messages_fts WHERE messages_fts MATCH 'ps3'`.
4. `.env` / `config.yaml` — usually pre-provisioned by Railway entrypoint; only diff-and-merge, never blind-copy over live.

## 3. Re-arm the 12h backup cron

Script lives at `~/.hermes/scripts/hermes_backup.sh` (also in repo `scripts_backup/`). If missing, restore it from the repo first, `chmod +x`.

```
cronjob create:
  name: Hermes GitHub Backup (12h)
  schedule: 0 */12 * * *
  script: hermes_backup.sh      # relative to ~/.hermes/scripts/ — filename only, NOT absolute path
  no_agent: true                # stdout delivered verbatim; empty = silent success
  deliver: telegram
```

## Hard rules (from past incident)

- Backup NEVER uses `git push -f`. A force-push once destroyed the PS3 files; they were only recoverable from logs.
- Backup NEVER deletes pre-existing repo files — add/update only; `git pull --rebase` before push.
- SQLite dbs must be snapshotted with the sqlite3 backup API (`.backup()` in Python), never raw-copied while the gateway is live.
- Cron `script` param must be a bare filename relative to `~/.hermes/scripts/` (absolute paths are rejected).

## Verify after restore

```bash
bash ~/.hermes/scripts/hermes_backup.sh; echo $?   # expect 0
cd /data/workspace/HermesBackup && git log --oneline -3 && ls ps3_games.json ps3-game-library.html
```
