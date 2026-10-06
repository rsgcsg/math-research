"""One-use final acceptance of the already completed, source-bound replay."""
import base64, gzip, hashlib, json, os, subprocess, sys, zipfile
from pathlib import Path
TESTED='7f630ef6686daa078c2aa637b4d6255d81f7ee3f'
RUN='37431407795'
SOURCE_HASH='328652e0ec6c9d8dd9d417f269fe3faeea40f21b590a4c94435c23e5b4d83231'
BRANCH='maintenance/unified-results-20261006'
ROOT=Path.cwd()
E=Path(os.environ['RUNNER_TEMP'])/'verified-evidence'
def git(*args):return subprocess.check_output(['git',*args])
def sha(x):return hashlib.sha256(x).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def require(ok,message):
    if not ok:raise RuntimeError(message)
def gzip_write(p,raw):
    b=bytearray(gzip.compress(raw,mtime=0));b[9]=255;p.write_bytes(b)
def main():
    source=os.environ['GITHUB_SHA']
    require(os.environ.get('GITHUB_REPOSITORY')=='rsgcsg/math-research','wrong repo')
    require(os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH,'wrong ref')
    run=json.loads(subprocess.check_output(['gh','api',f'repos/rsgcsg/math-research/actions/runs/{RUN}']))
    require(run['head_sha']==TESTED and run['status']=='completed' and run['conclusion']=='success','replay not complete/successful')
    coverage=read(E/'coverage.json')
    require(coverage['status']=='PASS' and coverage['source_commit']==TESTED,'aggregate mismatch')
    plan=read(E/'integration-shard-0/check-plan.json');frozen=read(E/'integration-shard-0/source-manifest.json')
    require(sha(canonical(frozen))==SOURCE_HASH,'frozen source hash')
    require(len(plan)==70 and len(plan)==len(set(plan)),'plan count')
    require(subprocess.check_output(['make','-n','check'],text=True).splitlines()==plan,'current plan differs')
    require(all(sha((ROOT/p).read_bytes())==s for p,s in frozen.items()),'current research differs')
    allowed_outputs={'certificates/dyadic_cyclic_orbit_validation.json':{'elapsed_seconds'},'certificates/finite_frame_validation.json':{'python'}}
    output_review=[];commands=[]
    for k in range(8):
        d=E/f'integration-shard-{k}';r=read(d/'report.json')
        require(r['shard']==k and r['commit']==TESTED and r['status']=='PASS' and r['source_unchanged'],'failed shard')
        require(read(d/'check-plan.json')==plan and read(d/'source-manifest.json')==frozen,'shard source/plan mismatch')
        require(r['source_manifest_sha256']==SOURCE_HASH and r['plan_sha256']==sha(canonical(plan)),'report fingerprint')
        for row in r['commands']:
            i=row['index'];require(type(i) is int and i%8==k and row['command']==plan[i] and row['returncode']==0,'command failed/misassigned')
            require(sha((d/f'{i:03d}.log').read_bytes())==row['log_sha256'],'log hash');commands.append(row)
        for p in r['changed_files']:
            require(p in allowed_outputs,'unexpected verifier output: '+p)
            original=git('show',TESTED+':'+p);actual=(d/'outputs'/p).read_bytes();a=json.loads(original);b=json.loads(actual)
            changed={key for key in a.keys()|b.keys() if a.get(key)!=b.get(key)}
            require(changed<=allowed_outputs[p],'mathematical evidence changed: '+p)
            require((ROOT/p).read_bytes()==original,'historical report overwritten')
            output_review.append(dict(shard=k,path=p,changed_runtime_fields=sorted(changed),original_sha256=sha(original),runtime_sha256=sha(actual),original_bytes_retained=True))
    require(sorted(r['index'] for r in commands)==list(range(70)),'missing/duplicate command')
    changes={
      'Makefile':('4b9878c21797071dfb10c962197def7d3c4a1d65301af3149628496cb9e179d5','3ca3dac462ad5951f34ca3e72d716cef4c18732a7f3aabc50408e16abc5cc0fe',[('check-qd-family check-qd-family','check-qd-family')]),
      'docs/RESULTS.md':('48f5c4f6786632838bf5c34c74080c1610793431b618bcf79f92ae747dd0bde5','e4b898bf7a0d8f4825bc6940498ffa87333befb9f00048ff3a6b3405c5c6f91c',[('排除C025边际的原Y延拓','排除C031边际的原Y延拓')]),
      'docs/proofs/q_defect_lift.md':('bec35a568adeb7dbfb6d7d552609d00ad699b96be7298213cceae61b41ae2c5f','ed5d46eea93c9940dec5d87c6809f477810bebe85bad809b0cc5d3c28c2d7a1e',[
          ('# T162：九条真实 Q 链接的最优局部失配罚项','# T162交叉验证 / T168：九条真实 Q 链接的罚项与精确计数包络'),
          ('## 1. 固定对象与结论','> 统一编号：本页§1–3独立交叉验证T162；§4–5的四段计数包络与单外点方法边界记为T168。旧证书中的原始标签保留，见[编号映射](../ID_ALIASES.md)。\n\n## 1. 固定对象与结论')]),
      'docs/proofs/full15_support_exclusion.md':('ab1277af1731a11094bd5c1dbfaf34243e354dd937d9c418b9c489f10740e3da','ef1854741a10bf2794a4eef9d2b3506ea970105b530039bdcd8f43af43be2550',[('沿用描述性名称，避免覆盖尚未全量归并的历史T141–T143编号。','该描述性证明对应T147/T148的独立证据链；T141–T143现已另行恢复并统一索引。')])}
    edit_review=[]
    for p,(old,new,replacements) in changes.items():
        f=ROOT/p;require(sha(f.read_bytes())==old,'patch base mismatch: '+p);text=f.read_text()
        for a,b in replacements:
            require(text.count(a)==1,'ambiguous replacement: '+p);text=text.replace(a,b,1)
        f.write_text(text);require(sha(f.read_bytes())==new,'patch result mismatch: '+p);edit_review.append(dict(path=p,before_sha256=old,after_sha256=new))
    require(subprocess.check_output(['make','-n','check'],text=True).splitlines()==plan,'closeout changed check plan')
    final_source={p:sha((ROOT/p).read_bytes()) for p in frozen}
    require([p for p in frozen if frozen[p]!=final_source[p]]==['Makefile'],'research executable changed')
    require(all((ROOT/p).read_bytes()==git('show',TESTED+':'+p) for p in git('ls-tree','-r','--name-only',TESTED,'certificates').decode().splitlines()),'inherited certificate differs')
    bundle=ROOT/'certificates/unified_check_20261006.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(E.rglob('*')):
            if not p.is_file():continue
            info=zipfile.ZipInfo(str(p.relative_to(E)),date_time=(2026,10,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
    gzip_write(ROOT/'certificates/unified_source_manifests_20261006.json.gz',canonical(dict(tested=frozen,final=final_source,plan=plan))+b'\n')
    receipt=dict(schema='hn-unified-integration-v1',status='PASS',date='2026-10-06',tested_commit=TESTED,run_id=RUN,source_files=len(frozen),tested_source_manifest_sha256=SOURCE_HASH,
        final_source_manifest_sha256=sha(canonical(final_source)),command_count=70,commands=sorted(commands,key=lambda r:r['index']),plan_unchanged_after_cleanup=True,research_executables_unchanged=True,original_certificates_unchanged=True,
        runtime_output_review=output_review,reviewed_closeout_changes=edit_review,raw_evidence=dict(path=str(bundle.relative_to(ROOT)),sha256=sha(bundle.read_bytes())),
        preserved_histories=['f986eb0a0de1e33769efa54aa73c3eac9d2ff711','b532e71453935088000fa54738163c28180b17b8','86a7f6c53e0d4058fdee6990c6cc2946bbd4fad1','3dc223a711cc37dbb610b48f136a5c5308871421'],
        local_audit_summary=dict(zip_inputs_reviewed=32,prior_inventory_hashes_confirmed=31,scientific_contributions_identical=146,legacy_modules_renamed=4,related_import_or_description_adjustments=3,
            user_upload='math-research-q-defect-final-20261006(2).zip',user_upload_sha256='3093f98a32c6367eea4dba000d7b5d4dc4108a0310d927cee8e17c8cee2755f1',source='Local review in this consolidation; archive list and original refs retained in docs/integration_sources.json. Not inferred from CI pass.'),
        publication_status_at_seal='VERIFIED_ON_INTEGRATION_BRANCH; main merge and branch cleanup are separate operations',
        scope='All 70 distinct Python commands from make -n check passed in eight isolated workspaces on identical frozen research source. Not a single serial make check invocation. Post-test Makefile edit only removes a duplicate prerequisite and leaves the exact command plan unchanged; documentation labels are corrected. Tests replay scoped finite evidence, not formalize all general theorems. No new HN bound, full15 law or endpoint result.')
    for c in receipt['preserved_histories']:subprocess.run(['git','merge-base','--is-ancestor',c,source],check=True)
    dump(ROOT/'certificates/unified_integration_validation.json',receipt)
    sources=read(ROOT/'docs/integration_sources.json');sources['status']='VERIFIED_PENDING_MAIN_MERGE';sources['verification_commit']=TESTED;sources['verification_run']=RUN;sources['remote_cleanup']='NOT_EXECUTED';sources['current_local_audit']=receipt['local_audit_summary'];dump(ROOT/'docs/integration_sources.json',sources)
    current=ROOT/'docs/CURRENT.md';current.write_text(current.read_text()+'\n## 6. 2026-10-06整合验收\n\n冻结研究源码在GitHub运行37431407795中完成全部70条不同Python检查，八个隔离工作树均通过。\n这是完整命令覆盖，不是单次串行make check；最终仅去掉一个重复Makefile依赖，实际命令清单完全不变，\n并纠正历史编号引用。所有研究程序和原数学证书字节不变；两份旧报告仅出现运行元数据差异，\n原文件保留，新输出、日志和哈希另存[完整证据包](../certificates/unified_check_20261006.zip)。\n合并与分支清理的实际状态以[来源清单](integration_sources.json)为准，不能由测试PASS推断已发布。\n')
    readme=ROOT/'README.md';text=readme.read_text().replace('make -j2 check                 # 同一依赖图，两任务并行；需要足够内存\n','');readme.write_text(text+'\n本次70条检查完整覆盖已通过；采用隔离分组重放，未声称单次串行全仓运行。\n历史分支及本地独有提交均保留真实Git历史；合并与清理结果见[分支/来源](docs/BRANCHES.md)。\n')
    static=json.loads(subprocess.check_output(['python3','-S','research/check_integration.py']));require(static['status']=='PASS','static audit');receipt['final_static_audit']=static;dump(ROOT/'certificates/unified_integration_validation.json',receipt)
    subprocess.run(['git','diff','--check'],check=True)
    expected=set(changes)|{'README.md','docs/CURRENT.md','docs/integration_sources.json','certificates/unified_integration_validation.json','certificates/unified_check_20261006.zip','certificates/unified_source_manifests_20261006.json.gz'}
    changed=set(git('diff','--name-only').decode().splitlines())|set(git('ls-files','--others','--exclude-standard').decode().splitlines());require(changed==expected,'unexpected closeout paths: '+str(changed^expected))
    subprocess.run(['git','add','--',*sorted(expected)],check=True);subprocess.run(['git','commit','-m','verification: seal complete 70-command replay, preserve original evidence, and reconcile final aliases'],check=True)
    require(git('ls-remote','origin','refs/heads/'+BRANCH).decode().split()[0]==source,'integration branch moved')
    auth=base64.b64encode(('x-access-token:'+os.environ['GH_TOKEN']).encode()).decode();print('::add-mask::'+auth,flush=True)
    env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+auth)
    subprocess.run(['git','push','--porcelain','origin','HEAD:refs/heads/'+BRANCH],check=True,env=env)
    out=Path(os.environ['RUNNER_TEMP'])/'sealed';out.mkdir();subprocess.run(['git','branch','verified-export','HEAD'],check=True)
    subprocess.run(['git','bundle','create',str(out/'sealed-source.bundle'),'verified-export','--tags'],check=True);subprocess.run(['git','archive','--format=zip','HEAD','-o',str(out/'sealed-source.zip')],check=True)
    dump(out/'publication.json',dict(status='VERIFIED_BRANCH_PUBLISHED',commit=git('rev-parse','HEAD').decode().strip(),tree=git('rev-parse','HEAD^{tree}').decode().strip(),receipt=receipt));print(json.dumps(dict(status='PASS',commands=70,static=static,commit=git('rev-parse','HEAD').decode().strip())),flush=True)
if __name__=='__main__':main()
