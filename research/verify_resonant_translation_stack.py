"""Independent complete contact compiler and infinite coloring obligations.

Standard library only. The sphere splits (x,y)/(z,w), in contrast to the
producer's (x,w)/(y,z); multiplication uses gcd of square-free radicands.
"""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path
import gzip
import hashlib
import json
import math

from verify_contact_translation_closure import multiplication, squared_distance

RAD = (1, 3, 11, 33, 5, 15, 55, 165)
DEN = 1248


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


@lru_cache(None)
def trace_solutions(total, rx, rw):
    sums = {}
    bound = math.isqrt(total)
    for x in range(-bound, bound+1):
        if (x-rx) % 336:
            continue
        limit = math.isqrt((total-x*x)//3)
        for y0 in range(-limit//144, limit//144+1):
            y = 144*y0
            if x*x+3*y*y <= total:
                sums.setdefault(x*x+3*y*y, []).append((x, y))
    result = []
    for z0 in range(-bound//144, bound//144+1):
        z = 144*z0
        if z*z > total:
            continue
        limit = math.isqrt((total-z*z)//3)
        for w in range(-limit, limit+1):
            if (w-rw) % 336:
                continue
            for x, y in sums.get(total-z*z-3*w*w, ()):
                if (x-rx-w+rw) % 672 == 0 and (z+y) % 288 == 0:
                    result.append((x, y, z, w))
    return tuple(sorted(result))


def compile_contacts(core):
    table = multiplication(RAD)
    zero = ((0,)*8, (0,)*8)
    rows = []
    differences = {}
    for i, p in enumerate(core['points']):
        for j, q in enumerate(core['points']):
            delta = tuple(tuple(13*(b-a) for a, b in zip(ax, bx)) for ax, bx in zip(p, q))
            assert delta[0][1] == delta[1][0] == 0
            fixed = sum(r*v*v for ax in delta for r, v in zip(RAD[2:], ax[2:]))
            total = DEN*DEN-fixed
            candidates = trace_solutions(total, delta[0][0] % 672, delta[1][1] % 672) if total >= 0 else ()
            differences[delta] = (total >= 0, len(candidates))
            for x, y, z, w in candidates:
                a, b = (x-delta[0][0]-w+delta[1][1])//672, (w-delta[1][1])//336
                c, d = (z+y)//288, -y//144
                assert x-delta[0][0] == 336*(2*a+b) and w-delta[1][1] == 336*b
                assert y == -144*d and z == 144*(2*c+d)
                point = ([x, y]+list(delta[0][2:]), [z, w]+list(delta[1][2:]))
                if squared_distance(point, zero, table) == [DEN*DEN]+[0]*7:
                    rows.append((i, j, a, b, c, d))
    assert len(rows) == len(set(rows))
    stats = dict(distinct_differences=len(differences),
                 nonnegative_budgets=sum(a for a, b in differences.values()),
                 trace_candidates=sum(b for a, b in differences.values()),
                 sphere_cache_size=trace_solutions.cache_info().currsize)
    return sorted(rows), stats


def check_cross_and_uniqueness(core):
    # In P, x's sqrt(3) coefficient and y's rational coefficient vanish. A
    # P-difference in L' therefore has zero JLambda coefficient. Divisibility
    # by 13 leaves 7Lambda, whose nonzero trace length is >=7 > diameter 4.
    assert core['coordinate_denominator'] == 96 and math.gcd(96*7, 13) == 1
    assert all(p[0][1] == p[1][0] == 0 for p in core['points'])
    assert max(sum((a-b)**2*r for ax, bx in zip(p, q) for a, b, r in zip(ax, bx, RAD))
               for p, q in combinations(core['points'], 2)) == 16*96**2
    table = multiplication(RAD+tuple(2*r for r in RAD))
    steps = []
    for m, n in product(range(-3, 4), repeat=2):
        norm = m*m+m*n+n*n
        if norm not in (3, 4):
            continue
        for sign in (-1, 1):
            if norm == 3:
                assert (m+2*n) % 3 == (2*m+n) % 3 == 0
                a, b, c, d = -sign*(m+2*n)//3, sign*(2*m+n)//3, 0, 0
            else:
                assert m % 2 == n % 2 == 0
                a, b, c, d = 0, 0, sign*m//2, sign*n//2
            x, y = [0]*16, [0]*16
            x[0], x[1], y[0], y[1] = 7*(2*a+b), -3*d, 3*(2*c+d), 7*b
            x[12], y[13] = 2*(2*m+n), 2*n
            assert squared_distance((x, y), ([0]*16, [0]*16), table) == [26**2]+[0]*15
            steps.append((a, b, c, d, m, n))
    assert len(steps) == 24
    assert 13**2-40 == 3*43 and 3*43 not in RAD
    assert all(43 % i for i in range(2, 7))
    return steps


def check_frame_obstruction(root, core, rows, saved):
    assert saved['shift'] == [3, 0, 4, 0]
    old = core['five_coloring']
    pairs = sorted({(old[i], old[j]) for i, j, a, b, c, d in rows if (a, b, c, d) == (3, 0, 4, 0)})
    assert list(map(list, pairs)) == saved['forbidden_color_pairs']
    assert len(pairs) == 16
    assert all(any(a == permutation[b] for a, b in pairs) for permutation in permutations(range(5)))
    # The actual two-core graph is nevertheless five-colorable. Directly
    # construct a residue coloring, then check every compiled induced edge.
    colors11 = ''.join(json.loads((root/'certificates/residue11_coloring.json').read_text())['rows'])
    assert len(colors11) == 121 and set(colors11) == set('01234')
    assert all(colors11[11*x+y] != colors11[11*u+v]
               for x, y, u, v in product(range(11), repeat=4)
               if ((x-u)**2+(y-v)**2) % 11 == 1)
    images = (1, 5, 0, 0, 4, 9, 0, 0)
    table = multiplication(RAD)
    assert all(images[i]*images[j] % 11 == g*images[k] % 11 for (i, j), (k, g) in table.items())
    word = []
    for shift in ((0, 0), (2016, 1152)):
        for p in core['points']:
            x, y = ((13*sum(a*b for a, b in zip(ax, images))+v)*pow(DEN, -1, 11) % 11 for ax, v in zip(p, shift))
            word.append(colors11[11*x+y])
    edges = set()
    for i, j, a, b, c, d in rows:
        if (a, b, c, d) == (0, 0, 0, 0):
            edges.update((tuple(sorted((i, j))), tuple(sorted((509+i, 509+j)))))
        elif (a, b, c, d) == (3, 0, 4, 0):
            edges.add((i, 509+j))
    assert len(edges) == 4915 and all(word[i] != word[j] for i, j in edges)
    return dict(forbidden_color_pairs=len(pairs), permutations_rejected=120,
                actual_vertices=1018, induced_edges=len(edges), actual_five_coloring=True)


def check_cluster(rows, steps, cluster):
    assert cluster['generators'] == [[3, 0, 4, 0], [-4, 1, -1, -3]]
    S = cluster['shifts']
    phase = cluster['phase_offsets']
    assert phase == [0, 4, 3, 3, 4, 4, 3, 4, 3, 3, 4, 4, 3, 4, 3, 0]
    assert cluster['period'] == [2, 2]
    words = cluster['words']
    assert len(words) == 4 and all(len(w) == 509 and set(w) <= set('01234') for w in words)

    def solve_shift(d):
        # Solve using coordinates (a,b), independently of the producer's (b,c).
        ell = d[1]
        if (d[0]+4*ell) % 3:
            return None
        k = (d[0]+4*ell)//3
        return (k, ell) if d[2] == 4*k-ell and d[3] == -3*ell else None

    assert all(solve_shift(tuple(a-b for a, b in zip(x, y))) is None
               for i, x in enumerate(S) for j, y in enumerate(S) if i != j)
    by_shift = {}
    for i, j, *d in rows:
        by_shift.setdefault(tuple(d), []).append((i, j))
    cross = {tuple(s[:4]) for s in steps}
    assert len(cross) == 12
    relation = []
    for s, x in enumerate(S):
        for t, y in enumerate(S):
            for d, pairs in by_shift.items():
                change = solve_shift(tuple(a+b-c for a, b, c in zip(x, d, y)))
                if change is not None:
                    relation.extend((s, t, i, j, *change) for i, j in pairs)
            for d in cross:
                change = solve_shift(tuple(a+b-c for a, b, c in zip(x, d, y)))
                if change is not None:
                    relation.extend((s, t, i, i, *change) for i in range(509))
    relation.sort()
    assert len(relation) == len(set(relation)) == cluster['relation_count'] == 108906
    assert digest(relation) == cluster['relation_sha256']
    assert list(map(list, sorted({r[-2:] for r in relation}))) == cluster['cluster_steps']
    constraints = set()
    checks = 0
    for s, t, i, j, k, ell in relation:
        for a, b in product(range(2), repeat=2):
            source = 2*a+b
            target = 2*((a+k) % 2)+(b+ell) % 2
            assert (int(words[source][i])+phase[s]) % 5 != (int(words[target][j])+phase[t]) % 5
            checks += 1
            u, v = 509*source+i, 509*target+j
            delta = (phase[s]-phase[t]) % 5
            constraints.update(tuple(sorted((-5*u-c-1, -5*v-(c+delta) % 5-1))) for c in range(5))
    assert len(constraints) == cluster['constraint_count'] == 70760
    parity_words = {}
    T, U = cluster['generators']
    for a, b in product(range(2), repeat=2):
        for s, offset in enumerate(S):
            label = tuple((x+a*y+b*z) % 2 for x, y, z in zip(offset, T, U))
            word = ''.join(str((int(v)+phase[s]) % 5) for v in words[2*a+b])
            parity_words.setdefault(label, set()).add(word)
    assert len(parity_words) == 16 and all(len(v) > 1 for v in parity_words.values())
    return dict(complete_relations=len(relation), phase_edge_checks=checks,
                free_core_words=4, phase_offsets=16, infinite_two_generator_array_five_colored=True)


def verify(root, data_override=None):
    if not __debug__:
        raise RuntimeError('Do not disable assertions in the certificate checker')
    raw = (root/'certificates/parts509_core.json').read_bytes()
    seed = (root/'certificates/contact_translation_closure.json').read_bytes()
    data = data_override if data_override is not None else json.loads(gzip.decompress((root/'certificates/resonant_translation_stack.json.gz').read_bytes()))
    assert data['schema'] == 1 and data['core_sha256'] == hashlib.sha256(raw).hexdigest()
    assert data['seed_sha256'] == hashlib.sha256(seed).hexdigest()
    assert data['parameter'] == dict(beta=[40, 169], first=7, second=3, denominator=13)
    assert data['cluster']['shifts'] == json.loads(seed)['probe']['shifts']
    core = json.loads(raw)
    rows, stats = compile_contacts(core)
    assert list(map(list, rows)) == data['contacts'] and stats == data['statistics']
    assert len(rows) == 8008 and len({r[2:] for r in rows}) == 49
    assert sum(any(r[2:]) for r in rows) == 3124
    assert sum(r[4] != 0 or r[5] != 0 for r in rows) == 1508
    core_edges = set(map(tuple, core['induced_edges']))
    assert all((r[4] != 0 or r[5] != 0) == (tuple(sorted(r[:2])) not in core_edges) for r in rows)
    basis = data['full_lattice_basis']
    assert basis == [[3, 0, 4, 0], [-4, 1, -1, -3], [-4, 3, 0, 0], [-3, 4, 4, -1]]
    assert all(tuple(v) in {r[2:] for r in rows} for v in basis)
    determinant = 0
    for p in permutations(range(4)):
        sign = (-1)**sum(p[i] > p[j] for i in range(4) for j in range(i+1, 4))
        determinant += sign*math.prod(basis[i][p[i]] for i in range(4))
    assert abs(determinant) == 1
    steps = check_cross_and_uniqueness(core)
    return dict(contacts=8008, shifts=49, ordered_core_pairs=509**2,
                statistics=stats, shell_transports=len(steps), full_basis_determinant=determinant,
                frame=check_frame_obstruction(root, core, rows, data['frame_obstruction']),
                cluster=check_cluster(rows, steps, data['cluster']),
                scope='Complete geometry of the four-index closure; five coloring only of the stated two-generator subarray; no new plane bound')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
