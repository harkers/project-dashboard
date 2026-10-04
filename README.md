# Project Dashboard

Static GitHub Pages dashboard for daily project activity reports.

## What it shows

- Daily and 7-day activity summaries
- Commits, issues, pull requests and comments
- Failed GitHub Actions runs
- Dirty, ahead/behind and diverged repositories
- Releases and changed TODO/workitem/plan files
- Per-repository drill-down

## Data

The dashboard reads `data/report.json`.

The intended flow is:

1. `daily-project-report` generates the daily report data.
2. The JSON is copied or committed into this repository as `data/report.json`.
3. GitHub Pages redeploys automatically.

## Local preview

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.
