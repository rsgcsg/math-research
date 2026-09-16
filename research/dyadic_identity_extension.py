"""E092: at most two bounded identity-action, one-word extension queries.

Not the old fourteen-motion joint problem. Negative SAT states have no
mathematical force; an explicit quotient loop is a separate exact obstruction
to the prescribed equalities only. This producer does not write files.
"""

from collections import Counter, deque
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json

from verify_quintic_tau_union import verify as geometry
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping
from verify_quintic_core_probe import digest


def quotient(vertices, edges, equalities):
    parent = list(range(vertices))
    adjacency = [[] for _ in parent]
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for x, y in equalities:
        a, b = find(x), find(y)
        if a != b:
            parent[max(a, b)] = min(a, b)
        if x != y:
            adjacency[x].append(y)
            adjacency[y].append(x)
    labels = {x: i for i, x in enumerate(sorted({find(v) for v in range(vertices)}))}
    projection = [labels[find(v)] for v in range(vertices)]
    qedges = sorted({tuple(sorted((projection[x], projection[y]))) for x, y in edges})
    loops = [(x, y) for x, y in edges if projection[x] == projection[y]]
    witness = None
    if loops:
        start, end = loops[0]
        previous = {start: None}
        queue = deque([start])
        while end not in previous:
            x = queue.popleft()
            for y in adjacency[x]:
                if y not in previous:
                    previous[y] = x
                    queue.append(y)
        path = [end]
        while path[-1] != start:
            path.append(previous[path[-1]])
        witness = dict(actual_edge=[start, end], equality_path=list(reversed(path)))
    return projection, qedges, witness


def query(vertices, edges, equalities, phases, budget):
    from pysat.solvers import Solver
    projection, qedges, loop = quotient(vertices, edges, equalities)
    count = max(projection) + 1
    summary = dict(vertices=count, edges=len(qedges), edge_sha256=digest(qedges),
                   projection_sha256=digest(projection), collapsed_vertices=vertices - count)
    if loop:
        return dict(status='REFUTED_IDENTITY_QUOTIENT_LOOP', quotient=summary,
                    loop_witness=loop, query=None, result=None)
    var = lambda vertex, color: 5 * vertex + color + 1
    clauses = [[var(v, c) for c in range(5)] for v in range(count)]
    clauses += [[-var(v, c), -var(v, d)] for v in range(count)
                for c, d in combinations(range(5), 2)]
    clauses += [[-var(x, c), -var(y, c)] for x, y in qedges for c in range(5)]
    neighbors = [set() for _ in range(count)]
    for x, y in qedges:
        neighbors[x].add(y)
        neighbors[y].add(x)
    x, y = qedges[0]
    anchor = [x, y]
    common = neighbors[x] & neighbors[y]
    if common:
        anchor.append(min(common))
    clauses += [[var(v, c)] for c, v in enumerate(anchor)]
    votes = [Counter() for _ in range(count)]
    for vertex, qvertex in enumerate(projection):
        votes[qvertex][int(phases[vertex])] += 1
    preferences = [var(v, max(votes[v], key=lambda c: (votes[v][c], -c))) for v in range(count)]
    print(json.dumps(dict(progress='identity_formula', quotient=summary,
                          equalities=len(equalities), clauses=len(clauses), budget=budget)), flush=True)
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        solver.set_phases(preferences)
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        stats = solver.accum_stats()
        status = ('SAT' if answer is True else 'UNKNOWN' if answer is None
                  else 'UNSAT_FIXED_IDENTITY_UNCERTIFIED')
        result = None
        if answer is True:
            model = {v for v in solver.get_model() if v > 0}
            qword = ''.join(str(next(c for c in range(5) if var(v, c) in model))
                            for v in range(count))
            word = ''.join(qword[v] for v in projection)
            assert all(word[x] != word[y] for x, y in edges)
            assert all(word[x] == word[y] for x, y in equalities)
            result = dict(word=word, checked_actual_edges=len(edges),
                          checked_equalities=len(equalities))
    return dict(status=status, quotient=summary, loop_witness=None,
                query=dict(conflict_budget=budget, stats=stats, anchor=anchor,
                           anchor_is_global_palette_gauge=True), result=result)


def run(root, budget):
    parent, context = geometry(root, geometry_context=True)
    print(json.dumps(dict(progress='complete_geometry_checked', geometry=parent['geometry'])), flush=True)
    definition = _new_definitions(context)[0]
    square = context['ring']['mul'](definition[1], definition[1])
    maps = [_mapping(context, definition),
            _mapping(context, ('u_squared', square, definition[2], False))]
    assert [len(m) for m in maps] == [29, 805]
    phases = context['word']
    stages = []
    for count, name in ((1, 'identity_u'), (2, 'identity_u_and_u_squared')):
        equalities = sum(maps[:count], [])
        result = query(len(context['points']), context['edges'], equalities, phases, budget)
        result.update(name=name, motions=['u', 'u_squared'][:count],
                      mapping_sha256=[digest(m) for m in maps[:count]],
                      complete_domains=[len(m) for m in maps[:count]])
        stages.append(result)
        print(json.dumps(dict(progress='stage_finished', name=name, status=result['status'],
                              stats=result['query']['stats'] if result['query'] else None)), flush=True)
        if result['status'] != 'SAT':
            break
        phases = result['result']['word']
    return dict(schema=1, experiment='E092', geometry=parent['geometry'],
                geometry_source_sha256=hashlib.sha256((root / 'certificates/quintic_tau_union.json').read_bytes()).hexdigest(),
                mappings=maps, stages=stages,
                scope='Single proper word with fixed identity palette actions only; no old fourteen domains retained, no all-word negative conclusion, no HN bound.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=20000)
    args = parser.parse_args()
    assert 1 <= args.budget <= 20000
    print('IDENTITY_FINAL_JSON=' + json.dumps(run(Path(__file__).resolve().parents[1], args.budget),
                                            separators=(',', ':')), flush=True)
