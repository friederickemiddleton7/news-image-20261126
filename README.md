# friederickemiddleton7/news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/friederickemiddleton7/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/friederickemiddleton7/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A single 1024x1024 PNG poster summarising Thursday 26 November 2026 in world news: the date in the largest type, one lead story (new US tariffs on 14 trading partners) and a 5x8 grid covering 37 more stories from Europe, the Americas, Asia-Pacific, the Middle East, Africa and global affairs.

`entry.png` is the poster. `make_image.py` is the deterministic build-time generator (Pillow, 2x supersample, real font metrics and assertions for every text run). `main.py` is the standard-library-only grader entrypoint: it writes the committed poster into `$MAKEFUN_OUTPUT_DIR` (default `/output`), validates the PNG signature and IHDR, and never writes into its own directory.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
