"""Independent dyadic order / HG(16) audit; no solver or producer imports."""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import json
from verify_quintic_residue5_ring import verify as checked_source
from verify_quintic_core_probe import conjugate_twice


def verify(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use -O.')

    def times(a, b):
        out = 0
        while b:
            if b & 1:
                out ^= a
            a <<= 1
            b >>= 1
            if a & 16:
                a ^= 19  # T^4+T+1
        return out

    def power(a, n):
        out = 1
        while n:
            if n & 1:
                out = times(out, a)
            a = times(a, a)
            n >>= 1
        return out

    assert all(power(a, 15) == 1 for a in range(1, 16))
    assert [a for a in range(16) if times(a, a)^a^1 == 0] == [6, 7]
    assert power(8, 5) == 1 and 8 != 1
    points = list(product(range(16), repeat=2))
    edges = [(i, j) for i, j in combinations(range(256), 2)
             if times(points[i][0]^points[j][0], points[i][1]^points[j][1]) == 1]
    assert len(edges) == 1920

    def color(p):
        packed = p[0] | (p[1] << 4)
        return ((packed & 17).bit_count() & 1) + 2*((packed & 143).bit_count() & 1)

    assert all(color(points[i]) != color(points[j]) for i, j in edges)
    clique = [(0, 0), (1, 1), (6, 7), (7, 6)]
    assert all(times(a^c, b^d) == 1 for (a, b), (c, d) in combinations(clique, 2))
    unit_codes = [a | (b << 4) for a, b in points if times(a, b) == 1]
    linear_pairs = [(a, b) for a, b in combinations(range(1, 256), 2)
                    if all(((a & d).bit_count() & 1) or ((b & d).bit_count() & 1)
                           for d in unit_codes)]
    assert len(linear_pairs) == 240 and (17, 143) in linear_pairs

    _, ctx = checked_source(root, geometry_context=True)
    mul, source_coords = ctx['mul'], ctx['coordinates']
    coordinates_cache = {}
    def coords(p):
        if p not in coordinates_cache:
            coordinates_cache[p] = source_coords(p)
        return coordinates_cache[p]
    one = (Q(1),)+(Q(0),)*31
    zero = (Q(0),)*32
    eta = (Q(0),)*16+one[:16]
    z = tuple(-Q(1, 2) if i == 0 else -Q(1, 6) if i == 9 else Q(0) for i in range(32))
    nu = tuple(Q(5, 6) if i == 0 else Q(1, 6) if i == 10 else Q(0) for i in range(32))
    eta_powers = [one]
    for _ in range(3):
        eta_powers.append(mul(eta, eta_powers[-1]))
    basis = eta_powers+[mul(z, p) for p in eta_powers]
    basis += [mul(nu, p) for p in basis[:]]
    basis_images = []
    for j in range(16):
        c, rem = divmod(j, 8)
        b, e = divmod(rem, 4)
        basis_images.append(tuple(times(power(8, e), times(power(zz, b), power(vv, c)))
                                  for zz, vv in ((6, 6), (6, 7), (7, 6), (7, 7))))
    rank_rows = {}
    for image in basis_images:
        packed = sum(v << (4*i) for i, v in enumerate(image))
        while packed:
            pivot = packed.bit_length()-1
            if pivot not in rank_rows:
                rank_rows[pivot] = packed
                break
            packed ^= rank_rows[pivot]
    assert len(rank_rows) == 16

    def residue(p):
        coefficients = coords(p)
        assert all(c.denominator & 1 for c in coefficients)
        out = [0]*4
        for c, image in zip(coefficients, basis_images):
            if c.numerator & 1:
                out = [x^y for x, y in zip(out, image)]
        return tuple(out)

    traces = [Q(4 if e == 0 else -1)*Q(2 if b == 0 else -1)*Q(2 if c == 0 else 5, 1 if c == 0 else 3)
              for c in range(2) for b in range(2) for e in range(4)]
    trace_matrix = []
    for i, a in enumerate(basis):
        row = []
        for j, b in enumerate(basis):
            ab = mul(a, b)
            assert residue(ab) == tuple(times(x, y) for x, y in zip(basis_images[i], basis_images[j]))
            row.append(sum(c*t for c, t in zip(coords(ab), traces)))
        trace_matrix.append(row)
        bar = tuple(Q(x)/2 for x in conjugate_twice(a))
        image = basis_images[i]
        assert residue(bar) == tuple(power(image[j], 4) for j in (3, 2, 1, 0))
    matrix = [row[:] for row in trace_matrix]
    determinant = Q(1)
    for i in range(16):
        pivot = next(j for j in range(i, 16) if matrix[j][i])
        if pivot != i:
            matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
            determinant = -determinant
        scale = matrix[i][i]
        determinant *= scale
        for j in range(i+1, 16):
            factor = matrix[j][i]/scale
            matrix[j] = [a-factor*b for a, b in zip(matrix[j], matrix[i])]
    assert determinant == Q(5**12 * 11**8, 3**24)

    def add(a, b):
        return tuple(x+y for x, y in zip(a, b))

    def subtract(a, b):
        return tuple(x-y for x, y in zip(a, b))

    def norm(p):
        return mul(p, tuple(Q(x)/2 for x in conjugate_twice(p)))

    def conjugate(p):
        return tuple(Q(x)/2 for x in conjugate_twice(p))

    def scale(q, p):
        return tuple(q*x for x in p)

    def inverse(p):
        columns = [coords(mul(p, b)) for b in basis]
        matrix = [[columns[j][i] for j in range(16)]+[Q(i == 0)] for i in range(16)]
        for i in range(16):
            pivot = next(j for j in range(i, 16) if matrix[j][i])
            matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
            matrix[i] = [a/matrix[i][i] for a in matrix[i]]
            for j in range(16):
                if j != i:
                    factor = matrix[j][i]
                    matrix[j] = [a-factor*b for a, b in zip(matrix[j], matrix[i])]
        answer = tuple(sum(matrix[j][-1]*basis[j][i] for j in range(16)) for i in range(32))
        assert mul(p, answer) == one
        return answer

    a = tuple(-x-3*y for x, y in zip(one, z))
    tip = add(one, a)
    spindle = [zero, one, a, tip, nu, mul(nu, a), mul(nu, tip)]
    assert len(set(spindle)) == 7
    spindle_edges = [(i, j) for i, j in combinations(range(7), 2)
                     if norm(subtract(spindle[i], spindle[j])) == one]
    assert len(spindle_edges) == 11
    spindle_word = []
    for p in spindle:
        r = residue(p)
        spindle_word.append(color((r[0], power(r[3], 4))))
    assert all(spindle_word[i] != spindle_word[j] for i, j in spindle_edges)
    assert not any(all(word[i] != word[j] for i, j in spindle_edges)
                   for word in product(range(3), repeat=7))

    def depth(p):
        return max((c.denominator & -c.denominator).bit_length()-1 for c in coords(p))

    X = ctx['points']
    Y = sorted(set(X) | {mul(ctx['tau'], p) for p in X})
    membership = []
    expected = {'P': {0: 374, 1: 15, 2: 120},
                'X': {0: 3734, 1: 150, 2: 1200},
                'Y': {0: 7407, 1: 300, 2: 2370}}
    for name, ps in (('P', ctx['blocks'][0]), ('X', X), ('Y', Y)):
        depths = list(map(depth, ps))
        histogram = dict(sorted(Counter(depths).items()))
        assert histogram == expected[name]
        first = {d: next(i for i, value in enumerate(depths) if value == d) for d in histogram}
        membership.append(dict(name=name, vertices=len(ps), depth_histogram=histogram,
                               first_index_by_depth=first))
    P = ctx['blocks'][0]
    assert P[0] == zero and P[153] == one
    scaled_parts_images = [residue(tuple(4*x for x in p)) for p in P]
    valuation_witnesses = []
    for j in range(4):
        index = next((i for i, image in enumerate(scaled_parts_images) if image[j]), None)
        valuation_witnesses.append(dict(component=j, parts_index=index,
                                        residue_of_four_p=None if index is None else scaled_parts_images[index][j],
                                        valuation_information='at_least_minus_one' if index is None else 'exactly_minus_two'))
    # Independently lift the four residue components to the unramified ring
    # (Z/8Z)[T]/(T^4+T+1). This resolves valuations -2,-1,0 of P exactly.
    modulus = 8
    one8 = (1, 0, 0, 0)
    def mult8(a, b):
        work = [0]*7
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                work[i+j] += x*y
        for i in range(6, 3, -1):
            work[i-4] -= work[i]
            work[i-3] -= work[i]
        return tuple(x % modulus for x in work[:4])
    def pow8(a, n):
        out = one8
        for _ in range(n):
            out = mult8(out, a)
        return out
    def eval8(poly, x):
        out = (0, 0, 0, 0)
        for a in reversed(poly):
            out = mult8(out, x)
            out = ((out[0]+a) % modulus,)+out[1:]
        return out
    def lift8(bits, polynomial):
        value = tuple((bits >> i) & 1 for i in range(4))
        assert all(v % 2 == 0 for v in eval8(polynomial, value))
        for step in (2, 4):
            candidates = [tuple(v+step*((mask >> i) & 1) for i, v in enumerate(value))
                          for mask in range(16)]
            candidates = [v for v in candidates if all(t % (2*step) == 0 for t in eval8(polynomial, v))]
            assert len(candidates) == 1
            value = candidates[0]
        return value
    beta8 = lift8(8, [1, 1, 1, 1, 1])
    z8 = {a: lift8(a, [pow(3, -1, modulus), 1, 1]) for a in (6, 7)}
    nu8 = {a: lift8(a, [1, -5*pow(3, -1, modulus), 1]) for a in (6, 7)}
    basis8 = []
    for zz, vv in ((6, 6), (6, 7), (7, 6), (7, 7)):
        basis8.append([mult8(pow8(beta8, e), mult8(pow8(z8[zz], b), pow8(nu8[vv], c)))
                       for c in range(2) for b in range(2) for e in range(4)])
    def residue8(p, component):
        coefficients = coords(p)
        assert all(c.denominator & 1 for c in coefficients)
        return tuple(sum(c.numerator*pow(c.denominator, -1, modulus)*v[j]
                         for c, v in zip(coefficients, basis8[component])) % modulus for j in range(4))
    local_minima, local_minimum_witnesses = [], []
    for j in range(4):
        valuations = []
        for p in P:
            value = residue8(tuple(4*x for x in p), j)
            valuation = min(((x & -x).bit_length()-1 for x in value if x), default=3)-2
            valuations.append(valuation)
        minimum = min(valuations)
        index = valuations.index(minimum)
        assert minimum < 1  # so the nonzero mod8 witness gives an exact value
        local_minima.append(minimum)
        local_minimum_witnesses.append(dict(component=j, parts_index=index, valuation=minimum,
                                            residue_of_four_p=list(residue8(tuple(4*x for x in P[index]), j))))
    assert local_minima == [-2, -2, 0, 0]
    h = add(eta, conjugate(eta))
    assert add(mul(h, h), h) == one
    u = scale(Q(1, 2), add(one, scale(3, mul(add(h, one), z))))
    r = conjugate(u)
    assert norm(u) == one
    assert residue(scale(2, u))[:2] == (6, 6)
    assert residue(scale(2, u))[2:] == (0, 0)
    rotation_membership = []
    for name, ps in (('P', P), ('Y', Y)):
        rotated = [mul(r, p) for p in ps]
        histogram = dict(sorted(Counter(map(depth, rotated)).items()))
        assert max(histogram) == 1
        rotation_membership.append(dict(name=name, vertices=len(ps), depth_histogram=histogram))

    # A small exact counterexample to preserving this specified four-color
    # marginal on R2 and using a fifth color to extend to (1/2)R2.
    t0 = add(mul(eta, z), mul(conjugate(eta), conjugate(z)))
    assert conjugate(t0) == t0 and conjugate(h) == h
    neighbors = []
    for t in (zero, h, t0, add(h, t0)):
        denominator = add(one, scale(2, mul(t, conjugate(z))))
        y = mul(mul(scale(2, u), mul(t, subtract(conjugate(z), z))), inverse(denominator))
        residue(y)
        assert norm(subtract(u, y)) == one
        neighbors.append(y)
    def ring_color(p):
        value = residue(p)
        return color((value[0], power(value[3], 4)))
    assert set(map(ring_color, neighbors)) == set(range(4))
    second_neighbors = [add(one, p) for p in neighbors]
    assert set(map(ring_color, second_neighbors)) == set(range(4))
    centers = [u, add(u, one)]
    assert all(depth(p) == 1 for p in centers)
    assert norm(subtract(*centers)) == one
    gadget = list(dict.fromkeys(neighbors+second_neighbors+centers))
    boundary = {gadget.index(p): ring_color(p) for p in neighbors+second_neighbors}
    center_ids = [gadget.index(p) for p in centers]
    gadget_edges = [(i, j) for i, j in combinations(range(len(gadget)), 2)
                    if norm(subtract(gadget[i], gadget[j])) == one]
    for a, b in product(range(5), repeat=2):
        word = dict(boundary)
        word.update(zip(center_ids, (a, b)))
        assert any(word[i] == word[j] for i, j in gadget_edges)
    assert len(gadget) == 10 and len(gadget_edges) == 13
    free_word = (0, 0, 0, 0, 1, 1, 1, 1, 1, 0)
    assert all(free_word[i] != free_word[j] for i, j in gadget_edges)
    assert depth(ctx['tau']) == 0
    return dict(status='PASS', target='HG(F16)', target_chromatic=4,
                vertices=256, pairs=32640, edges=len(edges), unit_directions=len(unit_codes),
                field_modulus_bits=19, linear_color_masks=[17, 143], proper_linear_pairs=240,
                quotient_algebra='F16^4', quotient_binary_rank=16,
                paired_components=[0, 3], conjugation_power=4,
                basis_products_checked=256, discriminant=str(determinant),
                spindle_edges=spindle_edges, spindle_four_word=spindle_word,
                membership=membership, tau_dyadic_integral=True,
                parts_valuation_witnesses=valuation_witnesses,
                parts_prime_valuation_minima=local_minima,
                parts_prime_minimum_witnesses=local_minimum_witnesses,
                balancing_rotation_formula='conjugate((1+3*(eta+eta^-1+1)*z)/2)',
                balancing_rotation_coefficients=list(map(str, coords(r))),
                balancing_rotation_membership=rotation_membership,
                parts_isometry_minimum_dyadic_depth=1,
                fixed_four_palette_extension_gadget=dict(vertices=len(gadget), edges=gadget_edges,
                     neighbors_four_colors=list(map(ring_color, neighbors)),
                     second_neighbors_four_colors=list(map(ring_color, second_neighbors)),
                     boundary_colors=boundary, center_ids=center_ids,
                     rejected_center_assignments=25, free_two_word=list(free_word),
                     coordinates=[list(map(str, coords(p))) for p in gadget]),
                scope='The entire 2-integral order has chromatic number 4. Original-frame P/X/Y have depth 2, while an exact rotation puts P/Y in depth 1. Only the specified four-color marginal extension is excluded; no five-color law on either layer or whole field is certified.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = verify(root)
    if args.write_report:
        (root/'certificates/cofinal_residue16_audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
