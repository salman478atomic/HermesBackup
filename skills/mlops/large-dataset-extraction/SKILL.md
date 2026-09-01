---
name: large-dataset-extraction
description: "Use when a large dataset must be downloaded and filtered."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Large Dataset Extraction (download → filter → subset)

Pattern for pulling a multi-GB public dataset and extracting a small filtered subset without filling the disk or getting OOM-killed. Validated reference case: Kaggle RAWG games dataset (899,585 rows × 54 cols, 2GB CSV) → 3,209 PlayStation 3 rows in 46s. Session specifics: `references/rawg-ps3-extraction.md`.

## Workflow

1. **Check the budget before downloading anything**
   - `df -h` — distinguish the persistent volume (often tiny, e.g. ~434MB on Railway) from the overlay `/` (often TBs free). Download and process in `/tmp`; keep only the small result on the persistent volume. A previous agent filled the small volume with a 1.86GB download and the user lost the whole deployment.
   - `cat /sys/fs/cgroup/memory.max` — container RAM may be ~1GB even when the host has hundreds of GB. Exit code 137 = OOM kill; it can happen on a single "harmless" peek at wide columns.

2. **Download with kagglehub (no token needed for public datasets)**
   ```python
   import kagglehub, os
   os.environ['KAGGLEHUB_CACHE'] = '/tmp/kagglehub'   # keep off the small volume
   p = kagglehub.dataset_download('<owner>/<slug>')
   ```
   ~1.9GB in about a minute. Then `os.listdir(p)` — datasets often ship several formats (CSV, Parquet, JSONL) at very different sizes; the content is the same, the format differs (Parquet ≈ 4:1 vs CSV is normal, not a "different smaller dataset").

3. **Verify identity before trusting it**
   Kaggle pages may be behind reCAPTCHA: retry `web_extract` with `?r=1` appended to the URL, or check the author's HuggingFace mirror. Cross-check exact filename, listed size, row count, and column count against what you downloaded, and show the user a small evidence table — a user burned by an unverified "mirror" claim before will ask "are you sure this is the right dataset?"

4. **Filter by streaming, never by loading**
   - Streaming `csv.DictReader` line-by-line gives flat memory at any size. Write matches out incrementally; do not accumulate rows in RAM.
   - Call `csv.field_size_limit(sys.maxsize)` FIRST — long description fields blow past the 128KB default and kill the reader with `field larger than field limit (131072)`.
   - pyarrow `iter_batches` also works but is OOM-prone under a 1GB cgroup when the batch is large × columns include huge text fields. If using it: small batches, only needed columns, and never `to_pylist()` a full-file-sized batch.
   - When only a predicate on ONE column is needed (e.g. platforms), stream just that column first to count matches, then do the full pass — cheap sanity numbers for the user.

5. **Validate the output before replacing anything**
   - Reload the output file; count must equal the filter count from step 4.
   - Every row's key set must equal the CSV header exactly (missing/extra fields = broken extraction).
   - Re-apply the predicate to output rows to prove nothing slipped in.
   - Commit the old file to git BEFORE overwriting, so the replacement is reversible.

6. **Scope discipline**
   Replace/produce exactly what was asked. Do NOT adapt a companion app or UI to the new data schema unless explicitly requested — the user interrupted such an unsolicited adaptation mid-run and said not to.

## Pitfalls
- `field larger than field limit (131072)` → `csv.field_size_limit(sys.maxsize)`.
- Exit 137 → cgroup OOM; smaller batches, fewer columns, or stream the CSV instead.
- /tmp is ephemeral: after a redeploy the raw dataset is gone — the small extracted subset on the persistent volume / backup repo is what survives. Re-download is cheap (~1 min).
- Never trust a dataset's identity from size alone; verify against the source page and say so with evidence.
