"""Independent direct checking for E092's identity-action extension query.

No SAT or producer import. Each positive word is checked on ALL actual unit
edges and complete motion domains. Negative search states remain unproved;
only an explicit actual-edge/equality-path contradiction proves a restricted
identity-action impossibility.
"""

from collections import deque
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json

from verify_quintic_tau_union import verify as geometry
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping
from verify_quintic_core_probe import digest
from verify_quintic_multiword_joint import _definitions as old_definitions
from verify_quintic_multiword_joint import _mapping as old_mapping


def _components(vertices, edges, equalities):
    neighbors = [set() for _ in range(vertices)]
    for x, y in equalities:
        neighbors[x].add(y)
        neighbors[y].add(x)
    projection = [-1] * vertices
    count = 0
    for start in range(vertices):
        if projection[start] >= 0:
            continue
        queue = deque([start])
        projection[start] = count
        while queue:
            x = queue.popleft()
            for y in neighbors[x]:
                if projection[y] < 0:
                    projection[y] = count
                    queue.append(y)
        count += 1
    qedges = sorted({tuple(sorted((projection[x], projection[y]))) for x, y in edges})
    return projection, qedges, dict(vertices=count, edges=len(qedges),
                                   edge_sha256=digest(qedges), projection_sha256=digest(projection),
                                   collapsed_vertices=vertices - count)


def _check(data, parent, context, mappings, source_sha):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema'] == 1 and data['experiment'] == 'E092'
    assert data['geometry'] == parent['geometry']
    assert data['geometry_source_sha256'] == source_sha
    assert data['mappings'] == [[list(p) for p in m] for m in mappings]
    assert [len(m) for m in mappings] == [29, 805]
    assert len(data['stages']) in (1, 2)
    if data['stages'][0]['status'] == 'SAT':
        assert len(data['stages']) == 2
    else:
        assert len(data['stages']) == 1
    reports = []
    for index, stage in enumerate(data['stages']):
        assert stage['name'] == ['identity_u', 'identity_u_and_u_squared'][index]
        assert stage['motions'] == ['u', 'u_squared'][:index + 1]
        assert stage['complete_domains'] == [29, 805][:index + 1]
        assert stage['mapping_sha256'] == [digest(m) for m in mappings[:index + 1]]
        equalities = sum(mappings[:index + 1], [])
        projection, qedges, qsummary = _components(len(context['points']), context['edges'], equalities)
        assert stage['quotient'] == qsummary
        loop_edges = [(x, y) for x, y in context['edges'] if projection[x] == projection[y]]
        status = stage['status']
        if status == 'REFUTED_IDENTITY_QUOTIENT_LOOP':
            assert loop_edges and stage['query'] is None and stage['result'] is None
            witness = stage['loop_witness']
            edge = tuple(witness['actual_edge'])
            path = witness['equality_path']
            assert edge in context['edges'] and len(path) >= 2
            assert path[0] == edge[0] and path[-1] == edge[1]
            allowed = {tuple(sorted(p)) for p in equalities}
            assert all(tuple(sorted(p)) in allowed for p in zip(path, path[1:]))
            reports.append(dict(stage=stage['name'], status='CHECKED_IDENTITY_ONLY_CONTRADICTION',
                                actual_edge=list(edge), equality_path=path))
            continue
        assert not loop_edges and stage['loop_witness'] is None
        query = stage['query']
        assert 1 <= query['conflict_budget'] <= 20000
        anchor = query['anchor']
        assert query['anchor_is_global_palette_gauge'] is True
        assert len(anchor) in (2, 3) and len(set(anchor)) == len(anchor)
        assert all(tuple(sorted((x, y))) in qedges for i, x in enumerate(anchor) for y in anchor[i + 1:])
        if status == 'SAT':
            result = stage['result']
            word = result['word']
            assert isinstance(word, str) and len(word) == len(context['points'])
            assert set(word) <= set('01234')
            assert all(word[x] != word[y] for x, y in context['edges'])
            assert all(word[x] == word[y] for x, y in equalities)
            assert result['checked_actual_edges'] == len(context['edges'])
            assert result['checked_equalities'] == len(equalities)
            reports.append(dict(stage=stage['name'], status='CHECKED_PROPER_IDENTITY_WORD',
                                checked_actual_edges=len(context['edges']), checked_equalities=len(equalities)))
        else:
            assert status in ('UNKNOWN', 'UNSAT_FIXED_IDENTITY_UNCERTIFIED')
            assert stage['result'] is None
            reports.append(dict(stage=stage['name'], status=status,
                                negative_mathematical_claim=False))
    return dict(status='PASS', experiment='E092', geometry=parent['geometry'], stages=reports,
                scope='Only saved single-word identity actions. No old-fourteen joint repair, all-proper negative theorem, full power-orbit coloring, or HN bound.')


def verify(root, mutation_checks=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    data = json.loads((root / 'certificates/dyadic_identity_extension.json').read_text())
    parent, context = geometry(root, geometry_context=True)
    definition = _new_definitions(context)[0]
    square = tuple({0: Q(7, 16), 4: -Q(3, 16), 9: Q(7, 16), 13: Q(1, 16)}.get(i, Q(0))
                   for i in range(32))
    assert square == context['ring']['mul'](definition[1], definition[1])
    mappings = [_mapping(context, definition),
                _mapping(context, ('u_squared', square, definition[2], False))]
    source_sha = hashlib.sha256((root / 'certificates/quintic_tau_union.json').read_bytes()).hexdigest()
    report = _check(data, parent, context, mappings, source_sha)
    old_maps = [(d[0], old_mapping(context['points'],
                  {p: i for i, p in enumerate(context['points'])},
                  context['ring']['mul'], d)) for d in old_definitions(context)]
    def pattern(word, indices):
        labels = {}
        return tuple(labels.setdefault(word[i], len(labels)) for i in indices)
    for stage, stage_report in zip(data['stages'], report['stages']):
        if stage['status'] == 'SAT':
            word = stage['result']['word']
            passed, failed = [], []
            for name, mm in old_maps:
                equal = pattern(word, [i for i, _ in mm]) == pattern(word, [j for _, j in mm])
                (passed if equal else failed).append(name)
            stage_report['old_fourteen_full_partition_audit'] = dict(passed=passed, failed=failed)
    if mutation_checks:
        cases = []
        bad = deepcopy(data)
        bad['mappings'][0][0][1] += 1
        cases.append(('altered_complete_mapping', bad))
        bad = deepcopy(data)
        bad['geometry_source_sha256'] = '0' * 64
        cases.append(('altered_geometry_source', bad))
        for index, stage in enumerate(data['stages']):
            if stage['status'] == 'SAT':
                bad = deepcopy(data)
                word = list(bad['stages'][index]['result']['word'])
                x, y = context['edges'][0]
                word[y] = word[x]
                bad['stages'][index]['result']['word'] = ''.join(word)
                cases.append((f'monochromatic_actual_edge_stage_{index + 1}', bad))
        rejected = []
        for name, bad in cases:
            try:
                _check(bad, parent, context, mappings, source_sha)
            except AssertionError:
                rejected.append(name)
            else:
                raise AssertionError('Mutation accepted: ' + name)
        report['rejected_mutations'] = rejected
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.mutations), indent=2))
