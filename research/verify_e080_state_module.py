"""Exact 25-state module audit of one fixed E080 permutation certificate.

This checker does not certify the geometry or a coloring of a residue graph.
The E080 independent positive checker separately verifies the physical domains.
Here we reconstruct the supplied permutations and their finite action module.
"""

from pathlib import Path
import hashlib
import json
import math


SOURCE_SHA256 = '3b9b7f893bb2d0b31bfc72d645924858d84961b33b56706f40498251a5663b00'
IDENTITY = tuple(range(25))


def compose(left, right):
    return tuple(left[right[i]] for i in IDENTITY)


def inverse(permutation):
    return tuple(permutation.index(i) for i in IDENTITY)


def conjugate(operator, translation):
    return compose(operator, compose(translation, inverse(operator)))


def power(permutation, exponent):
    result = IDENTITY
    for _ in range(exponent):
        result = compose(permutation, result)
    return result


def order(permutation):
    seen, lengths = set(), []
    for i in IDENTITY:
        if i in seen:
            continue
        x, length = i, 0
        while x not in seen:
            seen.add(x)
            length += 1
            x = permutation[x]
        lengths.append(length)
    return math.lcm(*lengths)


def permutation(values, size):
    assert isinstance(values, list) and len(values) == size
    assert all(type(x) is int for x in values)
    assert sorted(values) == list(range(size))


def f4_multiply(a, b):
    polynomial = 0
    for i in range(2):
        for j in range(2):
            if (a >> i) & 1 and (b >> j) & 1:
                polynomial ^= 1 << (i + j)
    if polynomial & 4:
        polynomial ^= 7  # v^2 + v + 1 = 0.
    return polynomial


