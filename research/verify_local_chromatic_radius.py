#!/usr/bin/env python3
"""Exact spindle geometry and local bad-needle/area bounds.
External Shukla/Polymath 5-chromatic graphs are inputs, not rechecked.
"""
from fractions import Fraction as F
from itertools import combinations, product
import json

Z=(F(0),)*4
ONE=(F(1),F(0),F(0),F(0))
S3=(F(0),F(1),F(0),F(0))
S11=(F(0),F(0),F(1),F(0))
S33=(F(0),F(0),F(0),F(1))

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def neg(a): return tuple(-v for v in a)
def sub(a,b): return add(a,neg(b))
def rat(a,p,q=1): return tuple(x*F(p,q) for x in a)
def mul(a,b):
    out=[F(0)]*4
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            factor=(3 if (i&j&1) else 1)*(11 if (i&j&2) else 1)
            out[i^j]+=x*y*factor
    return tuple(out)
def point(x,y): return x,y
def p_sub(a,b):return point(sub(a[0],b[0]),sub(a[1],b[1]))
def p_mul(a,b):return point(sub(mul(a[0],b[0]),mul(a[1],b[1])),add(mul(a[0],b[1]),mul(a[1],b[0])))
def norm2(z):return add(mul(z[0],z[0]),mul(z[1],z[1]))
def check(flag,msg):
    if not flag: raise RuntimeError(msg)

def spindle():
    A=point(rat(S3,1,2),rat(ONE,1,2))
    B=point(rat(S3,1,2),rat(ONE,-1,2))
    T=point(S3,Z)
    u=point(rat(ONE,5,6),rat(S11,1,6))
    pts=[point(Z,Z),A,B,T,p_mul(u,A),p_mul(u,B),p_mul(u,T)]
    center=point(rat(S3,1,2),rat(S33,1,22))
    radius_squared=rat(ONE,9,11)
    inside_sq=add(rat(ONE,7,22),rat(S33,1,22))
    nearer_sq=sub(rat(ONE,7,22),rat(S33,1,22))
    dists=[norm2(p_sub(p,center)) for p in pts]
    check(dists==[radius_squared,nearer_sq,inside_sq,radius_squared,inside_sq,nearer_sq,radius_squared],'containing disk')
    check(F(33)<F(11)**2 and F(33)<F(7)**2,'radical bounds')
    edges=[(i,j) for i,j in combinations(range(7),2) if norm2(p_sub(pts[i],pts[j]))==ONE]
    check(len(edges)==11,'11 exact unit edges')
    check(all(norm2(p_sub(pts[i],pts[j]))!=Z for i,j in combinations(range(7),2)),'distinct vertices')
    check(not any(all(labels[i]!=labels[j] for i,j in edges) for labels in product(range(3),repeat=7)),'no 3 coloring')
    check(any(all(labels[i]!=labels[j] for i,j in edges) for labels in product(range(4),repeat=7)),'valid 4 coloring')
    return {'vertices':7,'actual_unit_edges':len(edges),'chi':4,
            'enclosing_radius_exact':'3/sqrt(11)',
            'enclosing_disk_center_exact':['sqrt(3)/2','sqrt(33)/22'],
            'squared_distances_by_vertex':['9/11','(7-sqrt(33))/22','(7+sqrt(33))/22','9/11','(7+sqrt(33))/22','(7-sqrt(33))/22','9/11'],
            'local_unit_disk_3_palette_missing_fraction_lower_exact':'(1-3/sqrt(11))^2/7'}

def local_five_graphs():
    cases=[('polymath2021',31171,180942,F(1),F(6,5)),
           ('shukla2026_G8168',8168,41556,F(23,20),F(3,2)),
           ('shukla2026_G5713',5713,25482,F(5,4),F(2)),
           ('shukla2026_G773',773,3817,F(3,2),F(2))]
    out=[]
    for name,n,m,R,r in cases:
        check(r>R,'test disk radius')
        a=((r-R)/r)**2
        out.append({'source':name,'vertices':n,'edges':m,'graph_radius':str(R),
                    'test_disk_radius':str(r),
                    'tradeoff':f'{n}*missing_four_label_fraction + {m}*unit_needle_energy >= {a}',
                    'zero_energy_missing_four_fraction_at_least':str(a/n)})
    check(out[-1]['zero_energy_missing_four_fraction_at_least']=='1/12368','G773 local defect')
    return out

if __name__=='__main__':
    print(json.dumps({'result':'PASS',
                      'scope':'exact spindle and fractions; external Shukla/Polymath claims inputs only',
                      'spindle':spindle(),'five_chromatic_graph_tradeoffs':local_five_graphs()},indent=2,sort_keys=True))
