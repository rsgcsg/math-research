"""One-use exact-head, archive-first cleanup for this repository only."""
import base64,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
REPO='rsgcsg/math-research';PREFIX='archive/2026-10-06/'
TARGETS={
'research/full15-coupling-20260928':'4c3e2313902b40bbfbf63cbc673a45e2951f991f',
'research/generalized-partition-facets-20261006':'eaefe43b3ceec3fafd82a849db8ced2764e9e8af',
'research/intrinsic-eta-cycle-20260928':'09926d59b176c1f649aa30f7ec397fb8fa9ef9fa',
'research/joint-continuation-20260928':'b1e4aa8f307010fb7e5322a6cec6403665e32d0e',
'research/mixed-motion-20260929':'fc6d2c2972f6c234f06112576610d26525795cf8',
'research/q-chorded-w22-audit-20261006':'a8fc6be077250441e627077ee33e15b7f9c22e10',
'research/q-defect-20261006':'91849ffc04cc1e21193fbe3fddae2947072f7093',
'research/q-defect-lifting-20261006':'335c78d1d5f9e6f9c1058601039c237b4daaf221',
'research/transport-projection-20261004':'335c78d1d5f9e6f9c1058601039c237b4daaf221',
'research/triangular-lattice-20260928':'578bd83c3a47d9a2b9eeed6dc6cbd2651c0f1793',
'research/two-partition-w22-audit-20261006':'a0d51399b6fa9bd5b057b8cac910191a92f4f519'}
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def git(*args):return subprocess.check_output(['git',*args],text=True).strip()
def refs():return {ref:sha for sha,ref in (line.split() for line in git('ls-remote','--refs','origin').splitlines())}
def api(path,pages=False):return json.loads(subprocess.check_output(['gh','api']+(['--paginate','--slurp'] if pages else [])+['repos/'+REPO+'/'+path]))
def make_plan(snapshot,targets,main,ancestor,open_branches,active):
    require(snapshot.get('refs/heads/main')==main,'main moved');result=[]
    for b,s in targets.items():
        require(b.startswith(('research/','maintenance/')) and b!='main','invalid cleanup target')
        require(b not in open_branches and b not in active,'PR or workflow still uses '+b)
        tag='refs/tags/'+PREFIX+b;head='refs/heads/'+b
        require(snapshot.get(tag,s)==s,'archive conflict: '+b);require(ancestor(s,main),'unmerged history: '+b)
        if head not in snapshot:
            require(snapshot.get(tag)==s,'missing branch without exact archive: '+b)
            result.append(dict(branch=b,sha=s,archive_tag=PREFIX+b,create=False,delete=False));continue
        require(snapshot[head]==s,'branch moved: '+b)
        result.append(dict(branch=b,sha=s,archive_tag=PREFIX+b,create=tag not in snapshot,delete=True))
    return result

def selftest():
    m='a'*40;s='b'*40;b='research/demo';targets={b:s};ok={'refs/heads/main':m,'refs/heads/'+b:s}
    require(len(make_plan(ok,targets,m,lambda a,c:True,set(),set()))==1,'valid guard rejected')
    cases=[(dict(ok,**{'refs/heads/main':'c'*40}),targets,True,set(),set()),(dict(ok,**{'refs/heads/'+b:'c'*40}),targets,True,set(),set()),
           (dict(ok,**{'refs/tags/'+PREFIX+b:'c'*40}),targets,True,set(),set()),(ok,targets,False,set(),set()),(ok,targets,True,{b},set()),(ok,targets,True,set(),{b}),
           ({'refs/heads/main':m},targets,True,set(),set()),(ok,{'main':m},True,set(),set())]
    for snapshot,t,anc,opened,active in cases:
        try:make_plan(snapshot,t,m,lambda a,c:anc,opened,active)
        except RuntimeError:continue
        raise RuntimeError('unsafe cleanup plan accepted')
    return dict(status='PASS',unsafe_plans_rejected=len(cases))

