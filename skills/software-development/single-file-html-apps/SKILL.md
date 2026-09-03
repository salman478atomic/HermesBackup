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
- Regex built from a variable inside a JS string that lives inside a Python-edited file: backslash escaping across the three layers produced `\\\\` garbage TWICE. Write backslash-free patterns (`s.match(new RegExp(key + '[^0-9]*([0-9.]+)'))`), then print the exact file bytes after patching to confirm what actually landed.
- If the app mirrors a Python converter pipeline: build a fixture from converter output, run it through the JS adapter, diff field-by-field (normalize `undefined`→`null`, compare via `String()`), and report "N rows × M fields, 0 mismatches". Re-check idempotency (run the adapter on its own output; expect byte-identical records).
- **Minified/compressed CSS:** When patch fails repeatedly with "Could not find a match" and the file was last read with offset/limit pagination, the CSS is likely minified (no whitespace, selectors run together). Read the FULL file with execute_code, apply all changes via regex in a single Python pass, then write_file. Do NOT attempt incremental patch calls on minified CSS — you will loop.

## Horizontal-overflow fix class (card/list UIs)

"Page grows sideways / must scroll left-right" ⇒ an unbreakable string escapes a flex/grid chain:

- Add `min-width:0` on EVERY flex/grid child down the chain (row → content column → sub-line → chips).
- Replace `white-space:nowrap` on text slots (developer names, URLs, titles) with wrap + line-clamp. Provide utilities: `.clamp1/.clamp2 { display:-webkit-box; -webkit-line-clamp:N; -webkit-box-orient:vertical; overflow:hidden; overflow-wrap:anywhere; word-break:break-word }`.
- Guard the base: `html,body{max-width:100%;overflow-x:hidden}`; contain table scrolls inside their wrapper (wrapper `max-width:100%` + inner `overflow-x:auto`).
- Clamp generated-art text too (hero cards, cover art) — real data always contains a pathological value.

## Adding features: mine the data first

Standing user directive: use the FULL database potential — before building anything, dump raw-record fields with counts of non-empty values, then surface the untouched high-value ones (image lists, store lists, community counters, aliases, genre/tag gems). Prefer `_raw` passthrough fields over schema changes. Parsers must be empty/garbage-safe and deduplicated. Fix fixed line-order issues while there: give metadata slots a mandated, consistent order across ALL views.

## Visual design pass class ("make it look better" iterations)

The user iterates on look-and-feel across sessions. These critiques repeat — treat each as a fix class:

- **Image cropping:** portrait/square media (game covers, screenshots) crops badly in landscape boxes. Raise heights generously on the FIRST pass (20–45%: e.g. card cover 158→210px, modal hero 172→236px, thumbs 64→74px, grid tiles 1:1→4:5). A timid bump guarantees a second request.
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
