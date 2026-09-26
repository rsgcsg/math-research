"""Finite support calibration for T139; not a machine proof of the S-unit theorem."""
from fractions import Fraction as F
from itertools import combinations
from math import gcd
import json


def partitions(n):
    def visit(i, blocks):
        if i==n:
            yield tuple(tuple(b) for b in blocks);return
        for j in range(len(blocks)):
            blocks[j].append(i);yield from visit(i+1,blocks);blocks[j].pop()
        blocks.append([i]);yield from visit(i+1,blocks);blocks.pop()
    yield from visit(0,[])


def mul(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def norm(a): return a[0]*a[0]+a[1]*a[1]

def check():
    if not __debug__: raise RuntimeError('verification requires assertions')
    E=[(1,-1),(-1,1),(1,0),(-1,0),(0,1),(0,-1),(0,0)]
    D={sub(a,b) for a in E for b in E}
    det=lambda a,b:a[0]*b[1]-a[1]*b[0]
    assert max(abs(det(a,b)) for a in D for b in D)==4
    reports=[]
    for m,total,without,single_rank in [(6,203,41,3),(7,877,162,3)]:
        ps=list(partitions(m));assert len(ps)==total
        counts={1:0,2:0};normals=set()
        for blocks in ps:
            if any(len(b)==1 for b in blocks):continue
            vectors=[sub(E[i],E[block[0]]) for block in blocks for i in block[1:]]
            assert vectors and any(v!=(0,0) for v in vectors)
            rank=2 if any(det(v,w)!=0 for v,w in combinations(vectors,2)) else 1
            counts[rank]+=1
            if rank==1:
                x,y=next(v for v in vectors if v!=(0,0));g=gcd(x,y);x//=g;y//=g
                if x<0 or (x==0 and y<0):x,y=-x,-y
                normals.add((x,y))
        assert sum(counts.values())==without and counts[1]==single_rank
        assert normals=={(1,0),(0,1),(1,-1)}
        reports.append(dict(terms=m,all_partitions=total,without_singletons=without,rank_one=counts[1],rank_two=counts[2]))
    one=(F(1),F(0));two=(F(2),F(0));neg_two=(-F(2),F(0));v=(F(3,5),F(4,5));x=one;checks=0
    for _ in range(31):
        assert norm(x)==1
        # Matching, star at translated origin, and star at original origin.
        for a,b,t,xx,yy in [(two,two,one,x,x),(two,one,two,one,x),(one,neg_two,two,x,one)]:
            assert norm(sub(mul(a,xx),add(t,mul(b,yy))))==1;checks+=1
        x=mul(x,v)
    # Unique maximal exponent unless p=0, q=0, or p=q.
    directions=0
    for p in range(-30,31):
        for q in range(-30,31):
            if p==0 or q==0 or p==q:continue
            values=[p-q,q-p,p,-p,q,-q]
            assert values.count(max(values))==1;directions+=1
    powers={0:one};x=one
    for i in range(1,9):
        x=mul(x,v);powers[i]=x;powers[-i]=(x[0],-x[1])
    rank_one_pairs=0
    for n,x in powers.items():
        for m,y in powers.items():
            assert (norm(sub(x,add(one,y)))==1)==(n==0 or n==m)
            rank_one_pairs+=1
    return dict(status='PASS',support_partitions=reports,max_determinant=4,
                complete_rank_one_example_pair_calibrations=rank_one_pairs,
                exact_rational_examples=checks,direction_calibrations=directions,
                scope='Finite support and example checks only; no exception enumeration or HN bound.')


if __name__=='__main__': print(json.dumps(check(),indent=2))
