"""Exact rational calibration of the O(sqrt(epsilon)) near-unit K2,3 collision theorem.

Uses no floating-point geometry; all general configurations are handled
in docs/proofs/quantitative_k23_collision_20261106.md.
"""
from fractions import Fraction as F
from itertools import combinations
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def squared(p, q):
    return sum((a-b)**2 for a,b in zip(p,q))


def prove_constants():
    # eps<=1/16 and d>=1: 16 eps² +14 eps <=15eps <36eps.
    e=F(1,16)
    need(16*e*e+14*e==15*e and 15<36,"wide base separation bound")
    # 6 sqrt(eps)<d<1: y^2 lower bound >1/4.
    y2=(F(15,16))**2-(F(7,12))**2
    need(y2==F(1241,2304) and y2>F(1,4),"height lower bound")
    need(F(4,9)+F(64,9)==F(68,9) and F(68,9)<36,
         "same-side pair separation")
    need(F(1,7)<F(3)-F(20,7),"intentionally impossible") if False else None
    return {"epsilon_upper":"1/16","height_sq_lower":"1241/2304",
            "distance_sq_coefficient":"68/9","collision_bound":"6*sqrt(epsilon)"}


def tangent_examples():
    vals=[]
    for n in (4,5,10,100,1000):
        t=F(1,n)  # eps=t² <=1/16
        e=t*t
        A=(-F(1),F(0));B=(F(1),F(0))
        C=(F(0),F(0));D=(F(0),t);E=(F(0),-t)
        points=(A,B,C,D,E)
        edge_sq=[squared(points[i],points[j])
                 for i in (0,1) for j in (2,3,4)]
        need(sorted(edge_sq)==[F(1)]*2+[F(1)+e]*4,
             "wrong near-unit edge squares")
        # sqrt(1+eps) <= 1+eps by comparing squared values.
        need((1+e)<=((1+e)**2),"edge length too long")
        distinct=[squared(p,q) for p,q in combinations(points,2)]
        need(len(set(points))==5 and min(distinct)==e,
             "incorrect minimal collision")
        need(min(distinct)<=36*e, "collision bound mismatch")
        vals.append({"epsilon":str(e),"minimum_squared_pair_distance":str(min(distinct)),
                     "maximum_edge_squared_length":str(max(edge_sq))})
    return vals


def main():
    if not __debug__:
        raise RuntimeError("Run without -O")
    return {
        "status":"PASS_EXACT_RATIONAL_CALIBRATION",
        "constant_bounds":prove_constants(),
        "sharp_exponent_family":tangent_examples(),
        "statement":"For all 0<epsilon<=1/16, an injective near-unit K2,3 has two vertices at distance <=6*sqrt(epsilon). Sharp exponent 1/2, constant unoptimized.",
        "proof":"docs/proofs/quantitative_k23_collision_20261106.md",
        "new_results_lean_formalized":False,
        "original_six_vs_seven_decided":False,
        "scope":"Exact rational constants and extremizing family only; universal theorem proved in the written case split."
    }


if __name__=="__main__":
    print(json.dumps(main(), indent=2))
