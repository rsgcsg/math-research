"""Independent exact finite checks for the residue-29 literature audit.

No SAT import.  These checks refute a printed spectral constant and calibrate
restricted equivariance, not ordinary six-colorability of H29 or the plane.
"""
from itertools import combinations
from math import lcm
import json


def graph(p):
    points = [(a, b) for a in range(p) for b in range(p)]
    edges = [(i, j) for i, j in combinations(range(p*p), 2)
             if sum((x-y)**2 for x, y in zip(points[i], points[j])) % p == 1]
    return points, edges


def partitions(n, smallest=1):
    if not n:
        yield ()
    for first in range(smallest, n+1):
        for rest in partitions(n-first, first):
            yield (first,)+rest


def verify():
    if not __debug__:
        raise RuntimeError('Assertions are required; -O is not supported.')
    points, edges = graph(5)
    directions = [points[j] for i, j in edges if i == 0]
    assert directions == [(0, 1), (0, 4), (1, 0), (4, 0)]
    assert len(edges) == 50
    # Eigencharacter zeta^(2a+2b), zeta^5=1, zeta!=1.  The resulting
    # eigenvalue is 2*zeta^2+2*zeta^3.  Reduction below verifies its exact
    # equation X^2+2X-4=0, without floating-point trigonometry.
    def reduce_poly(coefficients):
        c = list(coefficients)+[0]*max(0, 5-len(coefficients))
        for degree in range(len(c)-1, 3, -1):
            value = c[degree]
            for j in range(5):
                c[degree-4+j] -= value
        return c[:4]
    eigenvalue = [0, 0, 2, 2]
    square = [0]*7
    for i, a in enumerate(eigenvalue):
        for j, b in enumerate(eigenvalue):
            square[i+j] += a*b
    for i, a in enumerate(eigenvalue):
        square[i] += 2*a
    square[0] -= 4
    assert reduce_poly(square) == [0, 0, 0, 0]
    c5 = [0, 1, 0, 1, 2]
    word5 = [c5[(a+b) % 5] for a, b in points]
    assert all(word5[i] != word5[j] for i, j in edges)

    # Transcription of Vinh math/0510092v1, printed p.4, Table 1.
    rows = ['3123412', '2341231', '4123123', '2312341',
            '1234123', '3412312', '1231234']
    word7 = [int(c)-1 for row in rows for c in row]
    _, edges7 = graph(7)
    assert len(edges7) == 196
    assert all(word7[i] != word7[j] for i, j in edges7)
    # The erroneous 2006 lower bound is 1+8/sqrt(7)>4, because 64>9*7.
    assert 8*8 > 3*3*7

    p = 29
    def multiply(x, y):
        return ((x[0]*y[0]-3*x[1]*y[1]) % p,
                (x[0]*y[1]+x[1]*y[0]) % p)
    def inverse(x):
        inv_norm = pow((x[0]*x[0]+3*x[1]*x[1]) % p, -1, p)
        return (x[0]*inv_norm % p, -x[1]*inv_norm % p)
    generator = (4, 13)
    rotations = []
    current = (1, 0)
    for _ in range(30):
        rotations.append(current)
        current = multiply(current, generator)
    assert current == (1, 0) and len(set(rotations)) == 30
    assert all((a*a+3*b*b) % p == 1 for a, b in rotations)
    edge_witnesses = []
    for g in rotations[1:]:
        x = inverse(((1-g[0]) % p, -g[1] % p))
        gx = multiply(g, x)
        assert ((x[0]-gx[0]) % p, (x[1]-gx[1]) % p) == (1, 0)
        edge_witnesses.append([list(g), list(x), list(gx)])
    minimum = next(n for n in range(1, 11)
                   if any(lcm(*part) == 30 for part in partitions(n)))
    assert minimum == 10
    return dict(status='EXACT_CALIBRATIONS_PASS',
                D5=dict(vertices=25, edges=50,
                        eigenvalue='-1-sqrt(5)', polynomial=[-4, 2, 1],
                        proper_three_word=word5),
                D7=dict(vertices=49, edges=196, proper_four_word=word7,
                        rejects='Vinh math/0606482v1 Theorem 1 printed p.2'),
                H29=dict(rotation_generator=list(generator),
                         rotation_order=30,
                         minimum_faithful_permutation_degree=10,
                         full_rotation_equivariant_color_lower_bound=11,
                         kernel_edge_witnesses=edge_witnesses),
                scope='No ordinary H29 or plane non-5/non-6 conclusion.')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