def main():
    tests=selftest();source=os.environ['GITHUB_SHA']
    require(os.environ.get('GITHUB_REPOSITORY')==REPO and os.environ.get('GITHUB_REF')=='refs/heads/main','wrong context')
    pull=api('pulls/11');require(pull['merged'] and pull['base']['ref']=='main','integration PR not merged')
    targets=dict(TARGETS);targets['maintenance/unified-results-20261006']=os.environ['EXPECTED_INTEGRATION_HEAD']
    require(pull['head']['sha']==targets['maintenance/unified-results-20261006'],'integration PR head mismatch')
    subprocess.run(['git','fetch','--no-tags','origin','+refs/heads/*:refs/remotes/origin/*','+refs/tags/*:refs/tags/*'],check=True)
    opened=[p for page in api('pulls?state=open&per_page=100',True) for p in page]
    open_branches={p[side]['ref'] for p in opened for side in ('head','base') if p[side].get('repo') and p[side]['repo']['full_name']==REPO}
    runs=[r for page in api('actions/runs?per_page=100',True) for r in page['workflow_runs']]
    active={r['head_branch'] for r in runs if r['status']!='completed' and str(r['id'])!=os.environ['GITHUB_RUN_ID']}
    def ancestor(a,b):
        p=subprocess.run(['git','merge-base','--is-ancestor',a,b]);require(p.returncode in (0,1),'ancestry unavailable');return p.returncode==0
    before=refs();plan=make_plan(before,targets,source,ancestor,open_branches,active);make_plan(refs(),targets,source,ancestor,open_branches,active)
    flags=[];specs=[]
    for r in plan:
        tag='refs/tags/'+r['archive_tag'];head='refs/heads/'+r['branch']
        if r['create']:flags.append('--force-with-lease='+tag+':');specs.append(r['sha']+':'+tag)
        if r['delete']:flags.append('--force-with-lease='+head+':'+r['sha']);specs.append(':'+head)
    auth=base64.b64encode(('x-access-token:'+os.environ['GH_TOKEN']).encode()).decode();print('::add-mask::'+auth,flush=True)
    env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+auth)
    if specs:subprocess.run(['git','push','--atomic','--porcelain',*flags,'origin',*specs],env=env,check=True)
    after=refs()
    for r in plan:
        require('refs/heads/'+r['branch'] not in after,'branch not deleted');require(after.get('refs/tags/'+r['archive_tag'])==r['sha'],'archive not retained')
        r.pop('create');r.pop('delete');r['status']='ARCHIVED_AND_DELETED'
    removed={k for k in before if k.startswith('refs/heads/') and k not in after};require(removed<={'refs/heads/'+b for b in targets},'unrelated branch disappeared')
    require(all(after.get(k)==s for k,s in before.items() if k.startswith('refs/tags/')),'old archive changed')
    report=dict(schema='hn-unified-branch-closeout-v1',status='PASS',date='2026-10-06',time_utc=datetime.now(timezone.utc).isoformat(),run_id=os.environ['GITHUB_RUN_ID'],
        main_at_cleanup=source,merged_pr=11,merge_commit=pull['merge_commit_sha'],targets=plan,old_tag_count=sum(k.startswith('refs/tags/') for k in before),old_tags_unchanged=True,
        heads_before={k[11:]:v for k,v in before.items() if k.startswith('refs/heads/')},heads_after={k[11:]:v for k,v in after.items() if k.startswith('refs/heads/')},guard_selftests=tests,
        guards=['explicit targets','exact SHA','merged ancestry','no open PR','no active workflow','tag conflict refusal','atomic archive-and-delete','per-ref expected-SHA leases','remote readback'],
        scope='Reference cleanup only. Original commits and evidence preserved. Mathematical UNKNOWNs unchanged. Unknown concurrent branches are not deleted.')
    out=Path(os.environ['RUNNER_TEMP'])/'final';out.mkdir();(out/'archive-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    sources=Path('docs/integration_sources.json');data=json.loads(sources.read_text());data['status']='MERGED_AND_ARCHIVED';data['remote_cleanup']=report;sources.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    branches=Path('docs/BRANCHES.md');branches.write_text(branches.read_text()+'\n## 已完成的远端收尾\n\nPR #11已合并到main；其包含原PR #7–10全部研究提交与本地独有历史。11个旧研究分支及本次维护分支\n均已建立同SHA归档标签并删除旧指针。原有标签未变。操作时保留的分支、精确SHA、逐项归档结果及\n运行号均记录在[integration_sources.json](integration_sources.json)的remote_cleanup字段。\n旧PR已归入统一整合，不重复计数成果。会过期的Actions包不是唯一备份，原始Git提交由永久标签保留。\n')
    current=Path('docs/CURRENT.md');current.write_text(current.read_text()+'\n## 7. 发布与分支归档已完成\n\n全部本地可读取成果和远端研究提交通过[PR #11](https://github.com/rsgcsg/math-research/pull/11)归入main。\n11个研究分支及1个维护分支已按精确SHA归档；未认证实验仍隔离保留，所有数学UNKNOWN原样保存。\n本次清理不新增定理编号，也没有普通HN新界；当前唯一研究入口就是本页。\n')
    static=json.loads(subprocess.check_output(['python3','-S','research/check_integration.py']));require(static['status']=='PASS','post-cleanup static audit')
    report['post_record_static_audit']=static;data['remote_cleanup']=report;sources.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');(out/'archive-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    require(set(git('diff','--name-only').splitlines())=={'docs/BRANCHES.md','docs/CURRENT.md','docs/integration_sources.json'},'unexpected record changes')
    subprocess.run(['git','diff','--check'],check=True);subprocess.run(['git','add','docs/BRANCHES.md','docs/CURRENT.md','docs/integration_sources.json'],check=True)
    subprocess.run(['git','commit','-m','maintenance: record exact archived branch heads and completed unified publication'],check=True)
    require(refs().get('refs/heads/main')==source,'main moved before receipt publication');subprocess.run(['git','push','--porcelain','origin','HEAD:refs/heads/main'],env=env,check=True)
    subprocess.run(['git','fetch','origin','+refs/tags/*:refs/tags/*'],check=True);subprocess.run(['git','branch','final-export','HEAD'],check=True)
    subprocess.run(['git','bundle','create',str(out/'full-history.bundle'),'final-export','--tags'],check=True);subprocess.run(['git','archive','--format=zip','HEAD','-o',str(out/'source.zip')],check=True)
    (out/'publication.json').write_text(json.dumps(dict(commit=git('rev-parse','HEAD'),tree=git('rev-parse','HEAD^{tree}'),status='ARCHIVE_AND_RECEIPT_PUBLISHED'),indent=2)+'\n')
    print(json.dumps(dict(status='PASS',archived=len(plan),remaining=sorted(report['heads_after']))),flush=True)
if __name__=='__main__':main()
