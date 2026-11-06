#!/usr/bin/env python3
"""Finite integer calibration only, not the infinite code classification or HN=7."""
from itertools import product
import json


def check(ok, description):
    if not ok:
        raise RuntimeError(description)


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
            'optimal_hex_robust_halfwidth':'(sqrt(7)-2)/(sqrt(7)+2)'}


if __name__=='__main__':
    print(json.dumps(compute(),sort_keys=True,indent=2))
