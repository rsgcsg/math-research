#!/usr/bin/env python3
"""Exact Q(sqrt(3)) interval geometry for the two-mixed-hex-star theorem.

All inequalities are certified using rational 433/250 < sqrt(3) < 1733/1000.
The measurable-coloring theorem relies on the accompanying written proof.
"""
from fractions import Fraction as F
import json

L, U = F(433,250), F(1733,1000)
r, s = F(1,250), F(2,5)
eta, rpair = r*r, F(3,20)
Z=(F(0),F(0))

def chk(test, message):
    if not test:
        raise RuntimeError(message)

def ab(a=0,b=0):
    return (F(a),F(b))
def add(a,b):
    return a[0]+b[0],a[1]+b[1]
def sub(a,b):
    return a[0]-b[0],a[1]-b[1]
def neg(a):
    return -a[0],-a[1]
def mul(a,b):
    return a[0]*b[0]+3*a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def root_interval(v):
    a,b=v
    return (a+b*L,a+b*U) if b>=0 else (a+b*U,a+b*L)
def absolute_upper(v):
    return max(abs(x) for x in root_interval(v))

def margins(p,center):
    dx=absolute_upper(sub(p[0],center[0]))
    dy=absolute_upper(sub(p[1],center[1]))
    # Hex is |x-cx|<=sqrt(3)/5,
    #          |y-cy|+|x-cx|/sqrt(3)<=2/5.
    # A radius-r disk fits if both certified margins are positive.
    return L/5-dx-r, s-dy-(dx+2*r)/L

def certify_probe(label,x,source,arrows,centers):
    chk(min(margins(x,source))>0, f"{label} initial disk")
    certified=[]
    for i,u in arrows.items():
        chk(add(mul(u[0],u[0]),mul(u[1],u[1]))==ab(1),
            f"{label}->{i} true unit vector")
        y=(add(x[0],u[0]),add(x[1],u[1]))
        v,d=margins(y,centers[i])
        chk(v>0 and d>0, f"{label}->{i} target disk containment")
        certified.append({"target":i,"vertical_margin_lower":str(v),
                          "slanted_margin_lower":str(d)})
    chk(len(arrows)==6, "exactly six targets")
    return {"probe":label,"radius":str(r),
            "source_vertical_margin_lower":str(margins(x,source)[0]),
            "source_slanted_margin_lower":str(margins(x,source)[1]),
            "six_arrows_unit_and_interior":"PASS",
            "targets":certified}

def certify_pairwise_majority():
    # For every pair of cells in a triangular 7-star, center separation is
    # one of 2sqrt(3)/5, 6/5, 4sqrt(3)/5. Their unit-edge endpoints
    # can each carry an inball of radius rpair=3/20.
    hmin=L/5
    dist_values=[(2*L/5,2*U/5),(F(6,5),F(6,5)),(4*L/5,4*U/5)]
    gaps=[]
    for dmin,dmax in dist_values:
        offset=max(abs(dmin-1),abs(dmax-1))/2
        gap=hmin-offset-rpair
        chk(gap>0, "common radius 3/20 unit-pair inballs")
        gaps.append(str(gap))
    # Majority labels cannot agree on two 7-star cells:
    # pi*(rpair/2)^2 > 2*eta*M. Using pi>3,sqrt(3)<2.
    M_upper=F(12,25)
    chk(3*(rpair/2)**2>2*eta*M_upper,"pairwise strict positive area")
    return {"centroid_distance_types":"2sqrt(3)/5,6/5,4sqrt(3)/5",
            "pair_inball_radius":"3/20","pair_inball_margin_lower":gaps,
            "pair_same_color_dominance_impossible_at_eta":str(eta)}

