---
name: single-file-webapp-verification
description: Use when a single-file HTML/JS app needs verification.
---

# Single-file WebApp Verification & Iteration

Workflow for apps that arrive as ONE .html file (inline CSS + several `<script>` blocks), typically delivered via Telegram (lands in `~/.hermes/cache/documents/doc_*.html`). The user cannot code — the agent owns verification, quality, and delivery.

## Workflow
1. **Locate & baseline:** pick the newest `doc_*.html` in `/data/.hermes/cache/documents/`. Compare its `APP_VERSION` with the copy in the project repo; if identical, edit the repo copy so history stays clean.
2. **Static pass:** extract `<script>` blocks (python `re.findall(r'<script>(.*?)</script>', src, re.DOTALL)`), then `node --check` each block.
3. **Structural pass (python):** duplicate `id=` attributes; every `$("id")` referenced in JS exists in HTML; every `onclick="fn(` names a defined function; tag balance (div/section/span/button/style/script); count `<style>` blocks — this project's standard is exactly 1.
4. **Runtime pass:** copy `templates/dom-stub-harness.js` to /tmp, extract blocks there, append app-specific tests. Load with `vm.runInThisContext`, NOT eval — the app starts with `"use strict"`, so top-level function declarations do not leak into global scope under indirect eval. Use REAL data fixtures sampled from the actual dataset, not invented records.
5. **Cross-language check:** when JS normalization must match a Python converter/ETL, run both on the same random-sample fixture and diff field-by-field; for counter sums parsed by regex in JS, cross-check totals against Python on the same rows.
6. **Design QA** — checklist below; the user reviews visually and catches what tests miss.
7. **Deliver:** bump `APP_VERSION` in the file, copy to `/tmp/<name>-v<ver>.html`, send with `MEDIA:` (the user opens the file directly — never just describe changes), then commit+push to the backup repo. NEVER force-push, NEVER delete pre-existing repo files.

## Design QA checklist (each item was a real user-caught bug)
- **Deterministic line placement:** any element that must sit on its own line needs `flex-basis:100%` — a short string will sneak onto the previous line otherwise (user caught dev name rendering on line 1 for short values only).
- **Clamp DB-generated strings:** `.clamp1/.clamp2` (`-webkit-line-clamp` + `overflow-wrap:anywhere`) — the DB contains 1192-char developer strings that blow out card width.
- **Kill horizontal page scroll:** `min-width:0` down the entire flex chain, `max-width:100%` on pill/stat rows, `html,body{overflow-x:hidden}`, and contain table scroll inside its wrapper.
- **Time-series charts:** zero-fill missing years/buckets or the bars "jump" (user caught).
- **Icons must match meaning** (heart=played, gamepad=playing, bookmark=wishlist, star=rating, storefront=stores); one generic icon for many metrics reads as lazy — map each metric to its own glyph.
- **Score colors must be semantic** (green=great → yellow → orange → red=poor), not shades of the accent color — users read them as quality levels.
- **Mine the unused fields:** after any feature pass, ask which dataset fields are still unused and surface them (screenshots, stores, counters, alt names) in modal/stats where they add value.
- After visual changes, re-run the FULL test suite and re-check that every JS-emitted class still has a CSS rule.

## Pitfalls
- The `patch` tool can delete a following line when the anchor sits directly above it (happened with a `.dots` CSS rule) — always read the returned diff and re-grep the surrounding rules after each patch.
- Don't hand-escape `new RegExp` built from data keys inside a patch payload; prefer minimal patterns like `key + '[^0-9]*([0-9.]+)'` and validate totals against Python.
- Test the negative paths: null/empty/"None"/garbage-string inputs to every parser, plus idempotency (run the adapter twice, expect byte-identical output).

## User context (S)
- No coding/UI knowledge: explain changes in plain Farsi with everyday analogies, no jargon; state what changed, what was verified, and exactly what to do with the file.
- Standing directive: pick the best approach and execute without over-asking.

## Support files
- `references/ps3-game-library.md` — the concrete app instance: schema, mappings, converter, version history, data quirks.
- `templates/dom-stub-harness.js` — Node starter rig (DOM stubs + block loader + PASS/FAIL reporter); copy to /tmp and append tests.
