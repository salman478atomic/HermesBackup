# HermesBackup Repository — Disaster Recovery Backup

## Repository

- **URL**: `https://github.com/salman478atomic/HermesBackup`
- **Owner**: salman478atomic
- **Auth**: GitHub PAT stored in Hermes memory under "GitHub Hermes Backup PAT"

## Current Contents (as of 2026-08-27)

### Original PS3 Project Files
- `ps3_games.json` — Full PS3 game database (~1.9MB, hundreds of entries)
- `ps3-game-library.html` — Web frontend with 10 dark themes

### Hermes Full-Data Backup
- `memories/` — MEMORY.md, USER.md
- `skills/` — All installed skills (500+ files across 14 categories)
- `config.yaml` — Hermes configuration
- `SOUL.md` — Agent identity
- `cron_executions.db` — Cron job database
- `state.db` — Session database
- `sessions/` — Session logs
- `kanban.db` — Kanban board
- `backup_info.json` — Backup metadata (timestamp, hostname, items list)

## Backup Schedule

- Cron job `hermes-auto-backup` (job_id: 8930eb520c07) runs every 12 hours
- Uses force-push to single `main` branch
- Script: `/data/workspace/hermes-backup.sh`

## Context

- User's Railway trial expires in ~1 month — all data will be wiped
- This backup ensures full Hermes state can be restored on redeployment
- User communicates in Farsi (Persian), prefers responses in Farsi
