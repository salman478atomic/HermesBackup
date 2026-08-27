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
