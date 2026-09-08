"""Exact four-point calibration separating monochromatic and joint moments."""
from itertools import combinations
from fractions import Fraction as F
from collections import defaultdict
from relations import color_partitions
from balanced_weights import solve


def verify():
    points=[(0,0),(1,1),(1,0),(0,1)]
    edges=[(i,j) for i,j in combinations(range(4),2)
           if sum((a-b)**2 for a,b in zip(points[i],points[j]))==1]
    assert edges==[(0,2),(0,3),(1,2),(1,3)]
    mu=[((0,0,1,1),F(1,2)),((0,1,2,3),F(1,2))]
    nu=[((0,0,1,2),F(1,2)),((0,1,2,2),F(1,2))]
    for law in (mu,nu):
        assert sum(p for c,p in law)==1
        assert all(c[i]!=c[j] for c,p in law for i,j in edges)
    def mono(law,mask):
        return sum(p for c,p in law if len({c[i] for i in range(4) if mask>>i&1})<=1)
    assert all(mono(mu,m)==mono(nu,m) for m in range(16))
    def joint(law):
        return sum(p for c,p in law if c[0]==c[1] and c[2]==c[3])
    assert (joint(mu),joint(nu))==(F(1,2),0)
    def single_color_law(law):
        out=defaultdict(F)
        for c,p in law:
            for color in range(4):
                out[tuple(i for i in range(4) if c[i]==color)]+=p/4
        return dict(out)
    assert single_color_law(mu)==single_color_law(nu)
    ranks=[]
    for n in range(1,6):
        partitions=list(color_partitions(n,[],n))
        rows=[[int(len({c[i] for i in range(n) if mask>>i&1})<=1) for c in partitions]
              for mask in range(1<<n)]
        _,rank=solve(rows,[0]*len(rows),len(partitions))
        assert rank==(1<<n)-n
        ranks.append(dict(points=n,partitions=len(partitions),monochromatic_rank=rank))
    return dict(square_induced_edges=edges,identical_moments_checked=16,
                distinct_joint_probabilities=['1/2','0'],partition_moment_ranks=ranks)
