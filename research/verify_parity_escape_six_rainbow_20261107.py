#!/usr/bin/env python3
"""Exact Q(sqrt3) check of a parity macro-palette escape and its six-ray obstruction.

The parity palette is an abstract color assignment to NONMIXED hexagons.
It satisfies the selected 4-freeze triangular gadget's limited abstract edges,
but is NOT a proper coloring of the plane or a weak coloring.
"""
from fractions import Fraction as F
from itertools import combinations, product
import json

LO,HI=F(433,250),F(1733,1000)
Z=(F(0),F(0))
def check(ok,msg):
    if not ok: raise RuntimeError(msg)
def plus(a,b):return a[0]+b[0],a[1]+b[1]
def minus(a,b):return a[0]-b[0],a[1]-b[1]
def times(a,b):return a[0]*b[0]+3*a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def scale(a,s):return a[0]*s,a[1]*s
def square(p):return plus(times(p[0],p[0]),times(p[1],p[1]))
def lower(a):return a[0]+a[1]*(LO if a[1]>=0 else HI)
def center(v):
    m,n=v
    return ((F(0),F(2*m+n,5)),(F(3*n,5),F(0)))
def residue(v):return(v[0]+3*v[1])%7
def pair_color(v):
    k=residue(v)
    check(k not in (0,1),"marked hex may not be a macro-color vertex")
    if k!=2:return k
    a,b=v[0]-2,v[1]
    check((-2*a+b)%7==0 and (a+3*b)%7==0,"index7 lattice coordinates")
    x,y=(-2*a+b)//7,(a+3*b)//7
    return 7 if (x+y)%2 else 2
D=((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1))
def rotate(v):
    m,n=v
    return(-n,m+n)
def rot(v,k):
    for _ in range(k):v=rotate(v)
    return v
LEAVES=(
    ((-2,1),(1,-2),(-1,-1),(2,-1)),
    ((-1,3),(0,3),(3,0),(2,-1)),
    ((-2,1),(0,3),(-2,4),(-3,3))
)
ORIENTATIONS=((1,3,0),(2,0,2),(4,1,4))
GEN1,GEN2=(-3,1),(1,2)

def norm(v):
    a,b=v
    return a*a+a*b+b*b

def verify_abstract_escape():
    diffs=[(a,b) for a in range(-2,3) for b in range(-2,3)
           if norm((a,b)) in (1,3,4)]
    check(len(diffs)==18 and all(residue(v)!=0 for v in diffs),
          "same code residue is T^2-independent")
    check({pair_color((2+x*GEN1[0]+y*GEN2[0],
                       x*GEN1[1]+y*GEN2[1])) for x,y in product(range(2),repeat=2)}
          =={2,7},"both escape colors appear on residue2")
    cert=[]
    for a,b,k in ORIENTATIONS:
        for x,y in product(range(2),repeat=2):
            shift=(b+x*GEN1[0]+y*GEN2[0],x*GEN1[1]+y*GEN2[1])
            rows=[]
            for row in LEAVES:
                leaf_sites=[(rot(u,k)[0]+shift[0],rot(u,k)[1]+shift[1])
                            for u in row]
                check(all(residue(u) in (2,4,5,6) for u in leaf_sites),
                      "each leaf belongs to a nonmixed coset")
                rows.append(tuple(pair_color(u) for u in leaf_sites))
            choices=[sorted(set(range(2,8))-set(row)) for row in rows]
            code3_vertex=[i for i,r in enumerate((0,4,5))
                          if (a*r+b)%7==3]
            check(len(code3_vertex)==1,"one triangle vertex lies in near-pure class 3")
            solutions=[assign for assign in product(*choices)
                       if len(set(assign))==3 and assign[code3_vertex[0]]==3]
            check(len(solutions)>=1,"limited four-leaf triangle constraints can all be colored")
            cert.append({"affine_multiplier":a,"shift":list(shift),
                         "triangle_leaf_color_words":[list(r) for r in rows],
                         "admissible_triangle_3_distinct":[list(solutions[0])],
                         "class3_triangle_vertex":code3_vertex[0]})
    check(len(cert)==12,"three orientations x four parity phases")
    return cert

def verify_six_rainbow_point():
    check(LO*LO<3<HI*HI,"exact rational sqrt3 enclosure")
    p=((F(1,50),F(6,5)),(F(27,25),F(0)))
    # p is the translated t-vertex in class1 of the original E unit triangle.
    sites={2:(0,3),3:(3,0),4:(1,1),
           5:(3,3),6:(1,4),7:(3,2)}
    r=F(1,100)
    h=(F(0),F(1,5))
    dmin=minus((1+r,F(0)),h)
    dmax=plus((1-r,F(0)),h)
    lo2,hi2=times(dmin,dmin),times(dmax,dmax)
    out=[]
    bounds=[]
    for label,v in sorted(sites.items()):
        check(pair_color(v)==label,"all six macro majority colors observed")
        c=center(v)
        diff=(minus(p[0],c[0]),minus(p[1],c[1]))
        d2=square(diff)
        margin_lo=lower(minus(d2,lo2))
        margin_hi=lower(minus(hi2,d2))
        check(margin_lo>0 and margin_hi>0,
              "radius 1/100 unit-neighbor ball strictly inside target hex incircle")
        bounds.extend((margin_lo,margin_hi))
        out.append({"color":label,"macro_center":list(v),
                    "distance_squared":[str(d2[0]),str(d2[1])+"*sqrt(3)"],
                    "squared_lower_margin_at_least":str(margin_lo),
                    "squared_upper_margin_at_least":str(margin_hi)})
    check(min(bounds)==F(6679,250000),"exact smallest six-ray squared margin")
    eta=F(1,62500)
    # Six near-pure macro cells cannot all have their designated color:
    # 6*eta*M < pi*(1/100)^2 with only pi>3, sqrt3<2.
    area_lb=F(3,10000)
    missed_ub=6*eta*F(12,25)
    check(area_lb>missed_ub,"six majority colors around one point are impossible")
    return {"probe_point":["1/50+6*sqrt(3)/5","27/25"],
            "translations_ball_radius":"1/100",
            "six_distinct_majority_sites":out,
            "minimum_exact_squared_disk_margin":str(min(bounds)),
            "common_translation_disk_area_gt":str(area_lb),
            "six_cell_leakage_lt":str(missed_ub),
            "conclusion":"this parity macro escape cannot extend to weak proper 6-coloring"}

if __name__=="__main__":
    triangles=verify_abstract_escape()
    rainbow=verify_six_rainbow_point()
    print(json.dumps({"status":"PASS","scope":"limited abstract triangle gadget has a six-color pseudo-model, but stronger all-visible six-ray gadget forbids this exact model; no chi=7 proof",
                      "limited_triangle_checks":len(triangles),
                      "triangles":triangles,"rainbow":rainbow},sort_keys=True,indent=2))
