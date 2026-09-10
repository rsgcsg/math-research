"""Independent finite calibrations for T081's written local-field proof.

Standard library only. No search/producer imports and no density-tower claim
is inferred from the finite tests. The field used for actual finite geometry
is Q(phi,i), phi^2=phi+1, not the enormous fields in the external construction.
"""
from fractions import Fraction as Q
from itertools import combinations, product


ONE = (Q(1), Q(0), Q(0), Q(0))
ZERO = (Q(0),) * 4


def poly_remainder(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def finite_multiply(a, b, polynomial):
    answer = 0
    while b:
        if b & 1:
            answer ^= a
        a <<= 1
        b >>= 1
    return poly_remainder(answer, polynomial)


def finite_fields():
    # All monic potential proper factors are tested, not assumed irreducible.
    polynomials = (0b11, 0b111, 0b1011, 0b10011, 0b100101, 0b1000011)
    count = 0
    for polynomial in polynomials:
        degree = polynomial.bit_length() - 1
        for d in range(1, degree // 2 + 1):
            assert all(poly_remainder(polynomial, factor)
                       for factor in range(1 << d, 1 << (d + 1)))
        order = 1 << degree
        assert [a for a in range(order)
                if finite_multiply(a, a, polynomial) == 1] == [1]
        # The coefficient of 1 is an F2-linear functional taking 1 to 1.
        assert all((a & 1) != ((a ^ 1) & 1) for a in range(order))
        count += order
    return len(polynomials), count


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def multiply(a, b):
    """Exact arithmetic in basis 1, phi, i, i*phi, phi^2=phi+1."""
    result = [Q(0)] * 4
    for j, x in enumerate(a):
        for k, y in enumerate(b):
            imaginary_degree = (j // 2) + (k // 2)
            sign = -1 if imaginary_degree == 2 else 1
            imaginary = imaginary_degree % 2
            phi_degree = (j % 2) + (k % 2)
            if phi_degree < 2:
                result[2 * imaginary + phi_degree] += sign * x * y
            else:
                result[2 * imaginary] += sign * x * y
                result[2 * imaginary + 1] += sign * x * y
    return tuple(result)


def conjugate(a):
    return (a[0], a[1], -a[2], -a[3])


def norm(a):
    return multiply(a, conjugate(a))


def inverse(a):
    columns = [multiply(a, tuple(Q(int(k == j)) for k in range(4)))
               for j in range(4)]
    rows = [[columns[j][k] for j in range(4)] + [ONE[k]]
            for k in range(4)]
    for j in range(4):
        pivot = next(k for k in range(j, 4) if rows[k][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scalar = rows[j][j]
        rows[j] = [entry / scalar for entry in rows[j]]
        for k in range(4):
            if k != j:
                scalar = rows[k][j]
                rows[k] = [x - scalar * y for x, y in zip(rows[k], rows[j])]
    answer = tuple(row[-1] for row in rows)
    assert multiply(a, answer) == ONE
    return answer


def residue(a):
    # phi has irreducible polynomial X^2+X+1 over F2; i reduces to 1.
    assert all(x.denominator % 2 for x in a)
    bits = [x.numerator % 2 for x in a]
    return (bits[0] ^ bits[2]) | ((bits[1] ^ bits[3]) << 1)


def actual_geometry():
    units = set()
    for coefficients in product(range(-2, 3), repeat=4):
        a = tuple(map(Q, coefficients))
        if not residue(a):
            continue
        w = multiply(a, inverse(conjugate(a)))
        assert norm(w) == ONE
        assert residue(w) == 1
        units.add(w)
        if len(units) == 24:
            break
    assert len(units) == 24
    box = {tuple(map(Q, coefficients))
           for coefficients in product(range(3), repeat=4)}
    points = sorted(box | units | {add(ONE, w) for w in units})
    colors = [residue(a) & 1 for a in points]
    edges = 0
    for j, k in combinations(range(len(points)), 2):
        if norm(subtract(points[j], points[k])) == ONE:
            assert colors[j] != colors[k]
            edges += 1
    # Direct nonintegral-coset edge calibration; no global coordinate formula
    # is being asserted for arbitrary elements of the valuation ring.
    coset_edges = 0
    for depth in range(1, 5):
        representative = (Q(1, 2 ** depth), Q(0), Q(0), Q(0))
        for w in units:
            other = add(representative, w)
            assert norm(subtract(other, representative)) == ONE
            assert (residue(subtract(other, representative)) & 1) == 1
            coset_edges += 1
    return len(points), len(points) * (len(points) - 1) // 2, edges, coset_edges


def local_witnesses():
    # (i-1)^2 + 2(i-1) + 2 = 0; Eisenstein over every unramified dyadic field.
    imaginary = (Q(0), Q(0), Q(1), Q(0))
    pi = subtract(imaginary, ONE)
    assert add(add(multiply(pi, pi), add(pi, pi)), add(ONE, ONE)) == ZERO
    assert 2 % 2 == 0 and 2 % 4 != 0
    # Sawin's field contains sqrt(-21). Both exact norm and the two split
    # residues are checked; the pole itself follows from the written proof.
    assert Q(10, 11) ** 2 + 21 * Q(1, 11) ** 2 == 1
    roots = [r for r in range(11) if (r * r + 21) % 11 == 0]
    assert roots == [1, 10]
    assert sorted((10 + r) % 11 for r in roots) == [0, 9]
    lifts = [r for r in range(121) if (r * r + 21) % 121 == 0]
    assert lifts == [10, 111]
    assert (10 + 10) % 11 != 0 and (10 + 111) % 121 == 0
    # A second exact unit witnesses the dyadic failure after adjoining sqrt3:
    # (1+i*sqrt15)/4 has norm1 and sqrt(-15) has dyadic split branches.
    assert Q(1, 4) ** 2 + 15 * Q(1, 4) ** 2 == 1
    for depth in range(3, 9):
        modulus = 2 ** depth
        assert any((r * r + 15) % modulus == 0 and r % 4 == 1
                   for r in range(modulus))


def verify():
    if not __debug__:
        raise RuntimeError('Do not disable assertions in a mathematical checker.')
    fields, residues = finite_fields()
    local_witnesses()
    points, pairs, edges, coset_edges = actual_geometry()
    assert (fields, residues, points, pairs, edges, coset_edges) == (6, 126, 129, 8256, 180, 96)
    print('T081 calibration: %d finite fields, %d residues; '
          '%d points, %d actual pairs, %d induced unit edges; '
          '%d nonintegral-coset edges; dyadic polynomial and split-prime units OK.'
          % (fields, residues, points, pairs, edges, coset_edges))
    print('Infinite coloring and external density corollary rely on the written proof, '
          'not on these finite calibrations.')


if __name__ == '__main__':
    verify()
