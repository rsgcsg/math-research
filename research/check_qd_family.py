#!/usr/bin/env python3
"""Exact standard-library checker for an all-d rational planar Q_d family.

This is a calibration of the constructive extension of the restored Q6
example, not a proof by enumeration for arbitrary d.  The arbitrary-d result
is the finite-exclusion induction recorded in qd_geometric_partial_isometry.md.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb
import argparse
from pathlib import Path
import hashlib
import json


ZERO = (F(0), F(0))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def norm2(p):
    return p[0] * p[0] + p[1] * p[1]


def direction(t):
    require(type(t) is int and t > 0 and t % 2 == 0, "parameter must be positive even")
    den = t * t + 1
    return (F(t * t - 1, den), F(2 * t, den))


def rho(q):
    """Reduction Z_(2) -> F_2; reject rationals with an even denominator."""
    require(isinstance(q, F), "rho expects an exact Fraction")
    require(q.denominator % 2 == 1, "even denominator is outside Z_(2)")
    return q.numerator % 2


def choose_direction(points, stage):
    differences = {sub(x, y) for x in points for y in points}
    nonzero = {w for w in differences if w != ZERO}
    forbidden_bound = 3 * (3**stage - 1)
    # The proof bounds the number of forbidden even parameters by the number
    # of forbidden circle directions.  Testing the first N+1 candidates must
    # therefore find an admissible one.
    for index in range(forbidden_bound + 1):
        t = 2 * (index + 1)
        v = direction(t)
        collision = v in nonzero
        extra_cross_edge = any(norm2(sub(w, v)) == 1 for w in nonzero)
        if not collision and not extra_cross_edge:
            return t, v, forbidden_bound, index + 1
    raise AssertionError("finite-exclusion bound contradicted by exact scan")


def audit_points(points, d):
    require(len(points) == 2**d, "wrong number of vertices")
    require(len(set(points)) == len(points), "collision in point set")
    for p in points:
        require(all(coord.denominator % 2 == 1 for coord in p),
                "even coordinate denominator")
    extra_edges, missing_edges = [], []
    for i, j in combinations(range(len(points)), 2):
        actual = norm2(sub(points[i], points[j])) == 1
        expected = ((i ^ j).bit_count() == 1)
        if actual and not expected:
            extra_edges.append((i, j))
        elif expected and not actual:
            missing_edges.append((i, j))
    if extra_edges:
        raise ValueError(f"unexpected non-cube unit edge(s): {extra_edges[:4]}")
    if missing_edges:
        raise ValueError(f"missing cube unit edge(s): {missing_edges[:4]}")
    return len(points) * d // 2


def verify_dimension(d):
    points = [ZERO]
    params, bounds, scanned = [], [], []
    for stage in range(d):
        t, v, bound, nscanned = choose_direction(points, stage)
        old = points
        points = old + [add(p, v) for p in old]
        params.append(t)
        bounds.append(bound)
        scanned.append(nscanned)

    edges = audit_points(points, d)
    # The parity color is the subset-size parity, and is also rho(x+y).
    colors = []
    for i, p in enumerate(points):
        color = rho(p[0] + p[1])
        require(color == (i.bit_count() % 2), "cube color / coordinate parity mismatch")
        colors.append(color)
    for i, j in combinations(range(len(points)), 2):
        delta = sub(points[i], points[j])
        require(rho(norm2(delta)) == (colors[i] ^ colors[j]),
                "distance-parity identity failed")
    return dict(d=d, vertices=len(points), parameters=params,
                odd_denominator_coordinates=True, pair_checks=comb(len(points), 2),
                induced_edges=edges, expected_edges=d * 2**(d - 1),
                distance_parity_checks=comb(len(points), 2),
                finite_exclusion_bounds=bounds, scanned_even_parameters=scanned,
                abstract_graph_partial_isomorphism_k_bound=(
                    None if d < 2 else str(F(2**d * (d - 1), 2**d - 2))),
                integer_k_lower_bound=(None if d < 2 else d))


def expect_rejected(label, thunk, phrase):
    try:
        thunk()
    except (ValueError, AssertionError) as exc:
        require(phrase in str(exc), f"{label}: wrong rejection: {exc}")
        return str(exc)
    raise AssertionError(f"mutation accepted: {label}")


def mutation_checks():
    points = [ZERO]
    for stage in range(2):
        _, v, _, _ = choose_direction(points, stage)
        points = points + [add(p, v) for p in points]
    assert len(points) == 4

    collision = points.copy()
    collision[3] = collision[0]
    collision_rejection = expect_rejected(
        "duplicate-coordinate mutation", lambda: audit_points(collision, 2), "collision")

    # Keep coordinates distinct but force the non-cube pair (00, 11) to be a
    # unit pair.  The checker must flag it as an extra edge before considering
    # the other altered incidences.
    extra_edge = points.copy()
    extra_edge[3] = (F(1), F(0))
    extra_rejection = expect_rejected(
        "accidental non-cube unit-edge mutation",
        lambda: audit_points(extra_edge, 2), "unexpected non-cube unit edge")
    require(len(set(extra_edge)) == 4, "edge mutation unexpectedly collided")
    require(norm2(sub(extra_edge[0], extra_edge[3])) == 1,
            "edge mutation did not create its target unit edge")
    require(((0 ^ 3).bit_count() != 1), "target pair is a cube edge")

    even_denominator_rejection = expect_rejected(
        "even-denominator parity mutation", lambda: rho(F(1, 2)), "even denominator")
    parity_point = points.copy()
    parity_point[3] = (parity_point[3][0] + F(1, 2), parity_point[3][1])
    point_denominator_rejection = expect_rejected(
        "even-denominator coordinate mutation",
        lambda: audit_points(parity_point, 2), "even coordinate denominator")
    return dict(status="PASS", rejected_mutations=4,
                collision=collision_rejection, accidental_extra_edge=extra_rejection,
                direct_even_denominator=even_denominator_rejection,
                point_even_denominator=point_denominator_rejection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-certificate", type=Path,
        help="also require the generated report to equal this saved JSON certificate")
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError("verification requires assertions")
    reports = [verify_dimension(d) for d in range(1, 9)]
    require([r["parameters"] for r in reports] == [
        [2], [2, 4], [2, 4, 6], [2, 4, 6, 8],
        [2, 4, 6, 8, 10], [2, 4, 6, 8, 10, 12],
        [2, 4, 6, 8, 10, 12, 14], [2, 4, 6, 8, 10, 12, 14, 16]],
        "unexpected deterministic greedy parameter sequence")
    mutations = mutation_checks()
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report = dict(schema="qd-geometric-partial-isometry-check-v1",
                  status="PASS", dimensions=reports, mutation_tests=mutations,
                  checker_sha256=source_hash,
                  scope="Exact finite calibration for d=1..8; arbitrary d follows the finite-exclusion proof, not enumeration. Geometric invariant 2-law versus abstract graph-partial-isomorphism k-bound; no ordinary HN chromatic lower bound.")
    if args.check_certificate:
        saved = json.loads(args.check_certificate.read_text(encoding="utf-8"))
        require(saved == report, "saved certificate does not match fresh checker output")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
