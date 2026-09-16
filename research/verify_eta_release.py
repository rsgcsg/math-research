"""Independent E094 formula reconstruction and optional RUP certification.

Thirteen E083 operator groups remain fixed.  Both eta and u operators, and
all five words, are free.  The checker reuses only independent E089 geometry,
BFS, proper-color CNF and free-motion encoding, never the producer or SAT.

The archival entry point requires a checked LRAT proof.  An internal helper
can distinguish a missing proof, but never turns solver UNSAT or raw DRUP into
mathematical evidence; deleting the archived proof makes verification fail.
"""

from pathlib import Path
import argparse
import copy
import hashlib
import json

from verify_dyadic_fixed_representation import (
    _base_clauses, _classes_by_bfs, _definitions, _free_motion_clauses,
    _mapping, geometry,
)
from verify_quintic_core_probe import digest
from verify_rup_lrat import check as check_rup


def _shift_auxiliaries(clauses, old_color_maximum, offset):
    """Preserve quotient literals; shift only freshly allocated auxiliaries."""
    return [[literal + offset if literal > old_color_maximum
             else literal - offset if literal < -old_color_maximum
             else literal for literal in clause] for clause in clauses]


def _reconstruct(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    source = root / 'certificates/quintic_multiword_return_joint.json'
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    prior = json.loads(source.read_text())
    assert prior['experiment'] == 'E083'
    parent, context = geometry(root, geometry_context=True)
    assert prior['geometry'] == parent['geometry']
    old = prior['result']
    words = old['words']
    n = len(context['points'])
    assert n == 10077 and len(words) == 5
    assert all(isinstance(word, str) and len(word) == n and set(word) <= set('01234') for word in words)
    assert all(word[i] != word[j] for word in words for i, j in context['edges'])
    definitions = _definitions(context)
    mappings = [_mapping(context, definition) for definition in definitions]
    assert len(definitions) == 15
    assert old['motions'] == [definition[0] for definition in definitions[:14]]
    assert old['mapping_sha256'] == [digest(mapping) for mapping in mappings[:14]]
    retained = [index for index in range(14) if index != 2]
    fixed = dict(words=words,
                 word_permutations=[old['word_permutations'][index] for index in retained],
                 color_permutations=[old['color_permutations'][index] for index in retained])
    classes, equations = _classes_by_bfs(n, fixed, [mappings[index] for index in retained])
    base = _base_clauses(n, context['edges'], classes)
    assert max(classes) == 6668 and len(base) == 49132 and equations == 443500
    sample = {}
    for atom, word in enumerate(words):
        for point, label in enumerate(word):
            for color in range(5):
                variable = classes[(atom * n + point) * 5 + color]
                truth = int(label) == color
                assert sample.setdefault(variable, truth) == truth
    assert all(any(sample[abs(literal)] == (literal > 0) for literal in clause) for clause in base)

    # Each independent call starts at the quotient variable maximum.  The
    # second block therefore needs an auxiliary-only shift.  This is exactly
    # sequential allocation, without importing the producer's stateful class.
    eta_clauses, eta_top = _free_motion_clauses(n, classes, mappings[2])
    u_local_clauses, u_local_top = _free_motion_clauses(n, classes, mappings[14])
    shift = eta_top - max(classes)
    u_clauses = _shift_auxiliaries(u_local_clauses, max(classes), shift)
    assert all(abs(literal) <= max(classes) or abs(literal) > eta_top
               for clause in u_clauses for literal in clause)
    initial = base + eta_clauses + u_clauses
    top = u_local_top + shift
    assert eta_top == 139043 and shift == 132375 and top == 139918
    assert len(eta_clauses) == 1984035 and len(u_clauses) == 11535
    assert len(initial) == 2044702
    assert max(abs(literal) for clause in initial for literal in clause) == top
    facts = dict(schema=1, experiment='E094', source_sha256=source_digest,
                 geometry=parent['geometry'], support=5,
                 retained_fixed_indices=retained,
                 free_motions=['eta', 'dyadic_u'],
                 free_domain_sizes=[len(mappings[index]) for index in (2, 14)],
                 mapping_sha256=[digest(mapping) for mapping in mappings],
                 equalities=equations, quotient_variables=max(classes),
                 base_clauses=len(base), classes_sha256=digest(classes),
                 formula_variables=top, formula_clauses=len(initial),
                 formula_sha256=digest(initial))
    return facts, initial


def _check_query_fields(record, facts):
    assert isinstance(record, dict)
    for key, expected in facts.items():
        assert record[key] == expected, f'E094 query mismatch: {key}'
    assert record['result'] is None, 'This entry point does not verify positive witnesses'
    assert isinstance(record['status'], str)
    assert record['solver'] in ('cadical195', 'glucose3')
    assert type(record['conflict_budget']) is int and 1 <= record['conflict_budget'] <= 20000


def _check_optional_proof(record, initial):
    if 'lrat_unchecked' not in record:
        return None
    lines = record['lrat_unchecked']
    assert isinstance(lines, list) and lines and all(isinstance(line, str) for line in lines)
    return check_rup(initial, lines)


def _check_required_proof(record, initial):
    proof = _check_optional_proof(record, initial)
    assert proof is not None, 'E094 archival verification requires the checked LRAT proof'
    return proof


def _check_eta_free_core(record, initial, base_count=49132, eta_count=1984035):
    """Reindex all hinted initial clauses; independently replay the short RUP."""
    count = len(initial)
    used_initial = set()
    parsed = []
    for line in record['lrat_unchecked']:
        fields = line.split()
        assert fields and fields[0] != 'c' and fields[1] != 'd'
        values = list(map(int, fields))
        identifier = values[0]
        stop = values.index(0, 1)
        clause = values[1:stop]
        hints = values[stop + 1:]
        assert hints and hints[-1] == 0 and all(h > 0 for h in hints[:-1])
        hints = hints[:-1]
        used_initial.update(hint for hint in hints if hint <= count)
        parsed.append((identifier, clause, hints))
    eta_start, eta_end = base_count + 1, base_count + eta_count
    eta_initial = sorted(i for i in used_initial if eta_start <= i <= eta_end)
    assert not eta_initial, 'This eta-free deduction requires zero eta-block initial hints'
    selected = sorted(used_initial)
    assert len(selected) == 1081
    core = [initial[identifier - 1] for identifier in selected]
    renumber = {identifier: new for new, identifier in enumerate(selected, 1)}
    core_lines = []
    for offset, (identifier, clause, hints) in enumerate(parsed, len(core) + 1):
        assert identifier not in renumber
        assert all(hint in renumber for hint in hints)
        core_lines.append(' '.join(map(str, [offset] + clause + [0] +
                                       [renumber[hint] for hint in hints] + [0])))
        renumber[identifier] = offset
    refutation = check_rup(core, core_lines)
    return dict(used_initial_clauses=len(selected),
                used_old_base_clauses=sum(i <= base_count for i in selected),
                used_eta_clauses=len(eta_initial),
                used_u_clauses=sum(i > eta_end for i in selected),
                eta_initial_clause_range=[eta_start, eta_end],
                used_initial_clause_ids=selected,
                core_formula_sha256=digest(core),
                reindexed_core_lrat_sha256=digest(core_lines),
                independently_checked_core_refutation=refutation,
                conclusion=('The thirteen retained fixed operators plus the free u '
                            'operator are already impossible; no eta joint obligation '
                            'is needed for this contradiction.'))


def verify(root, mutation_checks=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    paths = [root / 'certificates/dyadic_eta_release.json',
             root / 'certificates/dyadic_eta_release_proof_attempt.json']
    raw = [path.read_bytes() for path in paths]
    records = [json.loads(blob) for blob in raw]
    facts, initial = _reconstruct(root)
    for record in records:
        _check_query_fields(record, facts)
    assert records[0]['solver'] == 'cadical195' and records[1]['solver'] == 'glucose3'
    # The second file is the separately exported proof attempt.  The first
    # solver's unverified status/raw proof counts are retained as provenance,
    # not silently promoted to mathematical evidence.
    proof = _check_required_proof(records[1], initial)
    core = _check_eta_free_core(records[1], initial)
    report = dict(status='PASS', experiment='E094', geometry=facts['geometry'],
                  source_sha256=facts['source_sha256'],
                  query_artifact_sha256={path.name: hashlib.sha256(blob).hexdigest()
                                         for path, blob in zip(paths, raw)},
                  fixed_operator_groups=13, free_motions=facts['free_motions'],
                  quotient_variables=facts['quotient_variables'],
                  base_clauses=facts['base_clauses'],
                  formula_variables=facts['formula_variables'],
                  formula_clauses=facts['formula_clauses'],
                  formula_sha256=facts['formula_sha256'],
                  direct_checked_old_word_edges=5 * facts['geometry']['induced_edges'],
                  saved_E083_satisfies_retained_base=True,
                  solver_statistics_audited=False,
                  independent_rup_refutation=proof,
                  eta_free_core=core,
                  negative_mathematical_conclusion=True,
                  conclusion='CERTIFIED_RESTRICTED_REPRESENTATION_UNSAT',
                  scope=('Only five otherwise free words retaining the thirteen specified E083 '
                         'operators and free u; the independent core needs no eta obligation. '
                         'Missing checked LRAT is rejected by this archival entry point. '
                         'This is not an '
                         'unrestricted five-word/full-joint obstruction or an HN bound.'))
    if mutation_checks:
        source_bad = copy.deepcopy(records[0])
        source_bad['source_sha256'] = '0' * 64
        mapping_bad = copy.deepcopy(records[1])
        mapping_bad['mapping_sha256'][-1] = '0' * 64
        classes_bad = copy.deepcopy(records[1])
        classes_bad['classes_sha256'] = '0' * 64
        proof_bad = copy.deepcopy(records[1])
        proof_bad['lrat_unchecked'] = [f'{len(initial) + 1} 0 999999999 0']
        proof_missing_empty = copy.deepcopy(records[1])
        proof_missing_empty['lrat_unchecked'] = proof_missing_empty['lrat_unchecked'][:-1]
        proof_missing = copy.deepcopy(records[1])
        del proof_missing['lrat_unchecked']
        cases = [('source_sha256', lambda: _check_query_fields(source_bad, facts)),
                 ('complete_u_mapping_sha256', lambda: _check_query_fields(mapping_bad, facts)),
                 ('BFS_classes_sha256', lambda: _check_query_fields(classes_bad, facts)),
                 ('invalid_LRAT_hint', lambda: _check_required_proof(proof_bad, initial)),
                 ('missing_empty_clause', lambda: _check_required_proof(proof_missing_empty, initial)),
                 ('missing_proof', lambda: _check_required_proof(proof_missing, initial))]
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
    parser.add_argument('--mutations', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1], args.mutations), indent=2))
