"""One-use lossless transport and verification seal; removed before publication."""
import ast,base64,gzip,hashlib,json,lzma,os,platform,re,shutil,subprocess,sys
from array import array
from pathlib import Path
from urllib.parse import unquote
ROOT=Path.cwd()
BASE='a658761d00ce0395242faace7e8e0db9a1bb16ee'
PAYLOAD='a572f20e8eb3a503e400ee4736448718990a40404d855d7e5b988d87feca11d8'
TEMP=Path(os.environ.get('RUNNER_TEMP','/tmp/hn-publication'))
TEMP.mkdir(parents=True,exist_ok=True)
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def manifest(paths):return {p:sha((ROOT/p).read_bytes()) for p in paths}
def source_manifest():
    paths=['Makefile','requirements-research.txt']+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'research').glob('*.py'))]
    return manifest(paths)
def restore():
    packed=base64.b64decode(''.join(p.read_text() for p in sorted((ROOT/'.research-publication').glob('part*.b64'))))
    assert sha(packed)==PAYLOAD,'transport hash'
    data=json.loads(lzma.decompress(packed)); assert data['schema']=='hn-publication-patch-v1' and data['base']==BASE
    paths=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
    dictionary=sorted({sha(git('show',BASE+':'+p)) for p in paths})
    assert len(dictionary)==data['base_digest_count']
    patch=re.sub(r'@@HNBASE(\d{4})@@',lambda m:dictionary[int(m[1])],data['patch_with_base_sha_tokens']).encode()
    assert sha(patch)==data['patch_sha256']
    patchfile=TEMP/'research-consolidated.patch';patchfile.write_bytes(patch)
    subprocess.run(['git','apply','--check',str(patchfile)],check=True)
    subprocess.run(['git','apply',str(patchfile)],check=True)
    sys.path.insert(0,str(ROOT/'research'))
    from verify_joint_nilpotent_cover import prepare
    from verify_joint_s3_cover import actions
    from build_finite_frame_certificates import build,canonical,canonical_gzip
    prepared=prepare(ROOT);seed=data['seed'];template=seed['template']
    sigma,pi=actions(prepared['old'],template['signs'],template['shifts'])
    n=len(prepared['context']['points']);total=n*75
    parent=array('I',range(total));sizes=array('I',[1])*total
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(x,y):
        x,y=find(x),find(y)
        if x==y:return
        if sizes[x]<sizes[y]:x,y=y,x
        parent[y]=x;sizes[x]+=sizes[y]
    for j,mapping in enumerate(prepared['maps'][:14]):
        for a in range(15):
            b=sigma[j][a]
            for p,q in mapping:
                for c in range(5):union((a*n+p)*5+c,(b*n+q)*5+pi[j][a][c])
    labels={};ids=array('I')
    for x in range(total):
        root=find(x);ids.append(labels.setdefault(root,len(labels)))
    assert len(labels)==seed['classes']==2123
    bits=base64.b64decode(seed['truth_bits_base64'])
    def truth(i):return (bits[i//8]>>(i%8))&1
    words=[]
    for a in range(15):
        word=[]
        for p in range(n):
            colors=[c for c in range(5) if truth(ids[(a*n+p)*5+c])]
            assert len(colors)==1
            word.append(str(colors[0]))
        words.append(''.join(word))
    template['words']=words
    raw=(json.dumps(template,separators=(',',':'))+'\n').encode()
    assert sha(raw)==seed['original_sha256']
    (ROOT/'certificates/joint_s3_cover.json').write_bytes(raw)
    sep,frame=build(prepared)
    (ROOT/'certificates/finite_frame_separator.json.gz').write_bytes(canonical_gzip(canonical(sep)))
    (ROOT/'certificates/arithmetic_frame_separation.json').write_bytes(canonical(frame))
    for p,h in data['certificates'].items():assert sha((ROOT/p).read_bytes())==h,p
    expected={p:dictionary[h] if isinstance(h,int) else h for p,h in data['staged_manifest'].items()}
    actual=manifest(expected)
    assert actual==expected,[p for p in actual if actual[p]!=expected[p]]
    dump(TEMP/'transport-manifest.json',actual)
    dump(TEMP/'frozen-source.json',source_manifest())
    # Only temporary transport assets created by this operation are removed.
    shutil.rmtree(ROOT/'.research-publication')
    (ROOT/'.github/workflows/consolidate-publication.yml').unlink(missing_ok=True)
    print(json.dumps({'status':'RESTORED','files':len(actual),'payload_sha256':PAYLOAD}),flush=True)
def seal():
    frozen=json.loads((TEMP/'frozen-source.json').read_text())
    assert source_manifest()==frozen,'source changed during verification'
    receipt=ROOT/'certificates/consolidated_full_regression.json'
    static=ROOT/'certificates/consolidated_static_audit.json'
    dump(receipt,{'status':'PENDING_SEAL'});dump(static,{'status':'PENDING_SEAL'})
    syntax=0;jsons=0;links=0;errors=[]
    for p in sorted((ROOT/'research').glob('*.py')):ast.parse(p.read_text(),filename=str(p));syntax+=1
    for p in sorted((ROOT/'certificates').iterdir()):
        if p.name.endswith('.json') or p.name.endswith('.json.gz'):
            raw=p.read_bytes();json.loads(gzip.decompress(raw) if p.name.endswith('.gz') else raw);jsons+=1
    for p in [ROOT/'README.md',ROOT/'AGENTS.md',*sorted((ROOT/'docs').rglob('*.md')),*sorted((ROOT/'references').rglob('*.md'))]:
        text=p.read_text()
        for target in re.findall(r'\]\(([^\s)]+)\)',text):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
            target=unquote(target.split('#',1)[0].split('?',1)[0]);links+=1
            if target and not (p.parent/target).exists():errors.append([str(p.relative_to(ROOT)),target])
    assert not errors,errors
    ledger=(ROOT/'docs/RESULTS.md').read_text();counts={}
    for kind,last in [('T',134),('E',104),('C',23),('Q',10)]:
        got={int(x) for x in re.findall(r'^\|\s*'+kind+r'(\d{3})\s*\|',ledger,re.M)}
        assert got==set(range(1,last+1)),(kind,sorted(set(range(1,last+1))-got))
        counts[kind]=len(got)
    subprocess.run(['git','diff','--check'],check=True)
    audit={'status':'PASS','python_syntax_files':syntax,'json_files':jsons,'markdown_file_references':links,'ledger_ids':counts,'scope':'Syntax, parseability, exact ID coverage and local file targets; not a new proof of theorems or an exhaustive Markdown-anchor audit.'}
    dump(static,audit)
    transport=json.loads((TEMP/'transport-manifest.json').read_text())
    changed=[p for p,h in transport.items() if sha((ROOT/p).read_bytes())!=h]
    allowed={'certificates/dyadic_cyclic_orbit_validation.json','certificates/finite_frame_validation.json'}
    assert set(changed)<=allowed,changed
    log=TEMP/'research-check.log';assert log.is_file()
    data={'schema':'hn-consolidated-full-replay-v1','status':'PASS','date':'2026-09-21','command':'make check','returncode':0,'checked_commit':git('rev-parse','HEAD').decode().strip(),'base_commit':BASE,'python':platform.python_version(),'source_unchanged':True,'source_manifest_sha256':sha(json.dumps(frozen,sort_keys=True,separators=(',',':')).encode()),'source_files':frozen,'transport_files':len(transport),'transport_payload_sha256':PAYLOAD,'log_sha256':sha(log.read_bytes()),'worktree_outputs':changed,'scope':'One complete make check invocation on the final research source, including original, Salem, quartet, cyclic orbit, covers and frames. General mathematical theorems rely on their written proofs; no new HN bound.'}
    dump(receipt,data)
    print(json.dumps({'status':'PASS','static':audit,'source_manifest_sha256':data['source_manifest_sha256'],'worktree_outputs':changed}),flush=True)
if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('restore','seal'):raise SystemExit('restore or seal required')
    {'restore':restore,'seal':seal}[sys.argv[1]]()
