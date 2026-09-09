"""Exact voltage components of periodic two-color subgraphs; search-side code.

Coordinates, not color names, label deck translations. No finite-radius cutoff.
"""
from collections import deque
from itertools import combinations, product
import gzip
import json
import math

from finite_background_repair import prepare, ROOT
from parts_core import clauses


def bezout(a,b):
    if b == 0:return abs(a),1 if a>=0 else -1,0
    g,x,y=bezout(b,a%b)
    return g,y,x-(a//b)*y


def lattice(generators):
    """Return column Hermite parameters: generators (a,0),(b,g)."""
    b=g=0
    for x,y in generators:
        h,u,v=bezout(g,y);b=u*b+v*x;g=h
    if g:
        a=math.gcd(*(x-(y//g)*b for x,y in generators))
        return a,b%a if a else b,g
    return math.gcd(*(x for x,y in generators)),0,0


def residue(x,y,basis):
    a,b,g=basis
    if g:
        t=y//g;x-=t*b;y-=t*g
    return (x%a if a else x,y)


def components(sign,pair,neighbors,bg):
    types={(m,q) for m in range(3) for q in range(509) if bg((sign,m,0,q)) in pair}
    lookup={};records=[]
    while types:
        seed=min(types);loc={seed:(seed[0],0)};queue=deque([seed]);cycles=[]
        while queue:
            t=queue.popleft();m,n=loc[t]
            for v in neighbors((sign,m,n,t[1])):
                if bg(v) not in pair:continue
                u=(v[1]%3,v[3]);p=v[1:3]
                if u in loc:
                    dx,dy=p[0]-loc[u][0],p[1]-loc[u][1]
                    assert dx%3==0
                    cycles.append((dx//3,dy))
                else:loc[u]=p;queue.append(u)
        basis=lattice(cycles);index=len(records)
        for t,p in loc.items():lookup[t]=(index,p,basis)
        records.append(dict(types=len(loc),basis=basis))
        types.difference_update(loc)
    def key(v):
        s,m,n,q=v
        index,(a,b),basis=lookup[m%3,q]
        return (s,index,*residue((m-a)//3,n-b,basis))
    return key,records


def run(double=False):
    from pysat.solvers import Solver
    core,words,cross,equal,neighbors,bg,patch=prepare()
    cache={(s,p):components(s,p,neighbors,bg) for s in (1,-1) for p in combinations(range(5),2)}
    observations=[]
    schemes=[(p,) for p in combinations(range(5),2)]
    if double:
        schemes=[]
        for single in range(5):
            rest=sorted(set(range(5))-{single})
            for other in rest[1:]:
                schemes.append(((rest[0],other),tuple(c for c in rest if c not in (rest[0],other))))
    for left,right in product(schemes,repeat=2):
        keys={};options={};pairs={1:left,-1:right}
        for v in sorted(patch):
            if v[0]==0:options[v]=[(c,5*v[3]+c+1) for c in range(5)];continue
            c=bg(v);pair=next((p for p in pairs[v[0]] if c in p),None)
            if pair is None:options[v]=[(c,None)];continue
            key=cache[v[0],pair][0](v)
            key=(key[0],*pair,*key[1:])
            if key not in keys:keys[key]=2546+len(keys)
            lit=keys[key];options[v]=[(c,-lit),(pair[0]+pair[1]-c,lit)]
        cnf=clauses(509,core['induced_edges'],5)
        immediate=None
        for equality,edges in ((False,cross),(True,equal)):
            for a,b in sorted(edges):
                for (c,lc),(d,ld) in product(options[a],options[b]):
                    if (c!=d) if equality else (c==d):
                        cnf.append([-t for t in (lc,ld) if t is not None])
                        if lc is None and ld is None:immediate=dict(equality=equality,endpoints=[a,b],colors=[c,d])
        if immediate is not None:
            observations.append(dict(pairs=[left,right],status='FIXED_CONSTRAINT_OBSTRUCTION',witness=immediate))
            continue
        with Solver(name='cadical195',bootstrap_with=cnf) as solver:
            solver.conf_budget(10000);status=solver.solve_limited()
            rec=dict(pairs=[left,right],variables=2545+len(keys),
                     status='SAT_CANDIDATE' if status else 'UNSAT_SEARCH_ONLY' if status is False else 'UNKNOWN')
            observations.append(rec)
            if status:
                model=set(solver.get_model())
                rec['swaps']=[key for key,lit in keys.items() if lit in model]
                rec['base_word']=''.join(str(next(c for c in range(5) if 5*q+c+1 in model)) for q in range(509))
                print(json.dumps(rec),flush=True);break
    print('statuses',{s:sum(r['status']==s for r in observations) for s in {r['status'] for r in observations}},flush=True)
    return dict(schema=1,double=double,background_words=words,observations=observations,
                components=[dict(sign=s,pair=p,records=r) for (s,p),(key,r) in cache.items()],
                scope='One round of one or two disjoint color-pair component swaps per array; voltage census is exploratory')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--double',action='store_true');args=parser.parse_args()
    data=run(args.double)
    name='kempe_double_background.json.gz' if args.double else 'kempe_background.json.gz'
    (ROOT/'certificates'/name).write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
