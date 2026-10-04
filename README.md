# Project Dashboard

GitHub Pages dashboard for portfolio-level project activity and per-repository intelligence.

## Current MVP

- Portfolio summary across public repositories
- Click-through repository detail pages using `repo.html?repo=<name>`
- Repository description, visibility, default branch and language
- 7-day commits, issues closed, PRs merged and failed Actions
- Open issue / PR counts
- Delivery direction (`ACTIVE DELIVERY` or `IDLE`)
- Attention state and recent activity timeline
- Repository health checks
- Current issues and pull requests
- Direct GitHub / Issues / PRs / Actions / Releases links
- Optional local-state fields for dirty/ahead/behind/diverged data

## Data architecture

`data/report.json` is the portfolio summary.

Per-repository records are written to:

```text
data/repos/<repository>.json
```

The UI uses one reusable `repo.html` template rather than generating a separate HTML file for each repository.

## Automated GitHub refresh

`.github/workflows/refresh-data.yml` runs every six hours and can also be dispatched manually.

It runs:

```bash
python scripts/collect_github.py
```

The collector queries public repositories owned by `harkers`, writes portfolio and per-repository JSON, commits any changes, and lets the existing Pages deployment publish them.

Only public GitHub data is collected by the scheduled workflow. It does **not** attempt to expose private repositories.

## Local-only state

GitHub cannot see local working-tree state. Fields such as:

- dirty working tree
- ahead / behind
- branch divergence
- unpushed commits

must be supplied by a trusted local collector such as `daily-project-report`. The detail-page schema already supports these fields without pretending they came from GitHub.

## Local preview

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## GitHub Pages

Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**. The Pages deployment workflow will then publish changes automatically.
