"""E043: free five-color search on actual zeta_5-rotated Parts copies.

Search-side exact algebra uses F=Q(i,sqrt(3),sqrt(11),sqrt(5)), and eta
satisfies eta^2=((sqrt(5)-1)/2)*eta-1. This is not a periodic quotient.
The independent verifier does not import this module or a SAT solver.
"""
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
import math

RAD = (1, 3, 11, 33, 5, 15, 55, 165)


def digest(data):
    return hashlib.sha256(json.dumps(data, separators=(',', ':')).encode()).hexdigest()


def mul(a, b):
    result = [0]*16
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    result[i ^ j] += x*y*RAD[(i & j) % 8]*(-1 if i & j & 8 else 1)
    return result


def bar(a):
    return [x if i < 8 else -x for i, x in enumerate(a)]


def t2mul(a):
    result = [-x for x in a]
    for i, x in enumerate(a):
        result[i ^ 4] += x*(5 if i & 4 else 1)
    return result


def unit(delta, den):
    u, v = delta[:16], delta[16:]
    uu, vv, uv, vu = mul(u, bar(u)), mul(v, bar(v)), mul(u, bar(v)), mul(v, bar(u))
    if uv != vu:
        return False
    return [2*x+2*y+z for x, y, z in zip(uu, vv, t2mul(uv))] == [2*den*den]+[0]*15


def modular_filter():
    for prime in range(1009, 100000):
        if prime % 20 != 1 or any(prime % d == 0 for d in range(2, math.isqrt(prime)+1)):
            continue
        roots = {x*x % prime: x for x in range(prime)}
        if not all(r in roots for r in (3, 5, 11, prime-1)):
            continue
        t = (roots[5]-1)*pow(2, -1, prime) % prime
        eta = next((x for x in range(prime) if (x*x-t*x+1) % prime == 0), None)
        if eta is not None:
            break
    else:
        raise ValueError('No split filter prime found')
    f = []
    for i in range(16):
        z = roots[prime-1] if i & 8 else 1
        for bit, r in ((1, 3), (2, 11), (4, 5)):
            if i & bit:
                z = z*roots[r] % prime
        f.append(z)
    assert pow(eta, 5, prime) == 1 and eta != 1
    assert all(f[i]*f[j] % prime == RAD[(i & j) % 8]*(-1 if i & j & 8 else 1)*f[i ^ j] % prime
               for i, j in combinations(range(16), 2))
    return prime, f+[eta*x % prime for x in f]


def geometry(core, centers):
    den = core['coordinate_denominator']
    base = [tuple(x+y) for x, y in core['points']]
    occurrences = [[p+(0,)*16 for p in base]]
    for a in centers:
        center = base[a]
        occurrences.append([center+tuple(x-y for x, y in zip(p, center)) for p in base])
    points = sorted(set(p for copy in occurrences for p in copy))
    index = {p: i for i, p in enumerate(points)}
    copies = [[index[p] for p in copy] for copy in occurrences]
    prime, images = modular_filter()
    # Conjugate the F coefficient and replace eta by t-eta before evaluation.
    f = images[:16]
    eta = images[16]
    t = (f[4]-1)*pow(2, -1, prime) % prime
    conjugate_images = [(-x if i & 8 else x) % prime for i, x in enumerate(f)]
    conjugate_images += [(t-eta)*x % prime for x in conjugate_images]
    projected = [(sum(a*b for a, b in zip(p, images)) % prime,
                  sum(a*b for a, b in zip(p, conjugate_images)) % prime) for p in points]
    edges, candidates = [], 0
    for i, j in combinations(range(len(points)), 2):
        x, xb = projected[i]
        y, yb = projected[j]
        if ((x-y)*(xb-yb)-den*den) % prime:
            continue
        candidates += 1
        if unit(tuple(a-b for a, b in zip(points[i], points[j])), den):
            edges.append((i, j))
    original = set()
    for copy in copies:
        original.update(tuple(sorted((copy[i], copy[j]))) for i, j in core['induced_edges'])
    assert original <= set(edges)
    summary = dict(vertices=len(points), actual_pairs=len(points)*(len(points)-1)//2,
                   induced_edges=len(edges), copy_edges=len(original),
                   new_cross_edges=len(set(edges)-original),
                   point_sha256=digest(points), edge_sha256=digest(edges),
                   search_filter_prime=prime, search_filter_survivors=candidates)
    return points, copies, edges, summary


def solve(points, copies, edges, budget):
    from pysat.solvers import Solver
    k = 5
    clauses = [[k*v+c+1 for c in range(k)] for v in range(len(points))]
    clauses += [[-k*v-a-1, -k*v-b-1] for v in range(len(points)) for a, b in combinations(range(k), 2)]
    clauses += [[-k*a-c-1, -k*b-c-1] for a, b in edges for c in range(k)]
    # Only global color symmetry, not a fixed Parts coloring.
    triangle = [copies[0][i] for i in (0, 153, 150)]
    assert all(tuple(sorted(pair)) in set(edges) for pair in combinations(triangle, 2))
    clauses += [[k*v+c+1] for c, v in enumerate(triangle)]
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        record = dict(status='SAT' if answer else 'UNSAT_SEARCH_ONLY' if answer is False else 'UNKNOWN',
                      solver='cadical195', conflict_budget=budget, statistics=solver.accum_stats(),
                      variables=k*len(points), clauses=len(clauses),
                      symmetry_triangle_core_indices=[0, 153, 150])
        if answer:
            positive = set(solver.get_model())
            coloring = [next(c for c in range(k) if k*v+c+1 in positive) for v in range(len(points))]
            assert all(coloring[a] != coloring[b] for a, b in edges)
            record['five_coloring'] = ''.join(map(str, coloring))
    return record


