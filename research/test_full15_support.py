"""Six exact replays, independent encoder calibration and fail-closed tests."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
from audit_full_law_preparation import reconstruct
from verify_anchored_eta import read, require, geometry_check
from full15_support_semantics import reconstruct_case
from verify_full15_support import case_identity, replay_reconstruction


def rejects(fn):
    try:fn()
    except (ValueError,AssertionError,IndexError,KeyError,TypeError):return
    raise ValueError('malformed evidence accepted')


def small_cases():
    # Import the producer only in this cross-implementation test, not in the
    # independent proof checker. Padding supplies the fixed origin index.
    from full15_support_cnf import build
    data=dict(points=[None]*4644,edges=[[0,1],[0,4641],[1,4641]],
              mappings=[[[0,1],[1,0],[4641,4641]] for _ in range(15)])
    for weighted in (False,True):
        for case in range(3):
            expected=build(data,weighted,case)
            ids=sorted({1,len(expected['clauses'])//2,len(expected['clauses'])})
            actual=reconstruct_case(data,weighted,case,ids)
            require(actual['nv']==expected['nv'] and actual['full_clause_count']==len(expected['clauses'])
                    and actual['cnf_sha256']==expected['cnf_sha256'],'independent encoder disagreement')
            require(actual['initial_clauses']==[expected['clauses'][i-1] for i in ids],
                    'selected clause disagreement')
    for ids in [[0],[True],[1,1],[2,1],[-1],[10**10]]:
        rejects(lambda:reconstruct_case(data,False,0,ids))
    rejects(lambda:reconstruct_case(data,1,0,[1]))
    rejects(lambda:reconstruct_case(data,False,True,[1]))


def main():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    small_cases()
    root=Path(__file__).resolve().parents[1];data,summary=reconstruct(root)
    geometry_check(read(root/'certificates/eta_gauge_geometry.json'),data)
    reports=[];rejections=8
    for weighted in (False,True):
        for case in range(3):
            kind='weighted' if weighted else 'equal'
            c=read(root/'certificates'/f'full15_three_{kind}{case}.json.xz')
            case_identity(c,summary)
            require(c['weighted'] is weighted and c['case']==case,'filename/case mismatch')
            built=reconstruct_case(data,weighted,case,c['initial_clause_ids'])
            reports.append(replay_reconstruction(c,built))
            for key,value in [('schema','bad'),('input_semantic_sha256','bad'),
                              ('status','UNKNOWN'),('weighted',1),('case',True),('case',3)]:
                bad=deepcopy(c);bad[key]=value;rejects(lambda:case_identity(bad,summary));rejections+=1
            for key,value in [('cnf_sha256','bad'),('full_variable_count',True),
                              ('full_clause_count',c['full_clause_count']+1),
                              ('rup_clauses',[[]]),('rup_clauses',c['rup_clauses']+[[1]]),
                              ('rup_clauses',[[built['nv']+1],[]])]:
                bad=deepcopy(c);bad[key]=value;rejects(lambda:replay_reconstruction(bad,built));rejections+=1
            print(json.dumps(reports[-1],sort_keys=True),flush=True)
    for name in ['verify_full15_support.py','test_full15_support.py','test_weighted_transport.py','verify_three_atom_mass.py']:
        trial=subprocess.run([sys.executable,'-O',str(root/'research'/name)],capture_output=True,text=True,timeout=10)
        require(trial.returncode!=0 and 'requires assertions' in trial.stderr,'optimized mode accepted')
        rejections+=1
    print(json.dumps(dict(status='PASS',complete_six_cases=True,small_encoder_cases=6,
                         rejection_tests=rejections,hn_bound_changed=False)),flush=True)


if __name__=='__main__':main()
