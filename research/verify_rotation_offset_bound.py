"""Exact finite-place bounds for every nonzero-point return in the u orbit.

Standard library only, apart from existing independent geometry/field checks.
This does not enumerate the actual cross-layer edges, invoke SAT, or certify a
coloring. Zero is a single global vertex, not a finite-offset orbit.
"""

from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

from verify_quintic_core_probe import conjugate_twice, digest
from verify_quintic_tau_union import verify as geometry


SOURCE_HASHES = {
    'certificates/quintic_tau_union.json':
        '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1',
    'research/cofinal_residue16_verify.py':
        '1a3ff6b8f52cff3f2549eb4ffe09a0746c6ad33c85ef7fce562ce136dfb8ff0c',
}
POINT_SHA = '6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1'
ROWS_SHA = '1b2d008b0799760e15f6f87651cb0c0ca073f9866e7c602c2f3b2341e5204d51'
HIST_V0 = [(-2, 1970), (-1, 580), (0, 5696), (1, 1408),
           (2, 348), (3, 66), (4, 8)]
HIST_V3 = [(0, 6986), (1, 1348), (2, 1318), (3, 356), (4, 8), (5, 60)]
HIST_DIFF = [(-4, 8), (-3, 36), (-2, 128), (-1, 548), (0, 6026),
             (1, 838), (2, 1128), (3, 36), (4, 1328)]
JOINT_HIST = [(-2, 0, 1000), (-2, 2, 970), (-1, 0, 290), (-1, 3, 290),
              (0, 0, 4976), (0, 1, 548), (0, 2, 128), (0, 3, 36),
              (0, 4, 8), (1, 0, 548), (1, 1, 800), (1, 5, 60),
              (2, 0, 128), (2, 2, 220), (3, 0, 36), (3, 3, 30), (4, 0, 8)]


