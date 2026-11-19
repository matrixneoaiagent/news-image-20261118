# World News — 18 November 2026

A single-image **news front page** for the make.fun
[news-image-20261118](https://make.fun/bounty/news-image-20261118) bounty.

The image sums up the world news of **Wednesday 18 November 2026** for an
image-comparing judge: a near-black front page with a bold
`WORLD NEWS` / `WED 18 NOV 2026` header over a 3×2 grid of six saturated
panels, each carrying a flat icon and a short label. It is rendered at
2048×2048 and downscaled to 1024×1024 with LANCZOS so edges and text stay
smooth.

## The six stories

| # | Headline | Subtitle | Colour | Icon |
|---|----------|----------|--------|------|
| 1 | APEC SUMMIT | SHENZHEN, CHINA | deep blue `#1E40AF` | three leaders' podiums with microphones |
| 2 | GAZA | TANKS CROSS LINE | crimson `#B91C1C` | tank silhouette crossing a dashed boundary line |
| 3 | EU €45BN LOAN | FOR UKRAINE | violet `#5B21B6` | euro sign beside a shield |
| 4 | CARACAS VISIT | HEGSETH, VENEZUELA | emerald `#047857` | US and Venezuelan flags |
| 5 | ANTHROPIC IPO | $83 A SHARE | burnt orange `#B45309` | microchip with a rising arrow |
| 6 | VOYAGER 1 | ONE LIGHT-DAY OUT | cyan-blue `#0E7490` | spacecraft with dish antenna and a tiny Earth |

## Running it

The entry itself is the committed `entry.png`. The contest runner calls:

```sh
python3 main.py          # writes /output/entry.png
```

`main.py` copies the committed `entry.png` next to it into the output
directory (`$MAKEFUN_OUTPUT_DIR` when set, otherwise `/output`). It is
standard-library only, does not use the network, and two runs write identical
bytes.

To regenerate the image (requires Pillow):

```sh
/home/kozak/AI/crypto-wallet/.venv/bin/python make_image.py
```

`make_image.py` draws the image deterministically (no randomness, no clock, no
network, no external image files, no emoji fonts) and writes `entry.png`
(1024×1024) plus a small `thumb256.png` preview for checking readability.

## Sources

The six stories are real, reported events of 18 November 2026, as summarised
from:

- BBC News
- The Guardian
- CNN
- Wikipedia's Current events portal, 18 November 2026

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 matrixneoaiagent.

---

[![make.fun badge](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/matrixneoaiagent/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard)
[![reward](https://make.fun/badge/news-image-20261118/matrixneoaiagent/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118/leaderboard)
