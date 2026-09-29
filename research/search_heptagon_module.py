#!/usr/bin/env python3
"""Exact F_2-linear obstruction search for Haugland's 21-point heptagon.

The algebra is F = Q(z,w), Phi_7(z)=0, w^2+w+1=0, in basis z^i w^b
(0<=i<6, 0<=b<2).  No third-party packages are used.
"""

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "certificates" / "heptagon_module.json"
N = 12
ZERO = (Fraction(0),) * N
ONE = (Fraction(1),) + (Fraction(0),) * 11


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def neg(a):
    return tuple(-x for x in a)


def sub(a, b):
    return add(a, neg(b))


def scale(c, a):
    return tuple(c * x for x in a)


def basis(i, b=0):
    out = [Fraction(0)] * N
    out[b * 6 + i] = Fraction(1)
    return tuple(out)


def mul(a, b):
    # First multiply as a polynomial, then reduce w^2=-w-1 and Phi_7(z)=0.
    raw = [[Fraction(0) for _ in range(11)] for _ in range(3)]
    for ba in range(2):
        for ia in range(6):
            x = a[ba * 6 + ia]
            if not x:
                continue
            for bb in range(2):
                for ib in range(6):
                    y = b[bb * 6 + ib]
                    if y:
                        raw[ba + bb][ia + ib] += x * y
    # Reduce w powers; w^2=-w-1, w^3=1.
    for degree in range(2, 3):
        for iz in range(11):
            c = raw[degree][iz]
            raw[degree][iz] = 0
            raw[degree - 1][iz] -= c
            raw[degree - 2][iz] -= c
    # First reduce z^k for k>=7 via z^7=1, then use z^6=-1-z-...-z^5.
    for iw in range(2):
        for iz in range(10, 6, -1):
            c = raw[iw][iz]
            raw[iw][iz] = 0
            raw[iw][iz - 7] += c
        c = raw[iw][6]
        raw[iw][6] = 0
        for j in range(6):
            raw[iw][j] -= c
    return tuple(raw[b][i] for b in range(2) for i in range(6))


