# The World Today — 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/xJPtea/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/xJPtea/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A program that draws one newspaper front page summing up Saturday
21 November 2026 in a single 1024×1024 image. The page names the day
up front and covers seven verified stories from that day, across
regions and fields.

## The seven stories

1. **Middle East** — Saudi air defences intercept three Houthi ballistic
   missiles fired toward Riyadh before dawn.
2. **France** — Paris court jails three officers over the racist beating
   of music producer Michel Zecler.
3. **Climate** — COP31 talks deadlocked in overtime over fossil fuels
   and climate finance.
4. **Diplomacy** — Trump says Iran wants a deal, but not one he will
   accept; Tehran says diplomacy can still end the war.
5. **Markets** — Wall Street slides into correction as AI shares sell off;
   S&P 500 down 3.7%.
6. **California** — Jury convicts Rinderknecht over the 2025 Palisades
   Fire, which killed 12 and destroyed 6,800 structures.
7. **Europe** — Young protesters rally across the continent over living
   costs, housing and climate.

Every story and its source is recorded in [NEWS.md](NEWS.md), including
the stories that were deliberately left out because they belong to
earlier days.

## How it works

`main.py` is pure Python 3.13 standard library — no Pillow, no network.
It draws the page pixel by pixel with a hand-written 5×7 bitmap font
and a hand-written PNG encoder, so the output is byte-for-byte
deterministic: run it twice and the two files are identical.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
python3 test_entry.py                    # determinism + format checks
```

`test_entry.py` runs the program twice into two fresh directories and
asserts byte-identical output, a valid PNG header, 1024×1024 pixels,
and a file size of at most 1 MiB.

## License

MIT — see [LICENSE](LICENSE).
