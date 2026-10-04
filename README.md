# Project Dashboard

A GitHub Pages dashboard for portfolio-level project activity and per-repository intelligence.

The project is designed to answer two questions quickly:

1. **What changed across my GitHub projects?**
2. **Which repositories need attention or are not moving forward?**

It combines GitHub-derived repository activity with optional local machine state so the dashboard can distinguish remote project health from local working-tree conditions.

## Features

### Portfolio dashboard

The home page summarizes activity across all collected repositories, including:

- repository count
- commits
- issues created and closed
- pull requests created and merged
- failed GitHub Actions runs
- repository attention state
- recent delivery activity
- search and filtering

Each repository row links to a reusable drill-down page:

```text
repo.html?repo=<repository-name>
```

### Repository detail pages

Each repository page can show:

- repository name and description
- visibility
- default branch
- primary language
- 7-day commit activity
- open and closed issues
- open and merged pull requests
- recent GitHub Actions status
- failed CI runs
- latest release
- recent activity timeline
- priority issues
- repository health indicators
- direct links to GitHub, Issues, Pull Requests, Actions and Releases
- local dirty/ahead/behind/diverged state when supplied by the local collector

The UI uses one reusable `repo.html` template rather than generating a separate HTML file for every repository.

## Architecture

```text
GitHub repositories
       │
       ▼
scripts/collect_github.py
       │
       ├── data/report.json
       └── data/repos/<repo>.json
                │
                ▼
        GitHub Pages UI
        index.html
        repo.html

Local repositories
       │
       ▼
daily-project-report
       │
       └── optional local-state enrichment
```

GitHub is treated as the source of truth for remote repository activity. Local Git state is collected separately because GitHub cannot know whether a working tree is dirty, ahead, behind, or diverged.

See [docs/architecture.md](docs/architecture.md) for the full design.

## Repository structure

```text
.
├── .github/
│   └── workflows/
│       ├── deploy-pages.yml
│       └── refresh-data.yml
├── assets/
│   ├── app.js
│   ├── repo.js
│   └── style.css
├── data/
│   ├── report.json
│   └── repos/
│       └── <repository>.json
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── operations.md
│   └── local-integration.md
├── scripts/
│   └── collect_github.py
├── index.html
├── repo.html
└── README.md
```

## Automated GitHub refresh

The workflow:

```text
.github/workflows/refresh-data.yml
```

runs every six hours and can also be started manually from GitHub Actions.

It executes:

```bash
python scripts/collect_github.py
```

The collector queries public repositories owned by `harkers`, generates portfolio and per-repository JSON, commits changed data, and allows the Pages deployment workflow to publish the updated site.

Only public GitHub data is collected by the scheduled workflow. Private or sensitive repository data must not be exposed through a public Pages deployment.

## Local development

Clone or update the repository:

```bash
cd /home/stu/projects/project-dashboard
git pull
```

Run the GitHub collector manually:

```bash
python3 scripts/collect_github.py
```

Preview the site locally:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

Repository detail example:

```text
http://localhost:8000/repo.html?repo=workhub
```

## GitHub Pages deployment

In the repository, configure:

**Settings → Pages → Build and deployment → Source → GitHub Actions**

Once enabled, the Pages workflow publishes updates automatically after relevant repository changes.

The expected public URL is:

```text
https://harkers.github.io/project-dashboard/
```

## Local-state enrichment

GitHub cannot see local working-tree information such as:

- uncommitted files
- untracked files
- local commits not pushed
- branches behind remote
- diverged branches
- local TODO/workitem changes

Those fields should be collected locally and merged into the same per-repository data model by `daily-project-report` or a future dedicated local collector.

See [docs/local-integration.md](docs/local-integration.md).

## Data model

The dashboard deliberately separates:

- **GitHub facts** — repository metadata, issues, PRs, commits, Actions, releases
- **local facts** — dirty state, ahead/behind state, local branch conditions and worktree information
- **derived state** — health, attention and delivery direction

See [docs/data-model.md](docs/data-model.md).

## Operating model

Recommended operating pattern:

1. GitHub Actions refreshes remote GitHub data every six hours.
2. `daily-project-report` runs locally each night.
3. The local report enriches the repository JSON with machine-local Git state.
4. Updated JSON is committed to `project-dashboard`.
5. GitHub Pages republishes automatically.

Operational procedures and troubleshooting are documented in [docs/operations.md](docs/operations.md).

## Security and privacy

This repository currently targets a public GitHub Pages site.

Do not publish:

- confidential client information
- private repository metadata
- credentials or tokens
- sensitive issue titles or commit messages
- internal URLs
- personally identifiable information

If private project information is required, the deployment model should be changed before adding that data.

## Roadmap

Planned extensions include:

- P0 / P1 / P2 issue counts
- stale and blocked work detection
- trend comparison against the previous seven days
- transparent repository health scoring
- Workhub workitem integration
- agent execution and review history
- forward-progress state (`ACTIVE DELIVERY`, `BLOCKED`, `WAITING REVIEW`, `STALLED`, etc.)
- benchmark/model-routing data where relevant

The intent is to evolve the dashboard into a project-control surface rather than a simple GitHub statistics page.
