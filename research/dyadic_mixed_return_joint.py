"""E084 isolated dyadic mixed-return diagnostics and one-shot positive search.

Existing files are not modified. Each new stage has a single conflict budget.
The producer is not an independent positive or negative proof checker.
"""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import math

from quintic_multiword_joint import MultiwordEncoding
from verify_quintic_core_probe import conjugate_twice, digest
from verify_quintic_multiword_joint import _definitions
from verify_quintic_tau_union import verify as geometry
from verify_finite_joint_compression import partition_witness


SOURCE_SHA256 = 'e4ae7e9355783ee7606711ace881faba0353cbd01bef30c36b338dc3d3a844f9'


def pattern(word, indices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in indices)


def prepare(root):
    parent, context = geometry(root, geometry_context=True)
    source = root / 'certificates/quintic_multiword_return_joint.json'
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    old = json.loads(raw)
    assert old['geometry'] == parent['geometry']
    words = old['result']['words']
    assert len(words) == 5
    assert all(w[i] != w[j] for w in words for i, j in context['edges'])
    r = context['ring']; mul = r['mul']
    zero = (Q(0),) * 32
    one = (Q(1),) + zero[1:]
    eta = zero[:16] + one[:16]
    z = r['blocks'][0][64]
    bar = lambda a: tuple(Q(x) / 2 for x in conjugate_twice(a))
    add = lambda a, b: tuple(x + y for x, y in zip(a, b))
    h = add(eta, bar(eta))
    u = tuple((a + 3 * b) / 2 for a, b in zip(one, mul(add(h, one), z)))
    assert mul(u, bar(u)) == one
    assert mul(u, r['tau']) == mul(r['tau'], u)
    den = math.lcm(*(x.denominator for p in context['points'] for x in p))
    points = [tuple(int(x * den) for x in p) for p in context['points']]
    assert digest(points) == parent['geometry']['point_sha256']
    lookup = {p: i for i, p in enumerate(points)}
    standard = [tuple(Q(int(i == j)) for i in range(32)) for j in range(32)]

    def mapping(a, shift=zero, reflection=False):
        columns = [mul(a, bar(e) if reflection else e) for e in standard]
        scale = math.lcm(*(x.denominator for col in columns for x in col),
                         *((x * den).denominator for x in shift))
        sparse = [[(i, int(x * scale)) for i, x in enumerate(col) if x] for col in columns]
        shifted = [int(x * den * scale) for x in shift]
        pairs = []
        for index, p in enumerate(points):
            out = shifted[:]
            for value, column in zip(p, sparse):
                if value:
                    for i, coefficient in column:
                        out[i] += value * coefficient
            if any(x % scale for x in out):
                continue
            q = tuple(x // scale for x in out)
            if q in lookup:
                pairs.append((index, lookup[q]))
        return pairs

    old_definitions = _definitions(context)
    assert old['result']['motions'] == [d[0] for d in old_definitions]
    old_maps = [mapping(a, t, reflected) for _, a, t, reflected in old_definitions]
    assert [digest(m) for m in old_maps] == old['result']['mapping_sha256']
    new_definitions = [('dyadic_u', u, zero, False),
                       ('dyadic_u_tau_bar', mul(u, r['tau']), zero, True)]
    new_maps = [mapping(a, t, reflected) for _, a, t, reflected in new_definitions]
    assert list(map(len, new_maps)) == [29, 33]
    return parent, context, old, (one, eta, z, u, bar, mul), mapping, old_definitions + new_definitions, old_maps + new_maps


def diagnose(parent, context, old, algebra, mapping):
    one, eta, z, u, bar, mul = algebra
    zero = (Q(0),) * 32; tau = context['ring']['tau']
    definitions = [('dyadic_u', u, zero, False), ('dyadic_u_inverse', bar(u), zero, False),
                   ('dyadic_u_tau', mul(u, tau), zero, False),
                   ('dyadic_u_inverse_tau', mul(bar(u), tau), zero, False),
                   ('dyadic_u_bar', u, zero, True),
                   ('dyadic_u_tau_bar', mul(u, tau), zero, True),
                   ('translation_u', one, u, False),
                   ('translation_u_z', one, mul(u, z), False)]
    words = old['result']['words']; probes = []; maps = {}
    for name, a, t, reflected in definitions:
        pairs = mapping(a, t, reflected); maps[name] = dict(pairs)
        left = Counter(pattern(w, [i for i, j in pairs]) for w in words)
        right = Counter(pattern(w, [j for i, j in pairs]) for w in words)
        event = None
        if left != right:
            signed = {p: Q(left[p] - right[p], len(words))
                      for p in left.keys() | right.keys() if left[p] != right[p]}
            predicates, mass = partition_witness(signed)
            predicates = [dict(source=[pairs[i][0], pairs[j][0]],
                               image=[pairs[i][1], pairs[j][1]], equal=bool(bit))
                          for i, j, bit in predicates]
            counts = [sum(all((w[p[key][0]] == w[p[key][1]]) == p['equal'] for p in predicates)
                          for w in words) for key in ('source', 'image')]
            assert Q(counts[0] - counts[1], len(words)) == mass
            event = dict(predicates=predicates, counts=counts)
        probes.append(dict(motion=name, domain=len(pairs), mapping_sha256=digest(pairs),
                           mapping=pairs, full_partition_equal=left == right, event=event))
    maps['tau'] = dict(mapping(tau)); maps['bar'] = dict(mapping(one, reflection=True))
    maps['tau_inverse'] = {j: i for i, j in maps['tau'].items()}
    paths = [['bar', 'dyadic_u', 'tau'], ['bar', 'tau', 'dyadic_u'],
             ['dyadic_u_inverse', 'bar', 'tau'], ['tau_inverse', 'bar', 'dyadic_u'],
             ['dyadic_u_inverse', 'tau_inverse', 'bar'],
             ['tau_inverse', 'dyadic_u_inverse', 'bar']]
    common_paths = []; union = set()
    for path in paths:
        pairs = {i: i for i in range(len(context['points']))}
        for name in path:
            pairs = {i: maps[name][j] for i, j in pairs.items() if j in maps[name]}
        assert pairs.items() <= maps['dyadic_u_tau_bar'].items()
        union |= pairs.keys()
        common_paths.append(dict(path=path, domain=len(pairs), mapping=sorted(pairs.items())))
    assert len(union) == 33 and all(p['domain'] == 15 for p in common_paths)
    rotation_paths = []
    for path in [['dyadic_u', 'tau'], ['tau', 'dyadic_u']]:
        first, second = (maps[name] for name in path)
        pairs = {i: second[j] for i, j in first.items() if j in second}
        assert pairs == maps['dyadic_u_tau']
        rotation_paths.append(dict(path=path, domain=len(pairs), mapping=sorted(pairs.items())))
    assert not any(u[16:])
    fibers = defaultdict(set)
    for p in context['points']:
        fibers[p[16:]].add(p[:16])
    hits = sum(tuple(x + y for x, y in zip(p, u[:16])) in fiber
               for fiber in fibers.values() for p in fiber)
    assert hits == 0
    return dict(schema=1, experiment='E084', source_sha256=SOURCE_SHA256,
                geometry=parent['geometry'],
                unit=dict(coordinates=list(map(str, u)), norm_squared='1', commutes_with_tau=True),
                probes=probes, common_paths=common_paths, common_path_union_domain=len(union),
                rotation_paths=rotation_paths,
                fiber_summary=dict(fibers=len(fibers), size_histogram=dict(sorted(Counter(map(len, fibers.values())).items())),
                                   nonsingleton_sources=sum(len(f) for f in fibers.values() if len(f) > 1),
                                   translation_hits=hits),
                scope=('Diagnostics of the fixed E083 law only; pointwise union of path domains '
                       'does not establish complete joint invariance of their union'))


def run(root, budget):
    from pysat.solvers import Solver
    assert 1 <= budget <= 150000
    parent, context, old, algebra, mapping, definitions, maps = prepare(root)
    probe = diagnose(parent, context, old, algebra, mapping)
    print(json.dumps(dict(progress='geometry_and_probe_ready', domains=list(map(len, maps[-2:])))), flush=True)
    points = context['points']; enc = MultiwordEncoding(len(points), context['edges'], 5)
    lookup = {p: i for i, p in enumerate(points)}
    for a in range(5):
        for color, idx in enumerate([0, 153, 150]):
            enc.clauses.append([enc.color(a, lookup[context['ring']['blocks'][0][idx]], color)])
    history = []; positive = None
    with Solver(name='cadical195', bootstrap_with=enc.clauses) as solver:
        del enc.clauses
        for position, ((name, _, _, _), pairs) in enumerate(zip(definitions, maps), 1):
            clauses = enc.add_motion(pairs)
            solver.append_formula(clauses); del clauses
            print(json.dumps(dict(progress='added', motion=name, domain=len(pairs), variables=enc.top)), flush=True)
            if position < 15:
                continue
            if position == 15:
                # Search hint only. Every old word may be changed freely.
                solver.set_phases([enc.color(a, i, int(color))
                                   for a, word in enumerate(old['result']['words'])
                                   for i, color in enumerate(word)])
            before = solver.accum_stats()
            solver.conf_budget(budget)
            answer = solver.solve_limited()
            status = 'SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_FIXED_SUPPORT_ONLY'
            after = solver.accum_stats()
            stage = dict(motion=name, domains=position, domain=len(pairs), status=status,
                         conflict_budget=budget, conflicts_this_call=after['conflicts']-before['conflicts'],
                         cumulative_stats=after)
            history.append(stage); print(json.dumps(dict(stage=stage)), flush=True)
            if answer is not True:
                break
            positive = enc.decode(solver.get_model())
            positive.update(motions=[d[0] for d in definitions[:position]],
                            mapping_sha256=[digest(m) for m in maps[:position]],
                            mappings=maps[:position])
    certificate = dict(schema=1, experiment='E084', support=5, source_sha256=SOURCE_SHA256,
                       geometry=parent['geometry'], history=history, result=positive,
                       scope='Only listed full domains; fixed support UNSAT/UNKNOWN is not an all-word obstruction')
    return dict(probe=probe, certificate=certificate)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=150000)
    args = parser.parse_args()
    result = run(Path(__file__).resolve().parents[1], args.budget)
    print('E084_FINAL_JSON=' + json.dumps(result, separators=(',', ':')), flush=True)
