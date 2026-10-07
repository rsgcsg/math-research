"""Exact algebraic calibrations for the Family-158 subfield extension.

Only finite algebra is checked. The analytic transfer argument and the new
chromatic cofinality theorem are written proofs, not consequences of this PASS.
No SymPy, SAT solver, numerical optimizer, or Lean runtime is imported.
"""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations, product, permutations
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_keys(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'duplicate JSON key')
        result[k] = v
    return result


def rational(x):
    require(isinstance(x, list) and len(x) == 2, 'fraction shape')
    require(all(type(t) is int for t in x) and x[1] > 0, 'fraction integers')
    q = Q(*x)
    require([q.numerator, q.denominator] == x, 'fraction not canonical')
    return q


def mul(a, b):
    # Q(sqrt(2)), exact defining relation sqrt(2)^2 = 2.
    return (a[0]*b[0] + 2*a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def determinant(rows):
    a = [[Q(x) for x in row] for row in rows]
    n = len(a)
    require(all(len(row) == n for row in a), 'non-square matrix')
    d = Q(1)
    for k in range(n):
        pivot = next((j for j in range(k, n) if a[j][k]), None)
        if pivot is None:
            return Q(0)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            d = -d
        p = a[k][k]
        d *= p
        for j in range(k+1, n):
            ratio = a[j][k]/p
            for l in range(k+1, n):
                a[j][l] -= ratio*a[k][l]
    return d


def trim(a, p):
    a = [x % p for x in a]
    while len(a) > 1 and not a[-1]:
        a.pop()
    return a


def poly_product(a, b, p):
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return trim(out, p)


def remainder(a, b, p):
    a, b = trim(a, p), trim(b, p)
    require(b != [0], 'zero polynomial divisor')
    while a != [0] and len(a) >= len(b):
        degree, ratio = len(a)-len(b), a[-1]*pow(b[-1], -1, p) % p
        for i, x in enumerate(b):
            a[i+degree] -= ratio*x
        a = trim(a, p)
    return a


def irreducible(f, p):
    # A reducible degree n polynomial has a factor of degree <= floor(n/2).
    tests = 0
    for degree in range(1, (len(trim(f, p))-1)//2+1):
        for coefficients in product(range(p), repeat=degree):
            tests += 1
            require(remainder(f, list(coefficients)+[1], p) != [0],
                    'reducible polynomial')
    return tests


def perm_comp(a, b):
    return tuple(a[b[i]] for i in range(len(a)))


def group_generated(generators):
    identity = tuple(range(len(generators[0])))
    seen, todo = {identity}, [identity]
    while todo:
        a = todo.pop()
        for g in generators:
            h = perm_comp(g, a)
            if h not in seen:
                seen.add(h)
                todo.append(h)
    return seen


def verify(c):
    require(c.get('schema') == 'radical-transfer-algebra-calibration-v1', 'schema')
    require(c['basis'] == ['1','sqrt(2)','i','i*sqrt(2)'], 'basis')
    require(len(c['parameters']) == len(c['unit_rotations']) == 8, 'rotation count')
    points = []
    for t, raw in zip(c['parameters'], c['unit_rotations']):
        require(len(t) == 2 and all(type(v) is int for v in t), 'parameter')
        require(len(raw) == 4, 'coordinate size')
        v = [rational(x) for x in raw]
        real, imag = tuple(v[:2]), tuple(v[2:])
        require(add(mul(real, real), mul(imag, imag)) == (1, 0), 'unit norm')
        t = tuple(map(Q, t))
        t2 = mul(t, t)
        den = add((1, 0), t2)
        require(mul(den, real) == (1-t2[0], -t2[1]), 'Cayley real part')
        require(mul(den, imag) == (2*t[0], 2*t[1]), 'Cayley imaginary part')
        points.append(v)
    determinants = [determinant(rows) for rows in combinations(points, 4)]
    require(len(determinants) == 70 and all(determinants), 'general position')
    f = c['quintic']
    require(f == [-1,-1,0,0,0,1] and all(type(x) is int for x in f), 'quintic')
    a, b = c['mod2_factors']
    require(poly_product(a, b, 2) == trim(f, 2), 'mod2 factorization')
    checks2 = irreducible(a, 2)+irreducible(b, 2)
    require(a != b and len(a) == 3 and len(b) == 4, 'squarefree degrees')
    require(c['mod3_irreducible'] is True, 'irreducibility claim type')
    checks3 = irreducible(f, 3)
    require(sum(x for x in f) == -1 and sum(x*2**i for i, x in enumerate(f)) == 29,
            'real-root bracket')
    cubic = c['nonconstructible_cubic']
    require(cubic == [1,-3,0,1] and all(type(x) is int for x in cubic), 'cubic')
    checks_cubic = irreducible(cubic, 2)
    g, h = (1,2,3,4,0), (1,0,3,4,2)
    require(perm_comp(h, perm_comp(h,h)) == (1,0,2,3,4), 'transposition')
    group = group_generated([g,h])
    require(group == set(permutations(range(5))), 'S5 calibration')
    return dict(status='PASS_FINITE_ALGEBRA_ONLY', unit_rotations=8,
                nonzero_four_by_four_determinants=70,
                monic_divisor_checks=dict(mod2_factors=checks2,mod3_quintic=checks3,
                                         mod2_cubic=checks_cubic),
                generated_group_order=len(group),
                analytic_transfer_proved_by_this_program=False,
                lean_replay=False, finite_non5_graph_constructed=False)


def self_test(c):
    mutations = {}
    d = deepcopy(c);d['unit_rotations'][0][0] = [2,1];mutations['nonunit'] = d
    d = deepcopy(c);d['parameters'][0] = [1,0];mutations['wrong_parameter'] = d
    d = deepcopy(c);d['parameters'][1] = d['parameters'][0];d['unit_rotations'][1] = d['unit_rotations'][0];mutations['dependent_rotations'] = d
    d = deepcopy(c);d['unit_rotations'][0][0] = [True,1];mutations['bool_coordinate'] = d
    d = deepcopy(c);d['unit_rotations'][0][0] = [1.0,1];mutations['float_coordinate'] = d
    d = deepcopy(c);d['unit_rotations'][0][0] = [2,2];mutations['noncanonical_fraction'] = d
    d = deepcopy(c);d['unit_rotations'][0][0] = [1,0];mutations['zero_denominator'] = d
    d = deepcopy(c);d['mod2_factors'][0][0] = 0;mutations['wrong_factor'] = d
    d = deepcopy(c);d['quintic'][0] = 0;mutations['wrong_polynomial'] = d
    d = deepcopy(c);d['mod3_irreducible'] = 1;mutations['bool_integer_conflation'] = d
    for name, d in mutations.items():
        try:
            verify(d)
        except (ValueError, KeyError, TypeError):
            continue
        raise ValueError('accepted mutation: '+name)
    try:
        json.loads('{"x":1,"x":2}',object_pairs_hook=unique_keys)
    except ValueError:
        pass
    else:
        raise ValueError('accepted duplicate keys')
    process = subprocess.run([sys.executable,'-S','-O',str(Path(__file__).resolve())],
                             capture_output=True,text=True,timeout=15)
    require(process.returncode != 0 and 'requires non-optimized Python' in process.stderr,
            'optimized mode accepted')
    return sorted(mutations)+['duplicate_json','optimized_mode']


def main():
    if not __debug__:
        raise RuntimeError('Verification requires non-optimized Python')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--certificate',type=Path,default=ROOT/'certificates/radical_transfer_calibration.json')
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    c = json.loads(raw,object_pairs_hook=unique_keys)
    report = verify(c)
    report['certificate_sha256'] = hashlib.sha256(raw).hexdigest()
    report['rejection_tests'] = self_test(c) if args.self_test else []
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
