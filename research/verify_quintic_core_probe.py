"""Independent stdlib checker for the actual finite E043 quintic core probe.

Does not import its producer, a search algorithm, or a SAT library. Geometry
uses doubled multiplication in a 32-dimensional quotient algebra, rather
than the producer's separated norm formula. A different split-prime map is
verified on all 1024 basis products before excluding any physical pair.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math

RAD = (1, 3, 11, 33, 5, 15, 55, 165)


def digest(data):
    return hashlib.sha256(json.dumps(data, separators=(',', ':')).encode()).hexdigest()


def f_product(i, j):
    ai, ar = divmod(i, 8)
    bi, br = divmod(j, 8)
    factor = math.gcd(RAD[ar], RAD[br])
    radicand = RAD[ar]*RAD[br]//(factor*factor)
    return 8*((ai+bi) % 2)+RAD.index(radicand), factor*(-1 if ai == bi == 1 else 1)


def multiplication_twice():
    table = {}
    for i in range(32):
        ei, fi = divmod(i, 16)
        for j in range(32):
            ej, fj = divmod(j, 16)
            f, coefficient = f_product(fi, fj)
            if ei+ej < 2:
                table[i, j] = [(16*(ei+ej)+f, 2*coefficient)]
            else:
                g, scale = f_product(f, 4)
                table[i, j] = [(f, -2*coefficient), (16+f, -coefficient),
                               (16+g, coefficient*scale)]
    return table


def conjugate_twice(a):
    result = [0]*32
    for j, coefficient in enumerate(a):
        power, f = divmod(j, 16)
        coefficient *= -1 if f >= 8 else 1
        if power == 0:
            result[f] += 2*coefficient
        else:
            g, scale = f_product(f, 4)
            result[f] -= coefficient
            result[g] += coefficient*scale
            result[16+f] -= 2*coefficient
    return result


def product_twice(a, b, table):
    result = [0]*32
    left = [(i, x) for i, x in enumerate(a) if x]
    right = [(j, x) for j, x in enumerate(b) if x]
    for i, x in left:
        for j, y in right:
            for k, coefficient in table[i, j]:
                result[k] += x*y*coefficient
    return result


def filter_map(table):
    # This deliberately uses a different prime and root construction.
    for prime in range(4001, 100000):
        if prime % 20 != 1 or any(prime % d == 0 for d in range(2, math.isqrt(prime)+1)):
            continue
        if any(pow(r, (prime-1)//2, prime) != 1 for r in (3, 11)):
            continue
        break
    else:
        raise AssertionError('Missing verification prime')
    eta = next(pow(x, (prime-1)//5, prime) for x in range(2, prime)
               if pow(x, (prime-1)//5, prime) != 1)
    roots = {r: next(x for x in range(1, prime) if x*x % prime == r % prime)
             for r in (3, 11, -1)}
    roots[5] = (2*(eta+pow(eta, -1, prime))+1) % prime
    assert roots[5]*roots[5] % prime == 5
    assert eta != 1 and pow(eta, 5, prime) == 1
    field = []
    for imaginary in range(2):
        for radicand in RAD:
            image = roots[-1] if imaginary else 1
            for r in (3, 5, 11):
                if radicand % r == 0:
                    image = image*roots[r] % prime
            field.append(image)
    images = field+[eta*x % prime for x in field]
    assert all(sum(c*images[k] for k, c in row) % prime == 2*images[i]*images[j] % prime
               for (i, j), row in table.items())
    bars = []
    for i in range(32):
        vector = [int(i == j) for j in range(32)]
        bars.append(sum(x*y for x, y in zip(conjugate_twice(vector), images))*pow(2, -1, prime) % prime)
    assert all(images[i]*bars[i] % prime == RAD[i % 8] % prime for i in range(32))
    return prime, images, bars


def geometry(core, centers, table):
    den = core['coordinate_denominator']
    base = [tuple(x+y+[0]*16) for x, y in core['points']]
    copies_raw = [base]
    eta = [int(j == 16) for j in range(32)]
    for center in centers:
        copy = []
        for point in base:
            shifted = [x-y for x, y in zip(point, base[center])]
            doubled = product_twice(eta, shifted, table)
            assert all(x % 2 == 0 for x in doubled)
            copy.append(tuple(x//2+y for x, y in zip(doubled, base[center])))
        copies_raw.append(copy)
    points = sorted(set(point for copy in copies_raw for point in copy))
    index = {point: i for i, point in enumerate(points)}
    copies = [[index[point] for point in copy] for copy in copies_raw]
    owners = [{} for _ in points]
    for i, copy in enumerate(copies):
        for j, point in enumerate(copy):
            owners[point][i] = j
    prime, images, bars = filter_map(table)
    projected = [(sum(a*b for a, b in zip(point, images)) % prime,
                  sum(a*b for a, b in zip(point, bars)) % prime) for point in points]
    target = [4*den*den]+[0]*31
    edges, survivors = [], 0
    for i, j in combinations(range(len(points)), 2):
        a, abar = projected[i]
        b, bbar = projected[j]
        if ((a-b)*(abar-bbar)-den*den) % prime:
            continue
        survivors += 1
        delta = [a-b for a, b in zip(points[i], points[j])]
        if product_twice(delta, conjugate_twice(delta), table) == target:
            edges.append((i, j))
    internal = [edge for edge in edges if owners[edge[0]].keys() & owners[edge[1]].keys()]
    return points, copies, owners, edges, dict(vertices=len(points),
               actual_pairs=len(points)*(len(points)-1)//2, induced_edges=len(edges),
               copy_edges=len(internal), new_cross_edges=len(edges)-len(internal),
               point_sha256=digest(points), edge_sha256=digest(edges)), prime, survivors


def verify(root, certificate=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions; do not use python -O')
    path = certificate or root/'certificates/quintic_core_probe.json'
    data = json.loads(path.read_text())
    assert data['schema'] == 1 and data['experiment'] == 'E043'
    assert data['base_radicals'] == list(RAD)
    assert data['coordinate_denominator'] == 96
    centers = data['centers']
    assert centers in ([0], [0, 153], [0, 153, 150])
    raw = (root/'certificates/parts509_core.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == data['core_sha256']
    core = json.loads(raw)
    assert core['coordinate_denominator'] == 96 and len(core['points']) == 509
    assert all(type(x) is int for point in core['points'] for axis in point for x in axis)
    zero = [0]*8
    assert core['points'][0] == [zero, zero]
    assert core['points'][153] == [[96]+[0]*7, zero]
    assert core['points'][150] == [[48]+[0]*7, [0, 48]+[0]*6]
    table = multiplication_twice()
    points, copies, owners, edges, summary, prime, survivors = geometry(core, centers, table)
    assert all(data['geometry'][key] == value for key, value in summary.items())
    assert summary['vertices'] == 509+508*len(centers)
    assert summary['copy_edges'] == 2442*len(copies)
    edge_set = set(edges)
    base_edges = {tuple(sorted((owners[a][0], owners[b][0]))) for a, b in edges
                  if 0 in owners[a] and 0 in owners[b]}
    assert len(base_edges) == 2442 and base_edges == set(map(tuple, core['induced_edges']))
    assert all(tuple(sorted((copy[a], copy[b]))) in edge_set
               for copy in copies for a, b in base_edges)
    status = data['search']['status']
    assert status in ('SAT', 'UNKNOWN', 'UNSAT_SEARCH_ONLY')
    if status == 'SAT':
        word = data['search']['five_coloring']
        assert isinstance(word, str) and len(word) == len(points) and set(word) <= set('01234')
        assert all(word[a] != word[b] for a, b in edges)
    else:
        assert 'five_coloring' not in data['search']

    mechanism = data['mechanism']
    frames = mechanism.get('reference_color_frames')
    if frames is not None:
        assert mechanism['frame_status'] == 'SAT'
        assert len(frames) == len(copies) and all(sorted(frame) == list(range(5)) for frame in frames)
        old_word = core['five_coloring']
        assert len(old_word) == 509 and all(type(c) is int and 0 <= c < 5 for c in old_word)
        image_colors = []
        for owner in owners:
            allowed = {frames[i][old_word[j]] for i, j in owner.items()}
            assert len(allowed) == 1
            image_colors.append(allowed.pop())
        assert all(image_colors[a] != image_colors[b] for a, b in edges)
    projection_checked = False
    if 'unit_graph_projection' in mechanism:
        assert all(len(set(owner.values())) == 1 for owner in owners)
        projection = [next(iter(owner.values())) for owner in owners]
        assert all(tuple(sorted((projection[a], projection[b]))) in base_edges for a, b in edges)
        counts = {}
        for a, b in edges:
            if owners[a].keys() & owners[b].keys():
                continue
            for i in owners[a]:
                for j in owners[b]:
                    key = ','.join(map(str, sorted((i, j))))
                    counts[key] = counts.get(key, 0)+1
        assert mechanism['new_cross_edges_by_copy_pair'] == counts
        projection_checked = True
    return dict(status='VERIFIED_FINITE_QUINTIC_CORE_FIVE_COLORING' if status == 'SAT' else
                       'VERIFIED_GEOMETRY_ONLY_NO_NEGATIVE_COLORING_CERTIFICATE',
                **summary, verification_filter_prime=prime, exact_filter_survivors=survivors,
                verified_basis_products=len(table),
                reference_frames_verified=frames is not None, core_graph_projection_verified=projection_checked,
                scope='Finite induced graph only. The lower bound five relies on the separately replayed Parts certificate.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.certificate), indent=2))
