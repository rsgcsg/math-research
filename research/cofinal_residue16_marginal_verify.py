"""Independent exact audit for the universal mod-2 four-palette obstruction.

No SAT, production geometry, or other project verifier is imported.  The
eight-dimensional algebra is Q[E,Z]/(Phi_5(E), Z^2+Z+1/3).
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product


def verify():
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')

    def fm(a, b):
        out = 0
        while b:
            if b & 1:
                out ^= a
            a <<= 1
            b >>= 1
            if a & 16:
                a ^= 19
        return out

    def fp(a, n):
        out = 1
        for _ in range(n):
            out = fm(out, a)
        return out

    def tr(a):
        out = a ^ fp(a, 2) ^ fp(a, 4) ^ fp(a, 8)
        assert out in (0, 1)
        return out

    directions = [(a, fp(a, 14)) for a in range(1, 16)]
    spectrum = {(a, b): sum(1-2*tr(fm(a, x) ^ fm(b, y)) for x, y in directions)
                for a, b in product(range(16), repeat=2)}
    assert spectrum[(0, 0)] == 15
    assert max(v for k, v in spectrum.items() if k != (0, 0)) == 7
    assert min(spectrum.values()) == -5
    assert all(spectrum[(a, 0)] == spectrum[(0, a)] == -1 for a in range(1, 16))
    assert Counter(spectrum.values()) == {-5: 60, -1: 105, 3: 60, 7: 30, 15: 1}
    for ka, va in spectrum.items():
        for kb, vb in spectrum.items():
            assert va*vb >= -75
            assert (va*vb == -75) == ((ka == (0, 0) and vb == -5)
                                      or (kb == (0, 0) and va == -5))

    zero = (Q(0),)*8
    one = (Q(1),)+(Q(0),)*7
    eta = (Q(0), Q(1))+(Q(0),)*6
    z = (Q(0),)*4+(Q(1),)+(Q(0),)*3
    basis = [tuple(Q(i == j) for i in range(8)) for j in range(8)]

    def add(a, b):
        return tuple(x+y for x, y in zip(a, b))

    def scale(s, a):
        return tuple(s*x for x in a)

    def sub(a, b):
        return add(a, scale(-1, b))

    def mul(a, b):
        # Direct polynomial multiplication, then monic relation reductions.
        raw = [[Q(0)]*7 for _ in range(3)]
        for i, ai in enumerate(a):
            if ai:
                bi, ei = divmod(i, 4)
                for j, bj in enumerate(b):
                    if bj:
                        bjz, ej = divmod(j, 4)
                        raw[bi+bjz][ei+ej] += ai*bj
        for e in range(7):
            raw[0][e] -= raw[2][e]/3
            raw[1][e] -= raw[2][e]
        for bpower in range(2):
            for e in range(6, 3, -1):
                for k in range(4):
                    raw[bpower][e-4+k] -= raw[bpower][e]
                raw[bpower][e] = Q(0)
        return tuple(raw[bpower][e] for bpower in range(2) for e in range(4))

    eta_bar = scale(-1, tuple(Q(i < 4) for i in range(8)))
    z_bar = sub(scale(-1, one), z)
    eta_bar_powers = [one]
    for _ in range(3):
        eta_bar_powers.append(mul(eta_bar_powers[-1], eta_bar))
    bar_basis = eta_bar_powers + [mul(z_bar, a) for a in eta_bar_powers]

    def bar(a):
        out = zero
        for c, b in zip(a, bar_basis):
            out = add(out, scale(c, b))
        return out

    def norm(a):
        return mul(a, bar(a))

    def inv(a):
        columns = [mul(a, b) for b in basis]
        matrix = [[columns[j][i] for j in range(8)]+[Q(i == 0)] for i in range(8)]
        for i in range(8):
            p = next(j for j in range(i, 8) if matrix[j][i])
            matrix[i], matrix[p] = matrix[p], matrix[i]
            divisor = matrix[i][i]
            matrix[i] = [v/divisor for v in matrix[i]]
            for j in range(8):
                if j != i and matrix[j][i]:
                    factor = matrix[j][i]
                    matrix[j] = [x-factor*y for x, y in zip(matrix[j], matrix[i])]
        out = tuple(row[-1] for row in matrix)
        assert mul(a, out) == one
        return out

    def residue(a, zz):
        assert all(c.denominator & 1 for c in a)
        out = 0
        for i, c in enumerate(a):
            b, e = divmod(i, 4)
            if c.numerator & 1:
                out ^= fm(fp(8, e), fp(zz, b))
        return out

    def hg_image(a):
        return residue(a, 6), fp(residue(a, 7), 4)

    for a, b in product(basis, repeat=2):
        assert bar(bar(a)) == a
        assert bar(mul(a, b)) == mul(bar(a), bar(b))
        for zz in (6, 7):
            assert residue(mul(a, b), zz) == fm(residue(a, zz), residue(b, zz))
    assert mul(eta, eta_bar) == one
    assert add(add(mul(z, z), z), scale(Q(1, 3), one)) == zero
    h = add(eta, bar(eta))
    t0 = add(mul(eta, z), bar(mul(eta, z)))
    real_basis = [one, h, t0, mul(h, t0)]
    assert all(bar(t) == t for t in real_basis)
    ts = []
    for bits in product(range(2), repeat=4):
        t = zero
        for bit, b in zip(bits, real_basis):
            t = add(t, scale(bit, b))
        ts.append(t)
    assert {residue(t, 6) for t in ts} == set(range(16))
    u = scale(Q(1, 2), add(one, scale(3, mul(add(h, one), z))))
    assert norm(u) == one
    assert not all(c.denominator & 1 for c in u)
    assert all(c.denominator & 1 for c in scale(2, u))
    assert hg_image(scale(2, u)) == (6, 0)
    neighbors = []
    for t in ts:
        denominator = add(one, scale(2, mul(t, bar(z))))
        y = mul(mul(scale(2, u), mul(t, sub(bar(z), z))), inv(denominator))
        assert norm(sub(u, y)) == one
        assert all(c.denominator & 1 for c in y)
        neighbors.append(y)
    assert set(map(hg_image, neighbors)) == {(x, 0) for x in range(16)}
    shifted = [add(one, p) for p in neighbors]
    assert set(map(hg_image, shifted)) == {(x, 1) for x in range(16)}
    points = neighbors + shifted + [u, add(u, one)]
    assert len(set(points)) == 34
    edges = [(i, j) for i, j in combinations(range(34), 2) if norm(sub(points[i], points[j])) == one]
    expected = [(i, i+16) for i in range(16)]
    expected += [(i, 32) for i in range(16)]
    expected += [(i, 33) for i in range(16, 32)] + [(32, 33)]
    assert edges == sorted(expected)
    word = [0]*16+[1]*16+[1, 0]
    assert all(word[i] != word[j] for i, j in edges)
    return dict(status='PASS', spectrum=dict(sorted(Counter(spectrum.values()).items())),
                real_basis_residues=[residue(t, 6) for t in real_basis],
                vertices=34, actual_pairs_checked=561, actual_edges=49,
                free_two_word=''.join(map(str, word)),
                scope='Universal mod-2 four-color marginal obstruction, not a non-five-color graph.')


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), sort_keys=True, indent=2))
