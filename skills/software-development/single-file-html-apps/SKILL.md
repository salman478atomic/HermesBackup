---
name: single-file-html-apps
description: Verify or fix single-file HTML/JS apps without a browser.
---

Maintain durable single-file HTML apps (the kind a user re-sends as new versions over time). Covers verification without a browser, safe editing, common fix classes, and delivery. Session-specific app details live in `references/`.

## Verify without a browser (the rig)

1. Extract script blocks: `re.findall(r'<script>(.*?)</script>', src, re.DOTALL)` → `block0.js…blockN.js`.
2. Syntax: `node --check` each block.
3. Runtime: load blocks with **`vm.runInThisContext(code.join("\n"), {filename:"app.js"})`** plus DOM stubs (copy `templates/node-test-harness.js`). Pitfall: `eval` of blocks starting with `"use strict"` does NOT leak top-level `function` declarations into scope — every call fails with `X is not defined`. `vm.runInThisContext` does leak them. This is the #1 time-sink; use the template.
4. Static sanity: duplicate `id=` attributes; every `$("id")` referenced in JS exists in HTML; every `onclick="fn(` has a defined `fn`; tag balance (open vs close counts per tag); JS-emitted class names have CSS rules; preserve structural invariants the design depends on (e.g. exactly one `<style>` block).
5. Re-run the FULL suite after every patch round, not only new tests.

## Safe editing rhythm

- One atomic patch per concern. After each structural patch, re-grep every touched anchor — an insertion whose old_string spans an anchor line can silently delete the following line (a `.dots{...}` rule was lost and restored this way in v2.2.0; caught only by re-grepping).
- Never trust a diff from memory: after edits, re-extract blocks and re-run `node --check` + tests.
- **Version bumps drift:** across long sessions / model switches, the version constant you think you bumped can silently stay the old one (it stayed "2.5.3" through two bump attempts). Before bumping, grep the current value; after bumping, assert the new string exists in the file.
- Regex built from a variable inside a JS string that lives inside a Python-edited file: backslash escaping across the three layers produced `\\\\` garbage TWICE. Write backslash-free patterns (`s.match(new RegExp(key + '[^0-9]*([0-9.]+)'))`), then print the exact file bytes after patching to confirm what actually landed.
- If the app mirrors a Python converter pipeline: build a fixture from converter output, run it through the JS adapter, diff field-by-field (normalize `undefined`→`null`, compare via `String()`), and report "N rows × M fields, 0 mismatches". Re-check idempotency (run the adapter on its own output; expect byte-identical records).
- **Minified/compressed CSS:** When patch fails repeatedly with "Could not find a match" and the file was last read with offset/limit pagination, the CSS is likely minified (no whitespace, selectors run together). Read the FULL file with execute_code, apply all changes via regex in a single Python pass, then write_file. Do NOT attempt incremental patch calls on minified CSS — you will loop.

## Horizontal-overflow fix class (card/list UIs)

"Page grows sideways / must scroll left-right" ⇒ an unbreakable string escapes a flex/grid chain:

- Add `min-width:0` on EVERY flex/grid child down the chain (row → content column → sub-line → chips).
- Replace `white-space:nowrap` on text slots (developer names, URLs, titles) with wrap + line-clamp. Provide utilities: `.clamp1/.clamp2 { display:-webkit-box; -webkit-line-clamp:N; -webkit-box-orient:vertical; overflow:hidden; overflow-wrap:anywhere; word-break:break-word }`.
- Guard the base: `html,body{max-width:100%;overflow-x:hidden}`; contain table scrolls inside their wrapper (wrapper `max-width:100%` + inner `overflow-x:auto`).
- Clamp generated-art text too (hero cards, cover art) — real data always contains a pathological value.

## Bottom-sheet modal class (mobile web)

The "modal scroll janky / browser refreshes when pulling" report is a fix class, not a one-off:

- **Kill pull-to-refresh:** `overscroll-behavior:contain` on the sheet PLUS lock the body while open (`body.sheet-open{overflow:hidden}` added on open, removed on close). Without the body lock, Chrome fires refresh even with overscroll-behavior set.
- **Smooth drag-close recipe:** on `touchstart` record Y only when `scrollTop<=0`; on `touchmove` direction-lock (engage only if |dy|>10 AND |dy|>|dx|*1.4, otherwise release — horizontal scroll stays native); set `transition:none` during drag for 1:1 finger tracking; rubber-band upward pushes (dy/4); on `touchend` close if dy>120px OR velocity>0.55px/ms (flick), else restore transition and spring back. The 1:1 tracking (transition cut) is what makes it feel native — a transitioned transform fights the finger.

## Adding features: mine the data first

Standing user directive: use the FULL database potential — before building anything, dump raw-record fields with counts of non-empty values, then surface the untouched high-value ones (image lists, store lists, community counters, aliases, genre/tag gems). Prefer `_raw` passthrough fields over schema changes. Parsers must be empty/garbage-safe and deduplicated. Fix fixed line-order issues while there: give metadata slots a mandated, consistent order across ALL views.

