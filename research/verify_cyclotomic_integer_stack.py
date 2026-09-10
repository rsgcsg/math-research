"""Exact independent T076 calibrations and an induced cyclotomic Parts probe.

No SAT/search imports. Complex positions use the degree-96 algebra
Q(i,sqrt(3),sqrt(5),sqrt(11))[z]/(1+z+...+z^6). A modular filter is checked
as a ring homomorphism, then every surviving physical pair is multiplied
exactly. Infinite completeness is the written field/trace proof.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math

RAD = (1, 3, 11, 33, 5, 15, 55, 165)


def cyclo_product(a, b, p):
    values = [0]*p
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            values[(i+j) % p] += x*y
    return tuple(v-values[-1] for v in values[:-1])


def algebra_checks():
    primes = (5, 7, 13, 17, 19)
    palettes = 0
    for p in primes:
        assert all(p % d for d in range(2, math.isqrt(p)+1))
        # Phi_p(x+1) is Eisenstein at p.
        assert math.comb(p, 1) % (p*p) != 0
        assert all(math.comb(p, j) % p == 0 for j in range(1, p))
        legendre = [0]+[1 if pow(a, (p-1)//2, p) == 1 else -1 for a in range(1, p)]
        tau = tuple(a-legendre[-1] for a in legendre[:-1])
        assert cyclo_product(tau, tau, p) == ((-1 if p % 4 == 3 else 1)*p,)+(0,)*(p-2)
        assert set(tau[1:]) <= {0, 2, -2} and any(abs(a) == 2 for a in tau[1:])
        for k in range(3, 8):
            weights = [1, 1, k-2]+[a for _ in range((p-5)//2) for a in (1, k-1)]
            assert len(weights) == p-2 and sum(weights) % k == 0
            assert all(w % k for w in weights)
            palettes += 1
    square_classes = {(-1)**s*3**a*5**b*11**c for s, a, b, c in product(range(2), repeat=4)}
    assert len(square_classes) == 16 and -7 not in square_classes

    roots = set()
    examined = 0
    for a in product(range(-2, 3), repeat=6):
        examined += 1
        energy = 7*sum(x*x for x in a)-sum(a)**2
        if energy != 6:
            continue
        conjugate = [0]*7
        for j, x in enumerate(a):
            conjugate[-j % 7] = x
        conjugate = tuple(x-conjugate[-1] for x in conjugate[:-1])
        assert cyclo_product(a, conjugate, 7) == (1, 0, 0, 0, 0, 0)
        roots.add(a)
    expected = {tuple(sign*int(i == j) for i in range(6)) for j in range(6) for sign in (-1, 1)}
    expected.update({(1,)*6, (-1,)*6})
    assert roots == expected and examined == 15625
    assert sum([1]*5) % 5 == 0
    # C013: exact unit direction outside the integer cyclotomic stack.
    numerator = (-65, 93, 45, 21, 9, 3)
    assert cyclo_product((2, -1, 0, 0, 0, 0), numerator, 7) == (-127, 254, 0, 0, 0, 0)
    conjugate_numerator = [0]*7
    for j, a in enumerate(numerator):
        conjugate_numerator[-j % 7] = a
    conjugate_numerator = tuple(a-conjugate_numerator[-1] for a in conjugate_numerator[:-1])
    assert cyclo_product(numerator, conjugate_numerator, 7) == (127**2, 0, 0, 0, 0, 0)
    assert math.gcd(127, math.gcd(*numerator)) == 1
    assert any(a % 127 for a in numerator[1:])
    return dict(calibrated_primes=list(primes), palette_cases=palettes,
                seventh_trace_candidates=examined, seventh_unit_roots=len(roots),
                base_field_square_classes=len(square_classes),
                escaped_unit_numerator=list(numerator), escaped_unit_denominator=127)


def multiplication():
    table = {}
    for u, v in product(range(96), repeat=2):
        j, a = divmod(u, 16)
        k, b = divmod(v, 16)
        ai, ar = divmod(a, 8)
        bi, br = divmod(b, 8)
        factor = math.gcd(RAD[ar], RAD[br]) * (-1 if ai == bi == 1 else 1)
        radical = RAD.index(RAD[ar]*RAD[br]//math.gcd(RAD[ar], RAD[br])**2)
        index = 8*((ai+bi) % 2)+radical
        power = (j+k) % 7
        table[u, v] = ([(16*e+index, -factor) for e in range(6)] if power == 6
                       else [(16*power+index, factor)])
    return table


def conjugate(a):
    result = [0]*96
    for index, coefficient in enumerate(a):
        j, b = divmod(index, 16)
        coefficient *= -1 if b >= 8 else 1
        power = -j % 7
        if power == 6:
            for k in range(6):
                result[16*k+b] -= coefficient
        else:
            result[16*power+b] += coefficient
    return result


def norm(a, table):
    result = [0]*96
    left = [(i, x) for i, x in enumerate(a) if x]
    right = [(i, x) for i, x in enumerate(conjugate(a)) if x]
    for i, x in left:
        for j, y in right:
            for k, coefficient in table[i, j]:
                result[k] += x*y*coefficient
    return result


def probe(root):
    core_raw = (root/'certificates/parts509_core.json').read_bytes()
    core = json.loads(core_raw)
    residue = json.loads((root/'certificates/residue11_coloring.json').read_text())
    word = ''.join(residue['rows'])
    assert len(word) == 121 and set(word) == set('01234')
    assert all(word[11*x+y] != word[11*u+v]
               for x, y, u, v in product(range(11), repeat=4)
               if ((x-u)**2+(y-v)**2) % 11 == 1)
    shifts = [(0,)*5]+[tuple(int(i == j) for i in range(5)) for j in range(5)]
    shifts += [(-1,)*5, (1, 1, 0, 0, 0)]
    points, colors, labels = [], [], []
    images11 = (1, 5, 0, 0, 4, 9, 0, 0)
    for shift in shifts:
        for i, (x, y) in enumerate(core['points']):
            point = list(x)+list(y)+[0]*80
            for j, value in enumerate(shift, 1):
                point[16*j] += 96*value
            points.append(tuple(point))
            a, b = (sum(u*v for u, v in zip(axis, images11))*pow(96, -1, 11) % 11 for axis in (x, y))
            colors.append((int(word[11*a+b])+sum(shift)) % 5)
            labels.append((i, shift))
    assert len(points) == len(set(points)) == 4072
    table = multiplication()

    # Find a fully split prime independently; evaluate both z and z^-1.
    for prime in range(1009, 100000):
        if prime % 28 != 1 or any(prime % d == 0 for d in range(2, math.isqrt(prime)+1)):
            continue
        if all(pow(r, (prime-1)//2, prime) == 1 for r in (3, 5, 11)):
            break
    else:
        raise AssertionError('No modular filter found')
    roots = {x*x % prime: x for x in range(prime)}
    z = next(pow(x, (prime-1)//7, prime) for x in range(2, prime)
             if pow(x, (prime-1)//7, prime) != 1)
    assert pow(z, 7, prime) == 1 and z != 1
    field_images = []
    for imaginary in range(2):
        for rad in RAD:
            value = roots[prime-1] if imaginary else 1
            for r in (3, 5, 11):
                if rad % r == 0:
                    value = value*roots[r] % prime
            field_images.append(value)
    images = [pow(z, j, prime)*value % prime for j in range(6) for value in field_images]
    assert all(images[u]*images[v] % prime == sum(c*images[k] for k, c in row) % prime
               for (u, v), row in table.items())
    projected = [(sum(a*b for a, b in zip(point, images)) % prime,
                  sum(a*b for a, b in zip(conjugate(point), images)) % prime) for point in points]
    root_vectors = []
    for j in range(1, 7):
        a = [0]*96
        if j == 6:
            for k in range(6):
                a[16*k] = -96
        else:
            a[16*j] = 96
        root_vectors.extend((tuple(a), tuple(-x for x in a)))
    root_vectors = set(root_vectors)
    counts = dict(same_slice=0, root_steps=0, different_core_root_steps=0)
    edges, candidates = [], 0
    for i, j in combinations(range(len(points)), 2):
        u, ub = projected[i]
        v, vb = projected[j]
        if ((v-u)*(vb-ub)-96**2) % prime:
            continue
        candidates += 1
        delta = tuple(b-a for a, b in zip(points[i], points[j]))
        if norm(delta, table) != [96**2]+[0]*95:
            continue
        assert colors[i] != colors[j]
        edges.append((i, j))
        if labels[i][1] == labels[j][1]:
            counts['same_slice'] += 1
        else:
            assert delta in root_vectors
            counts['root_steps'] += 1
            counts['different_core_root_steps'] += labels[i][0] != labels[j][0]
    assert counts['different_core_root_steps'] > 0
    assert counts == dict(same_slice=19536, root_steps=3693, different_core_root_steps=130)
    assert len(edges) == 23229 and candidates == 26287 and prime == 2269
    digest = hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest()
    assert digest == 'a72121c3967bb5407da18ca9363078aa443b4ef2d45cf8d8a9d4717cfea38f35'
    return dict(vertices=len(points), edges=len(edges), actual_pairs=len(points)*(len(points)-1)//2,
                modular_prime=prime, exact_candidates=candidates, counts=counts,
                edge_sha256=digest,
                core_sha256=hashlib.sha256(core_raw).hexdigest())


def verify(root):
    if not __debug__:
        raise RuntimeError('Do not disable assertions in the proof checker')
    return dict(status='VERIFIED_CYCLOTOMIC_INTEGER_STACK_FIVE_COLORING',
                algebra=algebra_checks(), finite_probe=probe(root),
                scope='Written T076: K^2 plus the integer seventh-cyclotomic module exactly five; not the full compositum field or plane')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
