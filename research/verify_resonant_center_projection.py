"""Independent all-contact and center-aware infinite-coloring obligations.

No SAT imports. T072's independent compiler is rerun, not the search producer.
The written proof handles the universal integer labels; all finite obligations
are checked here, including the two actual signs of each cross-layer edge.
"""
from itertools import combinations, product
from pathlib import Path
import gzip
import hashlib
import json
import math

from verify_resonant_translation_stack import (
    compile_contacts, check_cross_and_uniqueness, digest,
)
from verify_contact_translation_closure import multiplication, squared_distance


def intermediate_three_direction(root, source, prior, rows, cross):
    """Retain the earlier positive W search as independently checked evidence."""
    from verify_resonant_twist_obstruction import BASIS, INVERSE
    assert [[sum(a*b for a, b in zip(row, column)) for column in BASIS]
            for row in INVERSE] == [[int(i == j) for j in range(4)] for i in range(4)]
    saved = json.loads((root/'certificates/resonant_three_direction_w.json').read_text())
    assert saved['schema'] == 1 and saved['source_sha256'] == hashlib.sha256(source).hexdigest()
    assert saved['selected'] == [0, 1, 3]
    shifts, phase = saved['shifts'], saved['phase_offsets']
    assert shifts == prior['cluster']['shifts'] and phase == prior['cluster']['phase_offsets']
    words = saved['words']
    assert len(words) == 8 and all(len(w) == 509 and set(w) <= set('01234') for w in words)
    def coord(step):
        return tuple(sum(a*b for a, b in zip(row, step)) for row in INVERSE)
    offsets = [coord(s) for s in shifts]
    assert len({s[2] for s in offsets}) == len(shifts) == 16
    by_step = {}
    for i, j, *d in rows:
        by_step.setdefault(coord(d), []).append((i, j))
    for d in {s[:4] for s in cross}:
        by_step.setdefault(coord(d), []).extend((i, i) for i in range(509))
    relation = []
    for s, x in enumerate(offsets):
        for t, y in enumerate(offsets):
            for d, pairs in by_step.items():
                change = tuple(a+b-c for a, b, c in zip(x, d, y))
                if change[2] == 0:
                    relation.extend((s, t, i, j, change[0], change[1], change[3]) for i, j in pairs)
    relation.sort()
    assert len(relation) == len(set(relation)) == saved['relation_count'] == 110748
    assert digest(relation) == saved['relation_sha256']
    checks = 0
    for s, t, i, j, da, db, dc in relation:
        for a, b, c in product(range(2), repeat=3):
            left = 4*a+2*b+c
            right = 4*((a+da) % 2)+2*((b+db) % 2)+(c+dc) % 2
            assert (int(words[left][i])+phase[s]) % 5 != (int(words[right][j])+phase[t]) % 5
            checks += 1
    assert checks == 885984
    return dict(complete_relations=len(relation), color_obligations=checks,
                scope='Intermediate T/U/W subarray, subsumed by full-X T074')


def finite_probe(core, word, rows, cross):
    """All physical point pairs, without using the contact list as an edge oracle."""
    shifts = ((0, 0, 0, 0), (3, 0, 4, 0), (-4, 1, -1, -3),
              (-4, 3, 0, 0), (-3, 4, 4, -1), (1, 0, 0, 0), (0, 0, 1, 0))
    centers = ((0, 0), (1, -2), (2, 0))
    rad = (1, 3, 11, 33, 5, 15, 55, 165, 2, 6, 22, 66, 10, 30, 110, 330)
    table = multiplication(rad)
    denominator = 1248
    points, labels, colors = [], [], []
    for m, n in centers:
        for a, b, c, d in shifts:
            for i, p in enumerate(core['points']):
                x, y = [[13*v for v in axis]+[0]*8 for axis in p]
                x[0] += 336*(2*a+b)
                x[1] -= 144*d
                y[0] += 144*(2*c+d)
                y[1] += 336*b
                x[12] += 96*(2*m+n)
                y[13] += 96*n
                points.append((tuple(x), tuple(y)))
                labels.append((i, a, b, c, d, m, n))
                colors.append((int(word[509*((a-b) % 3)+i])+(m-n) % 3) % 5)
    assert len(points) == len(set(points)) == 10689
    prime = 1031
    assert all(prime % d for d in range(2, math.isqrt(prime)+1))
    roots = {x*x % prime: x for x in range(prime)}
    images = []
    for r in rad:
        value = 1
        for p in (2, 3, 5, 11):
            if r % p == 0:
                value = value*roots[p] % prime
        images.append(value)
    assert all(images[i]*images[j] % prime == factor*images[k] % prime
               for (i, j), (k, factor) in table.items())
    residues = [tuple(sum(a*b for a, b in zip(axis, images)) % prime for axis in p) for p in points]
    edges, candidates = [], 0
    shell_counts = {0: 0, 3: 0, 4: 0}
    contact_set, cross_set = set(rows), set(cross)
    for i, j in combinations(range(len(points)), 2):
        (x, y), (u, v) = residues[i], residues[j]
        if ((x-u)**2+(y-v)**2-denominator**2) % prime:
            continue
        candidates += 1
        if squared_distance(points[i], points[j], table) != [denominator**2]+[0]*15:
            continue
        assert colors[i] != colors[j]
        left, right = labels[i], labels[j]
        delta = tuple(b-a for a, b in zip(left[1:], right[1:]))
        m, n = delta[-2:]
        shell = m*m+m*n+n*n
        assert shell in shell_counts
        shell_counts[shell] += 1
        if shell == 0:
            assert (left[0], right[0], *delta[:4]) in contact_set
        else:
            assert left[0] == right[0] and delta in cross_set
        edges.append((i, j))
    assert shell_counts[3] and shell_counts[4]
    return dict(vertices=len(points), edges=len(edges),
                actual_point_pairs=len(points)*(len(points)-1)//2,
                exact_radical_candidates=candidates, edges_by_shell=shell_counts,
                edge_sha256=digest(edges), includes_T_U_V_W=True)


