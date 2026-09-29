"""Semantic full-domain three-atom CNF after the proved weighted eta gauge.

Equal weights use three matching slots. Weights (2,1,1) use four slots,
but both heavy slots refer to the SAME coloring variables. This is integer
transport, not a restriction to weight-preserving permutations of atoms.
"""
import hashlib
from itertools import combinations

ETA_CASES = (
    ((0,0),(1,1),(2,2)),
    ((0,0),(1,2),(2,1)),
    ((0,1),(1,2),(2,0)),
)
SPLIT_CASES = ETA_CASES[:2] + (((0,1),(0,2),(1,0),(2,0)),)


def build(data, weighted, case):
    if type(weighted) is not bool or type(case) is not int or case not in range(3):
        raise ValueError('weight type / eta case')
    n=len(data['points']);k=5
    links=(SPLIT_CASES if weighted else ETA_CASES)[case]
    adj=[[] for _ in range(3*n)]
    for s,t in links:
        for a,b in data['mappings'][2]:
            x=s*n+a;y=t*n+b;adj[x].append(y);adj[y].append(x)
    component=[-1]*(3*n);count=0
    for first in range(3*n):
        if component[first]>=0:continue
        component[first]=count;todo=[first]
        while todo:
            for y in adj[todo.pop()]:
                if component[y]<0:component[y]=count;todo.append(y)
        count+=1
    def color(s,v,c):return k*component[s*n+v]+c+1
    rows=set()
    for t in range(count):
        choices=tuple(range(k*t+1,k*t+k+1));rows.add(choices)
        rows.update(tuple(sorted((-a,-b))) for a,b in combinations(choices,2))
    projected={tuple(sorted((component[s*n+a],component[s*n+b])))
               for s in range(3) for a,b in data['edges']}
    for a,b in projected:
        for c in range(k):rows.add(tuple(sorted({-k*a-c-1,-k*b-c-1})))
    clauses=[list(c) for c in sorted(rows)];top=k*count
    def perm(size):
        nonlocal top
        matrix=[]
        for _ in range(size):
            matrix.append(list(range(top+1,top+size+1)));top+=size
        for row in matrix+list(map(list,zip(*matrix))):
            clauses.append(row)
            clauses.extend([-a,-b] for a,b in combinations(row,2))
        return matrix
    atoms=[0,0,1,2] if weighted else [0,1,2]
    ranges={};geometry_end=len(clauses)
    for j,mm in enumerate(data['mappings']):
        if j==2:continue
        begin=len(clauses)+1
        support=perm(len(atoms));palettes=[perm(k) for _ in atoms]
        for slot,s in enumerate(atoms):
            for a,b in mm:
                target=list(range(top+1,top+k+1));top+=k
                for other,t in enumerate(atoms):
                    for c in range(k):
                        old=color(t,b,c);new=target[c];select=support[slot][other]
                        clauses.append([-select,-old,new]);clauses.append([-select,old,-new])
                for c in range(k):
                    for d in range(k):
                        clauses.append([-color(s,a,c),-palettes[slot][c][d],target[d]])
        ranges[str(j)]=[begin,len(clauses)]
    # A common recoloring remains free on each eta transport component.
    neighbors=[set() for _ in range(n)]
    for a,b in data['edges']:neighbors[a].add(b);neighbors[b].add(a)
    origin=4641
    triangle=next((origin,b,c) for b in sorted(neighbors[origin])
                  for c in sorted(neighbors[origin]&neighbors[b]) if b<c)
    pending=set(range(3))
    while pending:
        s=min(pending);reached={s};todo=[s]
        while todo:
            v=todo.pop()
            for a,b in links:
                w=b if a==v else a if b==v else None
                if w is not None and w not in reached:reached.add(w);todo.append(w)
        pending-=reached
        for c,v in enumerate(triangle):clauses.append([color(s,v,c)])
    digest=hashlib.sha256(f'p cnf {top} {len(clauses)}\n'.encode())
    for c in clauses:digest.update((' '.join(map(str,c))+' 0\n').encode())
    return dict(nv=top,clauses=clauses,cnf_sha256=digest.hexdigest(),
                components=count,component=component,normalization_triangle=list(triangle),
                motion_clause_ranges=ranges,geometry_clause_end=geometry_end)
