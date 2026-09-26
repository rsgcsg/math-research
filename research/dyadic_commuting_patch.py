"""Bounded actual eta/u commuting-square search; never a joint certificate.

The first query uses only transported Y edges after exact physical vertex
identification. The second, if reached, adds ALL actual unit pairs. A positive
first stage must not be described as a coloring of the induced point set.
No saved color, support permutation or finite-group action is frozen.
"""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import math

from verify_quintic_tau_union import verify as source_geometry
from verify_quintic_core_probe import (
    conjugate_twice, digest, filter_map, product_twice,
)
from verify_dyadic_mixed_return_joint import _new_definitions


def build_patch(root):
    report, context = source_geometry(root, geometry_context=True)
    table = context['ring']['table']
    source_den = math.lcm(*(x.denominator for p in context['points'] for x in p))
    base = [tuple(int(x * source_den) for x in p) for p in context['points']]
    one = (Q(1),) + (Q(0),) * 31
    eta = (Q(0),) * 16 + one[:16]
    u = _new_definitions(context)[0][1]
    mul = context['ring']['mul']
    assert mul(eta, u) == mul(u, eta)
    rotations = [one, eta, u, mul(eta, u)]
    ds = [math.lcm(*(x.denominator for x in r)) for r in rotations]
    denominator = 2 * source_den * math.lcm(*ds)
    raw_copies = []
    for rotation, den in zip(rotations, ds):
        coeff = [int(x * den) for x in rotation]
        scale = denominator // (2 * source_den * den)
        raw_copies.append([tuple(scale * x for x in product_twice(coeff, p, table))
                           for p in base])
    points = sorted(set(p for copy in raw_copies for p in copy))
    lookup = {p: i for i, p in enumerate(points)}
    copies = [[lookup[p] for p in copy] for copy in raw_copies]
    listed = sorted({tuple(sorted((copy[i], copy[j])))
                     for copy in copies for i, j in context['edges']})
    votes = [Counter() for p in points]
    for copy in copies:
        for i, v in enumerate(copy):
            votes[v][int(context['word'][i])] += 1
    phases = ''.join(str(max(vote, key=lambda c: (vote[c], -c))) for vote in votes)
    metadata = dict(
        vertices=len(points), denominator=denominator,
        actual_pairs=len(points) * (len(points) - 1) // 2,
        point_sha256=digest(points), copies_sha256=digest(copies),
        copy_labels=['Y', 'eta_Y', 'u_Y', 'eta_u_Y'],
        listed_edges=len(listed), listed_edge_sha256=digest(listed),
        pairwise_copy_intersections=[
            [a, b, len(set(copies[a]) & set(copies[b]))]
            for a, b in combinations(range(4), 2)],
    )
    return report, points, copies, listed, table, metadata, phases


def actual_edges(points, denominator, table):
    # Exact ring homomorphism: every true unit pair must survive this bucket
    # lookup. Verify products in filter_map before excluding any pair.
    prime, images, bars = filter_map(table)
    assert denominator % prime
    residues = [(sum(x * y for x, y in zip(p, images)) % prime,
                 sum(x * y for x, y in zip(p, bars)) % prime) for p in points]
    buckets = defaultdict(list)
    for i, pair in enumerate(residues):
        buckets[pair].append(i)
    displacements = [(d, denominator * denominator * pow(d, -1, prime) % prime)
                     for d in range(1, prime)]
    target = [4 * denominator * denominator] + [0] * 31
    memo, edges = {}, []
    candidates = 0
    for i, (a, b) in enumerate(residues):
        for dx, dy in displacements:
            for j in buckets.get(((a + dx) % prime, (b + dy) % prime), ()):
                if j <= i:
                    continue
                candidates += 1
                delta = tuple(x - y for x, y in zip(points[i], points[j]))
                good = memo.get(delta)
                if good is None:
                    good = product_twice(delta, conjugate_twice(delta), table) == target
                    memo[delta] = good
                if good:
                    edges.append((i, j))
        if i % 5000 == 0:
            print(json.dumps(dict(progress='actual_unit_pairs', vertex=i,
                                  total=len(points), edges=len(edges))), flush=True)
    edges.sort()
    assert len(edges) == len(set(edges))
    return edges, dict(filter_prime=prime, modular_candidate_pairs=candidates,
                       distinct_exact_differences=len(memo))


def query(n, edges, phases, budget):
    from pysat.solvers import Solver
    var = lambda v, c: 5 * v + c + 1
    clauses = [[var(v, c) for c in range(5)] for v in range(n)]
    clauses.extend([-var(v, a), -var(v, b)]
                   for v in range(n) for a, b in combinations(range(5), 2))
    clauses.extend([-var(a, c), -var(b, c)] for a, b in edges for c in range(5))
    # Only a global palette gauge; phase hints impose no constraints.
    a, b = edges[0]
    clauses.extend([[var(a, 0)], [var(b, 1)]])
    print(json.dumps(dict(progress='sat_formula', vertices=n, edges=len(edges),
                          clauses=len(clauses), budget=budget)), flush=True)
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        solver.set_phases([var(v, int(c)) for v, c in enumerate(phases)])
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        word = None
        if answer is True:
            positive = {v for v in solver.get_model() if v > 0}
            word = ''.join(str(next(c for c in range(5) if var(v, c) in positive))
                           for v in range(n))
            assert all(word[a] != word[b] for a, b in edges)
        return dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None
                    else 'UNSAT_SEARCH_ONLY_UNCERTIFIED', word=word,
                    conflict_budget=budget, stats=solver.accum_stats())


def run(root, budget):
    source, points, copies, listed, table, metadata, phases = build_patch(root)
    print(json.dumps(dict(progress='patch_built', geometry=metadata)), flush=True)
    first = query(len(points), listed, phases, budget)
    first['name'] = 'transported_edges_with_all_physical_identifications'
    stages = [first]
    print(json.dumps(dict(progress='listed_finished', status=first['status'],
                          stats=first['stats'])), flush=True)
    enumeration = None
    if first['status'] == 'SAT':
        edges, enumeration = actual_edges(points, metadata['denominator'], table)
        assert set(listed) <= set(edges)
        metadata.update(induced_edges=len(edges), edge_sha256=digest(edges),
                        additional_cross_edges=len(edges) - len(listed))
        violations = sum(first['word'][a] == first['word'][b] for a, b in edges)
        first['violations_on_induced_graph'] = violations
        if violations:
            second = query(len(points), edges, first['word'], budget)
        else:
            second = dict(status='SAT_DIRECT_REUSE', word=first['word'],
                          conflict_budget=0, stats=None)
        second['name'] = 'all_actual_unit_pairs'
        stages.append(second)
    return dict(schema=1, experiment='E095',
                source_sha256=hashlib.sha256(
                    (root / 'certificates/quintic_tau_union.json').read_bytes()).hexdigest(),
                source_geometry=source['geometry'], geometry=metadata,
                enumeration=enumeration, stages=stages,
                scope='Exactly the finite physical commuting patch; listed-edge SAT alone '
                      'is not induced-graph SAT. No invariant joint law, whole-host coloring, '
                      'all-support obstruction or HN bound follows from UNKNOWN.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=20000)
    args = parser.parse_args()
    assert 1 <= args.budget <= 20000
    print('COMMUTING_PATCH_JSON=' + json.dumps(
        run(Path(__file__).resolve().parents[1], args.budget), separators=(',', ':')),
        flush=True)
