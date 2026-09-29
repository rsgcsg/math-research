"""Independent rational Phi_21 check of the heptagon module certificate.

No search code, SAT, floats, or tensor multiplication is imported.  Infinite
unit-direction completeness is the valuation/Kronecker proof in the document.
"""
from fractions import Fraction as Q
from collections import Counter
from itertools import combinations
from pathlib import Path
import json


PHI = (1, -1, 0, 1, -1, 0, 1, 0, -1, 1, 0, -1, 1)
ZERO = (Q(0),) * 12
ONE = (Q(1),) + ZERO[1:]


def reduce_poly(a):
    a = list(a) + [Q(0)] * max(0, 12 - len(a))
    for k in range(len(a)-1, 11, -1):
        v = a[k]
        for j in range(13):
            a[k-12+j] -= v * PHI[j]
    return tuple(a[:12])


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def scale(a, q):
    return tuple(x*q for x in a)


def sub(a, b):
    return add(a, scale(b, -1))


def mul(a, b):
    out = [Q(0)] * 23
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return reduce_poly(out)


def power(n):
    return reduce_poly([Q(0)] * (n % 21) + [Q(1)])


def conjugate(a):
    out = ZERO
    for j, x in enumerate(a):
        out = add(out, scale(power(-j), x))
    return out


def inverse(a):
    cols = [mul(a, power(i)) for i in range(12)]
    rows = [[cols[j][i] for j in range(12)] + [ONE[i]] for i in range(12)]
    for j in range(12):
        k = next(i for i in range(j, 12) if rows[i][j])
        rows[j], rows[k] = rows[k], rows[j]
        v = rows[j][j]
        rows[j] = [x/v for x in rows[j]]
        for i in range(12):
            if i != j:
                v = rows[i][j]
                rows[i] = [x-v*y for x, y in zip(rows[i], rows[j])]
    result = tuple(row[-1] for row in rows)
    assert mul(a, result) == ONE
    return result


def norm(a):
    return mul(a, conjugate(a))


TENSOR_BASIS = tuple(power(3*i+7*b) for b in range(2) for i in range(6))


def from_tensor(a):
    assert len(a) == 12
    out = ZERO
    for v, b in zip(a, TENSOR_BASIS):
        assert len(v) == 2 and all(type(x) is int for x in v) and v[1] > 0
        out = add(out, scale(b, Q(*v)))
    return out


def tensor_parity(a):
    # The tensor integral basis has determinant +/-1 relative to Phi_21.
    # Solve its F2 change of basis using a complete 4096-vector dictionary.
    if any(x.denominator % 2 == 0 for x in a):
        raise ValueError('even denominator')
    key = sum((x.numerator % 2) << j for j, x in enumerate(a))
    return PARITY_INVERSE[key]


def phi_mask(a):
    values = [Q(x) for x in a]
    if any(x.denominator % 2 == 0 for x in values):
        raise ValueError('even denominator')
    return sum((x.numerator % 2) << j for j, x in enumerate(values))


PARITY_INVERSE = {}
for _mask in range(4096):
    _value = 0
    for _j, _b in enumerate(TENSOR_BASIS):
        if _mask >> _j & 1:
            _value ^= phi_mask(_b)
    assert _value not in PARITY_INVERSE
    PARITY_INVERSE[_value] = _mask


def geometry():
    assert power(21) == ONE and power(7) != ONE and power(3) != ONE
    z, w = power(3), power(7)
    denominators = [sub(power(12), power(-12)),
                    sub(z, power(-3)), sub(power(6), power(-6))]
    offsets = [inverse(denominators[0]), mul(w, inverse(denominators[1])),
               mul(power(14), inverse(denominators[2]))]
    points = [mul(power(3*j), a) for a in offsets for j in range(7)]
    assert len(set(points)) == 21
    r = sub(points[7], points[14])
    assert norm(r) == ONE
    mu = {scale(power(j), sign) for j in range(21) for sign in (-1, 1)}
    directions = mu | {mul(r, a) for a in mu}
    assert len(directions) == 84 and all(norm(d) == ONE for d in directions)
    pairs, arcs = [], set()
    for i, j in combinations(range(21), 2):
        d = sub(points[j], points[i])
        if norm(d) == ONE:
            pairs.append((i, j))
            arcs.update((d, scale(d, -1)))
    assert len(pairs) == 42 and arcs == directions
    # Exact identity used to establish the two distinct 7-adic valuations.
    numerator = sub(mul(w, add(z, power(-3))), power(14))
    expanded = add(add(scale(w, 3), ONE), mul(w, mul(mul(sub(z, ONE), sub(z, ONE)), power(-3))))
    denominator = mul(sub(z, power(-3)), add(z, power(-3)))
    assert numerator == expanded and mul(r, denominator) == numerator
    assert mul(add(scale(w, 3), ONE), add(scale(power(14), 3), ONE)) == scale(ONE, 7)
    assert all(all(x.denominator in (1, 7) for x in d) for d in directions)
    return r, mu, directions, pairs, points


