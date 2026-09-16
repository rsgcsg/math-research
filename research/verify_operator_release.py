"""E093: exact single-operator deletion and pointwise palette-product screen.

No SAT, producer, or unverified geometry cache.  This reuses E089's independent
geometric formulas, BFS literal components, and canonical proper-color CNF.
Unit propagation is implemented directly here.  Its deductions are one-sided:
not forcing the distinguished event never means a satisfying extension exists.
"""

from collections import Counter
from pathlib import Path
import argparse
import copy
import hashlib
import json

from verify_dyadic_fixed_representation import (
    _base_clauses, _classes_by_bfs, _definitions, _mapping, geometry,
)
from verify_quintic_core_probe import digest


SOURCE_PATHS = (
    'certificates/quintic_multiword_return_joint.json',
    'certificates/dyadic_identity_extension.json',
    'certificates/quintic_tau_union.json',
)


def _root_propagation(clauses):
    values, reasons, steps = {}, {}, []
    changed = True
    while changed:
        changed = False
        for identifier, clause in enumerate(clauses, 1):
            if any(values.get(abs(literal)) == (literal > 0) for literal in clause):
                continue
            unset = [literal for literal in clause if abs(literal) not in values]
            assert unset, 'Every retained fixed-operator base has the saved E083 model'
            if len(unset) == 1:
                literal = unset[0]
                reasons[abs(literal)] = len(steps)
                values[abs(literal)] = literal > 0
                steps.append([literal, identifier])
                changed = True
    return values, reasons, steps


def _event_record(n, classes, clauses, values, reasons, steps):
    ports = ((233, 239), (5557, 238))
    colors, variables = [], set()
    for atom in range(5):
        row = []
        for pair in ports:
            pair_colors = []
            for point in pair:
                ids = [classes[(atom * n + point) * 5 + color] for color in range(5)]
                selected = [color for color, variable in enumerate(ids)
                            if values.get(variable) is True]
                assert len(selected) <= 1
                pair_colors.append(selected[0] if selected else None)
                variables.update(ids)
            row.append(pair_colors)
        colors.append(row)
    counts = []
    for side in range(2):
        known = [None if None in row[side] else row[side][0] != row[side][1]
                 for row in colors]
        counts.append(None if None in known else sum(known))
    obstruction = counts == [4, 0]
    used = set()

    def require(variable):
        index = reasons[variable]
        if index in used:
            return
        used.add(index)
        literal, identifier = steps[index]
        for old in clauses[identifier - 1]:
            if abs(old) != abs(literal):
                assert abs(old) in reasons and reasons[abs(old)] < index
                require(abs(old))

    if obstruction:
        assert variables <= set(values)
        for variable in sorted(variables):
            require(variable)
    proof = [steps[index] for index in sorted(used)]
    # Replay the extracted short deductions in a fresh assignment, rather
    # than merely recording the propagation implementation's final state.
    replay = {}
    for literal, identifier in proof:
        clause = clauses[identifier - 1]
        assert literal in clause and abs(literal) not in replay
        assert all(replay.get(abs(old)) == (old < 0) for old in clause if old != literal)
        replay[abs(literal)] = literal > 0
    if obstruction:
        assert all(replay[variable] == values[variable] for variable in variables)
    return dict(source_pair=list(ports[0]), image_pair=list(ports[1]),
                point_colors=colors, forced_unequal_counts=counts,
                conclusion=('EXACT_OLD_EVENT_OBSTRUCTION' if obstruction
                            else 'UNDETERMINED_BY_ROOT_PROPAGATION'),
                old_base_unit_derivation=proof)