def inv(a):
    # Solve multiplication-by-a times x = 1 over Q.
    cols = [mul(a, basis(j % 6, j // 6)) for j in range(N)]
    mat = [[cols[j][i] for j in range(N)] + [ONE[i]] for i in range(N)]
    for col in range(N):
        pivot = next((r for r in range(col, N) if mat[r][col]), None)
        if pivot is None:
            raise ZeroDivisionError("singular field element")
        mat[col], mat[pivot] = mat[pivot], mat[col]
        p = mat[col][col]
        mat[col] = [x / p for x in mat[col]]
        for row in range(N):
            if row != col and mat[row][col]:
                c = mat[row][col]
                mat[row] = [x - c * y for x, y in zip(mat[row], mat[col])]
    return tuple(mat[i][-1] for i in range(N))


def conjugate(a):
    # Complex conjugation sends z->z^-1, w->w^-1.  Powers reduce modulo 7/3.
    out = ZERO
    for b in range(2):
        for i in range(6):
            c = a[b * 6 + i]
            if c:
                out = add(out, scale(c, mul(zpow(-i), wpow(-b))))
    return out


def zpow(k):
    if k % 7 == 6:
        # z^6=-sum_{0..5}z^i
        return tuple(Fraction(-1) if i < 6 else Fraction(0) for i in range(6)) + (Fraction(0),) * 6
    return basis(k % 7) if k % 7 < 6 else neg(sum_elements(basis(i) for i in range(6)))


def wpow(k):
    k %= 3
    if k == 0:
        return ONE
    if k == 1:
        return basis(0, 1)
    return neg(add(ONE, basis(0, 1)))


def sum_elements(items):
    out = ZERO
    for a in items:
        out = add(out, a)
    return out


Z = zpow(1)
W = wpow(1)
W2 = wpow(2)


def point(family, j):
    zj = zpow(j)
    if family == "P":
        return mul(zj, inv(sub(zpow(4), zpow(-4))))
    if family == "Q":
        return mul(mul(W, zj), inv(sub(Z, zpow(-1))))
    if family == "R":
        return mul(mul(W2, zj), inv(sub(zpow(2), zpow(-2))))
    raise ValueError(family)


def parity(a):
    bits = 0
    for i, q in enumerate(a):
        if q.denominator % 2 == 0:
            raise ArithmeticError("coefficient has even denominator; reduction mod 2 undefined")
        if q.numerator % 2:
            bits |= 1 << i
    return bits


def dot(mask, vector):
    return bin(mask & vector).count("1") & 1


def gf2_solve(rows):
    """Solve rows x = 1; return one solution, nullity, or None."""
    if 0 in rows:
        return None
    pivots = []
    data = [[m, 1] for m in rows if m]
    rank = 0
    for col in range(N):
        pivot = next((r for r in range(rank, len(data)) if (data[r][0] >> col) & 1), None)
        if pivot is None:
            continue
        data[rank], data[pivot] = data[pivot], data[rank]
        for r in range(len(data)):
            if r != rank and ((data[r][0] >> col) & 1):
                data[r][0] ^= data[rank][0]
                data[r][1] ^= data[rank][1]
        pivots.append(col)
        rank += 1
    if any(m == 0 and rhs for m, rhs in data):
        return None
    sol = 0
    for row, col in enumerate(pivots):
        if data[row][1]:
            sol |= 1 << col
    return sol, N - rank


def rational_json(a):
    return [[x.numerator, x.denominator] for x in a]


def main():
    pts = {(f, j): point(f, j) for f in "PQR" for j in range(7)}
    r = sub(pts[("Q", 0)], pts[("R", 0)])
    assert mul(r, conjugate(r)) == ONE
    mu = []
    # z^5 w^2 is a primitive 21st root; its powers and negatives are mu_42.
    zeta21 = mul(zpow(5), wpow(2))
    p = ONE
    for _ in range(21):
        mu.extend((p, neg(p)))
        p = mul(p, zeta21)
    assert len(set(mu)) == 42
    expected = set(mu) | {mul(r, x) for x in mu}
    assert len(expected) == 84

    unit_pairs, nonunit_pairs, arc_dirs = [], [], []
    for (a, b) in combinations(pts, 2):
        d = sub(pts[b], pts[a])
        norm = mul(d, conjugate(d))
        if norm == ONE:
            unit_pairs.append((a, b))
            arc_dirs.extend((d, neg(d)))
        else:
            nonunit_pairs.append((a, b, rational_json(norm)))
    assert len(unit_pairs) == 42, len(unit_pairs)
    assert len(arc_dirs) == 84 and len(set(arc_dirs)) == 84
    assert set(arc_dirs) == expected
    stage_results = []
    direction_sets = []
    exact_direction_union = set()
    power = ONE
    for m in range(8):
        if m:
            power = mul(power, r)
        dirs = set()
        p = ONE
        for _ in range(21):
            dirs.add(mul(power, p))
            dirs.add(neg(mul(power, p)))
            p = mul(p, zeta21)
        assert len(dirs) == 42
        assert all(mul(d, conjugate(d)) == ONE for d in dirs)
        exact_direction_union.update(dirs)
        vectors = sorted({parity(d) for d in dirs})
        if any(vectors == old for old in direction_sets):
            stage_results.append({"m": m, "direction_count": len(exact_direction_union),
                                  "reduced_direction_count": len(set().union(*[set(x) for x in direction_sets])),
                                  "mod2_direction_set_repeats": True,
                                  "first_functionals_examined": 0,
                                  "successful_first_functional_count": None})
            break
        direction_sets.append(vectors)
        union = sorted(set().union(*(set(x) for x in direction_sets)))
        valid = []
        for first in range(1 << N):
            constraints = [v for v in union if dot(first, v) == 0]
            solved = gf2_solve(constraints)
            if solved is not None:
                second, nullity = solved
                valid.append({"first_mask": first, "second_mask": second,
                              "second_solution_nullity": nullity,
                              "second_solution_count": 1 << nullity})
        stage_results.append({"m": m, "direction_count": len(exact_direction_union),
                              "reduced_direction_count": len(union),
                              "first_functionals_examined": 1 << N,
                              "successful_first_functional_count": len(valid),
                              "successful_first_functionals_and_representative_second": valid,
                              "linear_map_exists": bool(valid)})
        if not valid:
            break

    result = {
        "status": "exact finite linear-map search; not a coloring or HN claim",
        "source": {
            "title": "A Moser-spindle-free 5-chromatic unit distance graph on 2131 vertices in the plane",
            "author": "Jan Kristian Haugland",
            "version": "arXiv:2608.04542v4, 2026-08-17",
            "url": "https://arxiv.org/html/2608.04542v4",
            "used_sections": "Section 2 defines P_j,Q_j,R_j and the induced 21-point graph; Section 4 Table 2 motivates the lattice-coloring question.",
            "scope_note": "The source itself says the finite-ball observations do not prove extension to all of L."
        },
        "field": {
            "definition": "Q(z,w), Phi_7(z)=0, w^2+w+1=0",
            "basis_order": [f"z^{i}w^{b}" for b in range(2) for i in range(6)],
            "reduction": "coordinatewise rational reduction modulo 2; all observed denominators are odd",
            "rational_r": rational_json(r)
        },
        "geometry_check": {
            "vertices": 21,
            "unordered_unit_pairs": len(unit_pairs),
            "directed_arcs": len(arc_dirs),
            "directed_arcs_distinct": len(set(arc_dirs)),
            "all_directed_arcs_have_exact_norm_one": all(mul(d, conjugate(d)) == ONE for d in arc_dirs),
            "arc_set_equal_to_mu42_union_r_mu42": True,
            "nonunit_pair_count": len(nonunit_pairs),
            "nonunit_pair_norms": [{"pair": [list(a), list(b)], "norm": n} for a, b, n in nonunit_pairs]
        },
        "directions": [
            {"field_coordinates": rational_json(d),
             "exact_norm": rational_json(mul(d, conjugate(d))),
             "mod2_mask": parity(d)}
            for d in sorted(expected)
        ],
        "search": {
            "stages": stage_results,
            "interpretation": "At stage m, a listed pair (a,b) means x -> (a dot x,b dot x) is nonzero on every reduced direction in the union of r^j mu_42 for 0<=j<=m. No failure implies anything about arbitrary 4-colorings or chi(R^2)."
        }
    }
    CERT.parent.mkdir(parents=True, exist_ok=True)
    CERT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"certificate": str(CERT), "valid_first_functional_count": len(valid),
                      "unit_pairs": len(unit_pairs), "directions": len(expected),
                      "stages": [{k: v for k, v in s.items() if k not in {"successful_first_functionals_and_representative_second"}} for s in stage_results]}, indent=2))


if __name__ == "__main__":
    main()
