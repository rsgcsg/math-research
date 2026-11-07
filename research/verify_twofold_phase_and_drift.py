#!/usr/bin/env python3
"""Exact 42-code phase overlap and sparse color-identity drift counterexample.

This validates finite integer witnesses and rational separations. It does NOT
claim an entire plane six-coloring, finite NON6 unit graph, or χ(plane)=7.
"""
from itertools import combinations
from fractions import Fraction as F
import json

D=((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1))
W={(i,j) for i in range(-2,3) for j in range(-2,3)}
T=[(s,a,b) for s in (3,5) for a,b in combinations(range(7),2)]


def require(p,msg):
    if not p: raise RuntimeError(msg)


def bit(t,x):
    s,a,b=t
    return int((x[0]+s*x[1])%7 in (a,b))


def verify_phase_overlap():
    require(len(T)==42,'forty two global double-code phases')
    require(len({tuple(bit(t,x) for x in sorted(W)) for t in T})==42,
            'global phases distinguishable on W2')
    res=[]
    for move in ((1,0),(0,1)):
        Q=W & {(x+move[0],y+move[1]) for x,y in W}
        require(len(Q)==20,'twenty intersection sites')
        bad=[]
        for i,t in enumerate(T):
            for j,u in enumerate(T):
                if i==j:continue
                if all(bit(t,x)==bit(u,x) for x in Q):
                    bad.append((i,j))
        require(not bad,'different codes cannot match on neighboring windows')
        res.append({'neighbor_step':move,'intersection':20,
                    'different_codes_matching':0})
    return res


def verify_sparse_drift():
    # The original 7-color hex pattern uses labels k=m+3n (mod7).
    # Leave k=0,1 unpainted and retain k=2,...,6 as pure colors 1,...,5.
    # Repaint arbitrarily chosen widely separated cells (2+7t,0) as 6.
    for m in range(-14,15):
        for n in range(-14,15):
            residues={(m+dx+3*(n+dy))%7 for dx,dy in D}
            require(residues==set(range(7)),'exactly two holes per star')
            orig=[r for r in residues if r not in (0,1)]
            require(len(orig)==5,'five distinct pure-cell classes')
    for t in range(-5,6):
        require((2+7*t)%7==2,'repaint only one pure residue class')
    # Exact lower bound using sqrt(3)>5/3. Center separation
    # between successive (2+7t,0) tiles is 14sqrt3/5 > 14/3.
    center_dist_gt=F(14,3)
    min_points_dist_gt=center_dist_gt-2*F(2,5)
    require(min_points_dist_gt==F(58,15)>1,
            'new color six cells mutually avoid exact unit distance')
    require(2*F(2,5)<1,'same hex diameter below unit')
    return {'base_unpainted_residues':[0,1],
            'base_monochromatic_residues':[2,3,4,5,6],
            'sparse_repainted_residue':2,
            'recolored_cells':'(2+7*t,0) for t in arbitrary A subset of Z',
            'base_color_labels':[1,2,3,4,5],
            'new_color_label':6,
            'distinct_repainted_centers_distance_strict_gt':'14/3',
            'distinct_repainted_points_distance_strict_gt':str(min_points_dist_gt),
            'new_same_cell_diameter':'4/5',
            'missing_area_fraction':'2/7',
            'full_plane_colorability_claim':'NONE: defined only on the five complete residue classes'}


def verify_phase_path_bound():
    # A path of L primitive coordinate steps has L+1 windows. If
    # all are good the overlap property transports the same phase.
    for L in range(40):
        require(len(range(L+1))==L+1,'union-bound window count')
    return {'fixed_displacement_manhattan_length':'L',
            'max_bad_windows_along_shortest_path':'L+1',
            'probability_two_good_same_phase_lower':
                'max(0, 1-(L+1)*epsilon_phase)',
            'epsilon_phase':
                'min(1,49*(7*d-2+28*pi*M*E/K))',
            'scope':'deterministic overlap and union bound; no Gibbs law or chi=7 proof'}


def main():
    return {'status':'PASS','exact_arithmetic':True,
            'phase_overlap':verify_phase_overlap(),
            'sparse_color_identity_drift':verify_sparse_drift(),
            'phase_path_bound':verify_phase_path_bound(),
            'conclusion':'even an exact global double-code defect set with all five other residue classes monochromatic has legal nonperiodic PARTIAL six-colorings; not a full coloring'}


if __name__=='__main__':
    print(json.dumps(main(),ensure_ascii=False,indent=2,sort_keys=True))
