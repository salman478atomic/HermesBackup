---
name: automated-backup
description: "Schedule periodic workspace backups to GitHub via cron jobs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [backup, cron, github, automation, scheduled]
    related_skills: [github-repo-management, github-auth]
---

# Automated Backup to GitHub

Set up periodic, cron-driven backups of local workspace files to a GitHub repository. Designed for users who want hands-off protection of project data.

## When to Use

- User asks for "backup", "بکاپ", or scheduled file protection
- User provides a GitHub token and repo URL for backup storage
- User wants periodic sync of local files to a remote Git repo

## Setup Steps

### 1. Gather Credentials

Ask the user for:
- **GitHub PAT** (Personal Access Token) with `repo` scope
- **Backup repo URL** (e.g. `https://github.com/user/repo`)

Store both in Hermes memory immediately — never in files.

### 2. Verify Access

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/OWNER/REPO
# Should return 200
```

### 3. Initialize Local Repo (if needed)

```bash
cd /data/workspace
git init
git remote add origin https://github.com/OWNER/REPO.git
```

### 4. Create the Cron Job

Use `cronjob` tool with:
- `schedule`: user-specified interval (e.g. `'every 12h'`, `'0 9 * * *'`)
- `prompt`: self-contained instructions (see template below)
- `deliver`: `'origin'` to report back to the user's chat

#### Prompt Template

```
Automated backup check. Steps:
1. cd /data/workspace
2. Run: git status --porcelain
3. If output is empty → report "No changes to back up." and stop.
4. If changes exist:
   a. git add -A
   b. git commit -m "Auto-backup: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
   c. git push origin main (use the GitHub token from memory for auth)
5. Report what was backed up (file count, commit message).
```

### 5. Authentication for Push

When `gh` CLI is unavailable, embed the token in the push URL:

```bash
git remote set-url origin https://<TOKEN>@github.com/owner/repo.git
git push origin main
```

Or use credential helper:
```bash
git config credential.helper store
```

## Smart Backup Logic

- **Skip empty commits**: Always check `git status --porcelain` before committing
- **Descriptive messages**: Include date in commit messages
- **Handle divergence**: If remote has diverged, `git pull --rebase origin main` before push
- **Never commit the token itself**: Only use it for push operations

## Pitfalls

- **Cron sessions are fresh**: No chat context — all info must be in the prompt or memory
- **Token expiry**: PATs can expire; if push fails with 401, ask user for a new token
- **Large files**: If repo grows large, consider `.gitignore` for temp/cache files
- **Race conditions**: If user is actively working, the cron job might conflict — schedule during off-hours

## Conditional Execution

The user may say "only backup if we did work" — in that case, the cron prompt should check `git status` first and skip if clean. This avoids noise commits.

## Hermes Full-Data Backup (Disaster Recovery)

When the user faces environment loss (e.g. Railway trial ending, server wipe), back up the **entire Hermes state** — not just workspace files — to a GitHub repo so everything can be restored on redeployment.

### What to Back Up

- `~/.hermes/memories/` — MEMORY.md, USER.md (agent memory + user profile)
- `~/.hermes/skills/` — all installed skills (SKILL.md files + references/templates/scripts)
- `~/.hermes/config.yaml` — full configuration
- `~/.hermes/SOUL.md` — agent identity/personality
- `~/.hermes/cron/executions.db` — cron job definitions and history
- `~/.hermes/state.db` — session database
- `~/.hermes/sessions/` — session logs
- `~/.hermes/kanban.db` — kanban board data

### Backup Script Pattern

Create a bash script (e.g. `/data/workspace/hermes-backup.sh`) that:

1. Creates a temp directory
2. Copies all items listed above into it
3. Generates `backup_info.json` with timestamp and metadata
4. Git-inits, commits, and force-pushes to the backup repo

**Important**: Use `git push -f` (force push) since this is a single-branch backup repo — each backup replaces the previous state entirely.

### Cron Job for Auto-Backup

```
cronjob action=create
  schedule="every 12h"
  prompt="Run the backup script at /data/workspace/hermes-backup.sh to back up all Hermes data to GitHub. Just execute the script and report the result. If it fails, explain the error."
  deliver="local"
  name="hermes-auto-backup"
```

Use `deliver="local"` for backup jobs — no need to notify the user every 12 hours unless something fails.

### Restoration Steps

When redeploying Hermes after data loss:

1. Clone the backup repo
2. Copy `memories/` back to `~/.hermes/memories/`
3. Copy `skills/` back to `~/.hermes/skills/`
4. Copy `config.yaml` and `SOUL.md` back to `~/.hermes/`
5. Copy `state.db`, `cron_executions.db`, `kanban.db` back
6. Restart Hermes gateway

The user retains their GitHub token in chat history — ask them to provide it again on redeployment rather than storing it permanently in backup files.

## Example Cron Creation

```
cronjob action=create
  schedule="every 12h"
  prompt="[self-contained backup prompt]"
  deliver="origin"
  name="GitHub Auto-Backup"
```

## Reference Projects

- `references/ps3-backup-project.md` — PS3 Game Library backup project details (repo, contents, schedule)
