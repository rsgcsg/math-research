"""Produce a rational disjunction proof excluding even a planar unit homomorphism."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import gzip
import json


def run():
    n=5;N=11;edges=set()
    for i in range(n):
        j=(i+1)%n
        edges.update(tuple(sorted(p)) for p in [(i,j),(i+n,j),(j+n,i)])
    edges.update((i+n,2*n) for i in range(n));edges=sorted(edges)
    adj=[set() for _ in range(N)]
    for a,b in edges:adj[a].add(b);adj[b].add(a)
    cycles=set()
    for a,c in combinations(range(N),2):
        for b,d in combinations(adj[a]&adj[c],2):
            cycles.add(tuple(sorted((tuple(sorted((a,c))),tuple(sorted((b,d)))))))
    cycles=sorted(cycles)
    def row(terms):
        r=[Q(0)]*N
        for i,v in terms:r[i]+=v
        return r
    equations=[]
    for (a,c),(b,d) in cycles:
        equations.append([row([(a,1),(c,-1)]),row([(b,1),(d,-1)]),row([(a,1),(c,1),(b,-1),(d,-1)])])
    erows=[row([(a,1),(b,-1)]) for a,b in edges]
    def reduce(r,basis,depth):
        r=r[:];coeff=[Q(0)]*depth
        for p,s,expr in basis:
            factor=r[p]
            if factor:
                r=[x-factor*y for x,y in zip(r,s)]
                coeff=[x+factor*y for x,y in zip(coeff,expr)]
        return r,coeff
    nodes=0
    def search(basis,depth):
        nonlocal nodes
        nodes+=1
        if nodes>100000:raise RuntimeError('UNKNOWN_NODE_LIMIT')
        for edge,r in enumerate(erows):
            rr,coeff=reduce(r,basis,depth)
            if not any(rr):return dict(edge=edge,weights=list(map(str,coeff)))
        todo=[]
        for c,rows in enumerate(equations):
            rr=[reduce(r,basis,depth)[0] for r in rows]
            if all(any(r) for r in rr):todo.append((sum(sum(bool(v) for v in r) for r in rr),c))
        if not todo:raise RuntimeError('NECESSARY_LINEAR_MODEL_FEASIBLE; not a unit realization')
        _,c=min(todo);children=[]
        for raw in equations[c]:
            r,coeff=reduce(raw,basis,depth);p=next(i for i,v in enumerate(r) if v);q=r[p]
            r=[v/q for v in r];expr=[-v/q for v in coeff]+[1/q]
            nb=[]
            for j,s,e in basis:
                factor=s[p]
                nb.append((j,[a-factor*b for a,b in zip(s,r)],
                           [a-factor*b for a,b in zip(e+[Q(0)],expr)]))
            nb.append((p,r,expr));nb.sort()
            children.append(search(nb,depth+1))
        return dict(cycle=c,children=children)
    tree=search([],0)
    return dict(schema=1,experiment='E066',vertices=N,edges=edges,cycles=cycles,nodes=nodes,tree=tree,
                scope='No planar unit homomorphism for M(C5), allowing nonedge collisions')


if __name__=='__main__':
    data=run();root=Path(__file__).resolve().parents[1]
    (root/'certificates/mycielski_collision_refutation.json.gz').write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
    print(json.dumps({k:v for k,v in data.items() if k not in ('tree','cycles','edges')}))
