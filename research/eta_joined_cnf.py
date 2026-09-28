"""Independent semantic CNF reconstruction after the proved eta gauge.

Components are obtained by graph traversal on (state,vertex), not the search
encoder's Boolean union/find. Other motion supports and palettes are free.
"""
from collections import deque
from itertools import combinations
import hashlib
from verify_eta_joined_law import specifications, FULL
from verify_anchored_eta import require


def build(data, certificate, sigma):
    require(isinstance(sigma,list) and sigma and all(type(x) is int for x in sigma)
            and sorted(sigma)==list(range(len(sigma))), 'support permutation')
    specifications(certificate,data)
    n=len(data['points']);k=5;m=len(sigma);K=set(certificate['kernel_Y_indices'])
    observations=[]
    for j,mm in enumerate(data['mappings']):
        observations.append(mm if j in FULL else [[a,b] for a,b in mm if a in K and b in K])
    observations += [[[a,x],[b,y]] for j,a,b,x,y in certificate['pair_records'] if j not in FULL]
    graph=[[] for _ in range(m*n)]
    for state in range(m):
        for a,b in data['mappings'][2]:
            x=state*n+a;y=sigma[state]*n+b
            graph[x].append(y);graph[y].append(x)
    component=[-1]*(m*n);count=0
    for first in range(m*n):
        if component[first]!=-1:continue
        component[first]=count;todo=[first]
        while todo:
            v=todo.pop()
            for w in graph[v]:
                if component[w]==-1:
                    component[w]=count;todo.append(w)
        count+=1
    def color(state,vertex,col):
        return k*component[state*n+vertex]+col+1
    rows=set()
    for t in range(count):
        choices=[k*t+c+1 for c in range(k)]
        rows.add(tuple(choices))
        for a,b in combinations(choices,2):rows.add(tuple(sorted((-a,-b))))
    projected=set()
    for state in range(m):
        for a,b in data['edges']:
            projected.add(tuple(sorted((component[state*n+a],component[state*n+b]))))
    for a,b in projected:
        for c in range(k):rows.add(tuple(sorted({-k*a-c-1,-k*b-c-1})))
    clauses=[list(c) for c in sorted(rows)]
    top=k*count
    def perm(size):
        nonlocal top
        matrix=[]
        for i in range(size):
            row=list(range(top+1,top+1+size));top+=size;matrix.append(row)
        for row in matrix+list(map(list,zip(*matrix))):
            clauses.append(list(row))
            for i in range(size):
                for j in range(i+1,size):clauses.append([-row[i],-row[j]])
        return matrix
    for j,mm in enumerate(observations):
        if j==2:continue
        support=perm(m)
        palettes=[perm(k) for _ in range(m)]
        for state in range(m):
            for a,b in mm:
                target=list(range(top+1,top+k+1));top+=k
                for other in range(m):
                    for c in range(k):
                        old=color(other,b,c);new=target[c];select=support[state][other]
                        clauses.append([-select,-old,new]);clauses.append([-select,old,-new])
                for c in range(k):
                    for d in range(k):clauses.append([-color(state,a,c),-palettes[state][c][d],target[d]])
    neighbors=[set() for _ in range(n)]
    for a,b in data['edges']:neighbors[a].add(b);neighbors[b].add(a)
    origin=4641
    triangle=next((origin,b,c) for b in sorted(neighbors[origin])
                  for c in sorted(neighbors[origin]&neighbors[b]) if b<c)
    visited=set()
    for state in range(m):
        if state in visited:continue
        t=state
        while t not in visited:visited.add(t);t=sigma[t]
        for c,v in enumerate(triangle):clauses.append([color(state,v,c)])
    digest=hashlib.sha256(f'p cnf {top} {len(clauses)}\n'.encode())
    for c in clauses:digest.update((' '.join(map(str,c))+' 0\n').encode())
    return dict(nv=top,clauses=clauses,cnf_sha256=digest.hexdigest(),components=count,
                normalization_triangle=list(triangle),observation_count=len(observations))
