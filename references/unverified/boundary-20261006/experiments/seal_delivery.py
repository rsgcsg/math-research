"""Preserve exactly the completed or incomplete state, without promoting a search."""
from pathlib import Path
import os,signal,time,subprocess,json,hashlib,zipfile,shutil,traceback,platform
W=Path(__file__).resolve().parents[1];R=W/'repo';V=W/'verification';V.mkdir(exist_ok=True)
def git(*args,check=True):return subprocess.run(['git','-C',str(R),*args],capture_output=True,text=True,check=check)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Wait only for this turn's explicit supervisor. No unrelated process is terminated.
p=W/'verification/finish.pid';deadline=time.monotonic()+360
if p.exists():
 pid=int(p.read_text())
 while Path(f'/proc/{pid}/stat').exists() and time.monotonic()<deadline:
  if Path(f'/proc/{pid}/stat').read_text().split()[2]=='Z':break
  time.sleep(2)
report={'schema':'research-delivery-v1','date':'2026-10-06','base_commit':'91849ffc04cc1e21193fbe3fddae2947072f7093','ordinary_hn_new_bound':False,'full15_decided':False}
try:state=json.loads((V/'final_jobs.json').read_text())
except (OSError,ValueError):state={'status':'INCOMPLETE_NO_FINAL_RECEIPT'}
report['local_verification']=state
if state.get('status')=='PASS':
 mf=R/'Makefile';s=mf.read_text()
 if 'check: check-exact-pr-boundary' not in s:mf.write_text(s+'\ncheck: check-exact-pr-boundary\n')
 rp=R/'README.md';s=rp.read_text();rp.write_text('## 2026-10-06：固定局部边界的精确证书\n\n[22点P/R尖点上的Q区间及完整范围](docs/proofs/exact_local_pr_boundary_interval.md)。\n这不是全Y或full15正律，也不是普通HN新界。新增检查：`make check-exact-pr-boundary`。\n\n'+s)
 ledger=R/'docs/RESULTS.md';s=ledger.read_text();ledger.write_text(s+'\n\n## 2026-10-06 未编号接续：精确局部边界\n\n在T165分支的固定22点局部模型上，p=1/27,r=14/27时的完整q区间已由双侧整数对偶与精确有理正律闭合。\n[完整证明](proofs/exact_local_pr_boundary_interval.md)。\n为避免并行分支已有T160编号冲突，本条不抢占新T编号；一般HN/full15状态不变。\n')
 route=R/'docs/ROUTES.md';route.write_text('## 2026-10-06：固定22点边界优化终止\n\n精确q区间见[新证明](proofs/exact_local_pr_boundary_interval.md)。\n此固定局部截面已闭合，不再重复端点调权；后续必须检验V外完整运输与共同模式延拓。\n局部正律不得升级为全Y正律。\n\n'+route.read_text())
 # Preserve discovery separately: its numerical results are not used by the independent checker.
 assets=['research/check_exact_local_pr_boundary.py','certificates/exact_local_pr_boundary_interval.json','certificates/exact_local_pr_boundary_interval_validation.json','docs/proofs/exact_local_pr_boundary_interval.md','docs/CURRENT.md','docs/RESULTS.md','docs/ROUTES.md','README.md','Makefile']
 for rel in assets:assert (R/rel).is_file()
 git('config','user.name','Math Research Assistant');git('config','user.email','research-assistant@users.noreply.github.com')
 git('add','--',*assets);git('diff','--cached','--check')
 git('commit','-m','research: certify both endpoints of the fixed 22-point PR boundary')
 report['result_kind']='EXACT_LOCAL_BOUNDARY_ONLY'
else:
 report['result_kind']='INCOMPLETE_RESEARCH_CHECKPOINT'
 # Never publish unverified mathematical candidates as accepted repository results.
 candidate=R/'certificates/exact_local_pr_boundary_interval.json'
 if candidate.exists():
  for rel in ['certificates/exact_local_pr_boundary_interval.json','certificates/exact_local_pr_boundary_interval_validation.json','docs/proofs/exact_local_pr_boundary_interval.md','research/check_exact_local_pr_boundary.py']:
   p=R/rel
   if p.exists():q=W/'unverified'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),str(q))
 report['note']='No new theorem is claimed; numerical discovery and failures are retained outside accepted mathematical evidence.'
# Exact, independently derivable consequence of published T165: labelled a corollary, not a new breakthrough.
assert 4721*27-127352==115
corr='''# T165的一个定量推论（不是新的HN突破）\n\n从已发布的 `500q <= 114552p+25600r-17171` 和 `2r-p<=1` 直接得到\n\n    127352p-500q >= 4371.\n\n证明：第二式乘12800得到25600r<=12800p+12800，代入第一式即可。\n因此若q>=7/10，则p>=4721/127352=1/27+115/3438504。\n这只是已证明不等式的精确线性推论，不假设所有full15律都满足q>=7/10，\n不排除q较小的可行律，不给普通HN新界，也不作首创声明。\n'''
(W/'t165_quantitative_corollary.md').write_text(corr)
if (R/'.git').exists():
 report['local_commit']=git('rev-parse','HEAD').stdout.strip();report['local_tree']=git('rev-parse','HEAD^{tree}').stdout.strip();report['working_tree_status']=git('status','--short').stdout
 patch=Path('/mnt/data/math_research_boundary_20261006.patch');patch.write_text(git('diff','--binary',report['base_commit'],'HEAD').stdout)
 bundle=Path('/mnt/data/math_research_boundary_20261006.bundle');git('bundle','create',str(bundle),'HEAD')
 report['patch_sha256']=h(patch);report['bundle_sha256']=h(bundle)
 # Attempt a non-forced push only if actual research passed. Capture failure verbatim.
 if state.get('status')=='PASS':
  try:
   push=git('push','origin','HEAD:refs/heads/research/complete-boundary-20261006',check=False)
   (V/'push.log').write_text(push.stdout+push.stderr);report['push_returncode']=push.returncode;report['remote_published']=push.returncode==0
  except Exception:report['remote_published']=False;report['push_error']=traceback.format_exc()
 else:report['remote_published']=False;report['push_not_attempted_reason']='No completed new result'
report['verification_scope']='Only recorded successful independent runs; no new single whole-repository make check is claimed.'
(V/'delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Stop only any surviving explicitly identified children from this invocation; keep their incomplete logs.
for rel in ['experiments/local.pid','verification/replay.pid','verification/saturation.pid','verification/finish.pid']:
 p=W/rel
 if p.exists():
  pid=int(p.read_text());cmd=Path(f'/proc/{pid}/cmdline')
  if cmd.exists() and str(W).encode() in cmd.read_bytes():
   try:os.kill(pid,signal.SIGTERM)
   except ProcessLookupError:pass
archive=Path('/mnt/data/math_research_boundary_20261006.zip')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for top in ['verification','experiments','unverified']:
  folder=W/top
  if folder.exists():
   for p in folder.rglob('*'):
    if p.is_file() and p.name!='local_oracle' and p.suffix!='.pid':z.write(p,str(p.relative_to(W)))
 z.write(W/'t165_quantitative_corollary.md','t165_quantitative_corollary.md')
 if (R/'.git').exists():
  for rel in git('ls-files').stdout.splitlines():
   p=R/rel
   if p.is_file():z.write(p,'repo/'+rel)
 for p in [Path('/mnt/data/math_research_boundary_20261006.patch'),Path('/mnt/data/math_research_boundary_20261006.bundle')]:
  if p.exists():z.write(p,p.name)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
