"""One-use source-bound publication; not a substitute for a mathematical proof."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import time

BASE = '94df41d92d32bfa6e945ee05e32c413f59d567a1'
BRANCH = 'research/povm-vector-threshold-20261008'
SCIENCE = {
    'docs/proofs/binary_povm_vector_threshold.md': '78910cc7cfa231735e5ab043a95264b51cdb8700aebab5505e757162482415d2',
    'research/binary_povm_arithmetic.py': '8fcad807dac7a0267502ce21df6309de5ef92385a4828d0702ac7829c89da6c7',
    'research/verify_binary_povm_threshold.py': 'a122e2f65c273954231a90c170c859865b93b460b5e4f914cf2bb81e0a526fe6',
    'certificates/binary_povm_threshold.json': '53bd8b975abcc0adc1e648550977ef9029ca5d9b4563af9437e5321976d7a2fe',
}
INDICES = {
    'Makefile': '48f3a0b9f8ac5512cb272cddb486e94edc7f5c5c1810f50dc46a25083efdeb83',
    'README.md': '46d9f2d42b6d45e6e6d36377ec2e73ea34b76cc1b2543bd442289c8af871aec9',
    'docs/CURRENT.md': '223b0ef483085ab758bd6594aea3054648eff7e1c900106febfac87c5d0ca6e2',
    'docs/RESULTS.md': '4c51debbd3f067555ff8cb9b9ef1bd0f8103d76b58bb9d2cdddba6d294a9e231',
    'docs/ROUTES.md': 'b2938c977fd5c59c5493289d5569c46e50931c13b80f29bfe7679b13d209b41b',
    'references/LITERATURE_MAP.md': '9562cc14cdc7db8b832c140c130794ecdfaf7ab01cc2ca90d84d4819484b9f55',
}
TEMPORARY = ['.maintenance/binary_indices.patch', '.maintenance/seal_binary.py',
             '.github/workflows/binary-povm-seal.yml']


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args]).decode().strip()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def commit_tree(tree, parent, message):
    return subprocess.check_output(['git', 'commit-tree', tree, '-p', parent],
                                   input=message+'\n', text=True).strip()


def main():
    need(__debug__, 'optimized mode disabled')
    need(os.environ['GITHUB_REPOSITORY'] == 'rsgcsg/math-research', 'repository')
    need(os.environ['GITHUB_REF'] == 'refs/heads/'+BRANCH, 'branch')
    source = os.environ['GITHUB_SHA']
    need(git('rev-parse', 'HEAD') == source, 'source checkout')
    need(not git('status', '--porcelain'), 'unclean source')
    need(all(sha(Path(p).read_bytes()) == h for p, h in SCIENCE.items()), 'science hashes')
    patch = Path(TEMPORARY[0]).read_bytes()
    # One explicitly reviewed whitespace correction to a patch header, if present.
    patch = patch.replace(b'\n diff --git a/README.md', b'\ndiff --git a/README.md')
    need(sha(patch) == '059298b1ca2574cb0435042089b95d3abc380ba68e00eaac31e58dbb8cb2d288', 'indices patch hash')
    tmp = Path(os.environ['RUNNER_TEMP'])
    pp = tmp/'indices.patch'; pp.write_bytes(patch)
    subprocess.run(['git', 'apply', '--check', str(pp)], check=True)
    subprocess.run(['git', 'apply', str(pp)], check=True)
    need(all(sha(Path(p).read_bytes()) == h for p, h in INDICES.items()), 'index result hashes')
    for p in TEMPORARY:
        Path(p).unlink()
    receipt = Path('certificates/binary_povm_validation.json')
    dump(receipt, {'status': 'VERIFICATION_IN_PROGRESS'})
    scientific = git('ls-tree', '-r', '--name-only', BASE, 'research', 'certificates').splitlines()
    def check_old():
        for p in scientific:
            need(Path(p).read_bytes() == subprocess.check_output(['git','show',BASE+':'+p]), 'changed inherited '+p)
    check_old()
    plan = subprocess.check_output(['make', '-n', 'check'], text=True).splitlines()
    need(len(plan) == len(set(plan)) == 75, 'full command plan')
    all_source = git('ls-files', 'research', 'Makefile').splitlines()
    frozen = {p:sha(Path(p).read_bytes()) for p in all_source}
    out = Path('certificates/binary_povm_remote'); out.mkdir()
    # Snapshot before producing runtime evidence; test full entry in another tree.
    subprocess.run(['git','add','-A','--',*INDICES,*TEMPORARY,str(receipt)], check=True)
    snapshot = commit_tree(git('write-tree'), source, 'verification snapshot of reviewed binary POVM source')
    full = tmp/'full-check'
    subprocess.run(['git','worktree','add','--detach',str(full),snapshot], check=True)
    commands = [(['make','check-binary-povm'],0),
                (['make','check-compact-mixing','check-radical-transfer'],0),
                (['python3','-O','-S','research/verify_binary_povm_threshold.py'],1),
                (['python3','-S','research/check_integration.py'],0)]
    rows = []
    for i,(cmd,expected) in enumerate(commands):
        started=time.monotonic()
        p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        log=out/f'{i}.log';log.write_bytes(p.stdout)
        rows.append(dict(command=cmd,returncode=p.returncode,expected_returncode=expected,
                         seconds=round(time.monotonic()-started,3),log=str(log),sha256=sha(p.stdout)))
        print('CHECK',i,p.returncode,flush=True)
        need(p.returncode==expected, 'scoped check failed '+str(cmd))
        if expected:
            need(b'Binary POVM verifier requires non-optimized Python' in p.stdout, 'wrong rejection')
    started=time.monotonic()
    p=subprocess.run(['timeout','180s','make','check'],cwd=full,
                     stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    full_log=out/'bounded-full-check.log';full_log.write_bytes(p.stdout)
    full_record=dict(command=['timeout','180s','make','check'],returncode=p.returncode,
                     seconds=round(time.monotonic()-started,3),source_commit=snapshot,
                     log=str(full_log),sha256=sha(p.stdout),
                     scope='Separate identical-source worktree; exit124 means incomplete, not full coverage or a mathematical counterexample.')
    print('FULL_ENTRY',p.returncode,flush=True)
    need(p.returncode in (0,124), 'full entry encountered a non-timeout error')
    need(frozen=={p:sha(Path(p).read_bytes()) for p in all_source}, 'source changed in replay')
    check_old()
    manifest_hash=sha(json.dumps(frozen,sort_keys=True,separators=(',',':')).encode())
    report=dict(schema='hn-binary-povm-validation-v1',status='PASS_SCOPED_CHECKS',date='2026-10-08',
                base_commit=BASE,workflow_parent=source,run_id=os.environ['GITHUB_RUN_ID'],
                scientific_files=SCIENCE,reviewed_indices=INDICES,source_manifest=frozen,
                source_manifest_sha256=manifest_hash,commands=rows,full_make_plan=plan,
                bounded_full_check=full_record,full_make_check_passed=p.returncode==0,
                inherited_scientific_files_unchanged=len(scientific),
                new_claims_lean_formalized=False,new_hn_bound=False,full15_decided=False,
                other_research_branches_merged=False,
                scope='Fresh exact finite graph/POVM evidence, inherited compact/radical calibrations and static checks. General vector-threshold, conic alternative and arbitrary-dimension rigidity use the written proof, not finite samples. No priority claim. Original local consolidation histories are not imported by this focused publication.')
    dump(receipt,report)
    p=subprocess.run(['python3','-S','research/check_integration.py'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
    log=out/'final-static.log';log.write_bytes(p.stdout);need(p.returncode==0,'final static')
    report['final_static']=json.loads(p.stdout);report['final_static_log_sha256']=sha(p.stdout)
    dump(receipt,report)
    subprocess.run(['git','diff','--check'],check=True)
    expected=set(INDICES)|set(TEMPORARY)|{str(receipt)}|{str(p) for p in out.iterdir()}
    actual=set(git('diff','HEAD','--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    need(actual==expected,'unexpected changed paths '+str(actual^expected))
    subprocess.run(['git','add','-f','--',*INDICES,str(receipt),str(out)],check=True)
    subprocess.run(['git','commit','-m','verification: seal vector-threshold evidence and exact bounded full-check outcome'],check=True)
    need(git('ls-remote','origin','refs/heads/'+BRANCH).split()[0]==source,'branch moved')
    auth=base64.b64encode(('x-access-token:'+os.environ['GH_TOKEN']).encode()).decode()
    env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+auth)
    subprocess.run(['git','push','--porcelain','origin','HEAD:refs/heads/'+BRANCH],check=True,env=env)
    final=tmp/'published';final.mkdir()
    subprocess.run(['git','branch','binary-export','HEAD'],check=True)
    subprocess.run(['git','bundle','create',str(final/'source.bundle'),'binary-export','--tags'],check=True)
    subprocess.run(['git','archive','--format=zip','HEAD','-o',str(final/'source.zip')],check=True)
    dump(final/'publication.json',dict(status='PUBLISHED_TO_RESEARCH_BRANCH',commit=git('rev-parse','HEAD'),tree=git('rev-parse','HEAD^{tree}'),run_id=os.environ['GITHUB_RUN_ID']))
    print('PUBLISHED',git('rev-parse','HEAD'),flush=True)


if __name__=='__main__':
    main()
