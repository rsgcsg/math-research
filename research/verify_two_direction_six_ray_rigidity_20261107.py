#!/usr/bin/env python3
"""60 exact Q(sqrt3) unit leaves, ten independent hex-gadget sources.

Every ray is certified as a unit ray entering a radius-1/50 disk inside
its designated NONMIXED hex cell. The resulting no-rainbow hyperedge
is a necessary condition for a hypothetical weak measurable six-coloring.
The binary reference-or-sixth interface corollary is conditional and
does not settle chi(R^2)=7.
"""
from fractions import Fraction as F
from itertools import product
import json

LO, HI = F(433,250), F(1733,1000)
R=F(1,50)
ETA=F(1,62500)
# original code class, partner shift, probe offset from center C(a,0)
# in hundredths, six target macro-cell coordinates (unordered)
DATA=[
(2,(-3,1),(-75,0),[(-1,1),(2,0),(2,-2),(0,-1),(2,1),(0,2)]),
(2,(1,2),(67,111),[(2,0),(3,2),(3,0),(1,1),(3,3),(1,4)]),
(3,(-3,1),(-129,2),[(3,0),(0,1),(-1,1),(0,-1),(2,1),(0,2)]),
(3,(1,2),(100,55),[(3,0),(4,2),(5,-1),(5,2),(3,3),(6,0)]),
(4,(1,2),(79,63),[(4,0),(5,2),(3,2),(6,-1),(3,3),(6,0)]),
(4,(2,-3),(-28,-67),[(4,0),(6,-3),(2,0),(5,-3),(5,0),(3,1)]),
(5,(-3,1),(-44,58),[(5,0),(2,1),(5,-1),(3,0),(5,2),(6,0)]),
(5,(1,2),(38,65),[(5,0),(6,2),(3,2),(6,-1),(4,0),(4,3)]),
(6,(-3,1),(-98,59),[(6,0),(3,1),(5,-1),(3,0),(5,2),(3,3)]),
(6,(1,2),(72,9),[(6,0),(7,2),(8,-2),(6,-1),(8,1),(6,2)]),
]

def require(ok,reason):
    if not ok: raise RuntimeError(reason)
def enc(a,b):
    return (a+b*LO,a+b*HI) if b>=0 else (a+b*HI,a+b*LO)
def k(p):
    return (p[0]+3*p[1])%7

def verify_geometry():
    require(LO*LO<3<HI*HI,'sqrt3 rational enclosure')
    lower_hi=enc((1+R)**2+F(3,25),-F(2,5)*(1+R))[1]
    upper_lo=enc((1-R)**2+F(3,25), F(2,5)*(1-R))[0]
    global_min=F(1000)
    minimum_id=None
    rows=[]
    for a,shift,(ix0,iy0),targets in DATA:
        require(len(targets)==6 and len(set(targets))==6,
                'six distinct whole hex cells per probe')
        require((a,0) in targets and (a+shift[0],shift[1]) in targets,
                'source and precise partner of same residue')
        codes=[k(p) for p in targets]
        require(codes.count(a)==2 and sorted(c for c in codes if c!=a)==
                [c for c in range(2,7) if c!=a],
                'two cells of source class plus one of each other class')
        ix,iy=F(ix0,100),F(iy0,100)
        min_case=F(1000)
        for m,n in targets:
            z=F(2*(a-m)-n,5)
            y=iy-F(3*n,5)
            A=ix*ix+3*z*z+y*y
            B=2*ix*z
            d_lo,d_hi=enc(A,B)
            gaplo=d_lo-lower_hi
            gaphi=upper_lo-d_hi
            require(gaplo>0 and gaphi>0,
                    f'exact internal ray failed for class {a}, partner {shift}, target {(m,n)}')
            if min(gaplo,gaphi)<global_min:
                global_min=min(gaplo,gaphi)
                minimum_id=[a,list(shift),[m,n],
                            'lower' if gaplo<=gaphi else 'upper']
            min_case=min(min_case,gaplo,gaphi)
        rows.append({'source_class':a,'partner_shift':list(shift),
                     'probe_offset_hundredths':[ix0,iy0],
                     'all_six_rays_true':'PASS',
                     'case_min_squared_gap':str(min_case)})
    require(global_min==F(1637,25000),'global strict margin 1637/25000')
    return rows,global_min,minimum_id

def verify_generator_spans():
    spans=[]
    for a in range(2,7):
        ts=[t for c,t,_,_ in DATA if c==a]
        require(len(ts)==2,'two gadgets for each source class')
        require(all(k(t)==0 for t in ts),'both shifts in index-seven kernel L')
        determinant=ts[0][0]*ts[1][1]-ts[0][1]*ts[1][0]
        require(abs(determinant)==7,'independent shifts span all of L')
        spans.append({'class':a,'generators':[list(t) for t in ts],
                      'absolute_determinant':abs(determinant),
                      'full_kernel_generated':True})
    return spans

def verify_boolean_rainbow_formula():
    # For one source a and one of the two geometric witnesses:
    # source and its class-a partner are the duplicated original class.
    # Four additional leaves each have another original reference color.
    # With only reference(a) or sixth available at each macro,
    # six colors appear iff source/partner split and the other four are baseline.
    for a in range(2,7):
        for flags in product((0,1),repeat=6):
            source,partner,*others=flags
            labels=[6 if source else a-1,6 if partner else a-1]
            labels += [6 if flip else b-1
                       for b,flip in zip((b for b in range(2,7) if b!=a),others)]
            six_rainbow=len(set(labels))==6
            require(six_rainbow==bool(source!=partner and not any(others)),
                    'exact six-color binary interface truth table')
    return {'patterns_checked':5*64,'no_rainbow_implies':
            'x_a(v)!=x_a(v+t) forces >=1 sixth-colored helper in one of four other classes'}

def verify_area():
    # If all six target hexes are eta-near-monochromatic, positive-area
    # common unit-translate colors cannot cover all six labels.
    # pi>3,sqrt3<2 gives pi*r^2 > 6*eta*(6sqrt3/25).
    require(3*R*R>6*ETA*F(12,25),'strict weak-measurable palette contradiction margin')
    return {'small_disk_radius':str(R),'hex_area_exact':'6*sqrt(3)/25',
            'hex_majority_defect_threshold':str(ETA),
            'mass_contradiction':'pi/2500 > 6*(1/62500)*(6*sqrt(3)/25)'}

def main():
    rows,gmin,witness=verify_geometry()
    return {'result':'PASS',
            'scope':'60 exact rational-radical hex inball certificates; 5x64 binary assignments; no χ=7 proof',
            'witnesses':rows,'ray_count':60,'smallest_strict_squared_gap':str(gmin),
            'smallest_gap_at':witness,
            'rank_two_kernel_bases':verify_generator_spans(),
            'binary_six_rainbow_formula':verify_boolean_rainbow_formula(),
            'six_leaf_weak_color_area':verify_area()}

if __name__=='__main__':
    print(json.dumps(main(),sort_keys=True,indent=2))
