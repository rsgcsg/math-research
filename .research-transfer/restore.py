"""One-use reviewed-source transfer and frozen full-replay receipt.

This does not search for new theorems or trust the producer's success status.
All new witnesses must pass the separate standard-library checkers.
"""
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import ast
import base64
import hashlib
import json
import lzma
import os
import platform
import re
import shutil
import subprocess
import sys

BASE = '384275f1c655794b8efccfd75dfd31a8bc2d03d2'
PAYLOAD = '97984b81be89ee411877ea33b79e517d6db8deddbc7813548380d230496a320c'
PORTFOLIO = 'f068a4c099fa47a6950de3d7ef233d83692e98203ca9cc0356b9fd84f680fa94'
ROOT = Path.cwd()
TEMP = Path(os.environ.get('RUNNER_TEMP', '/tmp/hn-mixed-ports'))
TEMP.mkdir(parents=True, exist_ok=True)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def manifest():
    paths = ['Makefile','requirements-research.txt']+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'research').glob('*.py'))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}

def restore():
    require(git('rev-parse', BASE+'^{commit}').decode().strip()==BASE, 'base identity')
    require(subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD']).returncode==0, 'base ancestry')
    parts = sorted((ROOT/'.research-transfer').glob('part*.b64'))
    require(len(parts)==6, 'six exact transport parts')
    packed = base64.b64decode(''.join(p.read_text() for p in parts), validate=True)
    require(sha(packed)==PAYLOAD, 'payload hash')
    data = json.loads(lzma.decompress(packed))
    require(data['schema']=='hn-mixed-ports-transfer-v1' and data['base']==BASE, 'transfer identity')
    paths = list(data['file_sha256'])
    for name in paths:
        p = PurePosixPath(name)
        require(not p.is_absolute() and '..' not in p.parts, 'unsafe path')
        require(name in ('Makefile','README.md') or p.parts[0] in ('docs','research','certificates','references'), 'unapproved target')
    patch = TEMP/'verified-research.patch'
    patch.write_text(data['patch'])
    subprocess.run(['git','apply','--check',str(patch)],check=True)
    subprocess.run(['git','apply',str(patch)],check=True)
    for path, expected in data['file_sha256'].items():
        require(sha((ROOT/path).read_bytes())==expected, 'restored source mismatch '+path)
    dump(TEMP/'transport-source.json',data['file_sha256'])
    dump(TEMP/'frozen-source.json',manifest())
    dump(TEMP/'replay-start.json',{'utc':datetime.now(timezone.utc).isoformat(),'commit':git('rev-parse','HEAD').decode().strip()})
    # Only this operation's temporary transfer directory is removed.
    shutil.rmtree(ROOT/'.research-transfer')
    print(json.dumps({'status':'EXACT_SOURCES_RESTORED','files':len(paths),'payload_sha256':PAYLOAD}),flush=True)

def seal():
    frozen = json.loads((TEMP/'frozen-source.json').read_text())
    require(manifest()==frozen, 'source changed during replay')
    transport = json.loads((TEMP/'transport-source.json').read_text())
    require(all(sha((ROOT/p).read_bytes())==s for p,s in transport.items()), 'reviewed text changed')
    require(sha((ROOT/'certificates/Y_pair_portfolio.json.gz').read_bytes())==PORTFOLIO, 'positive portfolio changed')
    # These legacy tests write runtime fields; retain original evidence bytes
    # only after comparing every mathematical field with the checked ancestor.
    restored = []
    runtime = {'certificates/dyadic_cyclic_orbit_validation.json':['elapsed_seconds'],
               'certificates/finite_frame_validation.json':['python']}
    for path, fields in runtime.items():
        old = git('show','HEAD:'+path);new = (ROOT/path).read_bytes()
        if old==new:
            continue
        a,b=json.loads(old),json.loads(new)
        for field in fields:
            a.pop(field,None);b.pop(field,None)
        require(a==b,'unexpected legacy certificate change '+path)
        (ROOT/path).write_bytes(old)
        restored.append({'path':path,'runtime_fields':fields})
    for p in (ROOT/'research').glob('*.py'):
        ast.parse(p.read_text(),filename=str(p))
    subprocess.run(['git','diff','--check'],check=True)
    log = TEMP/'full-check.log'
    require(log.is_file() and log.stat().st_size>0,'missing replay log')
    source_digest = sha(json.dumps(frozen,sort_keys=True,separators=(',',':')).encode())
    start=json.loads((TEMP/'replay-start.json').read_text())
    receipt={'schema':'hn-lattice-ports-remote-replay-v1','status':'PASS','date':'2026-09-29',
             'command':'make check','returncode':0,'checked_commit':start['commit'],
             'source_base_commit':BASE,'run_id':os.environ.get('GITHUB_RUN_ID'),
             'started_utc':start['utc'],'completed_utc':datetime.now(timezone.utc).isoformat(),
             'python':platform.python_version(),'source_file_count':len(frozen),
             'source_manifest_sha256':source_digest,'source_files':frozen,'source_unchanged':True,
             'complete_output_sha256':sha(log.read_bytes()),'payload_sha256':PAYLOAD,
             'portfolio_sha256':PORTFOLIO,'runtime_only_outputs_restored':restored,
             'entrypoints':['research/verify.py','check-salem','check-quartet','check-orbit','check-covers',
                 'check-frames','check-preparation','check-pricing','check-rotations','check-rank2','check-next',
                 'check-cyclic-translates','check-eta-support','check-lattice-ports'],
             'scope':'Actual one-pass full make check on the expanded and frozen sources, including the independent lattice geometry, '
                     'all-Y two-terminal positive portfolio and rational Q6 counterexample. Source expansion is bound by manifest; '
                     'the checked commit still contains the lossless transfer. The next commit publishes the exact expanded tree. '
                     'No HN bound, full fifteen-domain result or formal proof-assistant verification is claimed.'}
    dump(ROOT/'certificates/lattice_ports_remote_validation.json',receipt)
    print(json.dumps({'status':'FULL_REPLAY_SEALED','source_manifest_sha256':source_digest,'files':len(frozen)}),flush=True)

if __name__=='__main__':
    require(len(sys.argv)==2 and sys.argv[1] in ('restore','seal'),'restore or seal argument required')
    {'restore':restore,'seal':seal}[sys.argv[1]]()
