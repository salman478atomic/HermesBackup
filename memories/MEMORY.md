User is "S" — communicates in Farsi (Persian). Respond in Farsi by default. NEVER use Chinese or any language other than Farsi and English.
§
Critical preference: NEVER stop mid-response after a colon or short phrase. Always complete the full task, all tool calls, and final answer in ONE response. This is the user's biggest frustration from past sessions.
§
Backup must NEVER force-push and NEVER delete pre-existing repo files.
§
User runs Hermes on Railway (9router → Telegram bot). Railway trial expired ~Aug 2026 and wiped all data — that's why GitHub backups exist. On fresh deploy: restore memories/skills/session history from backup repo, then re-create the 12h backup cron.
§
Volume-wipe incident: Kaggle download filled the Railway volume (agent misjudged space); user deleted volume → everything after Aug 27 backup lost. LESSON: check df -h before big downloads; /data volume is only ~434MB while / (overlay) has ~1TB — download/process in /tmp, keep only small results in /data.
§
PS3: db = 3209 RAWG games × 54 fields; app v2.5.3 = Namida-UI (AMOLED + copper #E87B0A, 1 style block) + RAWG layer (adapter both paths, user_score=rating/5×100). App arrives via Telegram → /data/.hermes/cache/documents/. Converter: ~/.hermes/scripts/rawg_to_app.py. Verified Sep 1: 37/37 + 8/8 + lightbox + imgfix tests green. v2.5.3 root-fix: 449 rows had literal "nan" background_image (pandas leak) → dataset rewritten to null + adapter/coverFor sanitize non-http both paths + img onerror→SVG fallback. Hero flex 2-col, modal contained, flick-close sheet, lightbox, gapless year chart. Rig: /tmp/ps3check/*.js.
§
Backup: 12h cron → ~/.hermes/scripts/hermes_backup.sh. K-Dense sci skills installed (4, at skills/science/): polars, EDA, database-lookup, scientific-visualization. Source: github.com/K-Dense-AI/scientific-agent-skills (163 skills, 30MB). Install more on demand — no full install (prompt bloat + 1GB RAM).
§
Standing directive from S: "همیشه بهترین راه رو انتخاب کن" — always pick the best/optimal approach (e.g. atomic multi-hunk patches over scattered edits, streaming over in-memory loads, selective skill installs). Don't over-ask; decide and execute.