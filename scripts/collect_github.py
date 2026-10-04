#!/usr/bin/env python3
import json, os, pathlib, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone
OWNER=os.getenv('GITHUB_OWNER','harkers'); TOKEN=os.getenv('GITHUB_TOKEN',''); ROOT=pathlib.Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; REPOS=DATA/'repos'; REPOS.mkdir(parents=True,exist_ok=True)
HEAD={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'project-dashboard'}
if TOKEN: HEAD['Authorization']=f'Bearer {TOKEN}'
def api(path,params=None):
    url='https://api.github.com'+path
    if params: url+='?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=30) as r: return json.load(r)
def pages(path,params=None,limit=100):
    params=dict(params or {}); params['per_page']=100; out=[]
    for p in range(1,11):
        params['page']=p; chunk=api(path,params); out.extend(chunk)
        if len(chunk)<100 or len(out)>=limit: break
    return out[:limit]
def safe(fn,default):
    try:return fn()
    except Exception as e:
        print('WARN',e); return default
now=datetime.now(timezone.utc); since=now-timedelta(days=7); since_s=since.isoformat().replace('+00:00','Z')
repos=pages(f'/users/{OWNER}/repos',{'type':'owner','sort':'updated','direction':'desc'},1000)
repos=[r for r in repos if not r.get('fork') and not r.get('archived')]
portfolio=[]; totals={'repositories':0,'commits':0,'issues_created':0,'issues_closed':0,'prs_created':0,'prs_merged':0,'comments':0,'failed_actions':0}; recent={'merged_prs':[],'closed_issues':[],'releases':[],'changed_workfiles':[]}; attention=[]
for r in repos:
    name=r['name']; full=r['full_name']; print('Collecting',full)
    commits=safe(lambda:pages(f'/repos/{full}/commits',{'since':since_s},300),[])
    issues=safe(lambda:pages(f'/repos/{full}/issues',{'state':'all','since':since_s,'sort':'updated','direction':'desc'},300),[])
    pulls=safe(lambda:pages(f'/repos/{full}/pulls',{'state':'all','sort':'updated','direction':'desc'},200),[])
    runs=safe(lambda:api(f'/repos/{full}/actions/runs',{'per_page':100}).get('workflow_runs',[]),[])
    releases=safe(lambda:api(f'/repos/{full}/releases',{'per_page':10}),[])
    issue_only=[x for x in issues if 'pull_request' not in x]
    created_issues=[x for x in issue_only if x.get('created_at','')>=since_s]; closed_issues=[x for x in issue_only if x.get('closed_at') and x['closed_at']>=since_s]
    created_prs=[x for x in pulls if x.get('created_at','')>=since_s]; merged_prs=[x for x in pulls if x.get('merged_at') and x['merged_at']>=since_s]
    failed=[x for x in runs if x.get('created_at','')>=since_s and x.get('conclusion') in {'failure','timed_out','action_required'}]
    attention_state='red' if failed else 'green'; direction='ACTIVE DELIVERY' if commits or merged_prs or closed_issues else 'IDLE'
    stats={'commits_7d':len(commits),'issues_closed_7d':len(closed_issues),'prs_merged_7d':len(merged_prs),'open_issues':r.get('open_issues_count',0),'open_prs':sum(1 for x in pulls if x.get('state')=='open'),'failed_actions_7d':len(failed)}
    health={'ci':not failed,'tests':None,'security':None,'issue_forms':None,'pr_template':None,'readme':None,'todo_schema':None}
    att=[]
    if failed: att.append({'severity':'error','message':f'{len(failed)} failing workflow run(s) in the last 7 days.'})
    timeline=[]
    for c in commits[:8]: timeline.append({'time':c['commit']['author']['date'],'text':f"commit {c['sha'][:7]} — {c['commit']['message'].splitlines()[0]}"})
    for p in merged_prs[:5]: timeline.append({'time':p['merged_at'],'text':f"PR #{p['number']} merged — {p['title']}"})
    timeline=sorted(timeline,key=lambda x:x['time'],reverse=True)[:12]
    detail={'name':name,'description':r.get('description') or 'No description.','github_url':r['html_url'],'visibility':r.get('visibility','public'),'default_branch':r.get('default_branch'),'language':r.get('language'),'direction':direction,'attention':attention_state,'last_activity':r.get('pushed_at'),'stats':stats,'local':{'dirty':None,'sync_state':'not collected'},'latest_release':({'name':releases[0].get('name') or releases[0].get('tag_name'),'url':releases[0].get('html_url')} if releases else None),'attention_items':att,'health':health,'timeline':timeline,'work':{'issues':[f"#{x['number']} {x['title']}" for x in issue_only if x.get('state')=='open'][:10],'prs':[f"#{x['number']} {x['title']}" for x in pulls if x.get('state')=='open'][:10]},'github':{'stars':r.get('stargazers_count',0),'forks':r.get('forks_count',0),'watchers':r.get('subscribers_count',r.get('watchers_count',0))}}
    (REPOS/f'{name}.json').write_text(json.dumps(detail,indent=2)+'\n')
    portfolio.append({'name':name,'description':detail['description'],'commits':len(commits),'issues_closed':len(closed_issues),'prs_merged':len(merged_prs),'failed_actions':len(failed),'dirty':None,'sync_state':'not collected','direction':direction,'attention':attention_state})
    totals['repositories']+=1; totals['commits']+=len(commits); totals['issues_created']+=len(created_issues); totals['issues_closed']+=len(closed_issues); totals['prs_created']+=len(created_prs); totals['prs_merged']+=len(merged_prs); totals['failed_actions']+=len(failed)
    if failed: attention.append({'severity':'error','message':f'{name} has {len(failed)} failing workflow run(s) in the last 7 days.'})
    recent['merged_prs'] += [f"{name} #{x['number']} — {x['title']}" for x in merged_prs[:3]]; recent['closed_issues'] += [f"{name} #{x['number']} — {x['title']}" for x in closed_issues[:3]]
    if releases: recent['releases'].append(f"{name} — {releases[0].get('name') or releases[0].get('tag_name')}")
report={'generated_at':now.isoformat(),'period':{'label':'Live 7-day GitHub report','start':since.date().isoformat(),'end':now.date().isoformat()},'summary':totals,'attention':attention,'repositories':portfolio,'recent':recent}
(DATA/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Wrote',len(portfolio),'repository records')