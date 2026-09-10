"""E046: attach a whole Parts copy across the C017 nonunit anchor pair.

Exact geometry and free five-color search. A separate checker reconstructs
the bridge and all actual unit pairs without importing this module or SAT.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import math
from quintic_core_probe import geometry, digest
from quintic_congruence_probe import embedding, norm2
from quintic_mixed_congruence_probe import product2, conjugate2, subtract


def run(root, budget=100000):
    from pysat.solvers import Solver
    raw = (root/'certificates/parts509_core.json').read_bytes()
    core = json.loads(raw)
    old, copies, old_edges, _ = geometry(core,[0,153,150],[1])
    base = [tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    a,b = [tuple(Q(x,96) for x in old[i]) for i in (84,337)]
    u,v = base[332],base[451]
    inverse_length = [Q(0)]*32
    inverse_length[0],inverse_length[4] = Q(3,2),Q(3,10)
    rotation = tuple(Q(x)/8 for x in product2(
        product2(subtract(b,a),conjugate2(subtract(v,u))),inverse_length))
    assert norm2(rotation) == (Q(2),)+(Q(0),)*31
    bridge = [tuple(x+Q(y)/2 for x,y in zip(a,product2(rotation,subtract(w,u)))) for w in base]
    assert bridge[332] == a and bridge[451] == b
    old_q = [tuple(Q(x,96) for x in point) for point in old]
    denominator = math.lcm(*(x.denominator for point in old_q+bridge for x in point))
    points = sorted({tuple(int(x*denominator) for x in point) for point in old_q+bridge})
    index = {p:i for i,p in enumerate(points)}
    old_ids = [index[tuple(int(x*denominator) for x in point)] for point in old_q]
    bridge_ids = [index[tuple(int(x*denominator) for x in point)] for point in bridge]
    prime,images,bars = embedding(10**6)
    assert denominator % prime
    residues = [(sum(x*y for x,y in zip(point,images)) % prime,
                 sum(x*y for x,y in zip(point,bars)) % prime) for point in points]
    edges = []
    target = (2*denominator**2,)+(0,)*31
    for i,j in combinations(range(len(points)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-denominator**2) % prime:
            continue
        if norm2(subtract(points[i],points[j])) == target:
            edges.append((i,j))
    inherited = {tuple(sorted((old_ids[i],old_ids[j]))) for i,j in old_edges}
    inherited.update(tuple(sorted((bridge_ids[i],bridge_ids[j]))) for i,j in core['induced_edges'])
    assert inherited <= set(edges)
    summary = dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,
                   induced_edges=len(edges),inherited_edges=len(inherited),
                   extra_bridge_edges=len(set(edges)-inherited),
                   overlap=len(set(old_ids)&set(bridge_ids)),
                   point_sha256=digest(points),edge_sha256=digest(edges))
    print(json.dumps(dict(stage='geometry',**summary)),flush=True)
    # Continue E045's positive law through the complete new Parts copy.
    # Matching the equality partition at the two shared vertices suffices
    # because the actual graph has no extra bridge edges.
    repair_raw = (root/'certificates/quintic_congruence_gap.json').read_bytes()
    core_word = json.loads(repair_raw)['repairing_core_word']
    assert core_word[332] == core_word[451]
    source_color,target_color = int(core_word[332]),int(core_word[64])
    palette = list(range(5))
    palette[source_color],palette[target_color] = palette[target_color],palette[source_color]
    repaired = [None]*len(points)
    old_owners = {v:j for copy in copies for j,v in enumerate(copy)}
    for i,v in enumerate(old_ids):
        repaired[v] = int(core_word[old_owners[i]])
    for j,v in enumerate(bridge_ids):
        c = palette[int(core_word[j])]
        assert repaired[v] is None or repaired[v] == c
        repaired[v] = c
    assert all(repaired[a] != repaired[b] for a,b in edges)
    clauses = [[5*v+c+1 for c in range(5)] for v in range(len(points))]
    clauses += [[-5*v-a-1,-5*v-b-1] for v in range(len(points)) for a,b in combinations(range(5),2)]
    clauses += [[-5*a-c-1,-5*b-c-1] for a,b in edges for c in range(5)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        search = dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',
                      conflict_budget=budget,stats=solver.accum_stats())
        if answer is True:
            model = set(x for x in solver.get_model() if x > 0)
            search['five_coloring'] = ''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(len(points)))
    return dict(schema=1,experiment='E046',core_sha256=hashlib.sha256(raw).hexdigest(),
                source_sha256=hashlib.sha256((root/'certificates/quintic_core_probe.json').read_bytes()).hexdigest(),
                source_anchors=[332,451],target_anchors=[84,337],coordinate_denominator=denominator,
                geometry=summary,search=search,
                repair=dict(source_sha256=hashlib.sha256(repair_raw).hexdigest(),
                            bridge_palette=palette,five_coloring=''.join(map(str,repaired))),
                scope='One precisely specified finite induced graph; no full joint or HN bound claim')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--budget',type=int,default=100000)
    args = parser.parse_args()
    result = run(Path(__file__).resolve().parents[1],args.budget)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
