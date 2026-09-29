"""Exact calibration and independent replay for triangular lattice certificates.

No searcher, NumPy or SAT package is imported. The large geometric tables are
rebuilt; small tests try to falsify the interval and permutation arguments.
"""
from pathlib import Path
from fractions import Fraction
from itertools import permutations, combinations
from copy import deepcopy
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import time

from audit_full_law_preparation import reconstruct, unique_keys
from verify_triangular_lattice import (require, interval_basis, floor_real,
    exact_representatives, all_contacts, check_word)
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice, digest


def permutations_test():
    identity = tuple(range(5))
    good = []
    for p in permutations(range(5)):
        for q in permutations(range(5)):
            if any(p[q[c]] != q[p[c]] for c in range(5)):
                continue
            if any(len({c, p[c], q[c]}) < 3 for c in range(5)):
                continue
            powers = [identity]
            for _ in range(5):
                powers.append(tuple(p[x] for x in powers[-1]))
            require(len(set(powers[:5])) == 5 and powers[5] == identity,
                    'five-cycle is forced')
            require(q in powers[2:5], 'only three slopes')
            good.append((p, q))
    require(len(good) == 72, '24 five-cycles times three slopes')
    # A proper, genuinely non-equivariant five-coloring of the actual lattice.
    def color(m, n):
        return 3 if (m, n) == (0, 0) else 4 if (m, n) == (10, 0) else (m+2*n) % 3
    checked = 0
    for m in range(-2, 13):
        for n in range(-2, 3):
            for h, k in ((1, 0), (0, 1), (1, -1)):
                require(color(m, n) != color(m+h, n+k), 'defect recoloring remains proper')
                checked += 1
    require(color(0, 0) != color(60, 0), 'order of any S5 element divides 60')
    return {'commuting_triangle_palette_pairs': len(good), 'defect_edges': checked}


