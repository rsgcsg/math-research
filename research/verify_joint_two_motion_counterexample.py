"""C024: exact four-point minimal separately-feasible/jointly-infeasible example.

Arithmetic is in Q(sqrt(7)); no floating geometry or solver is used. Minimality
for arbitrary point sets of size <=3 is proved in the accompanying document.
"""
from fractions import Fraction as Q
from itertools import combinations, product
import json


def scalar(a=0,b=0): return Q(a),Q(b)
def add(x,y): return x[0]+y[0],x[1]+y[1]
def neg(x): return -x[0],-x[1]
def mul(x,y): return x[0]*y[0]+7*x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def scale(x,t): return x[0]*t,x[1]*t
def cadd(x,y): return add(x[0],y[0]),add(x[1],y[1])
def csub(x,y): return add(x[0],neg(y[0])),add(x[1],neg(y[1]))
def cmul(x,y): return add(mul(x[0],y[0]),neg(mul(x[1],y[1]))),add(mul(x[0],y[1]),mul(x[1],y[0]))
def norm(x): return add(mul(x[0],x[0]),mul(x[1],x[1]))
def sqdist(x,y): return norm(csub(x,y))
def partition(w):
    return tuple(sorted(tuple(i for i,c in enumerate(w) if c==color) for color in set(w)))


def verify():
    if not __debug__: raise RuntimeError('verification requires assertions')
    a=(scalar(),scalar()); b=(scalar(1),scalar())
    c=(scalar(Q(1,4)),scalar(0,Q(1,4)))
    d=(scalar(Q(1,2)),scalar(Q(1,2)))
    points=[a,b,c,d]
    alpha=(scalar(Q(1,4),Q(1,4)),scalar(Q(1,4),Q(-1,4)))
    beta=(scalar(Q(-1,4),Q(1,4)),scalar(Q(1,4),Q(1,4)))
    assert norm(alpha)==norm(beta)==scalar(1)
    motions=[lambda z:cmul(alpha,z),lambda z:cadd(b,cmul(beta,z))]
    maps=[[(i,points.index(q)) for i,p in enumerate(points) if (q:=g(p)) in points] for g in motions]
    assert maps==[[(0,0),(2,3)],[(0,1),(2,3)]]
    distances={ij:sqdist(points[ij[0]],points[ij[1]]) for ij in combinations(range(4),2)}
    assert distances=={(0,1):scalar(1),(0,2):scalar(Q(1,2)),(0,3):scalar(Q(1,2)),
                      (1,2):scalar(1),(1,3):scalar(Q(1,2)),(2,3):scalar(Q(3,4),Q(-1,4))}
    edges=[list(ij) for ij,v in distances.items() if v==scalar(1)]
    words=[w for w in product(range(2),repeat=4) if all(w[i]!=w[j] for i,j in edges)]
    assert len(words)==4
    classes=sorted(set(partition(w) for w in words)); assert len(classes)==2
    reps=[(0,1,0,0),(0,1,0,1)]
    differences=[[int(w[0]==w[2])-int(w[0]==w[3]),int(w[0]==w[2])-int(w[1]==w[3])] for w in reps]
    assert differences==[[0,1],[1,0]]
    assert all(sum(row)==1 for row in differences)
    # Each single motion has its own deterministic proper law.
    assert differences[0][0]==differences[1][1]==0
    # Three short rigid copies yield an actual induced C5 witness, not just a
    # linear contradiction or an abstract non-bipartite graph.
    e=motions[0](b); f=motions[1](b)
    cycle=[a,b,f,d,e]
    cycle_edges=[(i,j) for i,j in combinations(range(5),2) if sqdist(cycle[i],cycle[j])==scalar(1)]
    assert cycle_edges==[(0,1),(0,4),(1,2),(2,3),(3,4)]
    assert not any(all(w[i]!=w[j] for i,j in cycle_edges) for w in product(range(2),repeat=5))
    assert all((0,1,0,1,2)[i]!=(0,1,0,1,2)[j] for i,j in cycle_edges)
    return dict(status='PASS',counterexample='C024',vertices=4,actual_pairs=6,unit_edges=edges,
                maximal_domains=[[list(p) for p in mm] for mm in maps],proper_labeled_two_colorings=4,
                proper_partitions=2,individual_witnesses=[list(w) for w in reps],
                same_event_difference_columns=differences,uniform_strict_gap=1,
                compiled_vertices=5,compiled_actual_pairs=10,compiled_unit_edges=[list(e) for e in cycle_edges],
                scope='Actual minimal four-point input: individual full-domain two-color laws exist, but no common law. Not a five-color HN obstruction.')


if __name__=='__main__': print(json.dumps(verify(),indent=2))
