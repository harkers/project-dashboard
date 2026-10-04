# Local Integration

## Purpose

The GitHub collector can only see remote GitHub state. Local repository state must be collected on the machine that owns the working copies.

For this setup, local repositories live under:

```text
/home/stu/projects
```

and `daily-project-report` is the intended enrichment source.

## Local-only facts

Useful values include:

- current local branch
- dirty working tree
- untracked files
- uncommitted files
- ahead/behind counts
- diverged branch state
- unpushed commits
- changed TODO/workitem/plan files
- local worktree information
- optionally future Workhub/agent state

## Recommended integration pattern

Do not make `daily-project-report` overwrite the GitHub collector's data blindly.

Instead:

1. GitHub collector writes remote facts.
2. Local collector reads the existing per-repository JSON.
3. Local collector updates only the `local` section and any explicitly local-derived fields.
4. JSON is validated.
5. The dashboard repo is committed and pushed.

Example:

```json
{
  "name": "workhub",
  "github": {
    "commits_7d": 41,
    "issues_open": 14,
    "prs_open": 3
  },
  "local": {
    "available": true,
    "path": "/home/stu/projects/workhub",
    "branch": "main",
    "dirty": false,
    "ahead": 2,
    "behind": 0,
    "diverged": false
  }
}
```

## Safe merge behaviour

The local enrichment process should preserve unknown keys.

Conceptually:

```python
record = load_existing_repo_json()
record["local"] = collect_local_state()
write_json(record)
```

Avoid regenerating the entire record locally unless the local collector intentionally owns the complete schema.

## Suggested nightly flow

```text
00:00
  │
  ├── sync/fetch repository metadata safely
  │
  ├── daily-project-report scans /home/stu/projects
  │
  ├── update data/repos/*.json local sections
  │
  ├── update portfolio attention if required
  │
  ├── validate JSON
  │
  ├── git add data/
  │
  ├── git commit
  │
  └── git push
           │
           ▼
      GitHub Pages deploy
```

## Repository matching

Use the repository's Git remote as the canonical identity where possible, rather than relying only on the directory basename.

For example:

```bash
git -C /home/stu/projects/workhub remote get-url origin
```

Normalize this to:

```text
harkers/workhub
```

This avoids collisions if two different owners have repositories with the same short name.

## Local status collection

Recommended Git commands:

### Current branch

```bash
git -C "$repo" symbolic-ref --quiet --short HEAD
```

### Dirty state

```bash
git -C "$repo" status --porcelain
```

### Upstream

```bash
git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
```

### Ahead count

```bash
git -C "$repo" rev-list --count "${upstream}..HEAD"
```

### Behind count

```bash
git -C "$repo" rev-list --count "HEAD..${upstream}"
```

Divergence exists when both ahead and behind are greater than zero.

## Failure handling

Local collection should be fail-safe.

If one repository fails:

- record the error
- mark local state as unavailable or stale
- continue scanning the remaining repositories
- do not terminate the entire report unless the canonical output cannot be written safely

Example:

```json
{
  "local": {
    "available": false,
    "error": "fetch failed"
  }
}
```

## Data freshness

The dashboard should eventually expose independent timestamps for each source:

```json
{
  "source_freshness": {
    "github": "2026-10-04T18:00:00Z",
    "local": "2026-10-05T00:01:12+01:00"
  }
}
```

That prevents stale local state from being mistaken for current GitHub state.

## Security

Before pushing local enrichment to a public dashboard, sanitize:

- absolute paths if they reveal sensitive structure
- private repository names
- branch names containing client identifiers
- issue/workitem text containing confidential information
- local usernames or machine-specific secrets

For public Pages, prefer publishing state such as `dirty=true` rather than detailed filenames unless those filenames are safe to expose.

## Future integration

Once Workhub and agent telemetry are ready, extend the same model rather than creating a separate reporting path.

Possible sections:

```json
{
  "workhub": {},
  "agents": {},
  "benchmarks": {}
}
```

The dashboard can then answer not only whether a repository is technically healthy, but whether the project is actively progressing, blocked, waiting for review, or stalled.
