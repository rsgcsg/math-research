"""Independent exact T080 verification; no producer, Sympy or solver imports.

Only the listed-direction Cayley graph is colored here. Neither the induced
unit graph on its vertices nor the full four-support field host is claimed.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math

from verify_cyclotomic_integer_stack import multiplication, norm


def rational(pair):
    assert isinstance(pair, list) and len(pair) == 2
    assert all(type(x) is int for x in pair) and pair[1] > 0
    value = Q(*pair)
    assert [value.numerator, value.denominator] == pair
    return value


def rank(rows):
    a = [list(map(Q, row)) for row in rows]
    pivot = 0
    for col in range(len(a[0])):
        candidate = next((j for j in range(pivot, len(a)) if a[j][col]), None)
        if candidate is None:
            continue
        a[pivot], a[candidate] = a[candidate], a[pivot]
        divisor = a[pivot][col]
        a[pivot] = [x/divisor for x in a[pivot]]
        for j in range(pivot+1, len(a)):
            multiplier = a[j][col]
            a[j] = [x-multiplier*y for x, y in zip(a[j], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def verify(root, certificate=None):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    path = certificate or root/'certificates/cyclotomic_direction_parity.json'
    raw = path.read_bytes()
    data = json.loads(raw)
    assert data['schema'] == 1 and data['theorem'] == 'T080'
    assert data['source'] == 'certificates/cyclotomic_sparse_coupling.json'
    source_raw = (root/data['source']).read_bytes()
    assert hashlib.sha256(source_raw).hexdigest() == data['source_sha256']
    source = json.loads(source_raw)
    expected_basis = ['1', 'sqrt(3)', 'i', 'i*sqrt(3)']
    assert data['coefficient_basis'] == source['coefficient_basis'] == expected_basis
    assert data['powers'] == source['powers'] == [0, 1, 2, 3]
    assert source['schema'] == 1 and source['counterexample'] == 'C015'
    assert data['graph'] == 'Cayley(sum_Z D, plus_or_minus_D); listed directions only'
    expected_weights = ((Q(1), Q(0), Q(-1), Q(3, 8)),
                        (Q(1), Q(0), Q(0), Q(3, 2)),
                        (Q(1), Q(0), Q(0), Q(3, 2)),
                        (Q(1), Q(0), Q(0), Q(11, 8)))
    assert len(data['character_weights']) == 4
    weights = tuple(tuple(rational(x) for x in row) for row in data['character_weights'])
    assert weights == expected_weights
    flat_weights = tuple(w for row in weights for w in row)
    labels = ['axis_'+str(j) for j in range(4)]+['triple_013', 'triple_023']
    labels += ['mixed_'+str(n)+'_'+str(d)+'_'+str(sign)
               for n, d in ((3, 2), (2, 3), (-10, 9), (-9, 10)) for sign in (-1, 1)]
    assert [x['label'] for x in source['unit_vectors']] == labels
    assert [x['label'] for x in data['generator_evaluations']] == labels
    expected_values = [Q(1)]*6+[Q(-1), Q(257, 463), Q(-397, 463), Q(323, 463),
                                  Q(35809, 5217031), Q(743041, 5217031),
                                  Q(1275761, 5217031), Q(568529, 5217031)]
    vectors, evaluations = [], []
    table = multiplication()
    for record, evaluation, expected in zip(source['unit_vectors'],
                                            data['generator_evaluations'], expected_values):
        encoded = record['coefficients']
        assert len(encoded) == 4 and all(len(a) == 4 for a in encoded)
        vector = tuple(rational(x) for a in encoded for x in a)
        full = [Q(0)]*96
        for j in range(4):
            for r, b in enumerate((0, 1, 8, 9)):
                full[16*j+b] = vector[4*j+r]
        assert norm(full, table) == [1]+[0]*95
        value = sum(x*w for x, w in zip(vector, flat_weights))
        assert value == rational(evaluation['value']) == expected
        assert value.numerator % 2 == value.denominator % 2 == 1
        vectors.append(vector)
        evaluations.append(value)
    assert len(set(vectors)) == 14 and rank(vectors) == 10

    # Adding the base-field triangle is outside this character's integral domain.
    # Its third vertex cannot already be in Gamma because L(Gamma) is 2-integral.
    triangle_tip = [Q(0)]*96
    triangle_tip[0] = triangle_tip[9] = Q(1, 2)
    assert norm(triangle_tip, table) == [1]+[0]*95
    triangle_tip[0] -= 1
    assert norm(triangle_tip, table) == [1]+[0]*95
    assert Q(1, 2)+Q(3, 8)*Q(1, 2) == Q(11, 16)

    # Exact finite calibration on all words with 0/1 coefficients, signs, and
    # support <= 3. Clearing denominators is injective, not a periodic quotient.
    denominator = 1
    for vector in vectors:
        for x in vector:
            denominator = denominator*x.denominator//math.gcd(denominator, x.denominator)
    scaled = [tuple(int(x*denominator) for x in vector) for vector in vectors]
    vertices = {}
    words = 0
    for size in range(4):
        for support in combinations(range(14), size):
            for signs in product((-1, 1), repeat=size):
                point = tuple(sum(sign*scaled[j][col] for j, sign in zip(support, signs))
                              for col in range(16))
                value = sum(sign*evaluations[j] for j, sign in zip(support, signs))
                assert value.denominator % 2 == 1 and value.numerator % 2 == size % 2
                assert sum(Q(x, denominator)*w for x, w in zip(point, flat_weights)) == value
                if point in vertices:
                    assert vertices[point] == size % 2
                vertices[point] = size % 2
                words += 1
    assert words == len(vertices) == 3305
    signed_directions = [tuple(sign*x for x in vector) for vector in scaled for sign in (-1, 1)]
    directed_edges = 0
    for point, color in vertices.items():
        for direction in signed_directions:
            neighbor = tuple(x+y for x, y in zip(point, direction))
            if neighbor in vertices:
                assert vertices[neighbor] == 1-color
                directed_edges += 1
    assert directed_edges == 2*9492
    return dict(theorem='T080', status='PASS', unit_generators=14, rational_rank=10,
                odd_character_values=14, finite_vertices=len(vertices),
                finite_listed_edges=directed_edges//2,
                added_base_field_triangle='three actual edges; tip outside Gamma',
                scope='listed-direction Cayley graph, not induced unit graph',
                certificate_sha256=hashlib.sha256(raw).hexdigest())


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
