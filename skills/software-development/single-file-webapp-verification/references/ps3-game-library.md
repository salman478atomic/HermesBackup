# PS3 Game Library app — concrete instance

Single-file app verified/iterated with this skill's workflow.

- **File:** `ps3-game-library.html` — repo copy at `/data/workspace/HermesBackup/` (pushed to GitHub `salman478atomic/HermesBackup`). User's copy arrives via Telegram → `/data/.hermes/cache/documents/`.
- **Data:** `ps3_games.json` — 3209 RAWG rows; all 54 raw fields kept verbatim in `_raw`; app-schema fields normalized by `rawgAdapter`.
- **Adapter runs on BOTH load paths** (remote fetch + IndexedDB cache), is idempotent, dedupes by `title|released|_raw.id`, and flags records with `_adapter: 2`.
- **Key mappings:** `rating`(1–5) → `user_score` 0–100 (clamp 100), `metacritic` → `critic_score`, pipe-joined → comma-joined, `esrb_rating` JSON → short code (M/T/E…), `ratings` JSON → top-segment sentiment, `parents_count`/DLC-name-pattern → `is_dlc`, `tba` → year "TBA".
- **Converter:** `~/.hermes/scripts/rawg_to_app.py` — reads `/tmp/ps3_full.json` → repo `ps3_games.json`; asserts 3209 rows and the exact 54-field `_raw` set.
- **Data fetch:** GitHub contents API with an in-file token; private repo, HTTP 200 verified.

## Version history
- v1.0.0 — base app
- v2.0.0 — RAWG data layer, adapter on both paths, real cover art
- v2.1.0 — Namida-UI merge (AMOLED black + copper #E87B0A, exactly 1 style block)
- v2.1.1 — added missing chart CSS (`.bands/.donut/.donutrow/.legend/.lol`) inherited unstyled from v1.0.0
- v2.2.0 — overflow clamps (clamp1/clamp2, min-width:0 chains), themes fully removed, modal extras: screenshots strip, store chips, per-metric community grid, alt names
- v2.2.1 — `.mdev{flex-basis:100%}`: developer always on its own row (user caught short-name edge case on screenshot)
- v2.3.0 — design pass: hero 244px / card 210px / grid 4:5 / modal hero 236px / thumbs 74px / shots 116px; semantic score colors (green→red); accent-glow active controls; heart/gamepad/bookmark status icons; star rating chip; storefront icon; per-metric community icons; gapless Releases-by-Year (zero-fill + peak-year subtitle); NEW charts: Community Status (`added_by_status` totals) + Playtime Profile (hour buckets)

## Data quirks
- Developer strings up to 1192 chars (mobile-garbage aggregates) — must clamp.
- 2760/3209 rows have `short_screenshots` (pipe-separated `{id, image: url}` — parse with `parsePipeImages`).
- `added_by_status` is a JSON-ish string; JS parses with `new RegExp(key + '[^0-9]*([0-9.]+)')` — totals cross-checked identical vs Python on a 100-row sample.
- Some rows' `ratings` lack a wrapper key the tests originally assumed — fixtures must use the real converter format.

## Test rig
`/tmp/ps3check/` (rebuild after any edit — /tmp is ephemeral):
- `test.js` — 37 core checks (adapter mapping/clamps/idempotency, sortList missing-last, matches() filters, coverFor, band math, labels)
- `modal_test.js` — 8 checks (parsePipeImages, subLine ordering with flex order, openGame no-throw on full record)
- `status_test.js` — added_by_status sums vs Python cross-check
