# iydebu profile README

What it is: GitHub profile repo iydebu/iydebu. Minimal, GitHub-native look (since 2026-09-28): plain markdown body,
GitHub Primer colours plus one teal accent (#14b8a6), transparent images in dark + light versions swapped with <picture>.
Debu rejected the busy pixel/iydebu.com theme as "hodgepodge"; keep it minimal.
Facts come from D:/Personal/Portfolio Website/site/content.js: real facts only, never list Debu's personal PC tools.
Stack: README.md (markdown + <picture>) + 2 generated SVGs, stdlib Python.

## Run it

    python tools/build_pixel.py            # Img/header-dark.svg + header-light.svg from tools/profile.json
    python tools/build_pixel.py stats DIR  # DIR/stats-dark.svg + stats-light.svg (needs GITHUB_TOKEN or gh auth)

## Conventions

- Text in the README is plain markdown; only the header wordmark and stats panel are images.
- Every generated image needs a dark AND a light version; the README swaps them with <picture>.
- .github/workflows/MAIN.yml rebuilds stats-*.svg + the GitHub-palette snakes daily into the `output` branch.
- Never push without asking Debu.

## Gotchas

- github-readme-stats.vercel.app and activity-graph are dead (503/402). Use our own stats.
- Local preview: gh api markdown + headless Chrome. The API rewrites image URLs through camo, so swap them after rendering.
- git push via the default credential helper hangs (GUI prompt); use
  git -c credential.helper= -c "credential.helper=!gh auth git-credential" push

Work history is in .hermes/JOURNAL.md.
