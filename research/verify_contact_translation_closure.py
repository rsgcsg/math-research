"""Independent exact checker for T069/T070 and the new E035 finite probe.

No search-side module or SAT solver is imported. Completeness of the finite
cross-layer compilation uses the explicitly checked quadratic shell equations;
the infinite separation theorem is a written proof, not an extrapolation.
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math

RAD = (1, 3, 11, 33, 5, 15, 55, 165)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def multiplication(rad):
    return {(i, j): (rad.index(a*b//math.gcd(a, b)**2), math.gcd(a, b))
            for i, a in enumerate(rad) for j, b in enumerate(rad)}


def squared_distance(p, q, table):
    result = [0]*len(p[0])
    for ax, bx in zip(p, q):
        delta = [(i, a-b) for i, (a, b) in enumerate(zip(ax, bx)) if a != b]
        for i, a in delta:
            for j, b in delta:
                k, factor = table[i, j]
                result[k] += a*b*factor
    return result


def verify_old(core, data):
    assert data == dict(q=23, first=13, second=7,
                        trace_radius_squared=[4, 1], trace_diameter_squared=[16, 1],
                        roots3_mod23=[7, 16], shift_color='((a-b+c-d) mod3)',
                        coloring='(core_color + shift_color) mod5')
    points = core['points']
    assert len(points) == 509 and core['coordinate_denominator'] == 96
    assert max(sum(v*v*r for ax in p for v, r in zip(ax, RAD)) for p in points) == 4*96**2
    assert max(sum((a-b)**2*r for ax, bx in zip(p, q) for a, b, r in zip(ax, bx, RAD))
               for p, q in combinations(points, 2)) == 16*96**2
    assert 7 > 4+1 and math.gcd(96*13*7*2, 23) == 1
    assert [a for a in range(23) if a*a % 23 == 3] == [7, 16]
    assert all((a*a+b*b) % 23 != 0 for a, b in product(range(23), repeat=2) if (a, b) != (0, 0))
    # Two ring maps to F_23[s]/(s^2-5), with sqrt(3) = +/-7.
    assert all(a*a % 23 != 5 for a in range(23))

    def times(a, b):
        return ((a[0]*b[0]+5*a[1]*b[1]) % 23, (a[0]*b[1]+a[1]*b[0]) % 23)

    table = multiplication(RAD)
    for r3 in (7, 16):
        roots = {3: (r3, 0), 5: (0, 1), 11: (0, 4)}
        images = []
        for r in RAD:
            z = (1, 0)
            for p in (3, 5, 11):
                if r % p == 0:
                    z = times(z, roots[p])
            images.append(z)
        for (i, j), (k, factor) in table.items():
            assert times(images[i], images[j]) == tuple(factor*v % 23 for v in images[k])
    # Exact finite calibration of simultaneous divisibility; the general step
    # follows by subtracting the two signed-root equations in the written proof.
    zeros = []
    for a, b, c, d in product(range(23), repeat=4):
        if all((13*(2*a+b)-7*r*d) % 23 == 0 and (13*r*b+7*(2*c+d)) % 23 == 0 for r in (7, 16)):
            zeros.append((a, b, c, d))
    assert zeros == [(0, 0, 0, 0)]
    # All twelve nonzero translation generators change the three-color word.
    unit = [(a, b) for a, b in product(range(-1, 2), repeat=2) if a*a+a*b+b*b == 1]
    assert len(unit) == 6 and all((a-b) % 3 != 0 for a, b in unit)
    beta = F(120, 529)
    assert F(13, 23)**2+3*beta == F(7, 23)**2+4*beta == 1
    transports = 0
    for m, n in product(range(-3, 4), repeat=2):
        norm = m*m+m*n+n*n
        if norm == 3:
            a, b = F(-m-2*n, 3), F(2*m+n, 3)
        elif norm == 4:
            a, b = F(m, 2), F(n, 2)
        else:
            continue
        assert a.denominator == b.denominator == 1 and a*a+a*b+b*b == 1
        transports += 2
    assert transports == 24
    return dict(core_trace_radius_squared=4, core_trace_diameter_squared=16,
                residue_label_inputs=23**4, ring_basis_products=128,
                shell_transports=transports, scope='Finite calibration of the written infinite theorem')


def verify_probe(core, data):
    assert (data['q'], data['first'], data['second'], data['beta'], data['denominator']) == (13, 7, 3, [40, 169], 1248)
    unit = [(a, b) for a, b in product(range(-1, 2), repeat=2) if a*a+a*b+b*b == 1]
    shifts = ([(0, 0, 0, 0)]+[(a, b, 0, 0) for a, b in unit]
              +[(0, 0, a, b) for a, b in unit]+[(2, 0, 0, 0), (3, 0, 0, 0), (3, 1, 0, 0)])
    centers = [(a, b) for a, b in product(range(-1, 2), repeat=2) if a*a+a*b+b*b <= 1]
    assert data['shifts'] == list(map(list, shifts)) and data['centers'] == list(map(list, centers))
    den = data['denominator']
    points = []
    for a, b, c, d in shifts:
        translation = ((F(7, 13)*(a+F(b, 2)), -F(3*d, 26)),
                       (F(3, 13)*(c+F(d, 2)), F(7*b, 26)))
        for p in core['points']:
            point = []
            for ax, offset in zip(p, translation):
                vals = [F(v, 96) for v in ax]
                vals[0] += offset[0]
                vals[1] += offset[1]
                assert all((v*den).denominator == 1 for v in vals)
                point.append(tuple(int(v*den) for v in vals))
            points.append(tuple(point))
    assert len(points) == len(set(points)) == data['base_vertices'] == 8144
    table = multiplication(RAD)
    prime = 1031
    assert all(prime % d for d in range(2, math.isqrt(prime)+1))
    roots = {v*v % prime: v for v in range(prime)}
    images = []
    for r in RAD:
        z = 1
        for p in (3, 5, 11):
            if r % p == 0:
                z = z*roots[p] % prime
        images.append(z)
    for (i, j), (k, factor) in table.items():
        assert images[i]*images[j] % prime == factor*images[k] % prime
    residues = [tuple(sum(v*r for v, r in zip(ax, images)) % prime for ax in p) for p in points]
    base = []
    candidates = 0
    for i, j in combinations(range(len(points)), 2):
        (a, b), (c, d) = residues[i], residues[j]
        if ((a-c)**2+(b-d)**2-den*den) % prime:
            continue
        candidates += 1
        if squared_distance(points[i], points[j], table) == [den*den]+[0]*7:
            base.append((i, j))
    assert len(base) == data['base_edges'] and digest(base) == data['base_edge_sha256']
    mixed = [(i, j) for i, j in base if i//509 != j//509]
    assert len(mixed) == data['mixed_base_edges'] > 0
    assert tuple(data['mixed_witness']) in mixed
    # Named rational resonance: -e1 + (7/13)(3e1+e2).
    assert F(23, 26)**2+3*F(7, 26)**2 == 1
    assert core['points'][0] == [[0]*8, [0]*8]
    assert core['points'][166] == [[-96]+[0]*7, [0]*8]
    assert (0, 15*509+166) in mixed
    beta = F(40, 169)
    assert F(1, 7) < beta < F(1, 4)
    assert F(7, 13)**2 == 1-3*beta and F(3, 13)**2 == 1-4*beta
    assert 1-beta == F(3*43, 169) and all(43 % d for d in range(2, 7))
    assert 3*43 not in RAD  # N=1 would require this absent rational square class.
    # Geometry distinguishes the alpha coefficients, so only the classified
    # +/- t_N J delta/sqrt(N) can be cross-layer differences. Enumerate every
    # one, and then also check all retained pairs directly in the 16D field.
    lookup = {p: i for i, p in enumerate(points)}
    table16 = multiplication(RAD+tuple(2*r for r in RAD))
    physical = []
    for m, n in centers:
        for x, y in points:
            x, y = list(x)+[0]*8, list(y)+[0]*8
            x[12] += 96*(2*m+n)
            y[13] += 96*n
            physical.append((tuple(x), tuple(y)))
    assert len(physical) == len(set(physical)) == data['vertices']
    cross = []
    counts = {3: 0, 4: 0}
    covered = set()
    for i, j in combinations(range(len(centers)), 2):
        m, n = (b-a for a, b in zip(centers[i], centers[j]))
        norm = m*m+m*n+n*n
        if norm not in (3, 4):
            assert norm == 1
            continue
        for sign in (-1, 1):
            # Undirected pairs also cover the reversed center direction.
            covered.add((m, n, sign))
            covered.add((-m, -n, sign))
            if norm == 3:
                x, y = (sign*F(-7*n, 26), F(0)), (F(0), sign*F(7*(2*m+n), 78))
            else:
                x, y = (F(0), sign*F(-3*n, 52)), (sign*F(3*(2*m+n), 52), F(0))
            delta = tuple(tuple(int(den*v) for v in ax)+(0,)*6 for ax in (x, y))
            for k, p in enumerate(points):
                target = tuple(tuple(a+b for a, b in zip(ax, bx)) for ax, bx in zip(p, delta))
                if target not in lookup:
                    continue
                a, b = i*len(points)+k, j*len(points)+lookup[target]
                assert squared_distance(physical[a], physical[b], table16) == [den*den]+[0]*15
                cross.append((a, b))
                counts[norm] += 1
    assert counts == {int(k): v for k, v in data['cross_edges_by_shell'].items()}
    assert all(counts.values())
    assert covered == {(m, n, sign) for m, n in product(range(-3, 4), repeat=2)
                       if m*m+m*n+n*n in (3, 4) for sign in (-1, 1)}
    edges = sorted([(z*len(points)+i, z*len(points)+j) for z in range(len(centers)) for i, j in base]+cross)
    assert len(edges) == len(set(edges)) == data['edges'] and digest(edges) == data['edge_sha256']
    assert data['status'] == 'SAT_WITNESS'  # UNKNOWN must not be silently upgraded.
    word = data['five_word']
    assert isinstance(word, str) and len(word) == len(physical) and set(word) <= set('01234')
    assert all(word[a] != word[b] for a, b in edges)
    target = sorted(set(base)|{tuple(sorted((i % len(points), j % len(points)))) for i, j in cross})
    assert len(target) == data['all_center_target_edges'] and digest(target) == data['target_edge_sha256']
    frames = data['frame_word']
    assert isinstance(frames, str) and len(frames) == 80
    assert all(set(frames[i:i+5]) == set('01234') for i in range(0, 80, 5))
    one_layer = ''.join(frames[5*(i//509)+core['five_coloring'][i % 509]] for i in range(len(points)))
    assert word == one_layer*len(centers)
    assert all(one_layer[i] != one_layer[j] for i, j in target)
    frame_edges = {tuple(sorted((5*(i//509)+core['five_coloring'][i % 509],
                                5*(j//509)+core['five_coloring'][j % 509]))) for i, j in target}
    assert len(frame_edges) == data['frame_edges'] and all(frames[i] != frames[j] for i, j in frame_edges)
    return dict(vertices=len(physical), edges=len(edges),
                distinct_base_pairs=len(points)*(len(points)-1)//2,
                base_radical_candidates=candidates, mixed_base_edges=len(mixed),
                cross_edges_by_shell=counts, induced_five_coloring=True,
                all_center_target_edges=len(target), frame_edges=len(frame_edges),
                scope='Specified 16-translation infinite array exactly five; full denominator-13 host remains between five and six')


def verify(root, data_override=None):
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled when checking certificates')
    data = data_override if data_override is not None else json.loads((root/'certificates/contact_translation_closure.json').read_text())
    assert data['schema'] == 1
    raw = (root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == data['core_sha256']
    core = json.loads(raw)
    return dict(old_closure=verify_old(core, data['old']), new_probe=verify_probe(core, data['probe']))


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
