"""Independent RUP check for the E083 fixed-operator quotient restriction.

No producer, MultiwordEncoding, DSU, SAT solver, or proof converter is imported.
Actual geometry is rebuilt; literal equalities form an undirected graph whose
connected components are found by BFS, numbered by their minimum vertices.
The CNF is then reconstructed directly and a RUP-only LRAT proof is checked.

This can refute only five words carrying E083's specified fourteen operators.
It is not a refutation of free five-word full-joint, larger supports, or HN.
"""

from collections import Counter, deque
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import copy
import hashlib
import json

from verify_quintic_core_probe import conjugate_twice, digest
from verify_quintic_tau_union import verify as geometry
from verify_rup_lrat import check as check_rup


def _definitions(context):
    mul = context['ring']['mul']
    zero = (Q(0),) * 32
    one = (Q(1),) + zero[1:]
    eta = zero[:16] + one[:16]
    z = tuple(-Q(1, 2) if j == 0 else -Q(1, 6) if j == 9 else Q(0)
              for j in range(32))
    nu = tuple(Q(5, 6) if j == 0 else Q(1, 6) if j == 10 else Q(0)
               for j in range(32))
    tau = tuple(-Q(1, 10) if j == 0 else Q(3, 10) if j == 10 else Q(0)
                for j in range(32))
    omega = tuple(-2 * a - 3 * b for a, b in zip(one, z))
    shift = tuple(a + b for a, b in zip(one, mul(eta, z)))
    result = [('tau', tau, zero, False), ('nu', nu, zero, False),
              ('eta', eta, zero, False), ('omega', omega, zero, False),
              ('bar', one, zero, True),
              ('bridge', tuple(-a for a in eta), shift, False),
              ('translation_one', one, one, False),
              ('translation_z', one, z, False)]
    power = one
    for exponent in range(1, 5):
        power = mul(power, eta)
        result.append((f'one_plus_eta_{exponent}', one,
                       tuple(a + b for a, b in zip(one, power)), False))
    result.extend([('bridge_shift', one, shift, False),
                   ('minus_bar', tuple(-a for a in one), zero, True)])
    u = tuple({0: Q(1, 8), 4: -Q(3, 8), 9: -Q(1, 8), 13: -Q(1, 8)}.get(j, Q(0))
              for j in range(32))
    result.append(('dyadic_u', u, zero, False))
    for _, coefficient, _, _ in result:
        conjugate = tuple(Q(a) / 2 for a in conjugate_twice(coefficient))
        assert mul(coefficient, conjugate) == one
    return result


def _mapping(context, definition):
    points = context['points']
    index = {p: i for i, p in enumerate(points)}
    _, coefficient, offset, reflected = definition
    result = []
    for i, p in enumerate(points):
        argument = tuple(Q(a) / 2 for a in conjugate_twice(p)) if reflected else p
        target = tuple(a + b for a, b in zip(context['ring']['mul'](coefficient, argument), offset))
        if target in index:
            result.append((i, index[target]))
    assert len({j for _, j in result}) == len(result)
    return result


def _classes_by_bfs(n, old, mappings):
    m, k = 5, 5
    size = n * m * k
    adjacency = [[] for _ in range(size)]
    node = lambda atom, point, color: (atom * n + point) * k + color
    equations = 0
    for t, mapping in enumerate(mappings):
        sigma = old['word_permutations'][t]
        palettes = old['color_permutations'][t]
        assert isinstance(sigma, list) and sorted(sigma) == list(range(m))
        assert isinstance(palettes, list) and len(palettes) == m
        assert all(isinstance(pi, list) and sorted(pi) == list(range(k)) for pi in palettes)
        for atom in range(m):
            for source, target in mapping:
                assert int(old['words'][sigma[atom]][target]) == palettes[atom][int(old['words'][atom][source])]
                for color in range(k):
                    a = node(atom, source, color)
                    b = node(sigma[atom], target, palettes[atom][color])
                    adjacency[a].append(b)
                    adjacency[b].append(a)
                    equations += 1
    classes = [0] * size
    count = 0
    for start in range(size):
        if classes[start]:
            continue
        count += 1
        classes[start] = count
        pending = deque([start])
        while pending:
            a = pending.popleft()
            for b in adjacency[a]:
                if not classes[b]:
                    classes[b] = count
                    pending.append(b)
    assert min(classes) == 1 and max(classes) == count
    return classes, equations


def _base_clauses(n, edges, classes):
    clauses = set()

    def add(literals):
        values = set(literals)
        if any(-literal in values for literal in values):
            return
        assert values and all(type(v) is int and v for v in values)
        clauses.add(tuple(sorted(values)))

    color = lambda atom, point, c: classes[(atom * n + point) * 5 + c]
    for atom in range(5):
        for point in range(n):
            ids = [color(atom, point, c) for c in range(5)]
            add(ids)
            for a, b in combinations(ids, 2):
                add([-a, -b])
        for source, target in edges:
            for c in range(5):
                add([-color(atom, source, c), -color(atom, target, c)])
    return sorted(clauses)


