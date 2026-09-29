"""Small exhaustive tests of weighted transport and palette gauge algebra.

These calibrate the written theorem, not the large-Y SAT result.
"""
from collections import Counter
from fractions import Fraction
from itertools import product, permutations, combinations
import json
from full15_support_cnf import SPLIT_CASES
from verify_anchored_eta import compose, inverse, require


def gauges(n,k,edges):
    adj=[[] for _ in range(n)]
    for i,j,p in edges:
        require(tuple(sorted(p))==tuple(range(k)),'palette')
        adj[i].append((j,p));adj[j].append((i,inverse(p)))
    out=[None]*n
    for first in range(n):
        if out[first] is not None:continue
        out[first]=tuple(range(k));todo=[first]
        while todo:
            i=todo.pop()
            for j,p in adj[i]:
                value=compose(out[i],inverse(p))
                if out[j] is None:out[j]=value;todo.append(j)
                else:require(out[j]==value,'nontrivial closed-walk holonomy')
    return out


def main():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    cases=0;split_only=0
    for p in product(range(6),repeat=6):
        a,b=p[:3],p[3:]
        left=Counter([a[0],a[0],a[1],a[2]])
        right=Counter([b[0],b[0],b[1],b[2]])
        matched=[all(a[i]==b[j] for i,j in e) for e in SPLIT_CASES]
        require((left==right)==any(matched),'three transport cases incomplete')
        expanded=(0,0,1,2)
        matching=any(all(a[expanded[i]]==b[expanded[q[i]]] for i in range(4))
                     for q in permutations(range(4)))
        require(matching==(left==right),'integer transport equivalence')
        split_only+=matched[2] and not any(matched[:2]);cases+=1
    # All 6^3 palette choices, with cycles, a diamond, and parallel edges.
    tested=0
    for q in product(tuple(permutations(range(3))),repeat=3):
        links=[(0,1),(0,2),(1,2),(2,0),(0,1)]
        edges=[(i,j,compose(inverse(q[j]),q[i])) for i,j in links]
        out=gauges(3,3,edges)
        require(all(compose(compose(out[j],p),inverse(out[i]))==tuple(range(3))
                    for i,j,p in edges),'incorrect graph gauge')
        tested+=1
    try:gauges(1,3,[(0,0,(1,0,2))])
    except ValueError:pass
    else:raise ValueError('accepted nontrivial loop')
    # Exact fractional flow, including the indispensable split case.
    weights=[Fraction(1,2),Fraction(1,4),Fraction(1,4)]
    a=[0,1,1];b=[1,0,0];mass={0:Fraction(1,2),1:Fraction(1,2)}
    flow=[[weights[i]*weights[j]/mass[a[i]] if a[i]==b[j] else Fraction(0)
           for j in range(3)] for i in range(3)]
    require(list(map(sum,flow))==weights and list(map(sum,zip(*flow)))==weights,'flow marginals')
    rows=[r for r in product((-1,0,1),repeat=3) if any(r) and next(x for x in r if x)>0]
    found=set()
    for a,b in combinations(rows,2):
        v=tuple(a[(j+1)%3]*b[(j+2)%3]-a[(j+2)%3]*b[(j+1)%3] for j in range(3))
        if all(x>0 for x in v) or all(x<0 for x in v):found.add(tuple(Fraction(x,sum(v)) for x in v))
    expected={(Fraction(1,3),)*3}|{tuple(Fraction(1,2) if i==j else Fraction(1,4)
                                      for i in range(3)) for j in range(3)}
    require(found==expected,'three-atom weight types')
    print(json.dumps(dict(status='PASS',transport_patterns=cases,split_only_patterns=split_only,
                         graph_gauges=tested,weight_types=len(found),hn_bound_changed=False)))


if __name__=='__main__':main()