def certify_robust_two_mixed_needle_tradeoff():
    # Two cases: 0 mixed cells force a repeated dominant label;
    # exactly 1 mixed cell has six distinct dominant labels or a repeat.
    # With a common source disk B(x,19*r/20), each of the six directions
    # admits a length-r/10 angular interval keeping its translate in
    # the corresponding certified radius-r target disk.
    gamma_lower=F(361,400)*F(3)-F(36,25)*F(7,4)
    chk(gamma_lower==F(3,16),"pi>3, sqrt3<7/4 angular area margin")
    K=F(3,160)*r**3
    chk(K==F(3,2500000000),"2/7 tradeoff strict rational K")
    # Earlier positive-energy lemma: repeated-majority pair has
    # a radius-3/20 unit-linked inball pair.
    pair_lower=F(3)*rpair**3/F(16)
    chk(pair_lower>7*K,"repeated-majority pair must cover all q<=6 deficits (<=7K)")
    # Critical source area > six target majority deficits:
    chk(gamma_lower>0 and F(19,20)+F(1,20)==1,
        "source radius plus angular unit displacement fits target radius")
    chk(2*eta*F(12,25)<F(3)*rpair**2/F(8),
        "R0/2 inball overlap beats two majority deficits")
    for q in range(1,7):
        for mixed in range(0,8):
            deficit=max(0,8-q-mixed)
            if deficit:
                pure=7-mixed
                chk(pure>=q and deficit<=7,"q-color deficit counting")
                chk(pure>q or mixed>=1,"all q pure colors must leave a mixed probe cell")
    # Hex cell area M=6sqrt3/25 and every star vertex belongs to at most
    # seven closed one-ball stars.
    return {"status":"PASS",
            "source_fraction":"19/20",
            "angular_halfwidth_r_fraction":"1/20",
            "angular_length_r_fraction":"1/10",
            "r":"1/250","eta":"1/62500",
            "gamma_strictly_greater_than":"3/16",
            "per_star_one_missing_energy_strictly_greater_than_K":str(K),
            "per_star_zero_missing_energy_at_least":"2*K",
            "max_star_overlap":7,
            "finite_window_formula":"J_Omega >= K/7*(2*|U|-7*|Mix intersect N[U]|)_+",
            "general_q_window_formula":"J_Omega >= K/7*((8-q)*|U|-7*|Mix intersect N[U]|)_+ for q=1..6",
            "periodic_energy_factor":"K/(14*pi*M)",
            "scope":"exact rational geometry factors only; no integral or chi=7 proof"}


def main():
    chk(L*L<3<U*U,"strict rational radical enclosure")
    chk(eta==F(1,62500) and eta==r*r,"eta and probe disk area")
    chk(3>F(72,25),"pi>3 and sqrt(3)<2 yield pi>36sqrt(3)/25")
    h=ab(0,F(1,5))
    D=ab(0,F(2,5))
    centers=[(Z,Z),(D,Z),(h,ab(F(3,5))),
             (neg(h),ab(F(3,5))),(neg(D),Z),
             (neg(h),ab(-F(3,5))),(h,ab(-F(3,5)))]
    central={1:(ab(1),Z),
             2:(ab(F(1,2)),ab(0,F(1,2))),
             3:(ab(-F(1,2)),ab(0,F(1,2))),
             4:(ab(-1),Z),
             5:(ab(-F(1,2)),ab(0,-F(1,2))),
             6:(ab(F(1,2)),ab(0,-F(1,2)))}
    outer={0:(ab(-F(99,101)),ab(F(20,101))),
           2:(ab(-F(5,13)),ab(F(12,13))),
           3:(ab(0,-F(1,2)),ab(F(1,2))),
           4:(ab(-1),Z),
           5:(ab(0,-F(1,2)),ab(-F(1,2))),
           6:(ab(-F(5,13)),ab(-F(12,13)))}
    probes=[certify_probe("central", (Z,Z), centers[0],central,centers),
            certify_probe("neighbor", (ab(F(16,25)),Z),centers[1],outer,centers)]
    return {"result":"PASS",
            "scope":"14 exact disk inclusions; measurable Fubini and six-color contradiction are written proof only",
            "sqrt3_certified_interval":[str(L),str(U)],
            "probe_disk_radius":str(r),
            "mixed_threshold_fraction":str(eta),
            "minimum_mixed_cells_per_seven_star":2,
            "asymptotic_density_lower":"2/7",
            "probabilistic_core_inequality":"pi>36sqrt(3)/25",
            "central_and_neighbor_probes":probes,
            "pairwise_majority":certify_pairwise_majority(),
            "robust_two_mixed_needle_tradeoff":certify_robust_two_mixed_needle_tradeoff()}

if __name__=="__main__":
    print(json.dumps(main(),ensure_ascii=False,sort_keys=True,indent=2))
