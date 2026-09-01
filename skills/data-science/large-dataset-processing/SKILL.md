---
name: large-dataset-processing
description: "Use when processing multi-GB datasets in constrained envs."
version: 1.0.1
author: Hermes Agent
license: MIT
---

# Large Dataset Processing (constrained RAM/volume)

## When to Use

Any dataset file (CSV/Parquet/JSONL) plausibly larger than available RAM (>200MB in the Railway env), any Kaggle/HuggingFace download, or any bulk filtering/transformation of the PS3 game data.

For Railway Hermes deploys: RAM cgroup limit ~1GB (check `/sys/fs/cgroup/memory.max`), persistent volume ~434MB, overlay `/` and `/tmp` ~1TB free. 48 CPUs. This environment shaped the validated patterns below.

## Golden flow (validated: 899,585-row / 2GB CSV → filtered JSON in ~46s)

1. **Download to `/tmp`, never `/data`** — raw datasets never touch the small volume. `kagglehub` downloads public datasets anonymously: `export KAGGLEHUB_CACHE=/tmp/kagglehub; kagglehub.dataset_download('<owner>/<slug>')` (~45MB/s observed).
2. **Filter streaming, row by row** — `csv.DictReader` over the file handle keeps memory flat regardless of file size. Write matches out incrementally (JSON array assembled with comma joins) — never accumulate all matches in RAM if they can be large.
3. **Only the small result moves to `/data`** (this case: 3209 rows = 13.4MB).
4. **Validate before replacing anything**: reload output, check every row's key-set equals the header, check the filter predicate holds for every row, report counts.

## Pitfalls (each one actually fired)

- **pyarrow/pandas full-file or wide-column reads OOM (exit 137)** at the 1GB cgroup even with `iter_batches` — batch iteration only helped when `columns=[...]` was narrowly selected; wide rows with a big text column (`description`) blew it. The row-streaming CSV path is the reliable one here. Metadata-only reads (`num_rows`, `schema_arrow.names`) are always safe.
- **`_csv.Error: field larger than field limit (131072)`** on rows with huge text fields → `csv.field_size_limit(sys.maxsize)` before reading. Bigger field limit = more memory per bad row; acceptable because rows are dropped/streamed, not accumulated.
- **Counting a filtered subset first** (cheap single-column pass) gives the user the expected result size and a sanity check before the full multi-column pass.
- Run long passes with `terminal(background=true, notify_on_complete=true)` + `process wait` — a 2GB pass exceeds the foreground comfort window.

## Verifying dataset identity (user will challenge you)

When a user doubts you downloaded the "right" dataset (mirror-size doubts etc.): compare **evidence**, not assurances — exact file names + byte sizes from the download dir against the Kaggle page, row count, and full column list. `web_extract` on the Kaggle URL may hit reCAPTCHA; retrying with `?r=1` or a web search of the dataset name usually surfaces the same spec table. Present the mapping as a table (page value vs downloaded value).

## Interaction rules for THIS user (S)

- Before any destructive replacement of a data file, show the **complete field list** (all columns, numbered, with a one-line description) and get explicit go-ahead.
- Old data file versions stay recoverable via git history — replace via commit, never delete outright.
- Do NOT touch downstream consumer apps (e.g. the PS3 HTML viewer) to match a new schema unless the user asks. State the incompatibility once, then stop.
- If the user says "صبر کن" / "stop" — halt immediately, summarize exactly what state things are in (what ran, what's written where, what was NOT touched), and wait.