def verify(root, data_override=None):
    if not __debug__:
        raise RuntimeError('Do not disable assertions in the certificate checker')
    source = (root/'certificates/resonant_translation_stack.json.gz').read_bytes()
    core_raw = (root/'certificates/parts509_core.json').read_bytes()
    saved = (data_override if data_override is not None else
             json.loads((root/'certificates/resonant_center_linear.json').read_text()))
    assert saved['schema'] == 1
    assert saved['source_sha256'] == hashlib.sha256(source).hexdigest()
    assert saved['core_sha256'] == hashlib.sha256(core_raw).hexdigest()
    assert saved['parameter'] == dict(beta=[40, 169], first=7, second=3, denominator=13)
    assert saved['pair'] is False and saved['states'] == [[0, 0], [1, 0], [2, 0]]
    assert saved['coloring_formula'] == '(word[509*((a-b)%3)+i]+(m-n)%3)%5'
    word = saved['word']
    assert len(word) == 1527 and set(word) == set('01234')
    core = json.loads(core_raw)
    rows, stats = compile_contacts(core)
    prior = json.loads(gzip.decompress(source))
    assert list(map(list, rows)) == prior['contacts']
    assert stats == prior['statistics'] and len(rows) == 8008
    cross = check_cross_and_uniqueness(core)
    assert len(cross) == 24 and all(len(s) == 6 for s in cross)
    intermediate = intermediate_three_direction(root, source, prior, rows, cross)
    edges = set()
    checks = {0: 0, 3: 0, 4: 0}

    def color(i, q, r):
        return (int(word[509*(q % 3)+i])+r % 3) % 5

    for i, j, a, b, c, d in rows:
        for q, r in product(range(3), repeat=2):
            assert color(i, q, r) != color(j, q+a-b, r)
            checks[0] += 1
            edges.add(tuple(sorted((509*q+i, 509*((q+a-b) % 3)+j))))
    for a, b, c, d, m, n in cross:
        shell = m*m+m*n+n*n
        assert shell in (3, 4)
        if shell == 3:
            assert c == d == 0 and (a-b) % 3 != 0 and (m-n) % 3 == 0
        else:
            assert a == b == 0 and (c-d) % 3 != 0 and (m-n) % 3 != 0
        for i, q, r in product(range(509), range(3), range(3)):
            assert color(i, q, r) != color(i, q+a-b, r+m-n)
            checks[shell] += 1
            if shell == 3:
                edges.add(tuple(sorted((509*q+i, 509*((q+a-b) % 3)+i))))
    assert checks == {0: 72072, 3: 54972, 4: 54972}
    assert len(edges) == saved['target_edges'] == 11196
    assert saved['target_vertices'] == 1527
    assert digest(sorted(edges)) == saved['edge_sha256']
    assert all(u != v and word[u] != word[v] for u, v in edges)
    # The target restricts to the full verified Parts graph at q=0.
    assert all(tuple(sorted(e)) in edges for e in core['induced_edges'])
    probe = finite_probe(core, word, rows, cross)
    return dict(status='VERIFIED_FULL_DENOMINATOR_13_CLOSURE_FIVE_COLORING',
                target_vertices=1527, target_edges=len(edges),
                directed_edge_orbits=len(rows)+509*len(cross),
                phase_states=9, color_checks_by_shell=checks,
                color_checks=sum(checks.values()),
                finite_probe=probe,
                intermediate_three_direction=intermediate,
                chromatic_number=5,
                lower_bound='Parts509, independently RUP-verified by make check',
                scope='Entire X; written T074 gives universal lift. Not all K^2+alphaLambda or the plane')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
