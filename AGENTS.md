# iydebu profile README

What it is: GitHub profile repo iydebu/iydebu, pixel-retro theme (teal #0b1416 / #14b8a6).
Stack: README.md (HTML) + generated SVGs, stdlib Python.

## Run it

    python tools/build_pixel.py              # rebuild Img/pixel/*.svg from tools/profile.json
    python tools/build_pixel.py stats out.svg # live stats panel (needs GITHUB_TOKEN or gh auth)

## Conventions

- Edit text/skills/links in tools/profile.json, never hand-edit SVGs.
- GitHub strips CSS/fonts in README HTML: all styling lives inside SVGs (pixel font drawn as rects).
- .github/workflows/MAIN.yml rebuilds pixel-stats.svg + pixel-snake.svg daily into the `output` branch.
- Never push without asking Debu.

## Gotchas

- github-readme-stats.vercel.app and activity-graph are dead (503/402); visitcount.itsvg.in 404. Use komarev + own stats.
- Local preview: gh api markdown + headless Chrome; output-branch images do not exist until the workflow runs once.

Work history is in .hermes/JOURNAL.md.
