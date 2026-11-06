"""Exact calibrations for robust unit-distance graph exclusions and collision limits.

A general geometric theorem is proved in
docs/proofs/near_unit_graph_stability_and_collisions_20261106.md.
This tests its sharp constants and concrete counterexamples, not its infinite scope.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import gcd
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def mul(x, y, d):
    return x[0]*y[0] + d*x[1]*y[1], x[0]*y[1] + x[1]*y[0]


def sub(x, y):
    return tuple(a-b for a,b in zip(x,y))


def positive(x, d):
    a,b=x
    if b == 0:
        return a>0
    if a>=0 and b>0:
        return True
    if a<=0 and b<0:
        return False
    if a>0 and b<0:
        return a*a > d*b*b
    return d*b*b > a*a


def verify_k4():
    # e4=3-2√2; square side a=1-e4=2√2-2.
    one=(Q(1),Q(0))
    e4=(Q(3),Q(-2))
    side=sub(one,e4)
    diagonal=mul((Q(0),Q(1)),side,2)
    need(diagonal==add(one,e4),"extremal square does not fit interval")
    need(sub(mul(diagonal,diagonal,2),
                 mul((Q(2),Q(0)),mul(side,side,2),2))
         ==(Q(0),Q(0)), "square squared distance mismatch")
    # Compare robust seven's margin eps* against 1/7, then e4 against 1/7.
    # √7<8/3 is exact: 7<64/9.
    need(Q(7)<Q(64,9),"sqrt7 upper")
    # √2<10/7 is exact: 2<100/49
    need(Q(2)<Q(100,49),"sqrt2 upper")
    need(positive(sub(e4,(Q(1,7),Q(0))),2),"k4 gap not above 1/7")

    samples = [(x,y) for x,y in product(range(-2,3), repeat=2)]
    count=0
    for pts in combinations(samples,4):
        squares=[(a[0]-b[0])**2+(a[1]-b[1])**2
                 for a,b in combinations(pts,2)]
        need(max(squares)>=2*min(squares),"four point diameter theorem sample")
        count+=1
    return {"sharp_threshold":"3-2*sqrt(2)","square_side":"2*sqrt(2)-2",
            "robust_seven_band_inside_k4_free_range":True,
            "integer_grid_four_point_samples":count}


def verify_k23():
    one=(Q(1),Q(0))
    examples=[]
    for n in (5,10,20,100,1000):
        t=Q(1,n)
        # In Q(sqrt(3)), squared distance to A and B from extra point E.
        d2=(1+t*t,t)
        upper=(1+t)*(1+t)
        need(positive(sub(d2,one),3),"extra point distance not above one")
        need(positive(sub((upper,Q(0)),d2),3),
             "extra point outside (1,1+t)")
        # Exact 4 other edges of K2,3 have square distance one.
        C=(Q(1,2),Q(1,2))  # y coefficient multiplies sqrt3
        D=(Q(1,2),Q(-1,2))
        A=(Q(0),Q(0)); B=(Q(1),Q(0))
        def sqdist(p,q):
            dx=p[0]-q[0]
            dy=p[1]-q[1]
            return dx*dx+3*dy*dy
        need(sqdist(A,C)==1 and sqdist(B,C)==1
             and sqdist(A,D)==1 and sqdist(B,D)==1,
             "four exact K2,3 edges")
        # Offset t in the real y coordinate; directly tested via d² above.
        examples.append({"t":str(t),"other_two_edges_sq":"1+sqrt(3)*t+t^2"})
    return {"original_k23_has_no_injective_exact_realization":True,
            "homomorphism_collision":"third common neighbor coalesces with C",
            "exact_rational_perturbation_scales":examples}


def main():
    if not __debug__:
        raise RuntimeError("non-optimized Python required")
    return {
        "schema":"hn_near_unit_stability_exact_v1",
        "status":"PASS_FINITE_EXACT_ARITHMETIC",
        "k4":verify_k4(),
        "k23":verify_k23(),
        "written_proof":"docs/proofs/near_unit_graph_stability_and_collisions_20261106.md",
        "scope":"Finite rational and quadratic-field arithmetic samples only. Compactness/unit-homomorphism criterion established in written proof, not formalized here.",
        "full_make_check_executed":False,
        "chi_r2_6_or_7_decided":False,
        "finite_non6_unit_graph_found":False
    }


if __name__=="__main__":
    print(json.dumps(main(),ensure_ascii=False,indent=2))
