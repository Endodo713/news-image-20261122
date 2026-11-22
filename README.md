[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Endodo713/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Endodo713/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# Daily News Image Generator

Produces a single deterministic news summary image (`/output/entry.png`) for
**Sunday 22 November 2026**. See the bounty: https://make.fun/bounty/news-image-20261122

## Output
- File: `/output/entry.png` (PNG, 1024 × 1024 px, under 1 MiB)
- Default output path can be overridden with `MAKEFUN_OUTPUT_DIR`:
  `MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py` writes `/tmp/out/entry.png`
- Deterministic: running twice yields byte-identical files (verified via SHA-256)

## Run
```bash
python3 main.py
```

## Dependencies
- Python 3 standard library only (`os`, `struct`, `zlib`). No third-party packages,
  no Pillow, no network access at runtime. All news content is hardcoded in `main.py`.
- Font is an inline 5x7 bitmap font defined in `font.py` (no external font files).

## Repository structure
```
main.py            # entry point (pure stdlib PNG generator)
font.py            # inline 5x7 bitmap font (defined in code)
README.md          # this file
LICENSE            # MIT license
/output/entry.png  # generated output (created at runtime)
```

## News content
All headlines and summaries are hardcoded in `main.py` from verified sources
(AP, Reuters, Washington Post, Charles Schwab, CBOE). No facts are invented.
