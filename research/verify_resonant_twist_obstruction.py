"""Independent exhaustive C012 word check, plus exact geometry and 3-color map.

Does not import the producer or any SAT implementation. No negative source
chromatic claim is made: the same infinite triangle host has a 3-coloring.
"""
from itertools import product
from pathlib import Path
import hashlib
import json

from verify_contact_translation_closure import multiplication, squared_distance

BASIS = ((3, 0, 4, 0), (-4, 1, -1, -3), (-4, 3, 0, 0), (-3, 4, 4, -1))
INVERSE = ((39, 52, -29, -25), (12, 16, -9, -8),
           (44, 59, -33, -28), (-36, -48, 27, 23))
RAD = (1, 3, 10, 30)
POINTS = ((0, 0, 0, 0), (13, 0, 0, 13), (26, 0, 0, 0))


def verify(root, data_override=None):
    if not __debug__:
        raise RuntimeError('Do not disable assertions in the certificate checker')
    data = (data_override if data_override is not None else
            json.loads((root/'certificates/resonant_twist_obstruction.json').read_text()))
    assert data['schema'] == 1
    source = (root/'certificates/resonant_translation_stack.json.gz').read_bytes()
    assert data['source_sha256'] == hashlib.sha256(source).hexdigest()
    assert data['core_labels'] == [0, 150, 153]
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    for i, v in zip(data['core_labels'], POINTS):
        expected = [[48*v[0]//13, 48*v[1]//13]+[0]*6,
                    [48*v[2]//13, 48*v[3]//13]+[0]*6]
        assert core['points'][i] == expected
    # Rows of INVERSE act on the columns of the actual geometric basis.
    assert [[sum(x*y for x, y in zip(row, column)) for column in BASIS]
            for row in INVERSE] == [[int(i == j) for j in range(4)] for i in range(4)]
    table = multiplication(RAD)
    zero = ([0]*4, [0]*4)

    def point_difference(i, j, step):
        a, b, c, d, m, n = step
        p, q = POINTS[i], POINTS[j]
        return ([q[0]-p[0]+7*(2*a+b), q[1]-p[1]-3*d, 2*(2*m+n), 0],
                [q[2]-p[2]+3*(2*c+d), q[3]-p[3]+7*b, 0, 2*n])

    def reduced_step(step, flip):
        coord = [sum(x*y for x, y in zip(row, step[:4])) for row in INVERSE]
        k, ell, n, h = coord
        # Tuple parity arithmetic, independent of the producer's bitwise encoding.
        e = ((flip//4) % 2, (flip//2) % 2, flip % 2)
        parity = tuple((v+n*w) % 2 for v, w in zip((k, ell, h), e))
        return parity, n % 5

    cross = []
    for m, n in product(range(-3, 4), repeat=2):
        shell = m*m+m*n+n*n
        if shell not in (3, 4):
            continue
        for sign in (-1, 1):
            if shell == 3:
                assert (m+2*n) % 3 == (2*m+n) % 3 == 0
                step = (-sign*(m+2*n)//3, sign*(2*m+n)//3, 0, 0, m, n)
            else:
                assert m % 2 == n % 2 == 0
                step = (0, 0, sign*m//2, sign*n//2, m, n)
            assert squared_distance(point_difference(0, 0, step), zero, table) == [676, 0, 0, 0]
            cross.append(step)
    assert len(cross) == 24
    labels = {label: i for i, label in enumerate(data['core_labels'])}
    rows = data['listed_contacts']
    assert len(rows) == 9 and len({tuple(row) for row in rows}) == 9
    assert {tuple(r[:2]) for r in rows} == {(0, 150), (0, 153), (150, 153)}
    for i, j, *shift in rows:
        assert squared_distance(point_difference(labels[i], labels[j], shift+[0, 0]), zero, table) == [676, 0, 0, 0]
    states = list(product(range(2), repeat=3))
    state_index = {s: i for i, s in enumerate(states)}
    expected_counts = [8, 0, 0, 4, 0, 4, 0, 8]
    candidate_words = 0
    triple_tests = 0
    assert len(data['cases']) == 8
    for flip, case in enumerate(data['cases']):
        assert case['flip'] == flip and case['normalized_triples'] == 0
        obligations = set()
        for step in cross:
            parity, n = reduced_step(step, flip)
            for q, state in enumerate(states):
                target = state_index[tuple((a+b) % 2 for a, b in zip(state, parity))]
                obligations.add((q, target, n))
        # Full enumeration of 5^7 words with color at state 000 normalized to 0.
        normalized = []
        for tail in product(range(5), repeat=7):
            word = (0,)+tail
            candidate_words += 1
            if all(word[q] != (word[t]+n) % 5 for q, t, n in obligations):
                normalized.append(word)
        assert list(map(list, normalized)) == case['normalized_words']
        assert len(normalized) == expected_counts[flip]
        all_words = [tuple((c+n) % 5 for c in word) for word in normalized for n in range(5)]
        by_pair = {}
        for i, j, *shift in rows:
            parity, n = reduced_step(shift, flip)
            targets = tuple(state_index[tuple((a+b) % 2 for a, b in zip(state, parity))] for state in states)
            by_pair.setdefault((labels[i], labels[j]), []).append((targets, n))
        def compatible(u, v, pair):
            return all(u[q] != (v[targets[q]]+n) % 5
                       for targets, n in by_pair[pair] for q in range(8))
        for a, b, c in product(normalized, all_words, all_words):
            triple_tests += 1
            assert not (compatible(a, b, (0, 1)) and compatible(a, c, (0, 2)) and compatible(b, c, (1, 2)))
    assert candidate_words == 625000 and triple_tests == 28800
    # Z[1/26,sqrt(3),sqrt(10)] -> F3: sqrt3=0, sqrt10=1.
    images = (1, 0, 1, 0)
    assert all(images[i]*images[j] % 3 == factor*images[k] % 3
               for (i, j), (k, factor) in table.items())
    assert all((x+y) % 3 != 0 for x, y in product(range(3), repeat=2) if (x*x+y*y) % 3 == 1)
    assert data['three_color_formula'] == '(base[i]+a-b-m+n)%3'
    assert data['base'] == [0, 2, 1]
    formula_checks = 0
    for i in range(3):
        for step in product(range(3), repeat=6):
            # Add base i to shift, rather than a difference between distinct cores.
            x, y = point_difference(0, i, step)
            image = sum(v*w for axis in (x, y) for v, w in zip(axis, images))*2 % 3
            a, b, c, d, m, n = step
            assert image == (data['base'][i]+a-b-m+n) % 3
            formula_checks += 1
    return dict(status='VERIFIED_FIVE_CYCLE_RULE_OBSTRUCTION_ON_THREE_COLOR_HOST',
                actual_core_points=3, exact_listed_contacts=9, cross_steps=24,
                normalized_words_enumerated=candidate_words,
                surviving_word_counts=expected_counts, normalized_triples_rejected=triple_tests,
                three_color_formula_checks=formula_checks,
                scope='C012 rules only; the actual infinite triangle host is exactly three, not six')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