## Visual design pass class ("make it look better" iterations)

The user iterates on look-and-feel across sessions. These critiques repeat — treat each as a fix class:

- **Image cropping — DIAGNOSE FIRST:** fetch a few actual image URLs and check real dimensions before touching frames. The PS3 case: media was LANDSCAPE (16:9), frames were portrait (3/4) with `object-fit:cover` ⇒ heads/feet cut no matter the height. Three rounds of height raises never fixed an aspect mismatch; matching frame aspect to media aspect (16/9 tiles, wide list thumbs) or `object-fit:contain` on a neutral card fixed it in one pass. Garbage values are broken media too: validate image URLs start with `http` (449 dataset rows carried the literal string "nan") and wire `onerror`→placeholder so a dead URL never renders a broken-image icon.
- **Don't redesign during a bug fix:** when the report is functional ("images cut", "tap doesn't open"), fix exactly that — the user explicitly corrected "I didn't say redesign, I said fix it" and "don't change what's already correct". Leave accepted areas untouched and re-verify them after unrelated edits.
- **Partial accent/outline treatments — confirm geometry BEFORE coding:** a vague "use the theme color on part of each card, keep it consistent" went through FIVE blind iterations (full top bars → "amateur"; single tiny corner bracket → "think outside the box"; HUD L-corners → rejected; horizontal fading top/bottom lines → "I meant the left SIDE"; plain vertical left lines → "from the left-edge middle to the top/bottom-edge middle"). Mirror the user's spatial words literally, and when the geometry is ambiguous, ask or offer 2-3 named options first — each blind guess cost a full version and eroded trust. CSS trick that landed it: one pseudo-element draws the whole L via two stacked `no-repeat` gradients (horizontal 2px bar + vertical 2px bar) sized to half the card.
- **No ring/donut indicators without asking:** sentiment donut rings were rejected outright ("I don't want circles"). Flat color boxes — background/border tinted by the metric color via a `--sc` custom property + `color-mix(in srgb, var(--sc) 10%, transparent)` — read better and were accepted.
- **Inventory existing accents before adding new ones:** the description block already carried a copper border-left; a blanket accent pass doubled it. Grep the palette's usage first, exempt elements that already have an accent, and apply any shared card treatment as ONE grouped CSS block over a shared selector list (row, gcard, gtile, bento .b, kv, …) so all card types stay consistent.
- **No uninvited layers on media:** a blurred duplicate of the image behind a contained hero read as "a second photo behind the modal" even at blur(16px) — user had the layer removed entirely. Controls (close buttons) don't belong ON the image either; put them in a bar above the card.
- **Deduplicate info before delivery:** the same score shown as a title badge AND a stat card was flagged on a screenshot ("see the duplicate elements?"). One fact, one home.
- **"Year X is missing" on charts:** sampling/step filters that drop intermediate bars read as bugs to users. Render EVERY category; stagger dense labels (`.x:nth-child(odd){transform:translateY(9px)}`), style zero-values as dim stubs instead of hiding them. The filter (JS) and the label stagger (CSS) live in different places — when a user reports missing items, check BOTH.
- **"Sections don't look separate":** plain divider rows read as one blob. Cardify list rows (surface + border + radius), put an accent tick/border on section and chart headers (`::before` accent bar), and give every card a hover state (accent ring + slight lift) so each box has identity.
- **"Theme color isn't defining":** if the accent appears in only a few spots, the user is right. Blanket pass: nav active tab (accent pill + glow), focus rings, header ticks, hover tints on chips/buttons/rows, chart gradients. The accent should be touchable in every view.
- **Icons:** same glyph for different actions or ambiguous glyphs get flagged. Give each semantic action a concrete icon (heart=played, gamepad=playing, bookmark=will-play; star for score chips; storefront for stores; per-metric icon map in stat grids).
- **Score colors must be semantic:** accent-shaded scales read as decoration. Use a real scale (green→lime→yellow→orange→red = great→poor).
- When the user says "you didn't try hard enough", do a full-pass pass (heights + color + icons + chart truth + separation in ONE version), not spot fixes.

## Delivery protocol

1. Bump the app's version constant.
2. Commit with a factual message; push (NEVER force-push; never delete pre-existing repo files).
3. `cp` the final file to `/tmp` with the version in the filename; send it as `MEDIA:/tmp/...` in the SAME response as a plain-language changelog — the user is a non-coder: what changed in everyday words, no CSS/JS jargon, and state explicitly that their data/settings survive.
4. Before delivering, grep the app for embedded secrets (API tokens in JS constants). If found, warn the user in plain words in the delivery message and recommend a scoped/limited token — do not print the secret itself.
5. Keep the user's design constraints sacred (palette, single style block, layout language). Fix behavior; do not redesign.
