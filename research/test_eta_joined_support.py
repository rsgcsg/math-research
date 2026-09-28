"""Full exact replay, malformed-input rejection and small RUP calibrations."""
from copy import deepcopy
from itertools import product, combinations
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from audit_full_law_preparation import reconstruct
from verify_anchored_eta import read, require, geometry_check, algebra_tests, mutations
from verify_eta_joined_law import expand_compact, check as positive_check
from verify_eta_minimum_support import check_rup, replay_case
from eta_joined_cnf import build


def rejects(fn):
    try:fn()
    except (ValueError,AssertionError,KeyError,IndexError,TypeError):return
    raise ValueError('malformed input was accepted')


def negative_identity(c, summary):
    require(c['schema']=='eta-joined-minimum-support-v1', 'negative schema')
    require(c['input_semantic_sha256']==summary['semantic_sha256'], 'negative input')
    require(c['target']=='F union Gamma union complete eta', 'negative scope')
    require(len(c['cases'])==2 and [case['sigma'] for case in c['cases']]==[[0,1],[1,0]]
            and all(type(x) is int for case in c['cases'] for x in case['sigma']),
            'exhaustive two-state cases')


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    data,summary=reconstruct(root)
    gc=read(root/'certificates/eta_gauge_geometry.json')
    compact=read(root/'certificates/eta_joined_three_compact.json.gz')
    neg=read(root/'certificates/eta_joined_minimum_support.json.xz')
    wc=None  # The exact-three replay has no dependency on the intermediate two-word law.
    geometry=geometry_check(gc,data);algebra=algebra_tests()
    rejected=mutations(gc,wc,data,summary)
    law=expand_compact(compact,data,summary)
    positive=positive_check(law,data,summary)
    for name,change in {
      'root-truncation':lambda c:c.__setitem__('root_colors',c['root_colors'][:-1]),
      'extra-root':lambda c:c.__setitem__('root_colors',c['root_colors']+'0'),
      'invalid-root-color':lambda c:c.__setitem__('root_colors','9'+c['root_colors'][1:]),
      'duplicate-support-image':lambda c:c['matches'][0].__setitem__('support',[0,0,0]),
      'nonpermutation-palette':lambda c:c['matches'][0]['palettes'].__setitem__(0,[0]*5),
      'wrong-word-hash':lambda c:c['word_sha256'].__setitem__(0,'0'*64),
      'changed-kernel':lambda c:c['kernel_Y_indices'].pop(),
      'changed-full-domain':lambda c:c['full_motions'].append(0),
      'changed-pair':lambda c:c['pair_records'][0].__setitem__(3,4641),
      'false-weights':lambda c:c.__setitem__('weights',['1/2','1/4','1/4']),
    }.items():
        bad=deepcopy(compact);change(bad)
        def trial():positive_check(expand_compact(bad,data,summary),data,summary)
        rejects(trial);rejected.append(name)
    negative_identity(neg,summary)
    for name,change in {
      'negative-schema':lambda c:c.__setitem__('schema','other-query'),
      'negative-input':lambda c:c.__setitem__('input_semantic_sha256','0'*64),
      'negative-target':lambda c:c.__setitem__('target','full fifteen domains'),
      'missing-support-case':lambda c:c['cases'].pop(),
      'duplicate-support-case':lambda c:c['cases'].__setitem__(1,c['cases'][0]),
    }.items():
        bad=deepcopy(neg);change(bad)
        rejects(lambda:negative_identity(bad,summary));rejected.append(name)
    reports=[]
    for case in neg['cases']:
        built=build(data,law,case['sigma'])
        reports.append(dict(sigma=case['sigma'],cnf_sha256=built['cnf_sha256'],**replay_case(case,built)))
        for name,change in {
          'CNF-hash':lambda c:c.__setitem__('cnf_sha256','0'*64),
          'initial-ID-range':lambda c:c['initial_clause_ids'].__setitem__(0,len(built['clauses'])+1),
          'initial-ID-type':lambda c:c['initial_clause_ids'].__setitem__(0,True),
          'proof-no-empty':lambda c:c['rup_clauses'].pop(),
          'proof-premature-empty':lambda c:c.__setitem__('rup_clauses',[[]]),
          'proof-fresh-variable':lambda c:c['rup_clauses'].__setitem__(0,[built['nv']+1]),
          'proof-after-empty':lambda c:c['rup_clauses'].append([1]),
        }.items():
            bad=deepcopy(case);change(bad)
            rejects(lambda:replay_case(bad,built));rejected.append(str(case['sigma'])+':'+name)
    # Enumerate every nonempty CNF from the eight non-tautological clauses on
    # two variables; brute truth tables cross-check each claimed RUP resolvent.
    small=[list(c) for c in [(1,),(-1,),(2,),(-2,),(1,2),(1,-2),(-1,2),(-1,-2)]]
    calibration=0
    for mask in range(1,256):
        cnf=[c for i,c in enumerate(small) if mask>>i&1]
        models=[bits for bits in product([False,True],repeat=2)
                if all(any(bits[abs(v)-1]==(v>0) for v in c) for c in cnf)]
        if models:
            rejects(lambda:check_rup(cnf,[[]]))
        else:
            # All unsatisfiable two-variable formulae have this elementary
            # resolution/RUP proof or are already refuted by unit propagation.
            try:check_rup(cnf,[[]])
            except ValueError:
                check_rup(cnf,[[1],[]])
        calibration+=1
    for filename in ['verify_eta_joined_law.py','verify_eta_minimum_support.py','test_eta_joined_support.py']:
        proc=subprocess.run([sys.executable,'-O',str(root/'research'/filename)],capture_output=True,text=True,timeout=20)
        require(proc.returncode!=0 and 'requires assertions' in proc.stderr,'optimized mode '+filename)
        rejected.append('optimized-'+filename)
    report=dict(status='PASS',geometry=geometry,algebra=algebra,positive=positive,
                negative=reports,small_CNF_truth_table_calibrations=calibration,
                rejected_mutations=rejected,minimum_support=3,
                scope='Independent standard-library replay on all actual Y edges; two exhaustive normalized two-state cases. No new ordinary HN bound.')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
