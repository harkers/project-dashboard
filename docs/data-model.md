# Data Model

## Overview

The dashboard uses generated JSON as its canonical presentation input.

There are two principal data sets:

```text
data/report.json
data/repos/<repository>.json
```

The first powers the portfolio dashboard. The second powers repository detail pages.

## Portfolio record

`data/report.json` contains:

```json
{
  "generated_at": "2026-10-04T14:00:00+01:00",
  "period": {
    "label": "Last 7 days",
    "start": "2026-09-28",
    "end": "2026-10-04"
  },
  "summary": {},
  "attention": [],
  "repositories": [],
  "recent": {}
}
```

### `summary`

Expected portfolio-level metrics include:

```json
{
  "repositories": 20,
  "commits": 71,
  "issues_created": 18,
  "issues_closed": 14,
  "prs_created": 12,
  "prs_merged": 9,
  "comments": 31,
  "failed_actions": 2
}
```

### `attention`

Each attention item should contain a severity and message:

```json
{
  "severity": "warning",
  "message": "workhub is ahead of origin by 2 commits."
}
```

Supported severity semantics:

- `info` — informational
- `warning` — requires review
- `error` — immediate attention required

### `repositories`

Each entry is a portfolio summary used to render the repository table.

Example:

```json
{
  "name": "workhub",
  "description": "Project orchestration and DAG workflow platform",
  "commits": 12,
  "issues_closed": 3,
  "prs_merged": 2,
  "failed_actions": 0,
  "dirty": false,
  "sync_state": "ahead"
}
```

## Per-repository record

Each file in `data/repos/` represents a single repository.

Recommended structure:

```json
{
  "name": "workhub",
  "full_name": "harkers/workhub",
  "description": "Project orchestration and DAG workflow platform",
  "html_url": "https://github.com/harkers/workhub",
  "visibility": "public",
  "default_branch": "main",
  "language": "Python",
  "generated_at": "2026-10-04T14:00:00Z",
  "github": {},
  "local": {},
  "derived": {},
  "recent_activity": [],
  "priority_issues": [],
  "open_pull_requests": [],
  "health_checks": []
}
```

## GitHub fields

GitHub-derived values should live under `github` where practical.

Example:

```json
{
  "github": {
    "commits_7d": 41,
    "issues_open": 14,
    "issues_closed_7d": 12,
    "prs_open": 3,
    "prs_merged_7d": 8,
    "failed_actions_7d": 1,
    "latest_release": "v0.8.2",
    "last_activity_at": "2026-10-04T12:42:00Z"
  }
}
```

## Local fields

Machine-local facts should live under `local`.

Example:

```json
{
  "local": {
    "available": true,
    "path": "/home/stu/projects/workhub",
    "branch": "main",
    "dirty": false,
    "ahead": 2,
    "behind": 0,
    "diverged": false,
    "untracked_files": 0,
    "uncommitted_files": 0
  }
}
```

If local state is unavailable, do not invent values. Prefer:

```json
{
  "local": {
    "available": false
  }
}
```

## Derived fields

Derived state should be explainable.

Example:

```json
{
  "derived": {
    "attention": "AMBER",
    "direction": "ACTIVE DELIVERY",
    "health_score": 87,
    "health_reasons": [
      "CI passing",
      "8 PRs merged in 7 days",
      "2 P1 issues remain open"
    ]
  }
}
```

### Attention state

Recommended values:

- `GREEN`
- `AMBER`
- `RED`

### Direction

Recommended values:

- `ACTIVE DELIVERY`
- `BLOCKED`
- `WAITING REVIEW`
- `WAITING USER`
- `STALLED`
- `MAINTENANCE`
- `IDLE`

## Health checks

Health should be backed by individual checks rather than an unexplained single number.

Example:

```json
{
  "health_checks": [
    {"name": "CI", "status": "pass", "detail": "Latest main workflow passed"},
    {"name": "Tests", "status": "pass", "detail": "Test workflow detected"},
    {"name": "Security", "status": "warn", "detail": "No dependency scan detected"}
  ]
}
```

Recommended statuses:

- `pass`
- `warn`
- `fail`
- `unknown`

## Compatibility rule

Collectors should be additive where possible. New fields should not break older dashboard data. The UI should tolerate missing optional properties and show `unknown` or omit the component rather than failing the whole page.

## Privacy rule

Only include data appropriate for the deployment visibility. A public GitHub Pages site must not receive sensitive private-repository or client information merely because a local collector can access it.