def _free_motion_clauses(n, classes, mapping):
    """Direct row/column permutation and selected-image truth encoding."""
    counter = max(classes)
    clauses = []

    def allocate():
        nonlocal counter
        counter += 1
        return counter

    def permutation():
        matrix = [[allocate() for _ in range(5)] for _ in range(5)]
        lines = matrix + [list(column) for column in zip(*matrix)]
        for line in lines:
            clauses.append(line[:])
            for a, b in combinations(line, 2):
                clauses.append([-a, -b])
        return matrix

    sigma = permutation()
    palettes = [permutation() for _ in range(5)]
    color = lambda atom, point, c: classes[(atom * n + point) * 5 + c]
    for atom in range(5):
        for source, target in mapping:
            selected_image = [allocate() for _ in range(5)]
            for image_atom in range(5):
                for c in range(5):
                    selector = sigma[atom][image_atom]
                    existing = color(image_atom, target, c)
                    selected = selected_image[c]
                    clauses.append([-selector, -existing, selected])
                    clauses.append([-selector, existing, -selected])
            for c in range(5):
                for d in range(5):
                    clauses.append([-color(atom, source, c),
                                    -palettes[atom][c][d], selected_image[d]])
    return clauses, counter


def _forced_pair_obstruction(n, classes, base, mapping):
    """A source/image pair event already forced by the old quotient alone."""
    assignment, reasons, trace = {}, {}, []
    changed = True
    while changed:
        changed = False
        for identifier, clause in enumerate(base, 1):
            if any(assignment.get(abs(literal)) == (literal > 0) for literal in clause):
                continue
            unset = [literal for literal in clause if abs(literal) not in assignment]
            assert unset, 'The saved E083 assignment already satisfies the base'
            if len(unset) == 1:
                literal = unset[0]
                assignment[abs(literal)] = literal > 0
                reasons[abs(literal)] = len(trace)
                trace.append(dict(literal=literal, clause_id=identifier))
                changed = True
    assert len(assignment) == 80
    source, image = (233, 239), (5557, 238)
    motion = dict(mapping)
    assert tuple(motion[point] for point in source) == image
    colors, needed = [], set()
    for atom in range(5):
        record = {}
        for side, pair in [('source', source), ('image', image)]:
            point_colors = []
            for point in pair:
                ids = [classes[(atom * n + point) * 5 + c] for c in range(5)]
                assert all(variable in assignment for variable in ids)
                selected = [c for c, variable in enumerate(ids) if assignment[variable]]
                assert len(selected) == 1
                point_colors.append(selected[0])
                needed.update(ids)
            record[side] = point_colors
        colors.append(record)
    counts = [sum(record[side][0] != record[side][1] for record in colors)
              for side in ('source', 'image')]
    assert counts == [4, 0]
    assert needed == {39, 40, 41}
    # Keep only the unit-propagation derivation ancestral to these three
    # classes; every referenced clause is in the old base, not the u CNF.
    used = set()

    def require(variable):
        index = reasons[variable]
        if index in used:
            return
        used.add(index)
        step = trace[index]
        for literal in base[step['clause_id'] - 1]:
            if abs(literal) != variable:
                assert reasons[abs(literal)] < index
                require(abs(literal))

    for variable in sorted(needed):
        require(variable)
    short = [dict(**trace[index], clause=list(base[trace[index]['clause_id'] - 1]))
             for index in sorted(used)]
    return dict(source_pair=list(source), image_pair=list(image),
                forced_word_colors=colors, unequal_counts=counts, denominator=5,
                base_root_forced_variables=len(assignment),
                relevant_forced_classes={str(v): assignment[v] for v in sorted(needed)},
                old_base_unit_derivation=short,
                scope=('The fixed old fourteen operators and proper-word constraints '
                       'already force unequal-event masses 4/5 and 0. No free-u CNF '
                       'or SAT result is used in this additional contradiction.'))


def _check_source_digest(source, claimed):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == claimed


def _check_classes_digest(classes, claimed):
    assert digest(classes) == claimed


def _check_proof(initial, variables, proof):
    assert proof['variables'] == variables
    assert proof['initial_clauses'] == len(initial)
    assert proof['formula_sha256'] == digest(initial)
    assert isinstance(proof['lrat'], list) and all(isinstance(line, str) for line in proof['lrat'])
    return check_rup(initial, proof['lrat'])


