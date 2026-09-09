"""Joint nine-state search, seeded by an independently checked finite coloring.

No negative result here certifies the infinite host. Equality variables are
merged before SAT, and only a real base triangle is symmetry-pinned.
"""
from itertools import product
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import time

from multicenter_cores import transform
from parts_core import clauses
from finite_background_repair import ROOT


def run(solver_name='glucose42',budget=200000):
    from pysat.solvers import Solver
    start=time.monotonic()
    core=json.loads((ROOT/'certificates/parts509_core.json').read_text())
    rec=json.loads(gzip.decompress((ROOT/'certificates/refined_center_arrays.json.gz').read_bytes()))['cases'][1]
    finite=json.loads(gzip.decompress((ROOT/'certificates/refined_center_finite.json.gz').read_bytes()))['cases'][2]
    index=lambda s,m,n,q:509*(1+9*s+3*(m%3)+n%3)+q
    nvertices=19*509;parent=list(range(nvertices))
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    def merge(a,b):
        a,b=find(a),find(b);parent[max(a,b)]=min(a,b)
    for sign in range(2):
        for q,r,m,n in rec['base_equal_instances']:merge(q,index(sign,m,n,r))
    for q,r,m,n,a,b in rec['dual_equal_instances']:merge(index(0,m,n,q),index(1,a,b,r))
    reps=sorted({find(v) for v in range(nvertices)});ids={v:i for i,v in enumerate(reps)}
    alias=[ids[find(v)] for v in range(nvertices)]
    edges=set()
    def edge(a,b):
        a,b=alias[a],alias[b];assert a!=b;edges.add(tuple(sorted((a,b))))
    for g in range(19):
        for q,r in core['induced_edges']:edge(509*g+q,509*g+r)
    for sign in range(2):
        for m,n in product(range(3),repeat=2):
            for q in range(509):edge(index(sign,m,n,q),index(sign,m+2,n+2,q))
        for q,r,m,n in rec['base_instances']:edge(q,index(sign,m,n,r))
    for q,r,m,n,a,b in rec['dual_instances']:edge(index(0,m,n,q),index(1,a,b,r))
    pointids={};seed=[None]*nvertices
    for g,(m,n,sign) in enumerate(finite['copy_specifications']):
        center=((32*m+16*n,)+(0,)*7,(0,16*n)+(0,)*6)
        for q,p in enumerate(core['points']):
            v=transform(p,center,sign)
            if v not in pointids:pointids[v]=len(pointids)
            destination=q if not sign else index(0 if sign==1 else 1,m,n,q)
            seed[destination]=int(finite['five_coloring'][pointids[v]])
    assert len(pointids)==finite['vertices'] and all(c is not None for c in seed)
    rename={seed[q]:i for i,q in enumerate((0,149,152))}
    assert len(rename)==3
    for c in range(5):
        if c not in rename:rename[c]=len(rename)
    seeded=[rename[seed[v]] for v in reps]
    assert all(tuple(sorted((a,b))) in set(map(tuple,core['induced_edges'])) for a,b in ((0,149),(0,152),(149,152)))
    cnf=clauses(len(reps),sorted(edges),5)
    cnf.extend([[5*alias[q]+i+1] for i,q in enumerate((0,149,152))])
    with Solver(name=solver_name,bootstrap_with=cnf) as solver:
        solver.set_phases([5*v+c+1 for v,c in enumerate(seeded)])
        solver.conf_budget(budget);status=solver.solve_limited()
        result=dict(schema=1,solver=solver_name,budget=budget,vertices=len(reps),edges=len(edges),
                    warm_start_violations=sum(seeded[a]==seeded[b] for a,b in edges),
                    status='SAT_CANDIDATE' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN',
                    stats=solver.accum_stats())
        if status:
            model=set(solver.get_model())
            colors=[next(c for c in range(5) if 5*v+c+1 in model) for v in range(len(reps))]
            result['core_words']=[''.join(str(colors[alias[509*g+q]]) for q in range(509)) for g in range(19)]
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    result['input_sha256']={name:hashlib.sha256((ROOT/'certificates'/name).read_bytes()).hexdigest()
                           for name in ('parts509_core.json','refined_center_arrays.json.gz','refined_center_finite.json.gz')}
    result['scope']='Nine-state quotient only; no negative host-colorability claim'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--solver',default='glucose42');parser.add_argument('--budget',type=int,default=200000)
    args=parser.parse_args();data=run(args.solver,args.budget)
    (ROOT/'certificates'/f'refined_warm_{args.solver}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='core_words'}),flush=True)
