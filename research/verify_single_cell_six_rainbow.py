#!/usr/bin/env python3
"""Exact Q(sqrt(3)) witness for 5x6 unit-ray palette-avalanche gadgets.

No floating point, external SAT solver, or heuristic inequalities. This does
NOT construct a finite NON6 unit-distance graph or prove chi(plane)=7.
"""
from fractions import Fraction as F
import json

LO, HI = F(433,250), F(1733,1000)
R=F(1,100)
ETA=F(1,62500)
CASES={
 2:(F(-21,20),F(0),[(-1,1),(2,-2),(0,-1),(-1,2),(-1,0),(2,0)]),
 3:(F(1),F(11,20),[(3,2),(4,2),(5,2),(3,3),(6,0),(3,0)]),
 4:(F(-7,10),F(-3,5),[(2,0),(5,-3),(3,-2),(2,1),(2,-1),(4,0)]),
 5:(F(-1),F(-11,20),[(2,0),(3,0),(3,-2),(4,-2),(3,1),(5,0)]),
 6:(F(-19,20),F(11,20),[(3,2),(3,0),(4,0),(3,3),(3,1),(6,0)]),
}


def require(ok,msg):
    if not ok:raise RuntimeError(msg)


def enclose_root3(a,b):
    """Exact enclosing rationals for a+b*sqrt(3)."""
    return (a+b*LO,a+b*HI) if b>=0 else (a+b*HI,a+b*LO)


def check():
    require(LO*LO<3<HI*HI, "strict rational enclosure of sqrt(3)")
    lower=a0,b0=(1+R)**2+F(3,25),-F(2,5)*(1+R)
    upper=a1,b1=(1-R)**2+F(3,25),F(2,5)*(1-R)
    lower_hi=enclose_root3(a0,b0)[1]
    upper_lo=enclose_root3(a1,b1)[0]
    min_gap=F(1_000_000)
    min_spot=None
    list_rows=[]
    for a,(xi,zeta,targets) in CASES.items():
        require(len(targets)==6, "six distinct leaves per source")
        require(len(set(targets))==6,"no repeated target macro cell")
        rows=[]
        for idx,(m,n) in enumerate(targets,1):
            require(((m+3*n)%7==idx+1) if idx<6 else ((m,n)==(a,0)),
                    "five original palettes plus unique recolored cell")
            b=F(2*a-2*m-n,5)
            dy=zeta-F(3*n,5)
            d0=xi*xi+3*b*b+dy*dy
            d1=2*xi*b
            dist_lo,dist_hi=enclose_root3(d0,d1)
            gap_low=dist_lo-lower_hi
            gap_high=upper_lo-dist_hi
            require(gap_low>0 and gap_high>0,
                    f"strict radius-r internal unit leaf failure a={a}, idx={idx}")
            for name,g in (("lower",gap_low),("upper",gap_high)):
                if g<min_gap:
                    min_gap=g
                    min_spot=(a,idx,name)
            rows.append({"color":idx, "hex":[m,n],
                         "distance_squared_form":[str(d0),str(d1)],
                         "lower_squared_margin_at_least":str(gap_low),
                         "upper_squared_margin_at_least":str(gap_high)})
        list_rows.append({"original_coset":a,
                          "center_probe_offset":[str(xi),str(zeta)],
                          "six_unit_leaf_targets":rows})
    require(len(list_rows)==5 and min_gap==F(583,62500) and min_spot==(5,2,"lower"),
            "30-margin exact minimum")
    require(3*R*R>6*ETA*F(12,25),
            "pi*r^2 > 6 eta M using pi>3, sqrt(3)<2")
    return {"status":"PASS",
            "scope":"30 exact hex inball distance certificates; no infinite measure or chi7 proof",
            "sqrt3_interval":[str(LO),str(HI)],
            "inball_radius":str(R),"majority_defect_threshold":str(ETA),
            "smallest_strict_squared_margin":str(min_gap),
            "smallest_margin_occurs_at":{"original_coset":min_spot[0],
                                          "leaf_color":min_spot[1],
                                          "which_bound":min_spot[2]},
            "weak_mass_obstruction":"pi/10000 > 6*(1/62500)*(6*sqrt(3)/25)",
            "five_gadgets":list_rows}


if __name__=="__main__":
    print(json.dumps(check(),ensure_ascii=False,sort_keys=True,indent=2))
