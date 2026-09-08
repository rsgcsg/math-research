"""Search-side rigid overlap census, repair compiler, and a repairable cascade.

The independent checker does not import this module or exact_geometry.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import hashlib
import json

from exact_geometry import add, sub, mul, cmul, field, distance_squared, induced_edges

ROOT = Path(__file__).resolve().parents[1]


def overlap_census(boundary):
    lengths, profiles = defaultdict(list), {}
    for a, b in permutations(range(14), 2):
        lengths[distance_squared(boundary[a], boundary[b])].append((a, b))
        u = [sub(boundary[b][k], boundary[a][k]) for k in range(2)]
        profiles[a, b] = []
        for p in boundary:
            v = [sub(p[k], boundary[a][k]) for k in range(2)]
            profiles[a, b].append((add(mul(u[0], v[0]), mul(u[1], v[1])),
                                   sub(mul(u[0], v[1]), mul(u[1], v[0]))))
    histogram, witnesses = Counter(), []
    for group in lengths.values():
        for source, target in product(group, repeat=2):
            target_lookup = {value: i for i, value in enumerate(profiles[target])}
            for sign in (1, -1):
                matched = []
                for i, (dot, cross) in enumerate(profiles[source]):
                    key = dot, tuple(sign*x for x in cross)
                    if key in target_lookup:
                        matched.append([i, target_lookup[key]])
                histogram[len(matched)] += 1
                if len(matched) == 14:
                    assert matched == [[i, i] for i in range(14)] and sign == 1
                if len(matched) == 4:
                    witnesses.append(dict(source=list(source), target=list(target),
                                          orientation=sign, mapping=matched))
    return dict(anchor_cases=sum(histogram.values()),
                overlap_histogram=dict(sorted(histogram.items())),
                max_nonidentity_overlap=4, four_overlap_anchor_witnesses=witnesses)


def compile_repair(boundary_edges, gates, coloring):
    """DIMACS literals use physical vertex index + 1; x means recolor to 4.

    SAT is equivalent to one-shot independent-set fresh-color repair ONLY.
    It is not equivalent to unrestricted five-colorability of the host.
    """
    clauses = [[-a-1, -b-1] for a, b in boundary_edges]
    for pairs in gates:
        palettes = [{coloring[a], coloring[b]} for a, b in pairs]
        assert all(len(p) == 2 for p in palettes)
        if all(p == palettes[0] for p in palettes):
            clauses.append([v+1 for pair in pairs for v in pair])
        for beta in sorted(set.intersection(*palettes)):
            clauses.append([-next(v for v in pair if coloring[v] != beta)-1
                            for pair in pairs])
    return clauses


def bad_gates(gates, coloring):
    return [j for j, pairs in enumerate(gates)
            if len({tuple(sorted((coloring[a], coloring[b]))) for a, b in pairs}) == 1]


def build():
    base_path = ROOT/'certificates/spindle_pair_gate.json'
    base_data = json.loads(base_path.read_text())
    base = [tuple(tuple(map(F, axis)) for axis in p) for p in base_data['points']]
    points = list(base)
    modules = [list(range(21))]
    edges = {tuple(e) for e in base_data['induced_edges']}
    parameters = []
    for i in range(7):
        shared = 7+2*i
        for t in range(2, 200):
            rotation = field(F(1-t*t, 1+t*t)), field(F(2*t, 1+t*t))
            proposed, mapping = list(points), []
            for k, p in enumerate(base):
                delta = tuple(sub(p[axis], base[7][axis]) for axis in range(2))
                rotated = cmul(rotation, delta)
                q = tuple(add(points[shared][axis], rotated[axis]) for axis in range(2))
                if k == 7:
                    assert q == points[shared]
                    mapping.append(shared)
                else:
                    mapping.append(len(proposed))
                    proposed.append(q)
            if len(set(proposed)) != len(proposed):
                continue
            expected = edges | {tuple(sorted((mapping[a], mapping[b])))
                                for a, b in base_data['induced_edges']}
            if set(induced_edges(proposed)) != expected:
                continue
            points, edges = proposed, expected
            modules.append(mapping)
            parameters.append(t)
            break
        else:
            raise RuntimeError('No clean single-port attachment pose found')
    gates = [[[m[a], m[b]] for a, b in base_data['boundary_pairs']] for m in modules]
    color = [-1]*len(points)
    for i, (a, b) in enumerate(gates[0]):
        color[a], color[b] = i % 3, 3
    for i, pairs in enumerate(gates[1:]):
        for a, b in pairs:
            assert color[a] in (-1, i % 3)
            color[a], color[b] = i % 3, (i+1) % 3
    initial_repair = [a for a, b in gates[0]]
    final_repair = [gates[1][0][1]] + initial_repair[1:]
    states = []
    for chosen in ([], initial_repair, final_repair):
        c = [4 if v in chosen else x for v, x in enumerate(color)]
        assert all(c[a] != c[b] for a, b in edges if c[a] >= 0 and c[b] >= 0)
        states.append(bad_gates(gates, c))
    assert states == [list(range(1, 8)), [0], []]
    full = [4 if v in final_repair else x for v, x in enumerate(color)]
    spindle = [(a, b) for a, b in base_data['induced_edges'] if a < 7 and b < 7]
    for m, pairs in zip(modules, gates):
        lists = [sorted(set(range(5)) - {full[a], full[b]}) for a, b in pairs]
        word = next(w for w in product(*lists) if all(w[a] != w[b] for a, b in spindle))
        for i, c in enumerate(word):
            assert full[m[i]] == -1
            full[m[i]] = c
    assert all(full[a] != full[b] for a, b in edges)
    unrestricted_four = [-1]*len(points)
    for m in modules:
        word = base_data['four_coloring']
        rename = next(p for p in permutations(range(4))
                      if all(unrestricted_four[v] in (-1, p[word[k]]) for k, v in enumerate(m)))
        for k, v in enumerate(m):
            unrestricted_four[v] = rename[word[k]]
    assert all(unrestricted_four[a] != unrestricted_four[b] for a, b in edges)
    boundary_edges = sorted((a, b) for a, b in edges if color[a] >= 0 and color[b] >= 0)
    clauses = compile_repair(boundary_edges, gates, color)
    for chosen, expected in ((initial_repair, False), (final_repair, True)):
        selected = {v+1 for v in chosen}
        actual = all(any((lit in selected) if lit > 0 else (-lit not in selected)
                         for lit in clause) for clause in clauses)
        assert actual == expected
    return dict(schema=1, base_sha256=hashlib.sha256(base_path.read_bytes()).hexdigest(),
                overlap=overlap_census(base[7:]), radicals=[1, 3, 11, 33],
                points=[[[str(c) for c in axis] for axis in p] for p in points],
                modules=modules, boundary_pairs=gates, induced_edges=sorted(edges),
                rotation_parameters=parameters, initial_boundary_coloring=color,
                initial_repair=initial_repair, exchanged_repair=final_repair,
                bad_gate_trace=states, final_five_coloring=full,
                unrestricted_four_coloring=unrestricted_four,
                repair_cnf=clauses,
                scope='A real repairable cascade, not an obstruction or a new HN bound')


if __name__ == '__main__':
    data = build()
    (ROOT/'certificates/gate_repair_cascade.json').write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(dict(vertices=len(data['points']), edges=len(data['induced_edges']),
                         rotations=data['rotation_parameters'], trace=data['bad_gate_trace'],
                         overlap=data['overlap']['overlap_histogram']), indent=2))
