# Architecture

## Purpose

Project Dashboard is a static GitHub Pages application backed by generated JSON. It provides a portfolio view across repositories and a reusable detail page for each repository.

The design intentionally separates **collection**, **storage**, and **presentation**.

## High-level flow

```text
GitHub API / gh CLI
        │
        ▼
scripts/collect_github.py
        │
        ├── data/report.json
        └── data/repos/<repo>.json
                 │
                 ▼
          Static site renderer
          index.html / repo.html
                 │
                 ▼
            GitHub Pages
```

A second local path provides machine-only state:

```text
/home/stu/projects/*
        │
        ▼
daily-project-report
        │
        └── local Git enrichment
                 │
                 ▼
        per-repository JSON
```

## Design principles

### 1. JSON is canonical

The website must not scrape Markdown reports. Collection should produce structured JSON first. Markdown reports may be generated from the same data, but should not become the source of truth.

### 2. GitHub facts and local facts stay separate

GitHub can report remote activity such as:

- commits
- issues
- pull requests
- workflow runs
- releases
- repository metadata

GitHub cannot report:

- dirty working trees
- untracked files
- local-only commits
- branch divergence before push
- local worktrees

The schema therefore keeps these concepts distinct.

### 3. One reusable repository page

The application does not generate one HTML file per repository. Instead:

```text
repo.html?repo=workhub
repo.html?repo=agent-fabric
repo.html?repo=mlx-broker
```

all use the same renderer and load different JSON files.

### 4. Static hosting, dynamic data generation

GitHub Pages is static hosting. The site appears "live" because GitHub Actions regenerates JSON regularly and redeploys the site.

## Main components

### `index.html`

Portfolio-level dashboard.

Responsibilities:

- summary KPIs
- attention state
- repository table
- search/filter
- recent delivery activity
- navigation to repository detail pages

### `repo.html`

Reusable repository detail surface.

Responsibilities:

- repository metadata
- 7-day delivery stats
- issue and PR state
- CI status
- health checks
- recent activity
- priority work
- local-state display when available

### `assets/app.js`

Loads and renders `data/report.json` for the portfolio page.

### `assets/repo.js`

Loads and renders `data/repos/<repo>.json` for the selected repository.

### `scripts/collect_github.py`

Remote GitHub collector.

Responsibilities:

- enumerate public repositories
- collect metadata and activity
- calculate summary counts
- write portfolio JSON
- write per-repository JSON

### `.github/workflows/refresh-data.yml`

Scheduled data refresh.

Responsibilities:

- run the collector every six hours
- update generated data
- commit changes when required

### `.github/workflows/deploy-pages.yml`

GitHub Pages deployment.

Responsibilities:

- publish the static site
- redeploy when relevant source/data files change

## Derived state

Some displayed values are not raw GitHub fields. These include:

- attention state
- delivery direction
- repository health

Derived values should remain explainable. Avoid opaque scoring where the user cannot see why a repository is marked healthy, amber, or red.

## Future architecture

The intended evolution is:

```text
GitHub collector ───────┐
                       │
Local repo collector ──┼──► canonical repository state
                       │
Workhub collector ─────┤
                       │
Agent telemetry ───────┘
                              │
                              ▼
                       dashboard JSON
                              │
                              ▼
                       GitHub Pages UI
```

This allows the dashboard to become a project-control layer without coupling the website to any single source system.
