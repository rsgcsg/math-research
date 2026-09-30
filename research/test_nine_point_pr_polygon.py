#!/usr/bin/env python3
"""Reject mathematically invalid local polygon certificates, after rehashing."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'research/verify_nine_point_pr_polygon.py'
C=json.loads((ROOT/'certificates/nine_point_pr_polygon.json').read_text())
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def bad_weight(d):d['vertices_of_projected_polytope'][0]['support'][0]['weight']='1'
def bad_partition(d):
    z=d['vertices_of_projected_polytope'][0]['support'][0]['partition']
    z[d['vertices'].index(5535)]=z[d['vertices'].index(877)]
mutations={
    'missing-certified-P-event':lambda d:d['P_events'].remove([229,877]),
    'missing-local-unit-edge':lambda d:d['induced_unit_edges'].pop(),
    'wrong-rational-weight':bad_weight,
    'unit-edge-monochromatic':bad_partition,
}
with tempfile.TemporaryDirectory() as folder:
    for name,mutate in mutations.items():
        d=deepcopy(C);mutate(d);d.pop('certificate_sha256')
        d['certificate_sha256']=hashlib.sha256(canonical(d)).hexdigest()
        p=Path(folder)/(name+'.json');p.write_text(json.dumps(d))
        run=subprocess.run([sys.executable,'-S',str(SCRIPT),'--certificate',str(p)],capture_output=True,text=True)
        assert run.returncode!=0,name
        assert 'Saved receipt differs' not in run.stderr,(name,'Only receipt mismatch rejected the mutation')
run=subprocess.run([sys.executable,'-O',str(SCRIPT)],capture_output=True,text=True)
assert run.returncode!=0 and 'run without -O' in run.stderr
print('PASS: four rehashed mathematical mutations rejected; optimized mode fails closed')