def mechanisms(points, copies, edges, core):
    """A positive construction diagnostic, independent of the free SAT word."""
    owners = [{} for _ in points]
    for j, copy in enumerate(copies):
        for i, p in enumerate(copy):
            owners[p][j] = i
    word = core['five_coloring']
    constraints = {ij: [set(), set()] for ij in combinations(range(len(copies)), 2)}
    for owner in owners:
        for i, j in combinations(owner, 2):
            constraints[i, j][0].add((word[owner[i]], word[owner[j]]))
    for a, b in edges:
        for i, pi in owners[a].items():
            for j, pj in owners[b].items():
                if i < j:
                    constraints[i, j][1].add((word[pi], word[pj]))
                elif j < i:
                    constraints[j, i][1].add((word[pj], word[pi]))

    def compatible(i, p, j, q):
        equal, different = constraints[i, j]
        return all(p[a] == q[b] for a, b in equal) and all(p[a] != q[b] for a, b in different)

    perms = list(permutations(range(5)))
    domains = [[perms[0]]]+[[p for p in perms if compatible(0, perms[0], j, p)]
                          for j in range(1, len(copies))]

    def visit(frames):
        j = len(frames)
        if j == len(copies):
            return frames
        for p in domains[j]:
            if all(compatible(i, q, j, p) for i, q in enumerate(frames)):
                result = visit(frames+[p])
                if result is not None:
                    return result
        return None

    frames = visit([])
    record = dict(frame_status='SAT' if frames is not None else 'NO_FRAME_FOUND_SEARCH_ONLY',
                  frame_domain_sizes=[len(d) for d in domains])
    if frames is not None:
        record['reference_color_frames'] = frames
    core_edges = set(map(tuple, core['induced_edges']))
    well_defined = all(len(set(owner.values())) == 1 for owner in owners)
    if well_defined:
        projection = [next(iter(owner.values())) for owner in owners]
        if all(tuple(sorted((projection[a], projection[b]))) in core_edges for a, b in edges):
            record['unit_graph_projection'] = 'Every occurrence maps to its original Parts vertex index'
            cross_counts = {}
            for a, b in edges:
                if owners[a].keys() & owners[b].keys():
                    continue
                for i in owners[a]:
                    for j in owners[b]:
                        key = ','.join(map(str, sorted((i, j))))
                        cross_counts[key] = cross_counts.get(key, 0)+1
            record['new_cross_edges_by_copy_pair'] = cross_counts
    return record


def run(root, budget, center_count):
    raw = (root/'certificates/parts509_core.json').read_bytes()
    core = json.loads(raw)
    assert core['coordinate_denominator'] == 96
    zero = [0]*8
    expected = ((0, [zero, zero]), (153, [[96]+[0]*7, zero]),
                (150, [[48]+[0]*7, [0, 48]+[0]*6]))
    assert all(core['points'][i] == p for i, p in expected)
    centers = [i for i, _ in expected][:center_count]
    points, copies, edges, summary = geometry(core, centers)
    print(json.dumps(dict(stage='geometry', centers=centers, **summary)), flush=True)
    search = solve(points, copies, edges, budget)
    print(json.dumps({k: v for k, v in search.items() if k != 'five_coloring'}), flush=True)
    mechanism = mechanisms(points, copies, edges, core)
    print(json.dumps(dict(stage='mechanism', **mechanism)), flush=True)
    return dict(schema=1, experiment='E043',
                host='P union (eta*(P-a)+a) for a in the listed centers; eta=exp(2*pi*i/5)',
                field='Q(i,sqrt(3),sqrt(11),sqrt(5))[eta], eta^2=((sqrt(5)-1)/2)*eta-1',
                base_radicals=list(RAD), coordinate_denominator=96,
                centers=centers, core_sha256=hashlib.sha256(raw).hexdigest(),
                geometry=summary, search=search, mechanism=mechanism,
                scope='Only this finite induced unit graph; not a field or plane coloring. Negative solver returns are not certificates.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--budget', type=int, default=100000)
    parser.add_argument('--centers', type=int, choices=(1, 2, 3), default=3)
    parser.add_argument('--output', type=Path, default=Path('certificates/quintic_core_probe.json'))
    args = parser.parse_args()
    if args.budget <= 0:
        parser.error('--budget must be positive')
    data = run(Path(__file__).resolve().parents[1], args.budget, args.centers)
    args.output.write_text(json.dumps(data, indent=2)+'\n')
