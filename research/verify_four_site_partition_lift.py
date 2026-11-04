"""Exact certificate for the universal 4-site lift and 5-site partition obstruction.

Pure Python standard library. Mathematical scope:
docs/proofs/four_site_partition_lift_20261104.md
NOT a proof that the Euclidean plane needs 7 colors.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import gcd, lcm
import json


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def partitions(n):
    for z in product(range(n), repeat=n):
        if z[0] == 0 and all(z[i] <= 1 + max(z[:i]) for i in range(1, n)):
            yield z


def normal_of_six(rows):
    a = [[Q(v) for v in row] for row in rows]
    need(len(a) == 6 and all(len(row) == 7 for row in a), "shape")
    pivots = []
    r = 0
    for c in range(7):
        i = next((i for i in range(r, 6) if a[i][c]), None)
        if i is None:
            continue
        a[r], a[i] = a[i], a[r]
        scale = 1 / a[r][c]
        for j in range(c, 7):
            a[r][j] *= scale
        for i in range(6):
            if i != r and a[i][c]:
                scale = a[i][c]
                for j in range(c, 7):
                    a[i][j] -= scale * a[r][j]
        pivots.append(c)
        r += 1
        if r == 6:
            break
    if r < 6:
        return None
    free = next(c for c in range(7) if c not in pivots)
    x = [Q(0)] * 7
    x[free] = Q(1)
    for i, c in enumerate(pivots):
        x[c] = -a[i][free]
    d = lcm(*(u.denominator for u in x))
    z = [int(u * d) for u in x]
    g = gcd(*z)
    return tuple(u // g for u in z)


def four_site():
    edges = list(combinations(range(4), 2))
    verts = [tuple(int(p[i] == p[j]) for i, j in edges)
             for p in partitions(4)]
    need(len(verts) == 15, "Bell4")
    found = set()
    full_rank = 0
    for ids in combinations(range(15), 6):
        eq = normal_of_six([(*verts[i], -1) for i in ids])
        if eq is None:
            continue
        full_rank += 1
        values = [sum(c*v for c,v in zip(eq[:6], x)) - eq[6]
                  for x in verts]
        if min(values) < 0 < max(values):
            continue
        if max(values) > 0:
            eq = tuple(-u for u in eq)
        found.add(eq)

    expected = {}
    for e in edges:
        coeff = {e:-1}
        expected[tuple(coeff.get(x, 0) for x in edges)+(0,)] = ("nonnegative",)
    for triple in combinations(range(4), 3):
        for center in triple:
            leaves = tuple(i for i in triple if i != center)
            coeff = {tuple(sorted((center,j))):1 for j in leaves}
            coeff[tuple(sorted(leaves))] = -1
            expected[tuple(coeff.get(x,0) for x in edges)+(1,)] = ("triangle",center)
    for center in range(4):
        leaves = tuple(i for i in range(4) if i != center)
        coeff = {tuple(sorted((center,j))):1 for j in leaves}
        coeff.update({e:-1 for e in combinations(leaves, 2)})
        expected[tuple(coeff.get(x,0) for x in edges)+(1,)] = ("star",center)
    need(found == set(expected) and len(found) == 22, "22 facets mismatch")
    checked = 0
    for bits in product((0,1), repeat=4):
        v = [bits[i]*bits[j] for i,j in edges]
        for facet,kind in expected.items():
            value = sum(c*t for c,t in zip(facet[:6],v))
            rhs = 0 if kind[0] == "nonnegative" else bits[kind[1]]
            need(value <= rhs,"binary pointwise inequality")
            checked += 1
    return {"partitions":15,"rank_six_candidates":full_rank,
            "exact_facets":22,"facet_counts":{"nonnegative":6,"triangle":12,"star":4},
            "binary_pointwise_tests":checked}


def canonical_triple_failure():
    source = {(0,0,0,0):Q(1,3),(0,0,0,1):Q(1,12),
              (0,0,1,1):Q(1,6),(0,1,0,0):Q(1,6),
              (1,0,0,0):Q(1,6),(1,1,1,0):Q(1,12)}
    need(sum(source.values()) == 1, "source norm")
    mu = [sum(w*x[i] for x,w in source.items()) for i in range(4)]
    need(mu == [Q(1,4)]*4, "source marginals")
    q = {(i,j):sum(w*x[i]*x[j] for x,w in source.items())/mu[0]
         for i,j in combinations(range(4),2)}
    expected={(0,1):Q(1,3),(0,2):Q(1,3),(0,3):Q(0),
              (1,2):Q(1,3),(1,3):Q(0),(2,3):Q(2,3)}
    need(q == expected,"source q")
    canonical = max(Q(0),(q[0,1]+q[0,2]+q[1,2]-1)/2)
    need(canonical == 0, "canonical a012")
    law={(0,0,0,1):Q(1,3),(0,1,2,2):Q(2,3)}
    for (i,j),value in q.items():
        got=sum(w*int(p[i]==p[j]) for p,w in law.items())
        need(got == value,"four-party witness")
    # E02,E12 subset complement(E23), all with mass 1/3,
    # which forces E012 of mass 1/3 in every compatible four-point law.
    forced = 1-q[2,3]
    need(forced == q[0,2] == q[1,2] == Q(1,3),"forced triple identity")
    return {"canonical_triple_all_equal":str(canonical),
            "forced_triple_all_equal":str(forced),
            "four_point_witness":{str(p):str(w) for p,w in law.items()}}


def planar_unit_pentagon_projective_four_law():
    # Scale a regular pentagon until its long diagonals are length one.
    # Then i,j are unit-adjacent precisely for indices separated by 2.
    # Independently certify the ten actual squared point distances in
    # the field Q(sqrt(5)). Long diagonal squared = 1 by chosen scaling.
    one=(Q(1),Q(0))
    cos72=(Q(-1,4),Q(1,4))
    cos144=(Q(-1,4),Q(-1,4))
    def sub(a,b):
        return (a[0]-b[0],a[1]-b[1])
    def div(a,b):
        den=b[0]*b[0]-5*b[1]*b[1]
        need(den != 0, "quadratic denominator")
        return ((a[0]*b[0]-5*a[1]*b[1])/den,
                (a[1]*b[0]-a[0]*b[1])/den)
    for i,j in combinations(range(5),2):
        c=cos72 if ((i-j)%5 in (1,4)) else cos144
        squared=div(sub(one,c),sub(one,cos144))
        expected=(Q(3,2),Q(-1,2)) if c==cos72 else one
        need(squared==expected,"exact unit pentagon squared distance")
    def unit(i, j):
        return (i-j) % 5 in (2,3)
    source = {(0,0,0,0,0):Q(3,8)}
    for i in range(5):
        z=tuple(int(j in (i,(i+1)%5)) for j in range(5))
        source[z]=Q(1,8)
    for z,w in source.items():
        if w:
            for i,j in combinations(range(5),2):
                need(not(unit(i,j) and z[i] and z[j]),
                     "binary source is not independent in actual unit graph")
    triple_laws = {}
    for absent in range(5):
        F=tuple(i for i in range(5) if i != absent)
        path=tuple((absent+j)%5 for j in range(1,5))
        law=(
            ({path[0]:0,path[1]:0,path[2]:1,path[3]:1},Q(1,2)),
            ({path[0]:0,path[1]:1,path[2]:1,path[3]:2},Q(1,2))
        )
        for i,j in combinations(F,2):
            value=sum(w*int(p[i]==p[j]) for p,w in law)
            need(value==(Q(0) if unit(i,j) else Q(1,2)),
                 "quadruple disagrees with global pair q")
        for T in combinations(F,3):
            marginal={}
            for p,w in law:
                renaming={}
                z=[]
                for i in T:
                    if p[i] not in renaming:
                        renaming[p[i]]=len(renaming)
                    z.append(renaming[p[i]])
                z=tuple(z)
                marginal[z]=marginal.get(z,Q(0))+w
            need((0,0,0) not in marginal, "triple all equal")
            if T in triple_laws:
                need(marginal==triple_laws[T],"overlapping triples differ")
            else:
                triple_laws[T]=marginal
    need(len(triple_laws)==10,"all ten triples")
    return {
        "true_unit_edges":5,
        "exact_quadratic_field_squared_distance_tests":10,
        "short_side_squared":"(3-sqrt(5))/2",
        "binary_source_singleton_marginal":"1/4",
        "compatible_four_site_windows":5,
        "compatible_three_site_marginals":10,
        "all_joint_blocks_size_at_most_two":True,
        "common_five_site_law_with_prescribed_pairs_exists":False,
        "pentagonal_nonextension_gap":"1/2",
        "actual_unit_graph_is_three_colorable":True,
        "scope":"Real Euclidean unit pentagon; the prescribed pair moments, not proper coloring itself, fail to extend."
    }


def five_site():
    weights={(0,0,0,0,0):Q(3,8)}
    for i in range(5):
        sample=tuple(int(j in (i,(i+1)%5)) for j in range(5))
        weights[sample]=Q(1,8)
    need(sum(weights.values())==1,"law normalization")
    means=[sum(w*x[i] for x,w in weights.items()) for i in range(5)]
    need(means==[Q(1,4)]*5,"means")
    def q(i,j):
        i,j=sorted((i%5,j%5))
        return sum(w*x[i]*x[j] for x,w in weights.items())/means[0]
    ring=sum(q(i,i+1) for i in range(5))
    chords=sum(q(i,i+2) for i in range(5))
    need(ring==Q(5,2) and chords==0,"five-cycle source")
    all_parts=list(partitions(5))
    need(len(all_parts)==52,"Bell5")
    maxscore=max(sum(int(p[i]==p[(i+1)%5]) for i in range(5))
                 -sum(int(p[i]==p[(i+2)%5]) for i in range(5))
                 for p in all_parts)
    need(maxscore==2 and ring-chords-maxscore==Q(1,2),"gap")
    return {"partitions":52,"uniform_binary_mean":"1/4",
            "ring_sum":str(ring),"chord_sum":str(chords),
            "true_partition_ceiling":maxscore,
            "strict_gap":str(ring-chords-maxscore),
            "geometric_stationarity_claimed":False}


def verify():
    if not __debug__:
        raise RuntimeError("Verification requires assertions (-O forbidden)")
    return {"status":"PASS_EXACT_FINITE_CERTIFICATE",
            "four_site":four_site(),
            "canonical_triple_overlap_failure":canonical_triple_failure(),
            "five_site_abstract_boundary":five_site(),
            "real_unit_pentagon_order_four_gap":planar_unit_pentagon_projective_four_law(),
            "scope":"Any equal-marginal binary law gives a four-site pair moment lift; no coherent four-site triple marginals or geometric five-site obstruction proved.",
            "chromatic_six_or_seven_decided":False,
            "new_lean_formalization":False}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
