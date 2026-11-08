#!/usr/bin/env python3
"""Pure rational certificates for a measurable unit-chord independent circle set.

No numerical integration, no proof of χ(R²)=7. The accompanying document
proves strict independence and the sharp 1/2 measurable independence sup.
"""
from fractions import Fraction as F
import json

def check(ok, message):
    if not ok: raise RuntimeError(message)

def main():
    x=F(5,6)
    T5=16*x**5-20*x**3+5*x
    check(T5==F(-475,486),"exact 5-angle Chebyshev identity")
    check(T5<F(-1,2),"cos(5 alpha)<cos(2pi/3)")
    # 5/6 > (1+sqrt5)/4  <=> 7/3>sqrt5, because 4*5/6-1=7/3.
    check(F(7,3)**2>5,"alpha < pi/5 without floating point")
    # If alpha/(2pi) rational, twice cosine is a rational algebraic integer.
    twice_cos=2*x
    check(twice_cos==F(5,3) and twice_cos.denominator!=1,
          "rational non-integer 2cos(alpha) excludes root-of-unity angle")
    # If beta=5alpha in (2pi/3,pi), I=(0,beta) and I+beta are disjoint.
    return {"result":"PASS",
            "unit_circle_radius_squared":"3",
            "unit_chord_cos_alpha":"5/6",
            "twice_cos_alpha_non_integer":"5/3",
            "cos_five_alpha":"-475/486",
            "angular_bound":"2*pi/3 < beta=5*alpha < pi",
            "explicit_independent_set":"{theta : (5 theta mod 2 pi) in (0,beta)}",
            "independent_set_angular_measure":"beta > 2*pi/3",
            "measurable_independent_density_sup":"1/2, not attained",
            "scope":"exact rational angle certification; ergodic and geometric arguments in written proof only"}

if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True,indent=2))
