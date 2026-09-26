"""Independent complete contact-table replay for the H=<eta,u> orbit.

The search producer is never imported. For every unordered representative
pair this checker solves the unit-contact quadratic over a split prime,
matches its roots against ALL 95 possible gains, uses a different split
prime, then checks exact integer algebra. Linear and identically-zero
reductions are included. The full T125 bound and orbit identification are
independently replayed by verify_rotation_orbit_equalities.
"""

from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import math
import time

from verify_quintic_core_probe import (
    RAD, conjugate_twice, digest, filter_map, product_twice,
)
from verify_rotation_orbit_equalities import verify as verify_equalities


def _split_map(table, start, reverse_roots=False):
    """Construct and verify a field homomorphism on all 1024 basis products."""
    prime = start
    while True:
        if (prime % 20 == 1 and
            not any(prime % d == 0 for d in range(2, math.isqrt(prime)+1)) and
            all(pow(r, (prime-1)//2, prime) == 1 for r in (3, 11))):
            break
        prime += 1
    fifth_roots = sorted({pow(x, (prime-1)//5, prime)
                         for x in range(1, prime)})
    if reverse_roots:
        eta = fifth_roots[-1]
    else:
        eta = next(pow(x, (prime-1)//5, prime) for x in range(2, prime)
                   if pow(x, (prime-1)//5, prime) != 1)
    assert eta != 1 and pow(eta, 5, prime) == 1
    roots = {}
    for r in (3, 11, -1):
        possible = [x for x in range(1, prime) if x*x % prime == r % prime]
        assert len(possible) == 2
        roots[r] = possible[-1] if reverse_roots else possible[0]
    roots[5] = (2*(eta + pow(eta, -1, prime)) + 1) % prime
    assert roots[5]*roots[5] % prime == 5
    field = []
    for imaginary in range(2):
        for radical in RAD:
            value = roots[-1] if imaginary else 1
            for r in (3, 5, 11):
                if radical % r == 0:
                    value = value*roots[r] % prime
            field.append(value)
    images = field + [eta*x % prime for x in field]
    assert all(sum(c*images[k] for k, c in terms) % prime ==
               2*images[i]*images[j] % prime
               for (i, j), terms in table.items())
    bars = [sum(x*y for x, y in zip(
        conjugate_twice([int(i == j) for j in range(32)]), images)) *
        pow(2, -1, prime) % prime for i in range(32)]
    return prime, images, bars


def _all_gains(table):
    one = (Q(1),) + (Q(0),)*31
    eta = (Q(0),)*16 + one[:16]
    u = tuple(Q({0: 1, 4: -3, 9: -1, 13: -1}.get(i, 0), 8)
              for i in range(32))
    mul = lambda a, b: tuple(Q(x, 2) for x in product_twice(a, b, table))
    inverse_u = tuple(Q(x, 2) for x in conjugate_twice(u))
    assert mul(u, inverse_u) == one
    powers = {0: one}
    for n in range(1, 10):
        powers[n] = mul(powers[n-1], u)
        powers[-n] = mul(powers[1-n], inverse_u)
    result = {}
    torsion = one
    for h in range(5):
        for n in range(-9, 10):
            result[h, n] = mul(torsion, powers[n])
        torsion = mul(torsion, eta)
    assert torsion == one and len(set(result.values())) == 95
    return result


def _canonical(i, j, h, n):
    if n < 0 or (n == 0 and h > 2) or (n == h == 0 and i > j):
        return j, i, (-h) % 5, -n
    return i, j, h, n


def _quadratic_roots(a, b, c, prime, inverse, square_root):
    """Roots of a*x^2-c*x+b; None means every residue is a root."""
    if a:
        radical = square_root[(c*c - 4*a*b) % prime]
        if radical < 0:
            return ()
        multiplier = inverse[2*a % prime]
        first = (c+radical)*multiplier % prime
        if radical == 0:
            return (first,)
        return first, (c-radical)*multiplier % prime
    if c:
        return (b*inverse[c] % prime,)
    return None if b == 0 else ()


def _root_tables(prime):
    inverse = [0]*prime
    for x in range(1, prime):
        inverse[x] = pow(x, -1, prime)
    roots = [-1]*prime
    for x in range(prime):
        roots[x*x % prime] = x
    return inverse, roots


def _self_test():
    prime = 7
    inverse, roots = _root_tables(prime)
    checked = 0
    for a in range(prime):
        for b in range(prime):
            for c in range(prime):
                result = _quadratic_roots(a, b, c, prime, inverse, roots)
                actual = set(range(prime)) if result is None else set(result)
                expected = {x for x in range(prime)
                            if (a*x*x-c*x+b) % prime == 0}
                assert actual == expected
                checked += 1
    assert _canonical(3, 8, 4, -2) == (8, 3, 1, 2)
    return checked


def _rebuild(context, progress=False):
    started = time.monotonic()
    assert context['bounds']['nonzero_unit_offset_absolute_bound'] == 9
    table = context['table']
    points = context['representative_points']
    den = context['denominator']
    assert len(points) == 4176 and den == 480
    gains = _all_gains(table)
    # First and second maps also replay the producer's diagnostic counts.
    # The actual completeness sieve additionally uses the third map, with
    # a different prime and opposite radical-root choices.
    maps = [filter_map(table), _split_map(table, 10001),
            _split_map(table, 20001, reverse_roots=True)]
    assert len({m[0] for m in maps}) == 3
    residues, factors = [], []
    for prime, images, bars in maps:
        invden = pow(den, -1, prime)
        residues.append([(sum(x*y for x, y in zip(p, images))*invden % prime,
                          sum(x*y for x, y in zip(p, bars))*invden % prime)
                         for p in points])
        evaluate = lambda rotation, basis: sum(
            x.numerator*pow(x.denominator, -1, prime)*y
            for x, y in zip(rotation, basis)) % prime
        factors.append({key: (evaluate(r, images), evaluate(r, bars))
                        for key, r in gains.items()})
        assert all(a*b % prime == 1 for a, b in factors[-1].values())
    prime = maps[0][0]
    inverse, square_root = _root_tables(prime)
    by_root = defaultdict(list)
    for key, pair in factors[0].items():
        by_root[pair[0]].append(key)
    p1 = residues[0]
    norm1 = [a*b % prime for a, b in p1]
    first_counts, second_counts = Counter(), Counter()
    contacts = set()
    exact_checks = alternate_survivors = degenerate = 0
    integer_gains = {}
    for key, rotation in gains.items():
        d = math.lcm(*(x.denominator for x in rotation))
        integer_gains[key] = (tuple(int(x*d) for x in rotation), d)
    transformed = {}
    for i, (x, xbar) in enumerate(p1):
        for j in range(i, len(points)):
            y, ybar = p1[j]
            a, b = xbar*y % prime, x*ybar % prime
            c = (norm1[i] + norm1[j] - 1) % prime
            roots = _quadratic_roots(a, b, c, prime, inverse, square_root)
            if roots is None:
                degenerate += 1
                possible = gains.keys()
            else:
                possible = [key for root in roots for key in by_root.get(root, ())]
            # On a self-pair, inverse gains name the same undirected orbit.
            candidates = {_canonical(i, j, h, n) for h, n in possible}
            for left, right, h, n in candidates:
                first_counts[h, n] += 1
                p2 = maps[1][0]
                z, zbar = residues[1][left]
                w, wbar = residues[1][right]
                g, gbar = factors[1][h, n]
                passes_second = ((z-g*w)*(zbar-gbar*wbar)-1) % p2 == 0
                if passes_second:
                    second_counts[h, n] += 1
                p3 = maps[2][0]
                z, zbar = residues[2][left]
                w, wbar = residues[2][right]
                g, gbar = factors[2][h, n]
                if ((z-g*w)*(zbar-gbar*wbar)-1) % p3:
                    continue
                alternate_survivors += 1
                # Use only the independent alternative second sieve to
                # decide which candidates receive an exact check.
                key = right, h, n
                coeff, d = integer_gains[h, n]
                if key not in transformed:
                    transformed[key] = product_twice(coeff, points[right], table)
                delta = [2*d*x-y for x, y in zip(points[left], transformed[key])]
                norm = product_twice(delta, conjugate_twice(delta), table)
                exact_checks += 1
                if norm == [4*(2*d*den)**2]+[0]*31:
                    assert passes_second
                    contacts.add((left, right, h, n))
        if progress and i % 500 == 0:
            print(json.dumps(dict(stage='independent_pair_quadratics', row=i,
                                  elapsed=round(time.monotonic()-started, 2),
                                  contacts=len(contacts), exact_checks=exact_checks)), flush=True)
    contact_rows = [list(row) for row in sorted(contacts)]
    actual_counts = Counter((h, n) for i, j, h, n in contacts)
    ordered = set()
    for i, j, h, n in contacts:
        ordered.add((i, j, h, n))
        ordered.add((j, i, (-h) % 5, -n))
    pair_counts = Counter((i, j) for i, j, h, n in ordered)
    assert max(pair_counts.values()) <= 2
    origin = [i for i, p in enumerate(points)
              if product_twice(p, conjugate_twice(p), table) == [4*den*den]+[0]*31]
    scan = [dict(h=h, n=n, first_survivors=first_counts[h, n],
                 second_survivors=second_counts[h, n], contacts=actual_counts[h, n])
            for h in range(5) for n in range(10) if n or h <= 2]
    return dict(contacts=contact_rows, contact_count=len(contact_rows),
                contact_sha256=digest(contact_rows), origin_neighbors=origin,
                origin_neighbor_count=len(origin),
                ordered_pair_gain_histogram=[list(row) for row in sorted(Counter(pair_counts.values()).items())],
                modular_filter_primes=[maps[0][0], maps[1][0]], scan=scan), dict(
                    unordered_pairs=len(points)*(len(points)+1)//2,
                    gain_candidates=95, first_prime=prime,
                    independent_second_prime=maps[2][0],
                    degenerate_zero_polynomials=degenerate,
                    first_survivors=sum(first_counts.values()),
                    alternate_second_survivors=alternate_survivors,
                    exact_checks=exact_checks,
                    self_loop_contacts=[list(row) for row in sorted(contacts) if row[0] == row[1]])


def _check(data, expected):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    assert type(data) is dict and set(data) == set(expected)
    assert json.dumps(data, sort_keys=True, separators=(',', ':')) == \
        json.dumps(expected, sort_keys=True, separators=(',', ':'))


def _mutations(data, expected):
    rejected = []

    def reject(name, mutate):
        damaged = deepcopy(data)
        mutate(damaged)
        try:
            _check(damaged, expected)
        except (AssertionError, KeyError, ValueError, TypeError):
            rejected.append(name)
        else:
            raise AssertionError('Mutation accepted: ' + name)

    def remove_edge(d):
        d['contacts'].pop()
        d['contact_count'] -= 1
        d['contact_sha256'] = digest(d['contacts'])

    def false_edge(d):
        d['contacts'][0][3] += 1
        d['contact_sha256'] = digest(d['contacts'])

    reject('omitted_contact_rehashed', remove_edge)
    reject('false_gain_rehashed', false_edge)
    reject('missing_origin_neighbor', lambda d: d['origin_neighbors'].pop())
    reject('wrong_representative', lambda d: d['representatives'].__setitem__(0, 1))
    reject('false_offset_bound', lambda d: d['completeness'].__setitem__('absolute_offset_bound', 4))
    reject('changed_equality_hash', lambda d: d.__setitem__('equality_sha256', '0'*64))
    reject('altered_sieve_count', lambda d: d['scan'][0].__setitem__('first_survivors', 0))
    reject('boolean_schema', lambda d: d.__setitem__('schema', True))
    return rejected


def verify(root, mutation_tests=False, progress=False, geometry_context=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    started = time.monotonic()
    root = Path(root)
    self_tests = _self_test()
    equality_report, context = verify_equalities(root, geometry_context=True)
    path = root/'certificates/rotation_orbit_contacts.json'
    data = json.loads(path.read_text())
    rebuilt, details = _rebuild(context, progress)
    expected = dict(
        schema=1, kind='complete_rotation_orbit_unit_contacts',
        equality_sha256=equality_report['certificate_sha256'],
        source_sha256=equality_report['source_sha256'],
        source_point_sha256=equality_report['source_point_sha256'],
        representatives=context['representatives'],
        representative_count=len(context['representatives']),
        convention='|r_i - eta^h u^n r_j| = 1; inverse edges identified',
        completeness=dict(theorem='T125 section 9', absolute_offset_bound=9,
                          canonical_rule='n>0; or n=0,h=1,2; or n=h=0,i<j'),
        **rebuilt,
        scope='Complete actual induced H-orbit graph, pending independent replay; no coloring or NON5 asserted.')
    _check(data, expected)
    mutations = _mutations(data, expected) if mutation_tests else []
    report = dict(status='PASS', kind=data['kind'],
                certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                equality_sha256=expected['equality_sha256'],
                representative_count=expected['representative_count'],
                contact_count=rebuilt['contact_count'],
                contact_sha256=rebuilt['contact_sha256'],
                origin_neighbor_count=rebuilt['origin_neighbor_count'],
                completeness_bound_replayed=True,
                independent_quadratic_self_tests=self_tests,
                mutation_rejections=mutations,
                reconstruction=details,
                elapsed_seconds=round(time.monotonic()-started, 3),
                scope='All actual unit contacts and origin stars in the infinite H orbit; '
                      'no coloring or lower-bound conclusion.')
    if geometry_context:
        return report, dict(context, contacts=rebuilt['contacts'],
                            origin_neighbors=rebuilt['origin_neighbors'],
                            contacts_data=expected)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutation-tests', action='store_true')
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1],
                            args.mutation_tests, args.progress), indent=2))