def independent_linear_masks(vectors):
    """Exhaust all first rows; binary elimination decides the second row.

    This proves only a linear F2^2-map statement, never a chromatic lower bound.
    """
    good = []
    for first in range(4096):
        pivots = {}
        consistent = True
        for v in vectors:
            if (first & v).bit_count() % 2:
                continue
            row = v | (1 << 12)
            for k in range(11, -1, -1):
                if row >> k & 1:
                    if k in pivots:
                        row ^= pivots[k]
                    else:
                        pivots[k] = row
                        break
            else:
                if row >> 12:
                    consistent = False
                    break
        if consistent:
            good.append((first, 12-len(pivots)))
    return good


def verify(data):
    assert data['field']['definition'] == 'Q(z,w), Phi_7(z)=0, w^2+w+1=0'
    assert data['field']['basis_order'] == [f'z^{i}w^{b}' for b in range(2) for i in range(6)]
    r, mu, directions, pairs, points = geometry()
    assert from_tensor(data['field']['rational_r']) == r
    g = data['geometry_check']
    assert (g['vertices'], g['unordered_unit_pairs'], g['directed_arcs'],
            g['directed_arcs_distinct'], g['nonunit_pair_count']) == (21, 42, 84, 84, 168)
    assert g['all_directed_arcs_have_exact_norm_one'] is True
    assert g['arc_set_equal_to_mu42_union_r_mu42'] is True
    recorded = set()
    for row in g['nonunit_pair_norms']:
        a, b = row['pair']
        i, j = 7*'PQR'.index(a[0])+a[1], 7*'PQR'.index(b[0])+b[1]
        assert 0 <= a[1] < 7 and 0 <= b[1] < 7 and i < j
        assert (i, j) not in recorded
        recorded.add((i, j))
        assert from_tensor(row['norm']) == norm(sub(points[j], points[i])) != ONE
    assert recorded == set(combinations(range(21), 2))-set(pairs)
    seen = set()
    for row in data['directions']:
        d = from_tensor(row['field_coordinates'])
        assert d not in seen and d in directions
        seen.add(d)
        assert from_tensor(row['exact_norm']) == norm(d) == ONE
        assert row['mod2_mask'] == tensor_parity(d)
    assert seen == directions

    # Direct formula in the OTHER (Phi_21) basis, not the producer's masks.
    assert phi_mask(r) == 0x576
    counts = Counter()
    for d in directions:
        v = sum((x.numerator % 2) << i for i, x in enumerate(d))
        color = ((v & 0x0ff).bit_count() % 2, (v & 0xf21).bit_count() % 2)
        assert color != (0, 0)
        counts[color] += 1
    assert sorted(counts.values()) == [28, 28, 28]

    stages = data['search']['stages']
    assert len(stages) == 3
    vectors, p, summaries = set(), ONE, []
    for m, stage in enumerate(stages):
        vectors.update(tensor_parity(mul(p, a)) for a in mu)
        p = mul(p, r)
        assert 0 not in vectors
        valid = dict(independent_linear_masks(sorted(vectors)))
        assert stage['m'] == m and stage['direction_count'] == 42*(m+1)
        assert stage['reduced_direction_count'] == len(vectors) == 21*(m+1)
        assert stage['first_functionals_examined'] == 4096
        assert stage['successful_first_functional_count'] == len(valid) == (546, 126, 0)[m]
        assert stage['linear_map_exists'] is bool(valid)
        saved = stage['successful_first_functionals_and_representative_second']
        assert len(saved) == len(valid)
        assert {row['first_mask'] for row in saved} == set(valid)
        for row in saved:
            first, second = row['first_mask'], row['second_mask']
            assert type(first) is int and type(second) is int and 0 <= second < 4096
            assert row['second_solution_nullity'] == valid[first]
            assert row['second_solution_count'] == 2**valid[first]
            assert all((first & v).bit_count() % 2 or (second & v).bit_count() % 2 for v in vectors)
        spectrum = Counter(sum(1 if (a & v).bit_count() % 2 == 0 else -1
                               for v in vectors) for a in range(4096))
        assert sum(spectrum.values()) == 4096
        assert sum(x*n for x, n in spectrum.items()) == 0
        assert sum(x*x*n for x, n in spectrum.items()) == 4096*len(vectors)
        summaries.append(dict(m=m, reduced_directions=len(vectors),
                              valid_first_rows=len(valid),
                              ordered_linear_maps=sum(2**n for n in valid.values()),
                              spectrum=sorted(spectrum.items())))
    expected_spectrum = {-13:378, -9:441, -5:756, -1:882, 3:378,
                         7:567, 11:504, 15:189, 63:1}
    assert spectrum == expected_spectrum
    # Integer Hoffman bound alpha <= floor(4096*13/(63+13))=700.
    assert 4096*13//76 == 700 and 5*700 < 4096
    # r^3 returns to the roots' reduction orbit; all higher layers repeat.
    assert tensor_parity(p) in {tensor_parity(a) for a in mu}
    return dict(points=21, actual_pairs=210, actual_edges=len(pairs),
                directed_units=len(directions), tensor_change_mod2=4096,
                stages=summaries, residue_graph_vertices=4096,
                residue_graph_edges=4096*63//2, independence_upper_bound=700,
                residue_graph_chromatic_lower_bound=6,
                scope='L1 <=4 by written complete-direction theorem; residue lower bound does NOT lift to L2 or the plane')


