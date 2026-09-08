"""One-point repair census and an escaped-field root-only coupled gate.

Search/generation only; verify_root_contact_repair.py independently replays
the geometry, all negative cases, and saved positive words.
"""
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json


def multiply(a, b):
    out = [F(0)] * 8
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            factor = 1
            for bit,p in enumerate((3,11,13)):
                if (i & j) & (1 << bit):
                    factor *= p
            out[i ^ j] += factor*x*y
    return tuple(out)


def quadrance(a,b):
    delta = [tuple(x-y for x,y in zip(aa,bb)) for aa,bb in zip(a,b)]
    return tuple(x+y for x,y in zip(multiply(delta[0],delta[0]), multiply(delta[1],delta[1])))


def extensions(edges, boundary, blocks):
    """Enumerate each 7-point block and then join against every actual edge."""
    groups = []
    for block in blocks:
        local = {v:i for i,v in enumerate(block)}
        inner = [(local[a],local[b]) for a,b in edges if a in local and b in local]
        lists = []
        for v in block:
            forbidden = {boundary[b if a == v else a] for a,b in edges
                         if v in (a,b) and (b if a == v else a) in boundary}
            lists.append(sorted(set(range(5)) - forbidden))
        groups.append([dict(zip(block,w)) for w in product(*lists)
                       if all(w[a] != w[b] for a,b in inner)])
    joint = []
    for parts in product(*groups):
        word = dict(boundary)
        for part in parts:
            word.update(part)
        if all(word[a] != word[b] for a,b in edges):
            joint.append([word[v] for v in range(len(word))])
    return groups, joint


def build(root):
    source = json.loads((root/'certificates/coupled_gate.json').read_text())
    edges = [tuple(e) for e in source['unit_edges']]
    mapping = {tuple(ref):i for i,refs in enumerate(source['occurrences']) for ref in refs}
    blocks = [[mapping[p,i] for i in range(7)] for p in range(2)]
    boundary = {int(v):c for v,c in source['boundary_coloring'].items()}
    census = []
    for v in sorted(boundary):
        for fresh in (1,2):
            changed = dict(boundary); changed[v] = fresh
            groups,joint = extensions(edges,changed,blocks)
            census.append(dict(vertex=v, new_color=fresh,
                               standalone_counts=list(map(len,groups)),
                               joint_count=len(joint), witness=joint[0] if joint else None))
    assert len(census) == 52 and sum(c['joint_count'] > 0 for c in census) == 48

    base = json.loads((root/'certificates/spindle_pair_gate.json').read_text())
    pts = [tuple(tuple(F(x) for x in axis)+(F(0),)*4 for axis in p) for p in base['points']]
    # Rational rotation with parameter 3: cos=-4/5, sin=3/5.
    c,s = F(-4,5), F(3,5)
    shift = [(F(5,8),)+(F(0),)*7, (F(0),)*5+(F(1,8),)+(F(0),)*2]
    new = []
    for x,y in pts:
        new.append((tuple(c*a-s*b+t for a,b,t in zip(x,y,shift[0])),
                    tuple(s*a+c*b+t for a,b,t in zip(x,y,shift[1]))))
    pts += new
    assert len(set(pts)) == 42
    unit = (F(1),)+(F(0),)*7
    all_edges = [(a,b) for a,b in combinations(range(42),2) if quadrance(pts[a],pts[b]) == unit]
    local = [tuple(e) for e in base['induced_edges']]
    assert set(all_edges) == set(local) | {(a+21,b+21) for a,b in local} | {(0,21)}
    b = {}
    for pose in range(2):
        for i in range(7):
            b[pose*21+7+2*i],b[pose*21+8+2*i] = (1,2) if i == 0 else (0,2)
    blocks = [list(range(7)),list(range(21,28))]
    groups,joint = extensions(all_edges,b,blocks)
    assert list(map(len,groups)) == [24,24] and not joint
    fixed = dict(b); fixed[9] = 4
    _,repaired = extensions(all_edges,fixed,blocks)
    assert repaired
    four = base['four_coloring'] + [1 if x == 0 else 0 if x == 1 else x for x in base['four_coloring']]
    assert all(four[a] != four[b] for a,b in all_edges)
    return dict(schema=1, coupled_one_point_census=census, escaped_root_pair=dict(
        radicals=[1,3,11,33,13,39,143,429],
        points=[[[str(x) for x in axis] for axis in p] for p in pts],
        edges=all_edges, boundary=b, original_standalone_counts=list(map(len,groups)),
        original_joint_count=0, repair_vertex=9, repair_color=4,
        repaired_word=repaired[0], unrestricted_four_word=four))


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    data = build(root)
    (root/'certificates/root_contact_repair.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(single_edits=52, repairable_edits=48,
                         escaped_vertices=42, escaped_edges=65, escaped_cross_edges=1)))
