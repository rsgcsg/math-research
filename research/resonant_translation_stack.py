"""Complete trace-sphere search for P + (7/13)Lambda + (3/13)JLambda.

No cutoff on translation labels: exact congruences and the positive trace
equation bound every candidate. An independent checker must replay exports.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import json
import math
import gzip
import hashlib

ROOT = Path(__file__).resolve().parents[1]
RAD = (1, 3, 11, 33, 5, 15, 55, 165)
DEN = 1248


def crange(limit, residue, step):
    return range(-limit+(residue+limit) % step, limit+1, step)


@lru_cache(None)
def sphere(budget, rx, rw):
    right = defaultdict(list)
    for y in crange(math.isqrt(budget//3), 0, 144):
        for z in crange(math.isqrt(budget-3*y*y), -y, 288):
            right[3*y*y+z*z].append((y, z))
    result = []
    for x in crange(math.isqrt(budget), rx, 336):
        for w in crange(math.isqrt((budget-x*x)//3), rw, 336):
            if (x-rx-w+rw) % 672:
                continue
            result.extend((x, y, z, w) for y, z in right.get(budget-x*x-3*w*w, ()))
    return tuple(result)


def unit(delta):
    norm = [0]*8
    for ax in delta:
        nz = [(i, a) for i, a in enumerate(ax) if a]
        for i, a in nz:
            norm[0] += a*a*RAD[i]
        for (i, a), (j, b) in combinations(nz, 2):
            norm[i ^ j] += 2*a*b*RAD[i & j]
    return norm == [DEN*DEN]+[0]*7


def contacts(core):
    differences = defaultdict(list)
    for i, p in enumerate(core['points']):
        for j, q in enumerate(core['points']):
            diff = tuple(tuple(b-a for a, b in zip(ax, bx)) for ax, bx in zip(p, q))
            differences[diff].append((i, j))
    records = []
    candidate_count = 0
    nonnegative = 0
    for index, (diff, pairs) in enumerate(sorted(differences.items())):
        dx, dy = [[13*a for a in ax] for ax in diff]
        assert dx[1] == dy[0] == 0
        fixed = sum(ax[k]*ax[k]*RAD[k] for ax in (dx, dy) for k in range(2, 8))
        budget = DEN*DEN-fixed
        if budget < 0:
            continue
        nonnegative += 1
        for x, y, z, w in sphere(budget, dx[0] % 672, dy[1] % 672):
            candidate_count += 1
            b = (w-dy[1])//336
            a = ((x-dx[0])//336-b)//2
            d = -y//144
            c = (z//144-d)//2
            assert x == dx[0]+336*(2*a+b) and w == dy[1]+336*b
            assert y == -144*d and z == 144*(2*c+d)
            xx, yy = dx.copy(), dy.copy()
            xx[0], xx[1], yy[0], yy[1] = x, y, z, w
            if unit((xx, yy)):
                records.extend((i, j, a, b, c, d) for i, j in pairs)
        if index % 15000 == 0:
            print('differences', index, 'contacts', len(records), flush=True)
    return sorted(records), dict(distinct_differences=len(differences),
                                  nonnegative_budgets=nonnegative,
                                  trace_candidates=candidate_count,
                                  sphere_cache_size=sphere.cache_info().currsize)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def cluster_relation(rows, shifts):
    def decode(d):
        ell = d[1]
        if d[3] != -3*ell or (d[2]+ell) % 4:
            return None
        k = (d[2]+ell)//4
        return (k, ell) if d[0] == 3*k-4*ell else None
    steps = [(a, b) for a, b in product(range(-1, 2), repeat=2) if a*a+a*b+b*b == 1]
    relation = []
    for s, x in enumerate(shifts):
        for t, y in enumerate(shifts):
            for i, j, *d in rows:
                pair = decode(tuple(a+b-c for a, b, c in zip(x, d, y)))
                if pair is not None:
                    relation.append((s, t, i, j, *pair))
            for a, b in steps:
                for d in ((a, b, 0, 0), (0, 0, a, b)):
                    pair = decode(tuple(a+b-c for a, b, c in zip(x, d, y)))
                    if pair is not None:
                        relation.extend((s, t, i, i, *pair) for i in range(509))
    assert len(relation) == len(set(relation))
    return sorted(relation)


def build():
    from parts_core import clauses
    from pysat.solvers import Solver
    raw = (ROOT/'certificates/parts509_core.json').read_bytes()
    seed_raw = (ROOT/'certificates/contact_translation_closure.json').read_bytes()
    core, seed = json.loads(raw), json.loads(seed_raw)['probe']
    rows, statistics = contacts(core)
    relation = cluster_relation(rows, seed['shifts'])
    phases = [int(seed['frame_word'][i]) for i in range(0, 80, 5)]
    constraints = set()
    for s, t, i, j, k, ell in relation:
        delta = (phases[s]-phases[t]) % 5
        for a, b in product(range(2), repeat=2):
            u, v = 509*(2*a+b)+i, 509*(2*((a+k) % 2)+(b+ell) % 2)+j
            constraints.update(tuple(sorted((-5*u-c-1, -5*v-(c+delta) % 5-1))) for c in range(5))
    with Solver(name='cadical195', bootstrap_with=clauses(2036, [], 5)+sorted(constraints)+[[1]]) as solver:
        solver.conf_budget(50000)
        assert solver.solve_limited() is True, 'No positive coloring certificate obtained'
        model = set(solver.get_model())
        words = [''.join(str(next(c for c in range(5) if 5*(509*a+i)+c+1 in model)) for i in range(509)) for a in range(4)]
    print('complete contacts', len(rows), 'relation', len(relation), 'positive constraints', len(constraints), flush=True)
    old = core['five_coloring']
    frame_pairs = sorted({(old[i], old[j]) for i, j, *s in rows if s == [3, 0, 4, 0]})
    return dict(schema=1, core_sha256=hashlib.sha256(raw).hexdigest(),
                seed_sha256=hashlib.sha256(seed_raw).hexdigest(),
                parameter=dict(beta=[40, 169], first=7, second=3, denominator=13),
                contacts=rows, statistics=statistics,
                frame_obstruction=dict(shift=[3, 0, 4, 0], forbidden_color_pairs=frame_pairs),
                cluster=dict(generators=[[3, 0, 4, 0], [-4, 1, -1, -3]],
                             shifts=seed['shifts'], phase_offsets=phases,
                             relation_count=len(relation), relation_sha256=digest(relation),
                             cluster_steps=sorted({r[-2:] for r in relation}),
                             period=[2, 2], words=words, constraint_count=len(constraints),
                             solver='cadical195', conflict_budget=50000),
                scope='Full four-index contact geometry compiled; specified two-generator infinite subarray five-colored, not the full closure or plane')


if __name__ == '__main__':
    data = build()
    (ROOT/'certificates/resonant_translation_stack.json.gz').write_bytes(
        gzip.compress(json.dumps(data, separators=(',', ':')).encode(), mtime=0))