def verify_extensions(data):
    assert data['schema'] == 'heptagon-table2-extensions-v1'
    assert data['source_url'] == 'https://arxiv.org/html/2608.04542v4'
    assert data['raw_html_sha256'] == 'c538a20c2c840b30c48f0b9cf822224053dddd6c93bc2b6fc1a74e266a1c9245'
    assert data['basis'] == '1,X,...,X^11; X=zeta21, z=X^3,w=X^7'
    assert data['color_labels'] == {'A': 1, 'B': 2, 'C': 3}
    assert data['shift'] == 'u_(j+14) cycles A to B to C to A'
    _, _, directions, _, p = geometry()
    # Source Table 1: family 0=P,1=Q,2=R, indices taken modulo7.
    arcs = [(0,3,0,4),(2,0,1,0),(2,1,2,4),(2,6,0,6),
            (1,4,1,6),(1,5,0,5),(0,1,0,0),(1,4,2,4),
            (2,1,2,5),(0,3,2,3),(1,3,1,1),(0,2,1,2)]
    u = [sub(p[7*c+(d+j)%7], p[7*a+(b+j)%7])
         for j in range(7) for a,b,c,d in arcs]
    assert len(u) == 84 and set(u) == directions
    labels = ['AAAAACAABABBCB', 'AAAACAABCCABBC', 'AAABBCBBAACAAB',
              'AAACBBACBBACCC', 'ABABABBAACACCB', 'ABACACCBCBABCA']
    assert len(data['extensions']) == 6
    for number, (row, label) in enumerate(zip(data['extensions'], labels), 1):
        assert row['row'] == number and row['first14'] == label
        assert len(row['masks']) == 2
        a, b = row['masks']
        assert type(a) is int and type(b) is int and 0 <= a < 4096 and 0 <= b < 4096
        for i, d in enumerate(u):
            value = ((a & phi_mask(d)).bit_count() % 2
                     + 2*((b & phi_mask(d)).bit_count() % 2))
            expected = [1,2,3][('ABC'.index(label[i % 14])+i//14) % 3]
            assert value == expected != 0
    return dict(explicit_source_patterns_extended=6, actual_direction_checks=504,
                scope='Extension of these six labelled patterns, not completeness of all global colorings')


def verify_three_tree(data):
    """Check a complete semantic coloring tree, without running a solver."""
    _, _, _, edges, _ = geometry()
    assert data['point_order'] == [f'{f}{j}' for f in 'PQR' for j in range(7)]
    assert data['edge_count'] == 42 and data['edges'] == [list(e) for e in edges]
    assert data['root_palette'] == [[0,0],[7,1],[14,2]] and data['palette_size'] == 3
    adjacency = [set() for _ in range(21)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen, pending = {0}, [0]
    while pending:
        v = pending.pop()
        for w in adjacency[v]-seen:
            seen.add(w)
            pending.append(w)
    assert len(seen) == 21  # Hence H-P0 lies in the arc-generated L1.
    for a, b in combinations((0,7,14), 2):
        assert b in adjacency[a]
    colors = {0:0, 7:1, 14:2}
    counts = [0,0]

    def walk(node):
        assert isinstance(node, dict)
        if set(node) == {'blocked_vertex'}:
            v = node['blocked_vertex']
            assert type(v) is int and 0 <= v < 21 and v not in colors
            assert {colors[w] for w in adjacency[v] if w in colors} == {0,1,2}
            counts[1] += 1
            return
        assert set(node) == {'vertex','children'}
        v, children = node['vertex'], node['children']
        assert type(v) is int and 0 <= v < 21 and v not in colors
        available = {0,1,2}-{colors[w] for w in adjacency[v] if w in colors}
        assert available and isinstance(children, dict)
        assert set(children) == {str(c) for c in available}
        counts[0] += 1
        for c in sorted(available):
            colors[v] = c
            walk(children[str(c)])
            del colors[v]

    walk(data['nodes'])
    assert counts == [193,22]
    assert data['stats'] == dict(branch_nodes=193, blocked_leaves=22, assigned_leaves=0)
    return dict(vertices=21, actual_edges=42, branches=counts[0], blocked_leaves=counts[1],
                result='H is not 3-colorable; H-P0 subset L1 and L1<=4 give chi(H)=chi(L1)=4')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions required')
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'certificates/heptagon_module.json').read_text())
    print(json.dumps(verify(data), sort_keys=True))
