"""T078 constructive residue coloring and dyadic finite probes.

Coordinates represent sum(a_j*z^j), z=exp(2*pi*i/7), j=0,...,5.
The written ramified-prime proof covers arbitrary rational coefficients.
The independent verifier does not import this producer.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json


def multiply(a, b):
    c = [0]*11
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i+j] += x*y
    for i in range(10, 5, -1):
        for j in range(6):
            c[i-6+j] -= c[i]
    return tuple(c[:6])


def power(k):
    return (-1,)*6 if k % 7 == 6 else tuple(int(j == k % 7) for j in range(6))


def conjugate(a):
    return tuple(sum(x*power(-j)[i] for j, x in enumerate(a)) for i in range(6))


def integral_part(a):
    """Subtract the canonical 7-primary fraction in Q/Z_(7)."""
    a = Fraction(a)
    prime_power, other = 1, a.denominator
    while other % 7 == 0:
        prime_power *= 7
        other //= 7
    representative = Fraction(a.numerator*pow(other, -1, prime_power) % prime_power, prime_power)
    return a-representative


def color(point):
    residue = sum(a.numerator*pow(a.denominator, -1, 7)
                  for a in map(integral_part, point)) % 7
    return (0, 1, 0, 1, 0, 1, 2)[residue]


def directions():
    v = (-1, 1, 1, 0, 1, 0)  # numerator of (-3+sqrt(-7))/4, denominator 2
    return sorted({tuple(s*x for x in multiply(a, power(k)))
                   for a in ((2, 0, 0, 0, 0, 0), v, conjugate(v))
                   for k in range(7) for s in (-1, 1)})


def box(width, ds):
    points = list(product(range(width), repeat=6))
    index = {p: i for i, p in enumerate(points)}
    edges = []
    for i, p in enumerate(points):
        for d in ds:
            j = index.get(tuple(a+b for a, b in zip(p, d)))
            if j is not None and i < j:
                edges.append((i, j))
    return points, sorted(edges)


def build():
    ds = directions()
    probes = []
    for width in (2, 3, 4, 5, 6):
        points, edges = box(width, ds)
        word = [color(tuple(Fraction(a, 2) for a in p)) for p in points]
        assert all(word[i] != word[j] for i, j in edges)
        probes.append(dict(width=width, vertices=len(points), edges=len(edges),
                           edge_sha256=hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest(),
                           word_sha256=hashlib.sha256(bytes(word)).hexdigest()))
    return dict(schema=1, theorem='T078', counterexample='C014',
                basis='1,z,z^2,z^3,z^4,z^5; Phi_7(z)=0',
                cycle_word=[0, 1, 0, 1, 0, 1, 2], denominator=2,
                direction_numerators=ds, probes=probes)


def search(width, budget):
    """Optional replay of E041's initial three-color SAT probe, not a checker."""
    from pysat.solvers import Solver
    points, edges = box(width, directions())
    clauses = [[3*i+c+1 for c in range(3)] for i in range(len(points))]
    clauses.extend([-3*i-c-1, -3*j-c-1] for i, j in edges for c in range(3))
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        return dict(width=width, vertices=len(points), edges=len(edges),
                    answer=answer, conflict_budget=budget, stats=solver.accum_stats(),
                    scope='Search only; build() supplies a separately checked formula')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--search-width', type=int)
    parser.add_argument('--budget', type=int, default=100000)
    args = parser.parse_args()
    if args.search_width is not None:
        print(json.dumps(search(args.search_width, args.budget)))
    else:
        result = build()
        path = Path(__file__).resolve().parents[1]/'certificates/cyclotomic_field_coloring.json'
        path.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result['probes'], indent=2))
