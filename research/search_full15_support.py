"""Budgeted finite-support searches; no unverified negative is a theorem."""
from pathlib import Path
import argparse,gzip,json,time,hashlib
from pysat.solvers import Solver
from full15_support_cnf import build,decode_words,SPLIT_TYPES
from audit_full_law_preparation import canonical
from closed_binary_proof import close_and_read

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True);p.add_argument('--sigma',required=True)
    p.add_argument('--kind',choices=['uniform','211'],default='uniform')
    p.add_argument('--budget',type=int,default=30000);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--proof',action='store_true');p.add_argument('--dimacs',action='store_true')
    p.add_argument('--solver',default='cadical195');p.add_argument('--seed-packet',action='store_true');a=p.parse_args()
    data=json.loads(gzip.decompress(a.cache.read_bytes()))
    expected=json.loads((Path(__file__).resolve().parents[1]/'certificates/full_law_preparation_audit.json').read_text())['independent_inputs']['semantic_sha256']
    if hashlib.sha256(canonical(data)).hexdigest()!=expected:raise ValueError('cache binding')
    sigma=list(map(int,a.sigma.split(',')))
    edges=SPLIT_TYPES[sigma[0]] if a.kind=='211' else list(enumerate(sigma))
    m=3 if a.kind=='211' else len(sigma)
    start=time.monotonic();b=build(data,edges,m,a.kind)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    info=dict(schema='full15-finite-support-search-v1',kind=a.kind,eta_case=sigma,eta_edges=edges,m=m,
              input_semantic_sha256=expected,nv=b['nv'],clauses=len(b['clauses']),
              cnf_sha256=b['clauses'].digest(b['nv']),budget=a.budget)
    print('BUILT',json.dumps(info),flush=True)
    if a.dimacs:b['clauses'].dimacs(b['nv'],str(a.out)+'.cnf')
    with Solver(name=a.solver,bootstrap_with=b['clauses'],with_proof=a.proof) as s:
        if a.seed_packet:
            from verify_eta_joined_law import expand_compact
            from verify_anchored_eta import read
            cert=read(Path(__file__).resolve().parents[1]/'certificates/eta_joined_three_compact.json.gz')
            old=expand_compact(cert,data,{'semantic_sha256':expected})['words']
            phase={}
            for state in range(m):
                w=old[state%3]
                for v,col in enumerate(w):
                    var=b['components'][state*len(w)+v]*5+int(col)+1
                    phase[var]=var
            s.set_phases(list(phase.values()))
            info['initial_hint']='published three-word S packet; not a constraint'
        s.conf_budget(a.budget);t=time.monotonic();ans=s.solve_limited()
        info.update(solver=a.solver,status='SAT_UNCHECKED' if ans is True else 'UNSAT_UNCERTIFIED' if ans is False else 'UNKNOWN_FIXED_SUPPORT',solve_seconds=time.monotonic()-t,stats=s.accum_stats())
        if ans is True:
            info['words']=decode_words(b,s.get_model(),len(data['points']))
            info['weights']=[1]*m if a.kind=='uniform' else [2,1,1]
        if ans is False and a.proof:
            trace,record=close_and_read(s)
            with gzip.open(str(a.out)+'.drup.gz','wt') as f:f.write('\n'.join(trace)+'\n')
            info['trace_lines']=len(trace);info['proof_stream']=record
    info['elapsed_seconds']=time.monotonic()-start
    a.out.write_text(json.dumps(info,indent=2)+'\n')
    print('RESULT',json.dumps({k:v for k,v in info.items() if k!='words'}),flush=True)
if __name__=='__main__':main()
