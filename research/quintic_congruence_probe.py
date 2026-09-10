"""Search whether the E043/E044 retraction preserves equality of distances.

Modular distance keys only group candidates; disagreements are resolved by
exact field arithmetic. This search is not its independent proof checker.
"""
from itertools import combinations
from pathlib import Path
import argparse
import json
import math
import hashlib
from quintic_core_probe import geometry, mul, bar, t2mul, RAD


def sqrt_mod(a, p):
    assert pow(a, (p-1)//2, p) == 1
    q, s = p-1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = next(z for z in range(2, p) if pow(z, (p-1)//2, p) == p-1)
    c, x, t, m = pow(z, q, p), pow(a, (q+1)//2, p), pow(a, q, p), s
    while t != 1:
        i, y = 1, t*t % p
        while y != 1:
            y = y*y % p
            i += 1
        b = pow(c, 1 << (m-i-1), p)
        x, t, c, m = x*b % p, t*b*b % p, b*b % p, i
    assert x*x % p == a % p
    return x


def embedding(start):
    p = start + (1-start) % 660
    while any(p % d == 0 for d in range(2, math.isqrt(p)+1)):
        p += 660
    eta = next(pow(x, (p-1)//5, p) for x in range(2, p)
               if pow(x, (p-1)//5, p) != 1)
    roots = {3: sqrt_mod(3, p), 11: sqrt_mod(11, p), -1: sqrt_mod(p-1, p)}
    roots[5] = (2*(eta+pow(eta, -1, p))+1) % p
    assert roots[5]**2 % p == 5
    f = []
    for i in range(16):
        x = roots[-1] if i & 8 else 1
        for bit, r in ((1, 3), (2, 11), (4, 5)):
            if i & bit:
                x = x*roots[r] % p
        f.append(x)
    bars = [(-x if i & 8 else x) % p for i, x in enumerate(f)]
    return p, f+[eta*x % p for x in f], bars+[pow(eta, -1, p)*x % p for x in bars]


def norm2(delta):
    u, v = delta[:16], delta[16:]
    uu, vv, uv, vu = mul(u, bar(u)), mul(v, bar(v)), mul(u, bar(v)), mul(v, bar(u))
    return tuple(2*x+2*y+z for x, y, z in zip(uu, vv, t2mul(uv))) + tuple(2*(x-y) for x, y in zip(vu, uv))


def run(root, angles, fiber=False):
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    points, copies, edges, summary = geometry(core, [0, 153, 150], angles)
    owners = {}
    for copy in copies:
        for j, i in enumerate(copy):
            assert i not in owners or owners[i] == j
            owners[i] = j
    base = [x+y for x, y in core['points']]
    lengths = {}
    for i in range(509):
        for j in range(i, 509):
            d = [x-y for x, y in zip(base[i], base[j])]
            lengths[i, j] = tuple(mul(d, bar(d)))
    maps = [embedding(10**6), embedding(2*10**6)]
    residues = [[(sum(x*y for x, y in zip(point, f)) % p,
                  sum(x*y for x, y in zip(point, b)) % p) for point in points]
                for p, f, b in maps]
    def key_of(i, j):
        return tuple((r[i][0]-r[j][0])*(r[i][1]-r[j][1]) % p
                     for (p, f, b), r in zip(maps, residues))
    if fiber:
        parent = list(range(509))
        records = []
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for iteration in range(509):
            collapsed = {}
            for i, j in combinations(range(len(points)), 2):
                if find(owners[i]) == find(owners[j]):
                    collapsed.setdefault(key_of(i, j), []).append((i, j))
            previous = len(records)
            for i, j in combinations(range(len(points)), 2):
                a, b = owners[i], owners[j]
                if find(a) == find(b):
                    continue
                for u, v in collapsed.get(key_of(i, j), ()):
                    if norm2([x-y for x, y in zip(points[i], points[j])]) != norm2([x-y for x, y in zip(points[u], points[v])]):
                        continue
                    parent[find(a)] = find(b)
                    records.append(dict(pair=[i,j], collapsed_pair=[u,v], owners=[a,b], collapsed_owners=[owners[u],owners[v]]))
                    conflict = next(((a,b) for a,b in core['induced_edges'] if find(a) == find(b)), None)
                    if conflict:
                        return dict(status='FIBER_LAWS_IMPOSSIBLE', angles=angles, records=records, conflicting_unit_edge=conflict)
                    break
            print(json.dumps(dict(stage='fiber_closure', iteration=iteration, forced_merges=len(records))), flush=True)
            if previous == len(records):
                break
        return dict(status='NO_FIBER_CONTRADICTION', angles=angles, forced_merges=len(records),
                    collapsed_modular_distances=len(collapsed), records=records)
    buckets = {}
    mismatches = 0
    for i, j in combinations(range(len(points)), 2):
        key = key_of(i, j)
        h = lengths[tuple(sorted((owners[i], owners[j])))]
        if key not in buckets:
            buckets[key] = (i, j, h)
        elif buckets[key][2] != h:
            a, b, old = buckets[key]
            if norm2([x-y for x, y in zip(points[i], points[j])]) == norm2([x-y for x, y in zip(points[a], points[b])]):
                return dict(status='COUNTEREXAMPLE', angles=angles, pairs=[[a,b],[i,j]],
                            owners=[[owners[a],owners[b]],[owners[i],owners[j]]],
                            projected_squared_numerators=[old, h], geometry=summary)
            mismatches += 1
            # A hash collision is not a negative result or a positive proof.
    return dict(status='NO_DISAGREEMENT' if not mismatches else 'HASH_COLLISIONS_UNRESOLVED',
                angles=angles, geometry=summary, modular_primes=[x[0] for x in maps],
                modular_distance_classes=len(buckets), unequal_hash_collisions=mismatches)


def certificate(root):
    from pysat.solvers import Solver
    raw = (root/'certificates/parts509_core.json').read_bytes()
    core = json.loads(raw)
    witness = run(root, [1])
    closure = run(root, [1], fiber=True)
    points, _, _, _ = geometry(core,[0,153,150],[1])
    anchor_candidates = []
    for record in closure['records']:
        a,b = record['collapsed_pair']
        u,v = record['pair']
        def signatures(s,t):
            return [(norm2([x-y for x,y in zip(p,points[s])]),
                     norm2([x-y for x,y in zip(p,points[t])])) for p in points]
        target_signatures = {}
        for j, signature in enumerate(signatures(u,v)):
            target_signatures.setdefault(signature,[]).append(j)
        candidates = [(i,j) for i,signature in enumerate(signatures(a,b))
                      for j in target_signatures.get(signature,())]
        assert sorted(candidates) == sorted([(a,u),(b,v)])
        anchor_candidates.append(len(candidates))
    equalities = [record['owners'] for record in closure['records']]
    clauses = [[5*v+c+1 for c in range(5)] for v in range(509)]
    clauses += [[-5*v-a-1, -5*v-b-1] for v in range(509) for a,b in combinations(range(5),2)]
    # Both pairs of the first congruence will be bichromatic; all six fiber
    # congruences will be monochromatic. These are extra test constraints,
    # not newly claimed physical unit edges.
    extra = witness['owners']
    clauses += [[-5*a-c-1, -5*b-c-1] for a,b in core['induced_edges']+extra for c in range(5)]
    clauses += [[sign*(5*a+c+1), -sign*(5*b+c+1)]
                for a,b in equalities for c in range(5) for sign in (-1,1)]
    with Solver(name='cd19', bootstrap_with=clauses) as solver:
        solver.conf_budget(100000)
        answer = solver.solve_limited()
        assert answer is True, 'No positive repair found; do not emit a certificate'
        model = set(x for x in solver.get_model() if x > 0)
        word = ''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(509))
        stats = solver.accum_stats()
    return dict(schema=1, results=['C017','T085','E045'],
                core_sha256=hashlib.sha256(raw).hexdigest(),
                source_sha256=hashlib.sha256((root/'certificates/quintic_core_probe.json').read_bytes()).hexdigest(),
                first_congruence=witness['pairs'], first_projected_pairs=witness['owners'],
                fiber_congruences=closure['records'], repairing_core_word=word,
                fiber_anchor_candidates=anchor_candidates,
                quadrance_walks={'2':[[0,0],[3,2],[2,1],[1,0]],'7':[[0,0],[6,2],[1,0]]},
                search_stats=stats,
                scope='Specified retraction and residue-isometry averaged law family only; explicit repair satisfies seven selected two-point congruences, not all joint constraints.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--angles', nargs='+', type=int, default=[1])
    parser.add_argument('--fiber', action='store_true')
    parser.add_argument('--output', type=Path, help='Build the fixed C017/T085/E045 certificate using SAT')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output:
        result = certificate(root)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(run(root, args.angles, args.fiber), indent=2))