def floors_test(table):
    bases = [(b, interval_basis(b)) for b in (64, 128, 256)]
    checked = 0
    for num in range(-21, 22):
        for den in (1, 2, 7, 480):
            coeff = [num]+[0]*31
            require(floor_real(coeff, den, bases) == num//den, 'rational floor')
            checked += 1
    require(floor_real([0, 1]+[0]*30, 1, bases) == 1, 'sqrt3 floor')
    require(floor_real([0, -1]+[0]*30, 1, bases) == -2, 'negative sqrt3 floor')
    p, q = 1, 0
    for _ in range(40):
        p, q = 2*p+3*q, p+2*q
    require(p*p-3*q*q == 1, 'Pell identity')
    require(floor_real([-p, q]+[0]*30, 1, bases) == -1, 'tiny negative algebraic floor')
    require(floor_real([p, -q]+[0]*30, 1, bases) == 0, 'tiny positive algebraic floor')
    require(conjugate_twice([-p, q]+[0]*30) == [-2*p, 2*q]+[0]*30, 'real element')
    try:
        floor_real([-p, q]+[0]*30, 1, bases[:1])
    except ValueError:
        pass
    else:
        raise AssertionError('insufficient interval precision was guessed')
    return {'rational_floors': checked, 'algebraic_boundary_cases': 4,
            'insufficient_precision_rejected': True}


def small_geometry(table):
    den = 60
    raw = [[0]*32 for _ in range(4)]
    raw[1][0], raw[1][8] = 36, 48       # (3+4i)/5
    raw[2][0], raw[2][8], raw[2][9] = 30, 60, -30  # i+1-omega
    raw[3][0] = 30                     # 1/2
    raw = list(map(tuple, raw))
    Q = sorted(raw)
    got, _ = all_contacts(Q, den, table)
    want = set()
    target = [4*den*den]+[0]*31
    for i in range(len(Q)):
        for j in range(i, len(Q)):
            for m in range(-4, 5):
                for n in range(-4, 5):
                    if i == j and (m, n) not in ((1, 0), (0, 1), (1, -1)):
                        continue
                    d = [x-y for x, y in zip(Q[i], Q[j])]
                    d[0] -= den*m+den*n//2
                    d[9] -= den*n//2
                    if product_twice(d, conjugate_twice(d), table) == target:
                        want.add((i, j, m, n))
    require(set(got) == want, 'bucket sieve equals enlarged direct exact scan')
    require(any(i!=j and (m or n) for i,j,m,n in got), 'nontrivial cross-orbit displacement tested')
    return {'small_representatives': len(Q), 'small_contact_types': len(got)}


def mutations(cert, Q, gains):
    tests = {
        'schema': lambda c: c.__setitem__('schema', 'not-a-certificate'),
        'representatives': lambda c: c.__setitem__('representative_sha256', '0'*64),
        'contacts': lambda c: c.__setitem__('gain_sha256', '0'*64),
        'constant_word': lambda c: c.__setitem__('word', '0'*len(Q)),
        'short_word': lambda c: c.__setitem__('word', c['word'][:-1]),
        'invalid_color': lambda c: c.__setitem__('word', '5'+c['word'][1:]),
        'boolean_slope': lambda c: c.__setitem__('slope', True),
        'float_slope': lambda c: c.__setitem__('slope', 2.0),
        'zero_slope': lambda c: c.__setitem__('slope', 0),
    }
    for label, mutate in tests.items():
        altered = deepcopy(cert)
        mutate(altered)
        try:
            check_word(altered, Q, gains)
        except ValueError:
            continue
        raise AssertionError('accepted mutation '+label)
    try:
        json.loads('{"a":1,"a":2}', object_pairs_hook=unique_keys)
    except ValueError:
        pass
    else:
        raise AssertionError('duplicate keys accepted')
    process = subprocess.run([sys.executable, '-O', __file__], capture_output=True,
                             text=True, timeout=10)
    require(process.returncode != 0 and 'requires assertions' in process.stderr,
            'optimized verification is rejected')
    return sorted(tests)+['duplicate_json', 'optimized_mode']


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-mixed', action='store_true',
                        help='Only recheck the published Y+lattice positive theorem')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    start = time.monotonic()
    data, summary = reconstruct(root)
    table = multiplication_twice()
    small = dict(**permutations_test(), **floors_test(table), **small_geometry(table))
    cert = json.loads((root/'certificates/triangular_lattice_five_coloring.json').read_text(),
                      object_pairs_hook=unique_keys)
    Q, den, points, pos = exact_representatives(data, 1, table)
    gains, filters = all_contacts(Q, den, table)
    require(cert['levels'] == 1 and len(Q) == 9624 and len(gains) == 79007,
            'correct positive subject')
    positive = check_word(cert, Q, gains)
    rejects = mutations(cert, Q, gains)
    mixed = None
    if not args.skip_mixed:
        Q5, d5, pts5, pos5 = exact_representatives(data, 5, table)
        G5, sieve5 = all_contacts(Q5, d5, table)
        expected = json.loads((root/'certificates/mixed_lattice_geometry.json').read_text())
        require(len(pts5) == expected['seed_points'], 'mixed seed size')
        require(len(Q5) == expected['representatives'], 'mixed quotient size')
        require(len(G5) == expected['contacts'], 'mixed contact count')
        require(digest(Q5) == expected['representative_sha256'], 'mixed representatives')
        require(digest(G5) == expected['gain_sha256'], 'mixed contacts')
        mixed = dict(seed_points=len(pts5), representatives=len(Q5), contacts=len(G5),
                     **sieve5, colorability='NOT_DECIDED_BY_THIS_CHECK')
    report = dict(status='PASS', input_semantic_sha256=summary['semantic_sha256'],
                  positive=positive, positive_sieve=filters, mixed=mixed,
                  small_tests=small, rejection_tests=rejects,
                  seconds=time.monotonic()-start,
                  scope='Replayed triangular saturation upper bound and mixed contact geometry. '
                        'No ordinary HN bound or unrestricted mixed-host coloring conclusion.')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
