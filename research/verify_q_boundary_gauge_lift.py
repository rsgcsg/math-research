#!/usr/bin/env python3
"""Verify T170: gauge-normalized T165 separator and stronger coarse lift."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"certificates/q_joint_boundary_gap.json"
CERT=ROOT/"certificates/q_boundary_gauge_lift.json"

def pair(a,b):
    return (a,b) if a<b else (b,a)

def require(cond,msg):
    if not cond:
        raise ValueError(msg)

def derive(source,gauge):
    terms=deepcopy(source["boundary"]["terms"])
    windows=source["boundary"]["saturated_windows"]
    incidence={pair(*t["pair"]):[] for t in terms}
    for j,W in enumerate(windows):
        for i,a in enumerate(W):
            for b in W[i+1:]:
                p=pair(a,b)
                if p in incidence:
                    incidence[p].append(j)
    for t in terms:
        t["transformed_coefficient"]=t["coefficient"]+sum(
            gauge[j] for j in incidence[pair(*t["pair"])]
        )
    sums={k:sum(t["transformed_coefficient"] for t in terms if t["type"]==k)
          for k in ("P","Q","R")}
    vals=[t["transformed_coefficient"] for t in terms]
    rhs=source["boundary"]["rhs"]+2*sum(gauge)
    positive=sum(max(0,x) for x in vals)
    return terms,{
        "coefficient_sums":sums,
        "positive_coefficient_sum":positive,
        "l1_coefficient_sum":sum(abs(x) for x in vals),
        "max_abs_coefficient":max(abs(x) for x in vals),
        "nonzero_coefficients":sum(x!=0 for x in vals),
    },rhs

def verify(cert,source):
    require(cert["schema"]=="q-boundary-gauge-lift-v1","schema")
    require(source["schema"]=="q-joint-boundary-gap-v1","source schema")
    g=cert["window_gauge"]
    require(len(g)==7 and all(type(x) is int for x in g),"integer seven-window gauge")
    require(sum(g)==cert["gauge_sum"]==167,"gauge sum")
    _,summary,rhs=derive(source,g)
    require(rhs==cert["face_rhs"]==336,"face rhs")
    require(summary==cert["transformed"],"transformed coefficient summary")
    require(summary["coefficient_sums"]=={"P":-263,"Q":500,"R":0},"aggregate cancellation")
    require(summary["positive_coefficient_sum"]-rhs==
            cert["coarse_lift_penalty"]==633,"coarse penalty")

    # On the zero-defect face, each saturated window has exactly two equal
    # pairs. Adding g_j times that equality to T165 therefore preserves the
    # face inequality and changes its rhs by exactly 2*sum(g_j).
    p=F(1,27); r=F(14,27)
    qbound=(F(rhs)-summary["coefficient_sums"]["P"]*p
            -summary["coefficient_sums"]["R"]*r)/summary["coefficient_sums"]["Q"]
    require(qbound==F(*cert["boundary_q_upper"])==F(1867,2700),"same boundary q upper")

    # For arbitrary words D=sum Z_j+T is a nonnegative integer.  D=0 gives
    # L'<=336; D>=1 gives L'<=969<=336+633D.
    # Existing T165 arithmetic gives E[D]=85p+19r-13.
    penalty=cert["coarse_lift_penalty"]
    A=263+85*penalty
    B=19*penalty
    C=rhs-13*penalty
    require((A,B,C)==(54068,12027,-7893),"unconditional coefficients")
    require(cert["unconditional_inequality"]["display"]==
            "500 q <= 54068 p + 12027 r - 7893","unconditional display")

    # Using 2r-p<=1, substitute r<=(1+p)/2.
    scalar_p=2*A+B
    scalar_c=2*C+B
    require((scalar_p,scalar_c)==(120163,-3759),"scalar elimination")
    require(cert["scalar_after_transitivity"]["display"]==
            "1000 q <= 120163 p - 3759","scalar display")

    # Compare with the previous lifted scalar bound.
    require(254704-120163==134541 and -8742-(-3759)==-4983
            and 134541==4983*27,"difference factorization")
    require(F(4459,120163)>F(1,27),"q>=7/10 conditional improvement")
    require(F(700+3759,120163)==F(*cert["consequence_if_q_at_least_7_10"]["p_lower"]),
            "conditional lower bound")
    return {
        "status":"PASS",
        "gauge":g,
        "face_rhs":rhs,
        "transformed":summary,
        "coarse_lift_penalty":penalty,
        "unconditional":"500q<=54068p+12027r-7893",
        "scalar":"1000q<=120163p-3759",
        "scope":cert["scope"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    source=json.loads(SOURCE.read_text())
    cert=json.loads(CERT.read_text())
    report=verify(cert,source)
    if args.self_test:
        bad=deepcopy(cert)
        bad["window_gauge"][0]+=1
        try:
            verify(bad,source)
        except ValueError:
            pass
        else:
            raise ValueError("mutated gauge accepted")
        print("self_tests_passed 1")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
