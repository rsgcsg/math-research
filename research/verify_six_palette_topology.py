#!/usr/bin/env python3
"""Finite exact checks for the six-palette/topology research note.

Scope: integer simplicial chain complex, 6-cycle patterns and rational
trigonometric envelopes. Does NOT prove the global weak-k palette lemma.
"""
from fractions import Fraction as F
from itertools import combinations, product
import json


def require(flag, why):
    if not flag:
        raise ValueError(why)


def gf2_rank(columns):
    pivots = {}
    for col in columns:
        v = col
        while v:
            j = v.bit_length() - 1
            if j not in pivots:
                pivots[j] = v
                break
            v ^= pivots[j]
    return len(pivots)


def verify_topology():
    edges = list(combinations(range(6), 2))
    triangles = list(combinations(range(6), 3))
    eindex = {e: j for j, e in enumerate(edges)}
    tindex = {t: j for j, t in enumerate(triangles)}
    d2 = []
    for a, b, c in triangles:
        d2.append((1 << eindex[a, b]) | (1 << eindex[a, c]) | (1 << eindex[b, c]))
    rank = gf2_rank(d2)
    require(rank == 10, "boundary rank should be ten over F2")
    boundaries = []
    for a, b, c in combinations(range(1, 6), 3):
        cycle = {tindex[a, b, c]: 1, tindex[0, b, c]: -1,
                 tindex[0, a, c]: 1, tindex[0, a, b]: -1}
        edge_boundary = [0] * len(edges)
        for ti, coef in cycle.items():
            i, j, k = triangles[ti]
            edge_boundary[eindex[j, k]] += coef
            edge_boundary[eindex[i, k]] -= coef
            edge_boundary[eindex[i, j]] += coef
        require(all(x == 0 for x in edge_boundary), "tetrahedral boundary not a cycle")
        boundaries.append(sum(1 << t for t in cycle))
    require(gf2_rank(boundaries) == 10, "tetrahedral cycles not independent")
    return {"vertices": 6, "edges": len(edges), "triangles": len(triangles),
            "rank_d2_mod2": rank, "tetrahedron_cycles_rank_mod2": 10,
            "betti_1_over_Q": 0, "betti_2_over_Q": 10,
            "old_five_color_graph_cycle_rank": 6}


def verify_annulus():
    # 31/10 < pi < 63/20; hence 31/45 < 2pi/9 < 7/10.
    theta_min, theta_max = F(31,45), F(7,10)
    sin40_lower = theta_min - theta_max**3 / 6
    require(sin40_lower > F(63,100), "sin(40 degrees) lower bound")
    cos40_lower = 1 - theta_max**2/2
    require(cos40_lower == F(151,200), "cos(40 degrees) lower bound")
    a, b = F(4,5), F(7,5)
    same_outer = 2*b*(theta_max/2)  # sin(pi/9) < pi/9 < 7/20
    mixed_sq_upper = a*a + b*b - 2*a*b*cos40_lower
    require(same_outer == F(49,50), "same outer radius bound")
    require(mixed_sq_upper == F(568,625), "mixed radius bound")
    require(mixed_sq_upper < same_outer**2 and b-a < same_outer,
            "one sector strict separation")
    cross_lower = 2*a*F(63,100)
    require(cross_lower == F(126,125) and cross_lower > 1,
            "different same-color sectors separation")
    return {"radii": [str(a), str(b)], "sectors": 9, "colors": 3,
            "same_sector_distance_lt": str(same_outer),
            "different_same_color_sectors_distance_gt": str(cross_lower),
            "mixed_radius_sq_lt": str(mixed_sq_upper),
            "sin_40_degrees_gt": str(sin40_lower)}


def verify_circle_words():
    proper = [w for w in product(range(3), repeat=6)
              if all(w[i] != w[(i+1)%6] for i in range(6))]
    bicol = sum(len(set(w))==2 for w in proper)
    tricol = sum(len(set(w))==3 for w in proper)
    require((len(proper), bicol, tricol)==(66,6,60), "circle C6 counts")
    require((0,1,2,0,1,2) in proper, "explicit three-color word")
    return {"proper_words":66,"two_color_words":6,"three_color_words":60,
            "example":[0,1,2,0,1,2]}



def verify_seven_skeleton():
    edges = list(combinations(range(7), 2))
    triangles = list(combinations(range(7), 3))
    tetrahedra = list(combinations(range(7), 4))
    eindex = {e: j for j, e in enumerate(edges)}
    tindex = {t: j for j, t in enumerate(triangles)}
    d2 = [sum(1 << eindex[e] for e in combinations(t, 2)) for t in triangles]
    d3 = [sum(1 << tindex[t] for t in combinations(T, 3)) for T in tetrahedra]
    require(gf2_rank(d2) == 15, "seven-label rank d2 should be 15")
    require(gf2_rank(d3) == 20, "seven-label rank d3 should be 20")
    for tetra in d3:
        edge_boundary = 0
        for j, face in enumerate(d2):
            if tetra & (1 << j):
                edge_boundary ^= face
        require(edge_boundary == 0, "boundary d2*d3 is nonzero")
    return {"vertices":7,"edges":21,"triangles":35,"tetrahedra":35,
            "rank_d2_mod2":15,"rank_d3_mod2":20,
            "betti_1_over_Q":0,"betti_2_over_Q":0,"betti_3_over_Q":15}

def main():
    print(json.dumps({"claim":"six palette topology finite calibration",
                      "scope":"not a proof of plane chi=7 or of weak measurable transfer",
                      "annulus": verify_annulus(), "circle": verify_circle_words(),
                      "simplex": verify_topology(), "seven_color_three_skeleton": verify_seven_skeleton(), "result":"PASS"}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
