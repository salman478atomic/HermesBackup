# PS3 Game Library Backup Project

## Repository

- **URL**: `https://github.com/salman478atomic/HermesBackup`
- **Owner**: salman478atomic
- **Contents**:
  - `ps3_games.json` — Full PS3 game database (title, genres, developer, publisher, platforms, year, playtime, tags, description, metacritic scores, user scores, content rating, player counts, series)
  - `ps3-game-library.html` — Web frontend with 10 dark themes (Midnight, Ocean, Aurora, Sunset, Forest, Grape, Amber, Crimson, Cyber, Nord) for browsing the game database

## Backup Schedule

- User requested: every 12 hours, but only if changes were made (no empty commits)
- Credential: GitHub PAT stored in Hermes memory under "GitHub Hermes Backup PAT"

## Notes

- The JSON file is large (~1.9MB) — contains hundreds of PS3 game entries
- The HTML file is a single-page app with embedded CSS/JS, no build step needed
