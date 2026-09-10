"""Bounded exact search for mixed partial congruences in E043.

The two specified anchor lengths are a search restriction, not a completeness
claim about all partial congruences. Modular motions only propose exact maps.
"""
from itertools import combinations
from pathlib import Path
import argparse
import json
from quintic_congruence_probe import embedding, norm2
from quintic_core_probe import geometry, mul, bar, t2mul


def subtract(a, b):
    return tuple(x-y for x, y in zip(a, b))


def product2(a, b):
    u, v = a[:16], a[16:]
    s, t = b[:16], b[16:]
    us, vt, ut, vs = mul(u,s), mul(v,t), mul(u,t), mul(v,s)
    return tuple(2*(x-y) for x,y in zip(us,vt)) + tuple(
        2*x+2*y+z for x,y,z in zip(ut,vs,t2mul(vt)))


def conjugate2(a):
    u, v = bar(a[:16]), bar(a[16:])
    return tuple(2*x+y for x,y in zip(u,t2mul(v))) + tuple(-2*x for x in v)


def descent_failure(mapping, owners, base):
    """Return at most four correspondences witnessing failure, or None.

    Two distinct projected source points determine two Euclidean isometries.
    If both fail, one witness for each plus the anchors suffices. Recheck all
    six distances in that set so that the returned disagreement is explicit.
    """
    projected = [(base[owners[i]],base[owners[j]]) for i,j in mapping]
    a,u = projected[0]
    second = next((j for j,(b,v) in enumerate(projected) if b != a),None)
    if second is None:
        return next(([mapping[0],mapping[j]] for j,(b,v) in enumerate(projected) if v != u),None)
    b,v = projected[second]
    ab,uv = subtract(b,a),subtract(v,u)
    if norm2(ab) != norm2(uv):
        return [mapping[0],mapping[second]]
    failures = []
    for reflection in (False,True):
        direction = conjugate2(ab) if reflection else ab
        for j,(x,y) in enumerate(projected):
            ax = subtract(x,a)
            if reflection:
                ax = conjugate2(ax)
            if product2(subtract(y,u),direction) != product2(uv,ax):
                failures.append(j)
                break
        else:
            return None
    ids = list(dict.fromkeys([0,second]+failures))
    assert any(norm2(subtract(projected[i][0],projected[j][0])) !=
               norm2(subtract(projected[i][1],projected[j][1])) for i,j in combinations(ids,2))
    return [mapping[j] for j in ids]


def run(root, anchors=None):
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    points, copies, _, _ = geometry(core,[0,153,150],[1])
    owners = {v:j for copy in copies for j,v in enumerate(copy)}
    base = [tuple(x+y+[0]*16) for x,y in core['points']]
    p, f, b = embedding(10**6)
    residues = [tuple(sum(x*y for x,y in zip(v,w)) % p for w in (f,b)) for v in points]
    index = {}
    for i,r in enumerate(residues):
        index.setdefault(r,[]).append(i)
    def key(i,j):
        return (residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1]) % p
    examined = 0
    for a,b in (anchors or [(84,337),(0,337)]):
        assert 0 <= a < len(points) and 0 <= b < len(points) and a != b
        length = norm2(subtract(points[a],points[b]))
        targets = [(u,v) for u,v in combinations(range(len(points)),2)
                   if key(u,v) == key(a,b) and norm2(subtract(points[u],points[v])) == length]
        for u,v in targets:
            for u,v in ((u,v),(v,u)):
                for reflection in (False,True):
                    source = residues[a][::-1] if reflection else residues[a]
                    end = residues[b][::-1] if reflection else residues[b]
                    factors = [(residues[v][j]-residues[u][j])*pow((end[j]-source[j]) % p,-1,p) % p for j in (0,1)]
                    ab = subtract(points[b],points[a])
                    if reflection:
                        ab = conjugate2(ab)
                    uv = subtract(points[v],points[u])
                    mapping = []
                    for i,r in enumerate(residues):
                        if reflection:
                            r = r[::-1]
                        target = tuple((residues[u][j]+factors[j]*(r[j]-source[j])) % p for j in (0,1))
                        for j in index.get(target,()):
                            ai = subtract(points[i],points[a])
                            if reflection:
                                ai = conjugate2(ai)
                            if product2(subtract(points[j],points[u]),ab) == product2(uv,ai):
                                mapping.append((i,j))
                    examined += 1
                    if len(mapping) < 4:
                        continue
                    chosen = descent_failure(mapping,owners,base)
                    if chosen:
                        chosen += [pair for pair in mapping if pair not in chosen][:4-len(chosen)]
                        return dict(status='MIXED_FOUR_POINT_WITNESS',anchors=[[a,b],[u,v]],
                                    reflection=reflection,partial_map=chosen,
                                    projected_map=[[owners[x],owners[y]] for x,y in chosen],
                                    full_motion_intersection=len(mapping),motions_examined=examined,
                                    scope='Exact positive witness only; not a coloring obstruction')
        print(json.dumps(dict(stage='anchor_length_complete',anchors=[a,b],targets=len(targets),motions_examined=examined)),flush=True)
    return dict(status='NO_FOUR_POINT_DESCENT_FAILURE_FOUND',motions_examined=examined,
                scope='Only specified source anchors tested; not all congruences')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--anchor',nargs=2,type=int,action='append',
                        help='Physical E043 anchor IDs; repeat for a bounded family')
    args = parser.parse_args()
    print(json.dumps(run(Path(__file__).resolve().parents[1],args.anchor),indent=2))
