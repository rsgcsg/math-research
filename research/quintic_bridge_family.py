"""E047: all six C017 Parts bridges, with exact induced geometry."""
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

PAIRS = [(332,451),(133,377),(379,129),(330,449),(447,328),(381,131)]


def build(root):
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    old,copies,old_edges,_ = geometry(core,[0,153,150],[1])
    old_q = [tuple(Q(x,96) for x in p) for p in old]
    base = [tuple(Q(x,96) for x in a+b+[0]*16) for a,b in core['points']]
    a,b = [old_q[i] for i in (84,337)]
    inverse = [Q(0)]*32
    inverse[0],inverse[4] = Q(3,2),Q(3,10)
    bridges = []
    for ui,vi in PAIRS:
        u,v = base[ui],base[vi]
        r = tuple(Q(x)/8 for x in product2(product2(subtract(b,a),conjugate2(subtract(v,u))),inverse))
        assert norm2(r) == (Q(2),)+(Q(0),)*31
        bridge = [tuple(x+Q(y)/2 for x,y in zip(a,product2(r,subtract(w,u)))) for w in base]
        assert bridge[ui] == a and bridge[vi] == b
        bridges.append(bridge)
    all_q = old_q+[p for bridge in bridges for p in bridge]
    denominator = math.lcm(*(x.denominator for p in all_q for x in p))
    def integer(p): return tuple(int(x*denominator) for x in p)
    points = sorted({integer(p) for p in all_q})
    index = {p:i for i,p in enumerate(points)}
    old_ids = [index[integer(p)] for p in old_q]
    bridge_ids = [[index[integer(p)] for p in bridge] for bridge in bridges]
    prime,images,bars = embedding(10**6)
    assert denominator % prime
    residues = [(sum(x*y for x,y in zip(p,images)) % prime,
                 sum(x*y for x,y in zip(p,bars)) % prime) for p in points]
    target = (2*denominator**2,)+(0,)*31
    edges = []
    for i,j in combinations(range(len(points)),2):
        if ((residues[i][0]-residues[j][0])*(residues[i][1]-residues[j][1])-denominator**2) % prime:
            continue
        if norm2(subtract(points[i],points[j])) == target:
            edges.append((i,j))
    old_set,bridge_set = set(old_ids),set().union(*map(set,bridge_ids))
    inherited = {tuple(sorted((old_ids[i],old_ids[j]))) for i,j in old_edges}
    for copy in bridge_ids:
        inherited.update(tuple(sorted((copy[i],copy[j]))) for i,j in core['induced_edges'])
    assert inherited <= set(edges)
    extra = set(edges)-inherited
    cross = [e for e in edges if not (set(e)<=old_set or set(e)<=bridge_set)]
    summary = dict(vertices=len(points),actual_pairs=len(points)*(len(points)-1)//2,
                   induced_edges=len(edges),inherited_edges=len(inherited),extra_edges=len(extra),
                   old_bridge_cross_edges=len(cross),bridge_union_vertices=len(bridge_set),
                   bridge_union_edges=sum(set(e)<=bridge_set for e in edges),
                   old_bridge_overlap=len(old_set&bridge_set),
                   pair_overlaps=[[i,j,len(set(bridge_ids[i])&set(bridge_ids[j]))] for i,j in combinations(range(6),2)],
                   point_sha256=digest(points),edge_sha256=digest(edges))
    return core,points,edges,old_ids,bridge_ids,denominator,summary


def run(root,budget=100000):
    from pysat.solvers import Solver
    core,points,edges,old_ids,bridge_ids,den,summary = build(root)
    print(json.dumps(dict(stage='geometry',**summary)),flush=True)
    clauses = [[5*v+c+1 for c in range(5)] for v in range(len(points))]
    clauses += [[-5*v-a-1,-5*v-b-1] for v in range(len(points)) for a,b in combinations(range(5),2)]
    clauses += [[-5*a-c-1,-5*b-c-1] for a,b in edges for c in range(5)]
    with Solver(name='cd19',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        search = dict(status='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_SEARCH_ONLY',
                      conflict_budget=budget,stats=solver.accum_stats())
        if answer is True:
            model = set(x for x in solver.get_model() if x>0)
            search['five_coloring'] = ''.join(str(next(c for c in range(5) if 5*v+c+1 in model)) for v in range(len(points)))
    sources = {name:hashlib.sha256((root/'certificates'/name).read_bytes()).hexdigest()
               for name in ('parts509_core.json','quintic_core_probe.json','quintic_congruence_gap.json')}
    return dict(schema=1,experiment='E047',sources=sources,source_anchors=PAIRS,target_anchors=[84,337],
                coordinate_denominator=den,geometry=summary,search=search,
                scope='Specified six bridges only; no full joint or new HN bound claim')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = run(Path(__file__).resolve().parents[1])
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='search'}))
    print(json.dumps({k:v for k,v in result['search'].items() if k!='five_coloring'}))
