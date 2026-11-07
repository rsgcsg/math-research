#!/usr/bin/env python3
"""Exact rational verifier for the adjacent two-defect hexagon shadow lemma.

Only checks elementary sharp rational inequalities; the proof that
the forced-color set satisfies them is in the accompanying document.
"""
from fractions import Fraction as F
import json

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
        "interpretation":"only the first-step forced sixth-color subset is shown unit-free"
    }
if __name__=="__main__":
    print(json.dumps(verify(),indent=2,sort_keys=True))
