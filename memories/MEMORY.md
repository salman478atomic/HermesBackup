GitHub HermesBackup repository: https://github.com/salman478atomic/HermesBackup — Personal access token (PAT) stored in memory under "GitHub Hermes Backup PAT".
§
User preference: Never stop after writing ":". Always continue the task without waiting for "continue". Complete the full action in one response without pausing.
§
Critical rule: NEVER stop mid-response. Always complete the full task, all tool calls, and final answer in ONE response. Do NOT end with a colon or short phrase that requires user to say "continue". This is the user's biggest frustration.
§
User is "S" — communicates in Farsi (Persian). Respond in Farsi by default. NEVER use Chinese or any language other than Farsi and English.
§
Critical preference: NEVER stop mid-response after a colon or short phrase. Always complete the full task, all tool calls, and final answer in ONE response. This is the user's biggest frustration from past sessions.
§
Backup repo: https://github.com/salman478atomic/HermesBackup (private). GitHub PAT for it: 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 (label: GitHub Hermes Backup PAT). Backup cadence: every 12 hours via cron job. Backup script at ~/.hermes/scripts/hermes_backup.sh.
§
User runs Hermes on Railway (9router → Telegram bot). Railway trial expired ~Aug 2026 and wiped all data — that's why GitHub backups exist. On fresh deploy: restore memories/skills/session history from backup repo, then re-create the 12h backup cron.
§
User's PS3 game library project: ps3_games.json (1932 records) + ps3-game-library.html live in the backup repo root. LESSON from past session: a `git push -f` destroyed these files once (recovered from logs). Backup must NEVER force-push and NEVER delete pre-existing repo files.
§
Old chat history (139 messages, session id restored_20260827_092929) was imported into live state.db and is searchable via session_search.