def verify(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')
    root = Path(root)
    for name, expected in SOURCE_HASHES.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected
    report, context = geometry(root, geometry_context=True)
    actual_geometry = report['geometry']
    assert actual_geometry['point_sha256'] == POINT_SHA
    assert actual_geometry['vertices'] == 10077
    assert actual_geometry['induced_edges'] == 49858
    points = context['points']
    ring = context['ring']
    field_mul, coordinates = ring['mul'], ring['coordinates']
    field_one = (Q(1),) + (Q(0),) * 31
    field_zero = (Q(0),) * 32
    field_eta = (Q(0),) * 16 + field_one[:16]
    field_z = tuple(-Q(1, 2) if i == 0 else -Q(1, 6) if i == 9 else Q(0)
                    for i in range(32))
    field_nu = tuple(Q(5, 6) if i == 0 else Q(1, 6) if i == 10 else Q(0)
                     for i in range(32))

    def conjugate(p):
        return tuple(Q(x) / 2 for x in conjugate_twice(p))

    # Work in the unramified degree-four algebra over Z/256Z. Its reduction
    # T^4+T+1 is irreducible over F2 (no roots and not (T^2+T+1)^2).
    modulus = 256
    one = (1, 0, 0, 0)
    t = (0, 1, 0, 0)

    def mul(a, b):
        w = [0] * 7
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                w[i+j] += x*y
        for i in range(6, 3, -1):
            w[i-4] -= w[i]
            w[i-3] -= w[i]
        return tuple(x % modulus for x in w[:4])

    def power(a, n):
        result = one
        for _ in range(n):
            result = mul(result, a)
        return result

    def evaluate(poly, value):
        result = (0, 0, 0, 0)
        for coefficient in reversed(poly):
            result = mul(result, value)
            result = ((result[0] + coefficient) % modulus,) + result[1:]
        return result

    def lift(bits, polynomial):
        value = tuple((bits >> i) & 1 for i in range(4))
        assert all(x % 2 == 0 for x in evaluate(polynomial, value))
        derivative = [i * polynomial[i] for i in range(1, len(polynomial))]
        assert any(x % 2 for x in evaluate(derivative, value))
        for exponent in range(1, 8):
            step = 1 << exponent
            good = []
            for mask in range(16):
                trial = tuple(x + step * ((mask >> i) & 1)
                              for i, x in enumerate(value))
                if all(x % (2*step) == 0 for x in evaluate(polynomial, trial)):
                    good.append(trial)
            assert len(good) == 1
            value = good[0]
        assert not any(evaluate(polynomial, value))
        return value

    eta = lift(8, [1, 1, 1, 1, 1])
    z = {b: lift(b, [pow(3, -1, modulus), 1, 1]) for b in (6, 7)}
    nu = {b: lift(b, [1, -5*pow(3, -1, modulus), 1]) for b in (6, 7)}
    bases = {
        j: [mul(power(eta, e), mul(power(z[b], f), power(nu[b], g)))
            for g in range(2) for f in range(2) for e in range(4)]
        for j, b in ((0, 6), (3, 7))
    }

    def image(coefficients, j):
        assert all(x.denominator & 1 for x in coefficients)
        residues = [x.numerator * pow(x.denominator, -1, modulus) % modulus
                    for x in coefficients]
        return tuple(sum(x*b[t] for x, b in zip(residues, bases[j])) % modulus
                     for t in range(4))

    def residue_valuation(value):
        assert any(value), 'Unresolved zero residue must not get a finite valuation'
        result = min((x & -x).bit_length()-1 for x in value if x)
        assert result < 8
        return result

    # Frobenius squared is NOT the fourth-power operation modulo 256.
    # Lift the conjugate root of T^4+T+1, then substitute it into coefficients.
    frobenius_t = lift(3, [1, 1, 0, 0, 1])
    frobenius = lambda value: evaluate(value, frobenius_t)
    assert frobenius(frobenius_t) == t
    assert all(frobenius(frobenius(tuple(int(i == j) for i in range(4))))
               == tuple(int(i == j) for i in range(4)) for j in range(4))
    field_powers = [field_one]
    for _ in range(3):
        field_powers.append(field_mul(field_eta, field_powers[-1]))
    field_basis = field_powers + [field_mul(field_z, p) for p in field_powers]
    field_basis += [field_mul(field_nu, p) for p in field_basis[:]]
    for j, p in enumerate(field_basis):
        assert coordinates(p) == [Q(i == j) for i in range(16)]
        assert image(coordinates(conjugate(p)), 0) == frobenius(bases[3][j])
        assert image(coordinates(conjugate(p)), 3) == frobenius(bases[0][j])
    # By linearity this checks conjugation on every integral coefficient
    # combination. Frobenius is invertible, preserving all 2-adic orders <8.

    u = tuple({0: Q(1, 8), 4: -Q(3, 8), 9: -Q(1, 8),
               13: -Q(1, 8)}.get(i, Q(0)) for i in range(32))
    h = tuple(a+b for a, b in zip(field_eta, conjugate(field_eta)))
    h_plus_one = tuple(a+b for a, b in zip(h, field_one))
    formula_u = tuple((a+3*b)/2 for a, b in
                      zip(field_one, field_mul(h_plus_one, field_z)))
    assert u == formula_u
    assert field_mul(u, conjugate(u)) == field_one
    two_u = coordinates(tuple(2*x for x in u))
    u_valuations = [residue_valuation(image(two_u, j))-1 for j in (0, 3)]
    assert u_valuations == [-1, 1]
    two_bar_u = coordinates(tuple(2*x for x in conjugate(u)))
    assert [residue_valuation(image(two_bar_u, j))-1 for j in (0, 3)] == [1, -1]

    rows, zero_indices, seen = [], [], {}
    for i, p in enumerate(points):
        if p == field_zero:
            zero_indices.append(i)
            continue
        coefficients = [4*x for x in coordinates(p)]
        images = [image(coefficients, j) for j in (0, 3)]
        values = [residue_valuation(value)-2 for value in images]
        assert all(residue_valuation(frobenius(value)) == value_order + 2
                   for value, value_order in zip(images, values))
        rows.append([i, *values])
        seen[i] = (values, images)
    assert zero_indices == [4641]
    assert len(rows) == 10076
    assert digest(rows) == ROWS_SHA
    x = [row[1] for row in rows]
    y = [row[2] for row in rows]
    delta = [b-a for a, b in zip(x, y)]
    assert sorted(Counter(x).items()) == HIST_V0
    assert sorted(Counter(y).items()) == HIST_V3
    assert sorted(Counter(delta).items()) == HIST_DIFF
    joint = [(a, b, count) for (a, b), count in sorted(Counter(zip(x, y)).items())]
    assert joint == JOINT_HIST
    terms = [max(delta)-min(delta), max(x)-min(x), max(y)-min(y), max(x)+max(y)]
    assert terms == [8, 6, 5, 9]
    # Only 17 valuation types, not 10076^2 exact norm calculations. Check
    # the derived one-sided inequality for every pair of realized types.
    for xp, yp, _ in joint:
        for xq, yq, _ in joint:
            a, b = yp+xq, xp+yq
            lower_c = min(xp+yp, xq+yq, 0)
            assert a-min(b, lower_c) <= 9
            assert b-min(a, lower_c) <= 9
            assert abs(xp-xq) <= 6
    extrema = {}
    for component, values in ((0, x), (3, y)):
        position = 0 if component == 0 else 1
        for label, target in (('min', min(values)), ('max', max(values))):
            i = next(i for i, (vs, _) in seen.items() if vs[position] == target)
            extrema[f'v{component}_{label}'] = dict(
                index=i, valuation=target, four_p_mod256=list(seen[i][1][position]))
    return dict(status='PASS', source_sha256=SOURCE_HASHES, geometry=actual_geometry,
                zero_indices=zero_indices, nonzero_points=len(rows), modulus=modulus,
                nonzero_residue_checks=2*len(rows), unresolved_residues=0,
                conjugation_basis_checks=2*len(field_basis),
                u_valuations_v0_v3=u_valuations,
                hist_v0=HIST_V0, hist_v3=HIST_V3, hist_difference=HIST_DIFF,
                joint_histogram=joint, bound_terms=terms,
                nonzero_unit_offset_absolute_bound=9,
                nonzero_equality_offset_absolute_bound=6,
                valuation_rows_sha256=ROWS_SHA, extrema=extrema,
                scope='Necessary complete offset bounds, including eta saturation; '
                      'origin handled separately; no offset edge table or coloring certificate')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
