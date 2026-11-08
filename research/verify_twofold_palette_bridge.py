#!/usr/bin/env python3
"""Exact finite-field and rational audit for conditional twofold palette bridge.

The twelve-leaf unit-triangle inequality is imported from the earlier
two-defect shadow proof; this script does NOT reverify its large geometry.
"""
from fractions import Fraction as F
from itertools import combinations
import json

def check(ok, msg):
    if not ok: raise RuntimeError(msg)

def ap(t):
    return any((a+c-2*b)%7==0 for a,b,c in
               ((a,b,c) for a in t for b in t for c in t if len({a,b,c})==3))

def main():
    counts=[]
    for a,b in combinations(range(7),2):
        other=set(range(7))-{a,b}
        mid=((a+b)*4)%7
        left=(2*a-b)%7
        right=(2*b-a)%7
        ap_candidates={mid,left,right}
        nonap_candidates=sorted(other-ap_candidates)
        check(len(ap_candidates)==3 and ap_candidates<=other,
              'three distinct AP completions of any two distinct F7 points')
        check(len(nonap_candidates)==2,'exactly two non-AP extensions')
        for t in other:
            check(ap((a,b,t))==(t in ap_candidates),
                  'direct AP cross-check')
        counts.append({'defect_pair':[a,b],
                       'arithmetic_progression_extensions':sorted(ap_candidates),
                       'non_arithmetic_extensions':nonap_candidates})
    eta=F(1,62500)
    M_over_sqrt3=F(6,25)
    deficit_over_sqrt3=12*eta*M_over_sqrt3
    # Strict comparison using pi > 3, sqrt(3) < 2.
    deficit_upper=2*deficit_over_sqrt3
    four_frozen_lower=F(3,19600)
    check(deficit_upper < four_frozen_lower,'twelve nearly pure macro-cells contradict triangle certificate')
    check(F(3,56448)*F(4,7)>eta,
          'per-cell defect bound pi/(56448 sqrt3) > eta from pi>3 and sqrt3<7/4')
    # The particular local recoding uses a single existing pure hexagon,
    # whose diameter 4/5 is strictly less than unit distance.
    check(F(4,5)<1,'single recolored hex has no unit pair')
    return {'status':'PASS',
            'field_prime':7,'two_defect_pairs_tested':len(counts),
            'all_have_exactly_two_non_AP_extensions':True,
            'near_monochromatic_max_12_leaf_deficit_over_sqrt3':str(deficit_over_sqrt3),
            'strict_rational_upper_for_12_leaf_deficit':str(deficit_upper),
            'strict_rational_lower_from_prior_four_frozen_triangle':str(four_frozen_lower),
            'threshold_eta':str(eta),
            'single_recolored_tile_diameter':'4/5<1',
            'pairs':counts,
            'scope':'conditional four-global-color bridge, not full HN=7 proof'}

if __name__=='__main__':
    print(json.dumps(main(),indent=2,sort_keys=True))
