#!/usr/bin/env python3
"""Exact rational verifier for the adjacent two-defect hexagon shadow lemma.

Only checks elementary sharp rational inequalities; the proof that
the forced-color set satisfies them is in the accompanying document.
"""
from fractions import Fraction as F
import json

def verify_periodic_partial_coloring():
    # Triangular lattice N=a^2+a*b+b^2 has no N=2 for integer a,b.
    # Every 7-star B1(v) has one vertex in each residue m+3n mod 7.
    diffs=[(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]
    for m in range(7):
        for n in range(7):
            residues={(m+a+3*(n+b))%7 for a,b in diffs}
            if residues != set(range(7)):
                raise RuntimeError("not seven residue classes in each star")
            if len([r for r in residues if r in (0,1)])!=2:
                raise RuntimeError("double code does not double dominate stars")
    norms={a*a+a*b+b*b for a in range(-12,13) for b in range(-12,13) if (a,b)!=(0,0)}
    if 1 not in norms or 3 not in norms or 2 in norms:
        raise RuntimeError("triangular center distances not 1,3,...")
    r=F(1,20)
    # For unit-free sixth-color disks:
    # nearby centers D=2 sqrt(3)/5 -> D+2r<1 if sqrt3<2.
    if not (F(4,5)+2*r<1):  # upper bound D<4/5
        raise RuntimeError("nearby disks have unit pair risk")
    if not (F(6,5)-2*r>1):
        raise RuntimeError("next nearest disks have unit pair risk")
    # Exact density formula for arbitrary r<1/10, limiting r->1/10:
    # density -> 5/7+pi/(84 sqrt3)
    return {
        "triangular_norm_two_absent":True,
        "seven_star_residues_rainbow":True,
        "two_defect_classes_in_every_star":2,
        "disk_radius_test":"1/20",
        "closest_center_class":"2*sqrt(3)/5",
        "next_nearest_center_class_at_least":"6/5",
        "six_color_partial_covered_density_formula":"5/7+25*pi*r^2/(21*sqrt(3))",
        "limit_r_up_to_1_over_10":"5/7+pi/(84*sqrt(3))",
        "scope":"strict unit-free only on partially colored domain; not 6 coloring of plane"
    }


def verify():
    hlo,hhi=F(69,200),F(7,20)
    if not ((5*hlo)**2<3<(5*hhi)**2):
        raise RuntimeError("irrational hex inradius bracket invalid")
    q=F(9,25)
    vals={
      "F0_vertical_pure_center":hhi*hhi+F(19,40)**2,
      "F0_left_top_bottom_pure":(hhi-F(1,8))**2+F(11,20)**2,
      "F0_left_far_pure":(2*hhi-F(1,8))**2+F(1,20)**2,
      "F1_vertical_pure_center":(F(7,5)-3*hlo)**2+F(19,40)**2,
    }
    expected={
      "F0_vertical_pure_center":F(557,1600),
      "F0_left_top_bottom_pure":F(565,1600),
      "F0_left_far_pure":F(533,1600),
      "F1_vertical_pure_center":F(7177,20000),
    }
    if vals!=expected or any(v>=q for v in vals.values()):
        raise RuntimeError("strict exclusion via pure hex circumdisks not certified")
    rect=(F(71,100)+F(1,8))**2+F(1,4)**2
    if rect!=F(30389,40000) or rect>=1:
        raise RuntimeError("forced color region diameter not below unit")
    if not (F(7,5)-2*hlo==F(71,100)):
        raise RuntimeError("neighbor hex upper x bound")
    return {
        "status":"PASS",
        "scope":"exact rational square bounds and rectangular diameter only, not chi7",
        "hex_inradius_bracket":[str(hlo),str(hhi)],
        "pure_cell_visibility_necessary_center_distance_range":["3/5","7/5"],
        "strictly_below_9_over_25":{k:str(v) for k,v in vals.items()},
        "forced_color_rectangle":{"min_x":"-1/8","max_x":"71/100",
                                   "min_y":"-1/8","max_y":"1/8"},
        "squared_diameter_strict_upper":str(rect),
        "positive_unit_squared_gap":str(1-rect),
        "partial_coloring_color_count":6,
        "periodic_global_partial_coloring":verify_periodic_partial_coloring(),
        "interpretation":"only the first-step forced sixth-color subset is shown unit-free"
    }
if __name__=="__main__":
    print(json.dumps(verify(),indent=2,sort_keys=True))
