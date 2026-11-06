#!/usr/bin/env python3
"""Finite integer calibration only, not the infinite code classification or HN=7."""
from itertools import product
from fractions import Fraction as Q
import json


def check(ok, description):
    if not ok:
        raise RuntimeError(description)



def verify_explicit_mixing():
    # Hex side 2/5: h=sqrt(3)/5 and area=6*sqrt(3)/25.
    # For seven-star center separations 2sqrt(3)/5, 6/5, 4sqrt(3)/5,
    # all unit-pair endpoints have balls of radius 3/20 inside their hexes.
    r=Q(3,20)
    check(Q(3)>Q(13,8)**2,'D_min: sqrt(3)>13/8')
    check(Q(3)>Q(5,4)**2,'D_middle: sqrt(3)>5/4')
    check(Q(3)<Q(7,4)**2,'D_max: sqrt(3)<7/4')
    # eta = pi*r^2/(16*AreaHex) = 3*pi/(512*sqrt(3)).
    check(r*r*Q(25,96)==Q(3,512),'exact eta coefficient')
    centers=[(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]
    norms={m*m+m*n+n*n for a,b in centers for c,d in centers
           for m,n in [(a-c,b-d)] if (m,n)!=(0,0)}
    check(norms=={1,3,4},'all seven-star center distances')
    return {'hex_side':'2/5','unit_endpoint_inball_radius':'3/20',
            'strong_mixing_area_fraction_gt':'3*pi/(512*sqrt(3))',
            'asymptotic_fraction_of_strongly_mixed_hexes_at_least':'1/7',
            'center_distance_squared_in_units_of_3s^2':sorted(norms),
            'scope':'conditional on weak measurable six coloring; not proof chi=7'}


def compute():
    disp=[(m,n) for m,n in product(range(-2,3), repeat=2)
          if 0<max(abs(m),abs(n),abs(m+n))<=2]
    check(len(disp)==18,'degree of the triangular square')
    near=[(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]
    valid=[(a,b) for a,b in product(range(7),repeat=2) if (a,b)!=(0,0)
           and all((a*m+b*n)%7 for m,n in disp)]
    check(len(valid)==12,'valid linear mod7 maps')
    slopes=sorted({(b*pow(a,-1,7))%7 for a,b in valid})
    check(slopes==[3,5], 'allowed chiral slopes')
    for a,b in valid:
        for m,n in product(range(7),repeat=2):
            check({(a*(m+i)+b*(n+j))%7 for i,j in near}==set(range(7)),
                  '1-perfect-code closed neighborhoods')
    for u,v in product(range(7),repeat=2):
        intersections=[(m,n) for m,n in product(range(7),repeat=2)
                       if (m+3*n)%7==u and (m+5*n)%7==v]
        check(len(intersections)==1,'opposite chiral cosets intersect')
    minimal={}
    for b in slopes:
        norms=[m*m+m*n+n*n for m,n in product(range(-7,8),repeat=2)
               if (m,n)!=(0,0) and (m+b*n)%7==0]
        check(min(norms)==7,'Eisenstein norm7 period lattice')
        minimal[str(b)]=min(norms)
    return {'status':'PASS', 'scope':'finite exact verification only; Dejter classification and HN open not checked',
            'square_graph_degree':len(disp),'closed_unit_ball_size':len(near),
            'nonzero_linear_mod7_candidates':48,'valid_linear_mod7_candidates':len(valid),
            'valid_chiral_slopes':slopes,'all_mod7_closed_neighborhoods_rainbow':True,
            'opposite_chiral_cosets_intersect':True,'shortest_same_color_norm':minimal,
            'optimal_hex_side':'2/(2+sqrt(7))',
            'optimal_hex_robust_halfwidth':'(sqrt(7)-2)/(sqrt(7)+2)',
            'quantitative_six_color_mixing':verify_explicit_mixing()}


if __name__=='__main__':
    print(json.dumps(compute(),sort_keys=True,indent=2))
