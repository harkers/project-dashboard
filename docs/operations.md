# Operations Guide

## Local checkout

Expected local path:

```text
/home/stu/projects/project-dashboard
```

Update the checkout with:

```bash
cd /home/stu/projects/project-dashboard
git pull
```

If the branch does not yet track the remote:

```bash
git fetch origin
git checkout -B main origin/main
```

## Manual data refresh

Run:

```bash
cd /home/stu/projects/project-dashboard
python3 scripts/collect_github.py
```

Inspect generated files:

```bash
find data -maxdepth 2 -type f | sort
```

Then preview the site:

```bash
python3 -m http.server 8000
```

Open:

```text
http://localhost:8000
```

## Automated refresh

The scheduled workflow:

```text
.github/workflows/refresh-data.yml
```

runs every six hours.

It should:

1. check out the repository
2. run `scripts/collect_github.py`
3. detect changed JSON
4. commit generated data when required
5. trigger or allow the Pages deployment to publish the new state

The workflow may also be run manually from the GitHub Actions UI.

## Pages deployment

Configure the repository once:

**Settings → Pages → Build and deployment → Source → GitHub Actions**

Expected site:

```text
https://harkers.github.io/project-dashboard/
```

## Verifying a deployment

Check:

1. the data-refresh workflow completed successfully
2. `data/report.json` has a recent `generated_at`
3. expected files exist in `data/repos/`
4. the Pages deployment workflow completed
5. the browser is not serving a cached copy

For local diagnosis:

```bash
python3 -m json.tool data/report.json >/dev/null
```

To validate all repository JSON files:

```bash
for f in data/repos/*.json; do
  python3 -m json.tool "$f" >/dev/null || echo "INVALID: $f"
done
```

## Common problems

### Dashboard shows stale data

Check the latest refresh workflow and inspect:

```bash
git log --oneline -- data/
```

Confirm `generated_at` in the JSON is current.

### Repository detail page says data is unavailable

Verify the file exists:

```bash
ls data/repos/<repo>.json
```

Then test it:

```bash
python3 -m json.tool data/repos/<repo>.json
```

### GitHub Pages is not publishing

Confirm the Pages source is set to GitHub Actions and inspect the deployment workflow logs.

### Local state is missing

This is expected unless a local collector has enriched the repository record. GitHub Actions cannot inspect `/home/stu/projects` on the user's machine.

### Local repository is ahead, behind or diverged

Do not have the dashboard automation silently merge or reset it. The collector should report the state and leave reconciliation to an explicit Git operation.

## Generated-data policy

Generated JSON may be committed to this repository because GitHub Pages needs the static files to render the current dashboard state.

Generated data should be reproducible from the collectors and should not contain secrets.

## Retention

For future historical reporting, recommended retention is:

- daily snapshots: 30 days
- weekly aggregates: 12 weeks
- monthly aggregates: 12 months

Do not retain unlimited high-volume issue comments or workflow payloads unless there is a clear reporting need.

## Safe operating rules

- never commit GitHub tokens
- never publish private-repository facts to a public Pages site without deliberate approval
- never expose local filesystem secrets
- never reset or clean a local repo from a reporting collector
- use fast-forward-only semantics for any automated repository update
- report uncertainty instead of guessing missing state