def _palette_products(words, new_word, edges):
    expected = {(a, b) for a in range(25) for b in range(a + 1, 25)
                if a // 5 != b // 5 and a % 5 != b % 5}
    assert len(expected) == 200
    reports = []
    for atom, word in enumerate(words):
        palette_vertices = [5 * int(a) + int(b) for a, b in zip(word, new_word)]
        assert set(palette_vertices) == set(range(25))
        witnesses = {}
        for source, target in edges:
            edge = tuple(sorted((palette_vertices[source], palette_vertices[target])))
            assert edge in expected
            witnesses.setdefault(edge, (source, target))
        assert set(witnesses) == expected
        witness_list = [[a, b, *witnesses[a, b]] for a, b in sorted(witnesses)]
        reports.append(dict(old_atom=atom, palette_vertices=25, palette_edges=200,
                            all_actual_edges_checked=len(edges), complete_tensor=True,
                            tensor_edge_sha256=digest(sorted(expected)),
                            actual_edge_witnesses=witness_list))
    return reports


def _pattern(word, points):
    labels = {}
    return tuple(labels.setdefault(word[point], len(labels)) for point in points)


def _mixture_obstruction(words, new_word, definitions, mappings):
    mapping = mappings[-1]
    source, image = [i for i, _ in mapping], [j for _, j in mapping]
    old_sources = {_pattern(word, source) for word in words}
    old_images = {_pattern(word, image) for word in words}
    new_pattern = _pattern(new_word, source)
    assert _pattern(new_word, image) == new_pattern
    assert not (old_sources & old_images)
    assert new_pattern not in old_sources | old_images
    old_mismatches = []
    for definition, old_map in zip(definitions[:14], mappings[:14]):
        left, right = [i for i, _ in old_map], [j for _, j in old_map]
        assert _pattern(new_word, left) != _pattern(new_word, right)
        old_mismatches.append(definition[0])
    return dict(u_source_patterns=[list(p) for p in sorted(old_sources)],
                u_image_patterns=[list(p) for p in sorted(old_images)],
                new_u_identity_pattern=list(new_pattern),
                old_word_cut_values=[1] * 5, new_word_cut_value=0,
                new_word_mismatched_old_domains=old_mismatches,
                conclusion='NO_NONNEGATIVE_REAL_MIXTURE_OF_THESE_SIX_PARTITIONS')


def _calculate(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    source_hashes = {path: hashlib.sha256((root / path).read_bytes()).hexdigest()
                     for path in SOURCE_PATHS}
    old_data = json.loads((root / SOURCE_PATHS[0]).read_text())
    new_data = json.loads((root / SOURCE_PATHS[1]).read_text())
    assert old_data['experiment'] == 'E083' and new_data['experiment'] == 'E092'
    parent, context = geometry(root, geometry_context=True)
    assert old_data['geometry'] == new_data['geometry'] == parent['geometry']
    old = old_data['result']
    words = old['words']
    new_word = new_data['stages'][-1]['result']['word']
    n, edges = len(context['points']), context['edges']
    assert n == 10077 and len(words) == 5
    assert all(isinstance(word, str) and len(word) == n and set(word) <= set('01234')
               for word in words + [new_word])
    assert all(word[i] != word[j] for word in words + [new_word] for i, j in edges)
    definitions = _definitions(context)
    mappings = [_mapping(context, definition) for definition in definitions]
    assert old['motions'] == [definition[0] for definition in definitions[:14]]
    assert old['mapping_sha256'] == [digest(mapping) for mapping in mappings[:14]]
    unit = definitions[-1][1]
    square = ('dyadic_u_squared', context['ring']['mul'](unit, unit), definitions[-1][2], False)
    new_mappings = [mappings[-1], _mapping(context, square)]
    assert [len(mapping) for mapping in new_mappings] == [29, 805]
    assert new_data['mappings'] == [[list(pair) for pair in mapping] for mapping in new_mappings]
    assert all(new_word[i] == new_word[j] for mapping in new_mappings for i, j in mapping)
    assert dict(new_mappings[0])[233] == 5557 and dict(new_mappings[0])[239] == 238
    products = _palette_products(words, new_word, edges)
    mixture = _mixture_obstruction(words, new_word, definitions, mappings)
    releases = []
    for omit in range(14):
        retained = [i for i in range(14) if i != omit]
        selected = dict(words=words,
                        word_permutations=[old['word_permutations'][i] for i in retained],
                        color_permutations=[old['color_permutations'][i] for i in retained])
        classes, equations = _classes_by_bfs(n, selected, [mappings[i] for i in retained])
        base = _base_clauses(n, edges, classes)
        # Independently retain the positive old assignment as a sanity check
        # that a base contradiction is not being mistaken for a u obstruction.
        sample = {}
        for atom, word in enumerate(words):
            for point, label in enumerate(word):
                for color in range(5):
                    variable = classes[(atom * n + point) * 5 + color]
                    truth = int(label) == color
                    assert sample.setdefault(variable, truth) == truth
        assert all(any(sample[abs(literal)] == (literal > 0) for literal in clause) for clause in base)
        values, reasons, steps = _root_propagation(base)
        event = _event_record(n, classes, base, values, reasons, steps)
        releases.append(dict(omitted=definitions[omit][0],
                             remaining_motions=[definitions[i][0] for i in retained],
                             equality_equations=equations, classes=max(classes),
                             classes_sha256=digest(classes), base_clauses=len(base),
                             base_clauses_sha256=digest(base),
                             clause_lengths={str(k): v for k, v in sorted(Counter(map(len, base)).items())},
                             root_forced_variables=len(values),
                             root_assignment_sha256=digest(sorted(values.items())),
                             saved_E083_satisfies_base=True, event=event))
    assert [record['omitted'] for record in releases
            if record['event']['conclusion'] == 'UNDETERMINED_BY_ROOT_PROPAGATION'] == ['eta']
    return dict(schema=1, experiment='E093', source_sha256=source_hashes,
                geometry=parent['geometry'], support=5,
                source_actual_word_edge_checks=6 * len(edges),
                new_word_identity_equalities=sum(map(len, new_mappings)),
                product_rule='palette vertex = 5 * old_color + new_color',
                palette_products=products, palette_mixture_obstruction=mixture,
                operator_releases=releases,
                scope=('Only single releases of E083 fixed operator groups on five equal-weight '
                       'otherwise free words; eta is undetermined, not SAT. Palette-merger '
                       'ceiling only for point-independent maps of the specified saved word pairs. '
                       'No unrestricted full-joint obstruction, support bound, or HN bound.'))


def _compare(saved, actual):
    assert saved == actual, 'Saved E093 data disagree with independent exact reconstruction'


def verify(root, certificate=None, mutation_checks=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    path = Path(certificate) if certificate else root / 'certificates/operator_release.json'
    saved = json.loads(path.read_text())
    actual = _calculate(root)
    _compare(saved, actual)
    report = dict(status='PASS', experiment='E093', geometry=actual['geometry'],
                  checked_word_edges=actual['source_actual_word_edge_checks'],
                  palette_product_edge_coverages=[len(p['actual_edge_witnesses'])
                                                  for p in actual['palette_products']],
                  palette_mixture_obstruction=actual['palette_mixture_obstruction']['conclusion'],
                  old_event_still_forced_after_release=[r['omitted'] for r in actual['operator_releases']
                                                        if r['event']['conclusion'] == 'EXACT_OLD_EVENT_OBSTRUCTION'],
                  undetermined_releases=['eta'], no_SAT_queries=True,
                  scope=actual['scope'])
    if mutation_checks:
        cases = []
        bad = copy.deepcopy(saved)
        bad['source_sha256'][SOURCE_PATHS[0]] = '0' * 64
        cases.append(('source_sha256', bad))
        bad = copy.deepcopy(saved)
        bad['operator_releases'][0]['classes_sha256'] = '0' * 64
        cases.append(('classes_sha256', bad))
        bad = copy.deepcopy(saved)
        bad['palette_products'][0]['actual_edge_witnesses'].pop()
        cases.append(('missing_tensor_edge', bad))
        bad = copy.deepcopy(saved)
        bad['operator_releases'][2]['event']['conclusion'] = 'SAT'
        cases.append(('promoted_eta_to_SAT', bad))
        rejected = []
        for name, bad in cases:
            try:
                _compare(bad, actual)
            except AssertionError:
                rejected.append(name)
            else:
                raise AssertionError(f'Mutation accepted: {name}')
        report['mutation_rejections'] = rejected
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', type=Path)
    parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.certificate,
                            args.mutations), indent=2))
