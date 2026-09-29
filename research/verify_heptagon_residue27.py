"""Independent finite graph replay; SAT UNKNOWN records prove nothing.

Multiplication uses cyclic length-seven convolution, followed by quotienting
the all-ones vector. No producer or third-party dependency is imported.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json


def decode(n):
    return tuple(n//3**j % 3 for j in range(6))


def encode(a):
    return sum(x*3**j for j, x in enumerate(a))


VALUES = [decode(n) for n in range(729)]


def multiply(a, b):
    coeffs = [0]*7
    for i, x in enumerate(VALUES[a]):
        for j, y in enumerate(VALUES[b]):
            coeffs[(i+j) % 7] += x*y
    return encode(tuple((x-coeffs[6]) % 3 for x in coeffs[:6]))


def power(a, n):
    out = 1
    for _ in range(n):
        out = multiply(out, a)
    return out


def add(a, b):
    return encode(tuple((x+y) % 3 for x, y in zip(VALUES[a], VALUES[b])))


def verify(data):
    assert data['field']['characteristic'] == 3 and data['field']['degree'] == 6
    assert data['field']['size'] == 729
    assert [pow(3, j, 7) for j in range(1,7)] == [3,2,6,4,5,1]
    # Independent irreducibility calibration: every nonzero element satisfies
    # x^728=1 (fast binary exponent below), in this 729-element quotient.
    def fast_power(a, n):
        out = 1
        while n:
            if n % 2:
                out = multiply(out, a)
            a = multiply(a, a)
            n //= 2
        return out
    assert all(fast_power(a, 728) == 1 for a in range(1,729))
    directions = [a for a in range(1,729) if multiply(a, fast_power(a,27)) == 1]
    assert len(directions) == 28
    roots2 = [a for a in range(729) if multiply(a,a) == 2]
    assert len(roots2) == 2
    assert all(fast_power(a,27) != a and add(fast_power(a,27),a) == 0 for a in roots2)
    edges = sorted((a,b) for a in range(729) for d in directions
                   for b in [add(a,d)] if a < b)
    assert len(set(edges)) == len(edges) == 10206
    degrees = Counter(v for edge in edges for v in edge)
    assert set(degrees.values()) == {28}
    digest = sha256('\n'.join(f'{u},{v}' for u,v in edges).encode()).hexdigest()
    summary = data['exact_graph_checks']
    assert summary['vertices'] == 729 and summary['edges'] == 10206
    assert summary['directions_d28_eq_1'] == summary['regular_degree'] == 28
    assert summary['sorted_edge_list_sha256'] == digest
    assert all(pair in edges for pair in ((0,1),(0,2),(1,2)))
    # Every independent character is determined by six F3 coordinates.
    # Pairing opposite directions makes its eigenvalue a rational integer.
    spectrum = Counter()
    for a in VALUES:
        zeros = sum(sum(x*y for x,y in zip(a, VALUES[d])) % 3 == 0 for d in directions)
        assert zeros % 2 == 0
        spectrum[(3*zeros-28)//2] += 1
    assert sum(spectrum.values()) == 729
    assert sum(v*n for v,n in spectrum.items()) == 0
    assert sum(v*v*n for v,n in spectrum.items()) == 729*28
    rows = data['sat'] + data.get('symmetry_normalized_sat', [])
    assert len(rows) == 4 and [row['colors'] for row in rows] == [5,6,5,6]
    assert all(row['status'] == 'UNKNOWN' and row['coloring'] is None for row in rows)
    return dict(vertices=729, directions=28, edges=len(edges), edge_sha256=digest,
                spectrum=sorted(spectrum.items()), unknown_queries=4,
                square_roots_of_2=roots2, conjugation_swaps_roots=True,
                scope='Exact residue graph only; recorded solver counters are provenance, not independently reproduced proof')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions required')
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'certificates/heptagon_residue27_probe.json').read_text())
    print(json.dumps(verify(data), sort_keys=True))
