#!/usr/bin/env python3
"""Exact toy checks for thermodynamic needle badness; NOT chi(plane)=7."""
from fractions import Fraction as F
from itertools import product
import json


def checked(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def odd_cycle(n):
    assignments = list(product((0, 1), repeat=n))
    bad_words = [tuple(i for i in range(n) if word[i] == word[(i+1) % n]) for word in assignments]
    minimum = min(map(len, bad_words))
    single = [bad for bad in bad_words if len(bad)==1]
    counts = [sum(i in w for w in single) for i in range(n)]
    checked(minimum == 1, 'odd-cycle two coloring must have at least one bad edge')
    checked(len(single)==2*n and counts==[2]*n, 'uniform symmetric optimal witness')
    lower = F(minimum,n)
    upper = max(F(ct,len(single)) for ct in counts)
    checked(lower==upper==F(1,n),'minmax gap')
    return {'n_vertices':n,'n_edges':n,'min_bad_edges_for_two_colors':minimum,
            'number_of_exactly_one_bad_edge_colorings':len(single),
            'symmetric_average_bad_probability_per_edge':str(upper),
            'beta_2_exact':str(lower)}


def seam_ratios():
    output=[]
    for L in (3,4,8,10,100):
        seam=F(4,L)-F(4,L*L)
        checked(seam==1-F((L-2)**2,L*L),'seam identity')
        output.append({'L':L,'boundary_stripe_upper_fraction':str(seam)})
    return output


def reported_parts_upper():
    # Numeric value copied from Parts 2020; not an independent geometry certificate.
    uncovered_fraction_reported = F(143017209, 10**12)
    q = 6
    upper = 2*uncovered_fraction_reported/q
    checked(upper == F(47672403,10**12), 'reported area to badness conversion')
    checked(upper < F(1,20000),'near-perfect six partial coloring implies tiny Potts badness')
    return {'source':'Jaan Parts 2020; area numerical report only',
            'reported_hole_fraction': str(uncovered_fraction_reported),
            'q':q,'random_filling_energy_upper_estimate':str(upper),
            'upper_in_decimal':format(float(upper), '.12f'),
            'general_formula':'a_q <= 2*hole_density/q'}


def robust_mixing_tradeoff():
    r = F(3,20)
    coefficient_over_sqrt3 = r**3*F(25,224*6)
    checked(coefficient_over_sqrt3 == F(9,143360), 'rigorous hex star overlap constant')
    checked(F(3,20)**2 * F(25,16*6) == F(3,512), 'monochromatic majority threshold coefficient')
    checked(F(3,20)**3/F(16) == F(27,128000), 'per star angular/area bad mass coefficient over pi')
    return {'star_n':7,'inradius_ball_radius':'3/20',
            'max_overcount':7,
            'strong_mixing_threshold':'3*pi/(512*sqrt(3))',
            'unnormalized_energy_contribution_per_uncovered_star':'27*pi/128000',
            'normalized_tradeoff_coefficient':'9/(143360*sqrt(3))'}


def main():
    result={'status':'PASS',
            'scope':'toy finite exact math only; no proof of six/seven or continuum integration',
            'odd_cycles':[odd_cycle(n) for n in (3,5,7,9)],
            'parts_partial_tiling_conversion':reported_parts_upper(),
            'robust_energy_mixing_tradeoff':robust_mixing_tradeoff(),
            'square_seam':[x for x in seam_ratios()],
            'periodization_boundary_formula':'4/L - 4/L^2',
            'thermodynamic_limit_claim':'mathematical written proof, not executable finite validation'}
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
