"""Exact finite checks; Python standard library only. No SAT trust required."""
from collections import Counter
from itertools import combinations, permutations, product
import json

DIRECTIONS = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))


def pairs(k):
    return tuple(frozenset(x) for x in combinations(range(k), 2))


def matchings(items):
    if not items:
        yield frozenset()
        return
    a, *rest = items
    for b in rest:
        for m in matchings([x for x in rest if x != b]):
            yield m | {frozenset((a, b))}


def act_pair(p, x):
    return frozenset(p[i] for i in x)


def act_matching(p, x):
    return frozenset(act_pair(p, y) for y in x)


def row_transition(k, previous, following):
    ds = (1, -1, following, following - 1, -previous, 1 - previous)
    counts = Counter(x % k for x in ds)
    return counts if set(counts) == set(range(1, k)) else None


def alternating(m, n):
    t, parity = divmod(n, 2)
    return (m + 5 * t + 2 * parity) % 6


def check_alternating():
    rows = []
    partners = {c: set() for c in range(6)}
    for n, m in product(range(2), range(6)):
        c = alternating(m, n)
        ns = [alternating(m + dx, n + dy) for dx, dy in DIRECTIONS]
        counts = Counter(ns)
        assert set(counts) == set(range(6)) - {c}
        assert sorted(counts.values()) == [1, 1, 1, 1, 2]
        repeated = next(x for x, v in counts.items() if v == 2)
        assert repeated == (c + (1 if n % 2 == 0 else -1)) % 6
        partners[c].add(repeated)
        assert alternating(m + 6, n) == c
        assert alternating(m + 1, n + 2) == c
        rows.append(dict(point=[m, n], color=c, neighbors=ns, repeated=repeated))
    assert all(len(x) == 2 for x in partners.values())
    assert alternating(0, 0) == alternating(4, 1) == 0
    return dict(periods=[[6, 0], [1, 2]], cells=rows,
                partners={str(k): sorted(v) for k, v in partners.items()})


def check_pair_logic():
    output = {}
    for k in (5, 6):
        domain = pairs(k)
        witnesses = Counter()
        for t, u in product(domain, repeat=2):
            common = [x for x in domain if not (x & t or x & u)]
            good = [(x, y) for x, y in product(common, repeat=2)
                    if (not x & y if k == 6 else len(x & y) == 1)]
            assert bool(good) == (t == u)
            witnesses[(len(t & u), len(good))] += 1
        output[str(k)] = {str(a): n for a, n in sorted(witnesses.items())}
    return output


def check_symmetry():
    ps = pairs(6)
    ms = tuple(matchings(list(range(6))))
    assert len(ps) == len(ms) == 15
    perms = tuple(permutations(range(6)))
    t, s = ps[0], ms[0]
    hp = [p for p in perms if act_pair(p, t) == t]
    hs = [p for p in perms if act_matching(p, s) == s]
    fixed_matchings = [m for m in ms if all(act_matching(p, m) == m for p in hp)]
    fixed_pairs = [x for x in ps if all(act_pair(p, x) == x for p in hs)]
    fixed_pair_endomorphism = [x for x in ps if all(act_pair(p, x) == x for p in hp)]
    assert not fixed_matchings and not fixed_pairs
    assert fixed_pair_endomorphism == [t]
    orbits = []
    remaining = set(ms)
    while remaining:
        m = next(iter(remaining))
        orbit = {act_matching(p, m) for p in hp}
        orbits.append(len(orbit))
        remaining -= orbit
    assert sorted(orbits) == [3, 12]
    return dict(pair_stabilizer=len(hp), matching_stabilizer=len(hs),
                invariant_pair_to_matching_functions=0,
                invariant_matching_to_pair_functions=0,
                invariant_pair_endomorphisms=1,
                pair_stabilizer_matching_orbits=sorted(orbits))


