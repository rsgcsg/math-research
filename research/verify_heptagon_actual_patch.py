"""Rebuild the radius-two L2 patch using Phi_21, independently of search.

All unit directions are complete by T150; finite edges are obtained by exact
integer-vector membership, not by floating point or an assumed short window.
"""
from fractions import Fraction
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json

from verify_heptagon_module import geometry, TENSOR_BASIS, ONE, mul, norm


def digest(value):
    return sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def inverse_basis():
    rows = [[TENSOR_BASIS[j][i] for j in range(12)]
            + [Fraction(i == j) for j in range(12)] for i in range(12)]
    for j in range(12):
        k = next(k for k in range(j,12) if rows[k][j])
        rows[k], rows[j] = rows[j], rows[k]
        p = rows[j][j]
        rows[j] = [x/p for x in rows[j]]
        for k in range(12):
            if k != j:
                p = rows[k][j]
                rows[k] = [a-p*b for a,b in zip(rows[k], rows[j])]
    assert all(x.denominator == 1 for row in rows for x in row)
    return [[int(x) for x in row[12:]] for row in rows]


def rebuild():
    r, mu, _, _, _ = geometry()
    directions, power = set(), ONE
    for _ in range(3):
        directions.update(mul(power,d) for d in mu)
        power = mul(power,r)
    assert len(directions) == 126 and all(norm(d) == ONE for d in directions)
    assert all((49*x).denominator == 1 for d in directions for x in d)
    integer_directions = {tuple(int(49*x) for x in d) for d in directions}
    points = {(0,)*12} | integer_directions
    points.update(tuple(a+b for a,b in zip(u,v)) for u in integer_directions for v in integer_directions)
    matrix = inverse_basis()
    def tensor(p):
        return tuple(sum(a*b for a,b in zip(row,p)) for row in matrix)
    pairs = sorted((tensor(p),p) for p in points)
    tensor_points, phi_points = zip(*pairs)
    assert len(set(tensor_points)) == len(points)
    index = {p:i for i,p in enumerate(phi_points)}
    edges = []
    for i,p in enumerate(phi_points):
        for d in integer_directions:
            q = tuple(a+b for a,b in zip(p,d))
            j = index.get(q)
            if j is not None and i < j:
                edges.append((i,j))
    edges.sort()
    assert len(set(edges)) == len(edges)
    return tensor_points, edges


def verify(data):
    assert data['schema'] == 'heptagon-actual-patch-v1'
    assert data['construction'] == 'B2={0} union U2 union {u+v:u,v in U2}; U2=mu42 union r*mu42 union r^2*mu42'
    assert data['field'] == 'Q(z,w), Phi_7(z)=0, w^2+w+1=0'
    assert data['basis_order'] == [f'z^{i}w^{b}' for b in range(2) for i in range(6)]
    assert data['denominator'] == 49 and data['unit_directions'] == 126
    points, edges = rebuild()
    g = data['geometry']
    assert g['vertices'] == len(points) == 7939 and g['edges'] == len(edges) == 38682
    assert g['point_list_sha256'] == digest(points)
    assert g['edge_list_sha256'] == digest(edges)
    degree = Counter(i for edge in edges for i in edge)
    assert g['max_degree'] == max(degree.values()) == 126
    triangle = g['origin_triangle_point_ids']
    assert len(set(triangle)) == 3 and points[triangle[0]] == (0,)*12
    assert g['origin_triangle_points'] == [list(points[i]) for i in triangle]
    edge_set = set(edges)
    assert all(tuple(sorted((a,b))) in edge_set for a in triangle for b in triangle if a != b)
    result = data['sat']
    assert result['colors_requested'] == 5
    assert result['symmetry_breaking'] == dict(triangle_point_ids=triangle, colors=[0,1,2])
    assert result['status'] == 'UNKNOWN' and 'word' not in result
    return dict(vertices=len(points), edges=len(edges),
                points_sha256=digest(points), edges_sha256=digest(edges),
                query_status='UNKNOWN', proper_coloring_certified=False,
                scope='Complete actual finite geometry certified using T150; no chromatic obstruction or positive coloring')


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('assertions required')
    root = Path(__file__).resolve().parents[1]
    data = json.loads(gzip.decompress((root/'certificates/heptagon_actual_patch.json.gz').read_bytes()))
    print(json.dumps(verify(data), sort_keys=True))
