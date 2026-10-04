const metricsEl = document.getElementById('metrics');
const attentionEl = document.getElementById('attention');
const repoRowsEl = document.getElementById('repo-rows');
const recentEl = document.getElementById('recent');
const periodEl = document.getElementById('period');
const healthEl = document.getElementById('health');
const searchEl = document.getElementById('search');

let report = null;

const metricOrder = [
  ['repositories', 'Repositories'],
  ['commits', 'Commits'],
  ['issues_created', 'Issues created'],
  ['issues_closed', 'Issues closed'],
  ['prs_created', 'PRs created'],
  ['prs_merged', 'PRs merged'],
  ['comments', 'Comments'],
  ['failed_actions', 'Failed CI'],
];

function statusClass(repo) {
  if (repo.failed_actions > 0 || repo.sync_state === 'diverged') return 'bad';
  if (repo.dirty || repo.sync_state === 'ahead' || repo.sync_state === 'behind') return 'warn';
  return 'good';
}

function statusText(repo) {
  if (repo.sync_state === 'diverged') return 'Diverged';
  if (repo.failed_actions > 0) return 'CI failing';
  if (repo.dirty) return 'Dirty';
  if (repo.sync_state === 'ahead') return 'Ahead';
  if (repo.sync_state === 'behind') return 'Behind';
  return 'Healthy';
}

function renderMetrics() {
  metricsEl.innerHTML = metricOrder.map(([key, label]) => `
    <div class="metric">
      <div class="value">${report.summary[key] ?? 0}</div>
      <div class="label">${label}</div>
    </div>
  `).join('');
}

function renderAttention() {
  const items = report.attention || [];
  if (!items.length) {
    attentionEl.innerHTML = '<div class="attention-item good">No immediate issues detected.</div>';
    healthEl.textContent = 'Healthy';
    healthEl.className = 'status-pill good';
    return;
  }

  const severe = items.some(i => i.severity === 'error');
  healthEl.textContent = severe ? 'Needs attention' : 'Watch';
  healthEl.className = `status-pill ${severe ? 'bad' : 'warn'}`;
  attentionEl.innerHTML = items.map(i => `<div class="attention-item ${i.severity === 'error' ? 'bad' : ''}">${i.message}</div>`).join('');
}

function renderRepos(filter = '') {
  const q = filter.trim().toLowerCase();
  const repos = (report.repositories || []).filter(r => !q || r.name.toLowerCase().includes(q));
  repoRowsEl.innerHTML = repos.map(repo => {
    const cls = statusClass(repo);
    return `<tr>
      <td><strong>${repo.name}</strong></td>
      <td>${repo.commits ?? 0}</td>
      <td>${repo.issues_closed ?? 0}</td>
      <td>${repo.prs_merged ?? 0}</td>
      <td>${repo.failed_actions ?? 0}</td>
      <td><span class="badge ${cls}">${statusText(repo)}</span></td>
    </tr>`;
  }).join('');
}

function renderRecent() {
  const groups = report.recent || {};
  const cards = [
    ['Merged PRs', groups.merged_prs],
    ['Closed issues', groups.closed_issues],
    ['Releases', groups.releases],
    ['Changed work files', groups.changed_workfiles],
  ];
  recentEl.innerHTML = cards.map(([title, items]) => `
    <article class="recent-card">
      <h3>${title}</h3>
      ${(items && items.length) ? `<ul>${items.map(x => `<li>${x}</li>`).join('')}</ul>` : '<p class="muted">None.</p>'}
    </article>
  `).join('');
}

async function load() {
  try {
    const res = await fetch('data/report.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    report = await res.json();
    periodEl.textContent = `${report.period?.label || 'Current report'} · generated ${report.generated_at || 'unknown'}`;
    renderMetrics();
    renderAttention();
    renderRepos();
    renderRecent();
  } catch (err) {
    periodEl.textContent = `Could not load report: ${err.message}`;
    healthEl.textContent = 'No data';
    healthEl.className = 'status-pill bad';
  }
}

searchEl.addEventListener('input', e => renderRepos(e.target.value));
load();
