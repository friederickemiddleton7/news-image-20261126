# World News — 26 November 2026

A single 1024×1024 PNG poster summarising **Thursday 26 November 2026** in world news: the date in the largest type, one lead story (new US tariffs on 14 trading partners) and a 5×8 grid covering 37 more stories from Europe, the Americas, Asia-Pacific, the Middle East, Africa and global affairs.

`entry.png` is the poster. `make_image.py` is the deterministic build-time generator (Pillow, 2× supersample, real font metrics and assertions for every text run). `main.py` is the standard-library-only grader entrypoint: it writes the committed poster into `$MAKEFUN_OUTPUT_DIR` (default `/output`), validates the PNG signature and IHDR, and never writes into its own directory.

Run locally: `MAKEFUN_OUTPUT_DIR=out python3 main.py`