def check_wheels():
    result = {}
    for k in (5, 6, 7):
        defects = Counter()
        for rim in product(range(1, k), repeat=6):
            if all(rim[i] != rim[(i + 1) % 6] for i in range(6)):
                defects[6 - len(set(rim))] += 1
        assert min(defects) == 7 - k
        result[str(k)] = dict(sorted(defects.items()))
    return result


def check_column_family():
    # Exhausts every local window of the arbitrary binary-step sequence.
    checked = 0
    for previous, delta, n in product(range(3), (0, -1), range(3)):
        following = (previous + delta) % 3
        c = n
        neighbors = [3 + (n + following) % 3, (n + 1) % 3,
                     3 + (n + 1 + previous) % 3, 3 + (n + previous) % 3,
                     (n - 1) % 3, 3 + (n - 1 + following) % 3]
        counts = Counter(neighbors)
        assert set(counts) == set(range(6)) - {c}
        repeated = next(x for x, count in counts.items() if count == 2)
        where = [i for i, x in enumerate(neighbors) if x == repeated]
        assert (where[0] - where[1]) % 6 == 3
        checked += 1
    def c(m, n):
        j, parity = divmod(m, 2)
        return n % 3 if parity == 0 else 3 + (n - j) % 3
    partners = {i: set() for i in range(6)}
    for m, n in product(range(6), range(3)):
        counts = Counter(c(m + a, n + b) for a, b in DIRECTIONS)
        assert set(counts) == set(range(6)) - {c(m, n)}
        repeated = next(x for x, count in counts.items() if count == 2)
        partners[c(m, n)].add(repeated)
    assert all(len(s) == 3 for s in partners.values())
    return dict(local_even_cases=checked, periods=[[6, 0], [0, 3]],
                rows=[[c(m, n) for m in range(6)] for n in range(3)],
                partners={i: sorted(s) for i, s in partners.items()})


def check_triangle_support():
    def c(m, n):
        q = (m - 2*n) % 8
        group = q // 4
        return 3*group + ((q % 2) + group - n) % 3
    cells = []
    partners = {i: set() for i in range(6)}
    for q, n in product(range(8), range(3)):
        m = q + 2*n
        a = c(m, n)
        ns = [c(m + x, n + y) for x, y in DIRECTIONS]
        counts = Counter(ns)
        assert set(counts) == set(range(6)) - {a}
        assert sorted(counts.values()) == [1, 1, 1, 1, 2]
        p = next(b for b, count in counts.items() if count == 2)
        assert a // 3 == p // 3
        partners[a].add(p)
        assert c(m + 8, n) == c(m + 6, n + 3) == a
        cells.append(dict(q=q, n_mod3=n, color=a, neighbors=ns, repeated=p))
    assert partners == {i: set(range(3*(i//3), 3*(i//3)+3)) - {i} for i in range(6)}
    return dict(periods=[[8, 0], [6, 3]], cells=cells,
                partners={i: sorted(s) for i, s in partners.items()})


def run():
    affine = {}
    for k, r in ((5, 2), (6, 3), (7, 3)):
        counts = Counter((a + r*b) % k for a, b in DIRECTIONS)
        assert set(counts) == set(range(1, k))
        assert 6 - len(counts) == 7-k
        affine[k] = dict(sorted(counts.items()))
    transitions = []
    for a, b in product(range(6), repeat=2):
        counts = row_transition(6, a, b)
        if counts:
            transitions.append(dict(previous=a, following=b,
                                    duplicate=next(x for x, count in counts.items() if count == 2)))
    assert {(t['previous'], t['following']) for t in transitions} == {
        (2, 3), (3, 2), (3, 3), (4, 4), (4, 5), (5, 4)}
    return dict(affine_phases=affine, row_transitions=transitions,
                alternating_certificate=check_alternating(),
                pair_logic=check_pair_logic(), symmetry=check_symmetry(),
                wheel_defect_counts=check_wheels(), column_family=check_column_family(),
                triangle_support=check_triangle_support())


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
