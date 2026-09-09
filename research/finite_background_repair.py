"""Finite-support repair experiments on the T060/T061 infinite host.

SAT is only a candidate until an independent checker verifies the overrides.
An UNSAT search result excludes this fixed patch/background, not the host.
"""
from itertools import combinations
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[1]
STEPS = ((2,2),(-2,-2),(-2,4),(2,-4),(4,-2),(-4,2))


def prepare(root=ROOT):
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    data = json.loads(gzip.decompress((root/'certificates/refined_center_arrays.json.gz').read_bytes()))
    rec = next(r for r in data['cases'] if r['refinement'] == 3)
    words = json.loads((root/'certificates/multicenter_cores.json').read_text())['both_arrays_coloring']['three_core_words']
    adj = [[] for _ in core['points']]
    shifts = [[] for _ in core['points']]
    for q,r in core['induced_edges']:
        adj[q].append(r); adj[r].append(q)
        for u,v in ((q,r),(r,q)):
            dx,dy = (tuple(x-y for x,y in zip(a,b)) for a,b in zip(core['points'][u],core['points'][v]))
            if any(dx[i] for i in range(1,8)) or any(dy[i] for i in range(8) if i != 1):
                continue
            if dy[1] % 48 or (dx[0]-dy[1]) % 96:
                continue
            m,n = (dx[0]-dy[1])//96,dy[1]//48
            assert m*m+m*n+n*n == 1
            shifts[u].append((v,-3*m,-3*n))
    cross = set(); equal = set()
    pair = lambda a,b: tuple(sorted((a,b)))
    for kind,target in (('base_instances',cross),('base_equal_instances',equal)):
        for q,r,m,n in rec[kind]:
            for s in (1,-1): target.add(pair((0,0,0,q),(s,m,n,r)))
    for kind,target in (('dual_instances',cross),('dual_equal_instances',equal)):
        for q,r,m,n,a,b in rec[kind]: target.add(pair((1,m,n,q),(-1,a,b,r)))
    def neighbors(v):
        s,m,n,q = v
        for r in adj[q]: yield (s,m,n,r)
        if s:
            for r,a,b in shifts[q]: yield (s,m+a,n+b,r)
            for a,b in STEPS: yield (s,m+a,n+b,q)
    def background(v):
        s,m,n,q = v
        return (int(words[0 if s == 0 else 1 if s == 1 else 2][q])+(m % 3 if s else 0)) % 5
    patch = {(0,0,0,q) for q in range(509)}
    patch.update(v for e in cross | equal for v in e)
    return core,words,cross,equal,neighbors,background,patch


def experiment(layers=0,budget=100000,root=ROOT,free_background=False):
    from pysat.solvers import Solver
    start=time.monotonic()
    core,words,cross,equal,neighbors,background,patch=prepare(root)
    for _ in range(layers): patch.update(w for v in tuple(patch) for w in neighbors(v))
    vertices=sorted(patch); ids={v:i for i,v in enumerate(vertices)}
    if free_background:
        vertices += [(s,m,None,q) for s in (1,-1) for m in range(3) for q in range(509)]
        ids={v:i for i,v in enumerate(vertices)}
    edges={tuple(sorted((ids[a],ids[b]))) for a,b in cross}
    allowed=[set(range(5)) for v in vertices]; boundary_edges=0
    for i,v in enumerate(vertices):
        if v[2] is None:
            s,m,_,q=v
            for r in core['induced_edges']:
                if q == r[0]: edges.add(tuple(sorted((i,ids[(s,m,None,r[1])]))))
            for state in range(3):
                if state != m: edges.add(tuple(sorted((i,ids[(s,state,None,q)]))))
            continue
        for w in neighbors(v):
            if w in ids: edges.add(tuple(sorted((i,ids[w]))))
            else:
                boundary_edges+=1
                if free_background: edges.add(tuple(sorted((i,ids[(w[0],w[1]%3,None,w[3])]))))
                else: allowed[i].discard(background(w))
    print(json.dumps(dict(layers=layers,vertices=len(vertices),edges=len(edges),
                         boundary_edges=boundary_edges,list_sizes={str(k):sum(len(a)==k for a in allowed) for k in range(6)})),flush=True)
    with Solver(name='cadical195') as solver:
        lit=lambda v,c:5*v+c+1
        for v,colors in enumerate(allowed):
            solver.add_clause([lit(v,c) for c in sorted(colors)])
            for a,b in combinations(range(5),2): solver.add_clause([-lit(v,a),-lit(v,b)])
            for c in set(range(5))-colors: solver.add_clause([-lit(v,c)])
        for a,b in sorted(edges):
            for c in range(5): solver.add_clause([-lit(a,c),-lit(b,c)])
        for a,b in sorted(equal):
            for c in range(5):
                solver.add_clause([-lit(ids[a],c),lit(ids[b],c)])
                solver.add_clause([lit(ids[a],c),-lit(ids[b],c)])
        solver.conf_budget(budget); status=solver.solve_limited()
        result=dict(schema=1,layers=layers,conflict_budget=budget,solver='cadical195',
                    status='SAT_CANDIDATE' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN',
                    vertices=len(vertices),edges=len(edges),boundary_edges=boundary_edges,
                    background_words=words,free_background=free_background,stats=solver.accum_stats())
        if status:
            model=set(solver.get_model())
            color=lambda i:next(c for c in range(5) if lit(i,c) in model)
            if free_background:
                result['background_phase_words']=[''.join(str(color(ids[(s,m,None,q)])) for q in range(509))
                                                  for s in (1,-1) for m in range(3)]
                result['patch_coloring']=[[*v,color(i)] for i,v in enumerate(vertices) if v[2] is not None]
            else:
                result['overrides']=[[*v,color(i)] for i,v in enumerate(vertices) if color(i) != background(v)]
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    result['input_sha256']={name:hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()
                            for name in ('parts509_core.json','refined_center_arrays.json.gz','multicenter_cores.json')}
    result['scope']=('Fixed finite patch with jointly variable three-state backgrounds' if free_background else
                     'Fixed finite patch and fixed background')+' only; no negative host-colorability claim.'
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--layers',type=int,default=0)
    parser.add_argument('--free-background',action='store_true')
    parser.add_argument('--batch',action='store_true')
    parser.add_argument('--budget',type=int,default=100000);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.batch:
        cases=[experiment(layer,args.budget) for layer in range(3)]
        cases.append(experiment(0,args.budget,free_background=True))
        result=dict(schema=1,cases=cases)
    else:result=experiment(args.layers,args.budget,free_background=args.free_background)
    args.output.write_bytes(gzip.compress(json.dumps(result,separators=(',',':')).encode(),mtime=0))
    if args.batch:
        print(json.dumps([dict(layers=r['layers'],free_background=r['free_background'],status=r['status'])
                          for r in result['cases']]),flush=True)
    else:
        print(json.dumps({k:v for k,v in result.items() if k not in ('overrides','background_words','patch_coloring','background_phase_words')}),flush=True)