def verify(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    source = Path(root) / 'certificates/quintic_multiword_joint.json'
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    certificate = json.loads(raw)
    assert certificate['experiment'] == 'E080' and certificate['support'] == 5
    result = certificate['result']
    names = result['motions']
    assert names == ['tau', 'nu', 'eta', 'omega', 'bar', 'bridge',
                     'translation_one', 'translation_z', 'one_plus_eta_1',
                     'one_plus_eta_2', 'one_plus_eta_3', 'one_plus_eta_4', 'bridge_shift']
    assert len(result['word_permutations']) == len(result['color_permutations']) == 13
    operators = {}
    for name, sigma, palettes in zip(names, result['word_permutations'], result['color_permutations']):
        permutation(sigma, 5)
        assert isinstance(palettes, list) and len(palettes) == 5
        for palette in palettes:
            permutation(palette, 5)
        operators[name] = tuple(5 * sigma[a] + palettes[a][c]
                                for a in range(5) for c in range(5))
        assert sorted(operators[name]) == list(IDENTITY)

    eta, nu, bar = (operators[name] for name in ('eta', 'nu', 'bar'))
    one = operators['translation_one']
    assert order(eta) == 5 and order(nu) == 3 and order(bar) == 2
    assert operators['tau'] == nu
    assert operators['omega'] == inverse(nu)
    assert compose(eta, nu) == compose(nu, eta)
    for rotation in (eta, nu):
        assert conjugate(bar, rotation) == inverse(rotation)
    singer = compose(eta, nu)
    assert order(singer) == 15
    translations = []
    current = one
    for _ in range(15):
        translations.append(current)
        current = conjugate(singer, current)
    assert current == one and len(set(translations)) == 15
    assert all(power(p, 2) == IDENTITY for p in translations)
    assert all(compose(a, b) == compose(b, a) for a in translations for b in translations)

    group = {IDENTITY}
    independent = []
    for generator in translations:
        if generator not in group:
            independent.append(generator)
            group |= {compose(generator, h) for h in tuple(group)}
    assert len(group) == 256 and len(independent) == 8
    assert all(compose(a, b) in group for a in group for b in group)
    assert all(power(h, 2) == IDENTITY for h in group)
    for h in group:
        assert conjugate(nu, h) in group and conjugate(eta, h) in group
        # Addition in H is composition; these are module polynomial identities.
        ah = conjugate(nu, h)
        aah = conjugate(nu, ah)
        assert compose(h, compose(ah, aah)) == IDENTITY
        total, current = IDENTITY, h
        for _ in range(5):
            total = compose(total, current)
            current = conjugate(eta, current)
        assert total == IDENTITY

    # Evaluate the eight standard F2 basis monomials 1,e,e^2,e^3 and v times them.
    basis = []
    current = one
    for _ in range(4):
        basis.append(current)
        current = conjugate(eta, current)
    basis += [conjugate(nu, h) for h in basis[:]]
    images = []
    for bits in range(256):
        image = IDENTITY
        for i, h in enumerate(basis):
            if bits & (1 << i):
                image = compose(image, h)
        images.append(image)
    assert len(set(images)) == 256 and set(images) == group
    # Thus the cyclic module is F4[e]/Phi5(e), not merely a quotient of it.
    for a in range(256):
        for b in range(256):
            assert compose(images[a], images[b]) == images[a ^ b]

    # Phi5 factors over F4 into two distinct irreducible quadratics.
    v, vv = 2, 3
    assert f4_multiply(v, v) == vv
    assert v ^ vv == 1 and f4_multiply(v, vv) == 1
    first, second = [1, v, 1], [1, vv, 1]
    product_coefficients = [0] * 5
    for i, a in enumerate(first):
        for j, b in enumerate(second):
            product_coefficients[i + j] ^= f4_multiply(a, b)
    assert product_coefficients == [1] * 5
    assert all(f4_multiply(x, x) ^ f4_multiply(coefficient, x) ^ 1
               for coefficient in (v, vv) for x in range(4))

    fixed = [i for i in IDENTITY if all(h[i] == i for h in group)]
    assert fixed == [3, 8, 14, 19, 23]
    blocks = []
    for a in range(5):
        states = range(5 * a, 5 * a + 5)
        orbits = {tuple(sorted({h[i] for h in group})) for i in states}
        assert sorted(map(len, orbits)) == [1, 4]
        kernel_size = sum(all(h[i] == i for i in states) for h in group)
        assert kernel_size == 64
        blocks.append(dict(support=a, fixed_color=fixed[a] % 5,
                           orbit_sizes=[1, 4], kernel_size=kernel_size))
    for n in range(1, 5):
        predicted = compose(one, conjugate(power(eta, n), one))
        assert operators[f'one_plus_eta_{n}'] == predicted
    normalizers = {name: all(conjugate(p, h) in group for h in group)
                   for name, p in operators.items()}
    assert all(normalizers[name] for name in ('tau', 'nu', 'eta', 'omega', 'bar'))
    assert all(not normalizers[name] for name in ('bridge', 'translation_z', 'bridge_shift'))
    assert order(operators['bridge']) == 12
    bridge_relation_mismatch = sum(a != b for a, b in zip(power(operators['bridge'], 10), IDENTITY))
    assert bridge_relation_mismatch == 23
    digest = lambda value: hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()
    return dict(status='PASS', experiment='E080_STATE_MODULE_AUDIT', source_sha256=SOURCE_SHA256,
                states=25, permutation_sha256=digest([operators[name] for name in names]),
                translation_group_size=256, binary_rank=8, distinct_singer_conjugates=15,
                additive_group_sha256=digest(sorted(group)), basis_sha256=digest(basis),
                cyclic_module='F2[v,e]/(v^2+v+1,Phi5(e)) = F16 x F16',
                scalar_polynomial_and_cyclotomic_relations=True,
                basis_images_checked=256, addition_pairs_checked=65536,
                irreducible_quadratic_factorization_over_F4=True, blocks=blocks,
                normalizes_group=normalizers, bridge_order=12,
                bridge_tenth_power_moved_states=23,
                scope=('The supplied finite permutations only; not a global geometric group action, '
                       'a residue map on Y, proper coloring of HG(F16), or an HN bound'))


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