def _check_data(root, data, parent, context, _capture=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema'] == 1 and data['experiment'] == 'E089'
    assert data['search_model'] == 'E083_fixed_operator_quotient'
    assert data['result'] is None
    source = root / 'certificates/quintic_multiword_return_joint.json'
    _check_source_digest(source, data['source_sha256'])
    prior = json.loads(source.read_text())
    assert prior['experiment'] == 'E083'
    assert prior['geometry'] == data['geometry'] == parent['geometry']
    assert data['support'] == 5
    old = prior['result']
    words = old['words']
    n = len(context['points'])
    assert n == 10077 and len(words) == 5
    assert all(isinstance(w, str) and len(w) == n and set(w) <= set('01234') for w in words)
    assert all(w[i] != w[j] for w in words for i, j in context['edges'])
    definitions = _definitions(context)
    mappings = [_mapping(context, definition) for definition in definitions]
    assert old['motions'] == [definition[0] for definition in definitions[:14]]
    assert old['mapping_sha256'] == [digest(mapping) for mapping in mappings[:14]]
    classes, equations = _classes_by_bfs(n, old, mappings[:14])
    base = _base_clauses(n, context['edges'], classes)
    sample = {}
    for atom, word in enumerate(words):
        for point, label in enumerate(word):
            for c in range(5):
                variable = classes[(atom * n + point) * 5 + c]
                truth = int(label) == c
                assert sample.setdefault(variable, truth) == truth
    assert all(any(sample[abs(literal)] == (literal > 0) for literal in clause) for clause in base)
    quotient = data['quotient']
    assert quotient['original_color_variables'] == n * 25 == 251925
    assert quotient['equality_equations'] == equations
    assert quotient['quotient_color_variables'] == max(classes) == 718
    assert quotient['base_clauses'] == len(base)
    _check_classes_digest(classes, quotient['classes_sha256'])
    assert quotient['base_clauses_sha256'] == digest(base)
    assert quotient['clause_lengths'] == {str(k): v for k, v in sorted(Counter(map(len, base)).items())}
    assert quotient['saved_E083_assignment_checks'] is True
    new = mappings[14]
    assert len(new) == 29
    pair_obstruction = _forced_pair_obstruction(n, classes, base, new)
    additions, variables = _free_motion_clauses(n, classes, new)
    initial = base + additions
    assert variables == 1593 and max(abs(lit) for clause in initial for lit in clause) == variables
    proof = data['refutation']
    assert len(data['history']) == 1
    assert data['history'][0]['motion'] == 'dyadic_u'
    assert data['history'][0]['domain'] == len(new)
    refutation = _check_proof(initial, variables, proof)
    if _capture is not None:
        # A private mutation-test context filled only after a successful full
        # rebuild.  The public verifier never accepts caller-supplied caches.
        _capture.update(source=source, classes=classes, initial=initial, variables=variables)
    return dict(status='PASS', experiment='E089', geometry=parent['geometry'],
                source_sha256=data['source_sha256'],
                bfs_literal_components=max(classes), literal_equalities=equations,
                base_clauses=len(base), initial_clauses=len(initial), variables=variables,
                old_operators=14, new_motion='dyadic_u', new_domain=29,
                saved_E083_satisfies_base=True, independent_rup_refutation=refutation,
                direct_forced_pair_obstruction=pair_obstruction,
                scope=('Only the exact E083 fixed fourteen word/color operators on five '
                       'otherwise free proper words cannot extend by a free u operator. '
                       'Not unrestricted five-word full-joint, arbitrary support, or an HN bound.'))


def verify(root, certificate=None, mutation_checks=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    path = Path(certificate) if certificate else root / 'certificates/dyadic_fixed_representation.json'
    data = json.loads(path.read_text())
    parent, context = geometry(root, geometry_context=True)
    audit = {}
    report = _check_data(root, data, parent, context, audit if mutation_checks else None)
    if mutation_checks:
        bad_hint = copy.deepcopy(data['refutation'])
        final_id = bad_hint['lrat'][-1].split()[0]
        bad_hint['lrat'][-1] = f'{final_id} 0 999999999 0'
        missing_empty = copy.deepcopy(data['refutation'])
        missing_empty['lrat'] = missing_empty['lrat'][:-1]
        cases = [
            ('source_sha256', lambda: _check_source_digest(audit['source'], '0' * 64)),
            ('classes_sha256', lambda: _check_classes_digest(audit['classes'], '0' * 64)),
            ('missing_LRAT_hint', lambda: _check_proof(audit['initial'], audit['variables'], bad_hint)),
            ('missing_empty_clause', lambda: _check_proof(audit['initial'], audit['variables'], missing_empty)),
        ]
        rejected = []
        for name, action in cases:
            try:
                action()
            except (AssertionError, ValueError, KeyError):
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
