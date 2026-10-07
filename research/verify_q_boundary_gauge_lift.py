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

    # Exact dual certificate for optimality inside the R-cancelling gauge class.
    # Index the non-Q rows in their inherited source order. For each selected
    # transformed coefficient b_i, max(0,b_i) >= b_i. The selected rows have
    # old-coefficient sum -700 and cover each of the seven window gauges seven
    # times, hence their transformed sum is -700+7*sum(g)=469 for every real
    # gauge with sum(g)=167. Q is unchanged and contributes a fixed positive
    # sum 500, so no such gauge can have positive coefficient sum below 969.
    opt=cert["optimality_certificate"]
    nonq=[t for t in source["boundary"]["terms"] if t["type"]!="Q"]
    selected=opt["selected_non_q_indices"]
    require(len(selected)==len(set(selected))==33 and
            all(type(i) is int and 0<=i<len(nonq) for i in selected),
            "optimality selected row indices")
    incidence={pair(*t["pair"]):[] for t in nonq}
    for j,W in enumerate(source["boundary"]["saturated_windows"]):
        for ia,a in enumerate(W):
            for b in W[ia+1:]:
                pkey=pair(a,b)
                if pkey in incidence:
                    incidence[pkey].append(j)
    old_sum=sum(nonq[i]["coefficient"] for i in selected)
    window_counts=[sum(j in incidence[pair(*nonq[i]["pair"])] for i in selected)
                   for j in range(7)]
    q_terms=[t for t in source["boundary"]["terms"] if t["type"]=="Q"]
    q_positive=sum(max(0,t["coefficient"]) for t in q_terms)
    lower=old_sum+sum(window_counts[j]*g[j] for j in range(7))
    require(old_sum==opt["selected_original_coefficient_sum"]==-700,
            "optimality selected old coefficient sum")
    require(window_counts==opt["selected_window_incidence_counts"]==[7]*7,
            "optimality equal window incidence")
    require(lower==opt["non_q_positive_lower_bound"]==469,
            "optimality non-Q positive lower bound")
    require(q_positive==opt["fixed_q_positive_sum"]==500,
            "optimality fixed Q positive sum")
    require(lower+q_positive==opt["total_positive_lower_bound"]==
            summary["positive_coefficient_sum"]==969,
            "optimality attained total positive sum")
    require(opt["minimum_coarse_lift_penalty"]==
            summary["positive_coefficient_sum"]-rhs==633,
            "optimality attained coarse penalty")

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
        "gauge_class_optimal_positive_sum":969,
        "gauge_class_optimal_penalty":633,
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
        rejected=0
        for mutant in (bad, deepcopy(cert)):
            if mutant is not bad:
                mutant["optimality_certificate"]["selected_non_q_indices"][0]=2
            try:
                verify(mutant,source)
            except ValueError:
                rejected+=1
            else:
                raise ValueError("mutated T170 certificate accepted")
        print("self_tests_passed",rejected)
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
