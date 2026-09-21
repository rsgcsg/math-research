"""T133-T134/E103-E104 witness builder; not a proof checker.

The finite S3 permutations were found by a bounded subgroup-automaton search.
Rebuilding the saved witness does not need a SAT solver. All coordinates and
partial maps are rebuilt from the existing exact geometry. Run the independent
verify_finite_frame_separation.py to validate these certificates.
"""
from collections import deque
from pathlib import Path
import gzip
import hashlib
import json
import math
from verify_joint_nilpotent_cover import prepare
from verify_quintic_core_probe import RAD, conjugate_twice

ID = [0, 1, 2]
TRANSP = [1, 0, 2]
# Each row describes the three-sheet permutation above the five base vertices.
S3 = [
    [TRANSP] * 5,
    [TRANSP, ID, ID, ID, TRANSP],
    [ID] * 5, [ID] * 5, [TRANSP] * 5,
    [[2,1,0], [2,1,0], [0,2,1], [0,2,1], [2,1,0]],
    [ID] * 5,
    [[0,2,1], [1,2,0], [2,1,0], [2,0,1], [1,2,0]],
    [ID] * 5, [ID] * 5, [ID] * 5, [ID] * 5,
    [[1,2,0], [2,0,1], [2,0,1], [1,2,0], [1,2,0]],
    [ID] * 5,
]

def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()

def composition(a, b):
    return tuple(a[b[i]] for i in range(len(a)))

def group_closure(generators, k):
    group = {tuple(range(k))}; queue = deque(group)
    while queue:
        a = queue.popleft()
        for b in generators:
            c = composition(b, a)
            if c not in group:
                group.add(c); queue.append(c)
    return sorted(group)

def build(prepared):
    old = prepared['old']; maps = prepared['maps']; points = prepared['context']['points']
    n = len(points); sigma = old['word_permutations']; pi = old['color_permutations']
    edges = [[] for _ in range(n * 25)]
    for j, mapping in enumerate(maps[:14]):
        for a in range(5):
            b = sigma[j][a]; fiber = S3[j][a]
            reverse = [fiber.index(i) for i in range(3)]
            for p, q in mapping:
                for c in range(5):
                    x = (a*n+p)*5+c; y = (b*n+q)*5+pi[j][a][c]
                    edges[x].append((y, fiber)); edges[y].append((x, reverse))
    root = 27786; target = 1191; values = {root: 0}; queue = deque([root])
    while queue:
        x = queue.popleft()
        for y, permutation in edges[x]:
            v = permutation[values[x]]
            if y in values:
                if values[y] != v:
                    raise ValueError('Saved permutations do not factor the whole component')
            else:
                values[y] = v; queue.append(y)
    if values[target] == 0:
        raise ValueError('Saved cover does not separate the requested lifts')
    separator = dict(
        schema='finite-frame-separator-v1', experiment='E103',
        geometry=prepared['report']['geometry'], source_sha256=prepared['source_sha256'],
        permutations=S3, root=root, target=target,
        component_labels=[[x, values[x]] for x in sorted(values)],
        expected=dict(component_vertices=24235, directed_component_edges=117150,
                      cover_degree=3, monodromy_order=6, literal_classes=2048,
                      proper_clauses=14563, forced_literals=195,
                      unequal_counts=[12,0], support=15),
        scope='One specified S3 cover: equality separation succeeds; proper clauses still exclude u-joint.')
    del edges
    p = 5701
    squares = {x*x % p: x for x in range(p//2, 0, -1)}
    eta = next(pow(x, (p-1)//5, p) for x in range(2,p) if pow(x, (p-1)//5, p) != 1)
    roots = {r: squares[r % p] for r in [3,11,-1]}
    roots[5] = (2*(eta+pow(eta,-1,p))+1) % p
    images = []
    for imaginary in range(2):
        for rad in RAD:
            x = roots[-1] if imaginary else 1
            for r in [3,5,11]:
                if rad % r == 0:
                    x = x*roots[r] % p
            images.append(x)
    images += [eta*x % p for x in images[:16]]
    bars = [sum(x*y for x,y in zip(conjugate_twice([int(i==j) for i in range(32)]), images))*pow(2,-1,p) % p
            for j in range(32)]
    coords = [[sum((x.numerator*pow(x.denominator,-1,p) % p)*y for x,y in zip(v, embedding)) % p
               for embedding in [images,bars]] for v in points]
    actions = []
    for j, mapping in enumerate(maps):
        reflected = j in (4,13)
        for (x,y),(xx,yy) in zip(mapping,mapping[1:]):
            a,b = coords[x]; aa,bb = coords[xx]
            if reflected:
                a,b=b,a; aa,bb=bb,aa
            if aa==a:
                continue
            scale=(coords[yy][0]-coords[y][0])*pow(aa-a,-1,p)%p
            if not scale:
                continue
            shift=[(coords[y][0]-scale*a)%p, (coords[y][1]-pow(scale,-1,p)*b)%p]
            actions.append(dict(scale=scale,shift=shift,reflection=reflected)); break
        else:
            raise ValueError('No affine interpolation pair')
    gauge={0:tuple(range(5))}
    while len(gauge)<5:
        before=len(gauge)
        for a in range(4):
            b=sigma[2][a]
            if a in gauge:
                gauge[b]=composition(pi[2][a],gauge[a])
            if b in gauge:
                gauge[a]=composition(tuple(pi[2][a].index(c) for c in range(5)),gauge[b])
        if len(gauge)==before:
            raise ValueError('Chosen base tree is disconnected')
    gauge=[list(gauge[a]) for a in range(5)]
    generators=[composition(tuple(gauge[sigma[j][a]].index(c) for c in range(5)),
                            composition(pi[j][a],gauge[a])) for j in range(14) for a in range(5)]
    palette=group_closure(generators,5)
    frame=dict(schema='arithmetic-frame-separation-v1',experiment='E104',
               geometry=prepared['report']['geometry'],source_sha256=prepared['source_sha256'],
               prime=p,images=images,bars=bars,actions=actions,gauge=gauge,
               palette_group=palette,coordinate_sha256=digest(coords),
               expected=dict(injective_points=10077,palette_order=24,palette_fixed_colors=[4],
                             derived_orders=[24,12,4,1],motion_domains=list(map(len,maps)),
                             affine_group_order=2*p*p*(p-1),
                             cover_states=5*2*p*p*(p-1)*24),
               scope='Symbolic finite solvable cover; injective same-state literal invariant for all 15 equation systems. No new proper 15-domain law.')
    return separator,frame

def canonical(data):
    return (json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode()

def canonical_gzip(raw):
    # CPython 3.11/3.12 may delegate mtime=0 to zlib and emit OS=3.
    # The saved certificate uses OS=255; this header byte is not mathematical data.
    compressed = gzip.compress(raw, mtime=0)
    return compressed[:9] + bytes([255]) + compressed[10:]


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args(); root=Path(__file__).resolve().parents[1]
    destination=args.output_dir or root/'certificates'; destination.mkdir(parents=True,exist_ok=True)
    prepared=prepare(root)
    for data,name in zip(build(prepared),['finite_frame_separator.json.gz','arithmetic_frame_separation.json']):
        raw=canonical(data)
        if name.endswith('.gz'):
            raw=canonical_gzip(raw)
        (destination/name).write_bytes(raw)
        print(json.dumps(dict(status='BUILT',file=name,sha256=hashlib.sha256(raw).hexdigest())))

if __name__=='__main__':
    main()
