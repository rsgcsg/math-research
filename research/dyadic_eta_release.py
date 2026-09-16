"""One bounded query releasing eta, retaining the other thirteen operators.

This is a strict five-word representation, not a complete full-joint search.
All words, eta and u operators are free; only the other E083 operators stay
fixed. A negative solver answer is untrusted unless separately certified.
"""

import argparse
import hashlib
import json
from pathlib import Path

from dyadic_fixed_representation import QuotientEncoding
from verify_dyadic_fixed_representation import (
    _base_clauses, _classes_by_bfs, _definitions, _mapping)
from verify_quintic_core_probe import digest
from verify_quintic_tau_union import verify as geometry


def run(root, budget=20000, solver_name='cadical195'):
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    from pysat.solvers import Solver
    source = root / 'certificates/quintic_multiword_return_joint.json'
    old = json.loads(source.read_text())['result']
    parent, context = geometry(root, geometry_context=True)
    n = len(context['points'])
    definitions = _definitions(context)
    mappings = [_mapping(context, definition) for definition in definitions]
    assert [d[0] for d in definitions[:14]] == old['motions']
    assert [digest(m) for m in mappings[:14]] == old['mapping_sha256']
    retained = [i for i in range(14) if i != 2]
    fixed = {key: [old[key][i] for i in retained]
             for key in ('word_permutations', 'color_permutations')}
    fixed['words'] = old['words']
    classes, equations = _classes_by_bfs(n, fixed, [mappings[i] for i in retained])
    base = _base_clauses(n, context['edges'], classes)
    assert max(classes) == 6668 and len(base) == 49132
    enc = QuotientEncoding(n, 5, classes)
    formula = list(base)
    for index in (2, 14):
        formula.extend(enc.add_motion(mappings[index]))
    metadata = dict(
        schema=1, experiment='E094', source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        geometry=parent['geometry'], support=5, retained_fixed_indices=retained,
        free_motions=['eta', 'dyadic_u'], free_domain_sizes=[len(mappings[i]) for i in (2, 14)],
        mapping_sha256=[digest(m) for m in mappings], equalities=equations,
        quotient_variables=max(classes), base_clauses=len(base),
        classes_sha256=digest(classes), formula_variables=enc.top,
        formula_clauses=len(formula), formula_sha256=digest(formula),
        solver=solver_name, conflict_budget=budget)
    print(json.dumps(dict(progress='formula_ready', **metadata)), flush=True)
    with Solver(name=solver_name, bootstrap_with=formula, with_proof=True) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        metadata['status'] = ('SAT' if answer is True else 'UNKNOWN' if answer is None
                              else 'UNSAT_RESTRICTED_REPRESENTATION_UNCERTIFIED')
        metadata['stats'] = solver.accum_stats()
        metadata['result'] = None
        if answer is True:
            decoded = enc.decode(solver.get_model())
            sigmas = list(old['word_permutations']) + [decoded['word_permutations'][1]]
            palettes = list(old['color_permutations']) + [decoded['color_permutations'][1]]
            sigmas[2] = decoded['word_permutations'][0]
            palettes[2] = decoded['color_permutations'][0]
            metadata['result'] = dict(
                status='SAT', words=decoded['words'], word_permutations=sigmas,
                color_permutations=palettes, motions=[d[0] for d in definitions],
                mappings=mappings, mapping_sha256=metadata['mapping_sha256'])
        elif answer is False:
            proof = solver.get_proof()
            metadata['raw_proof_lines'] = len(proof)
            additions = [line for line in proof if not line.lstrip().startswith('d')]
            metadata['raw_proof_additions'] = len(additions)
            if len(additions) <= 20000:
                metadata['drup_unchecked'] = additions
            if len(additions) <= 512:
                from mixed_shell_stack import rup_hints
                try:
                    metadata['lrat_unchecked'] = rup_hints(formula, additions)
                except (AssertionError, ValueError, RuntimeError) as error:
                    metadata['proof_conversion_error'] = type(error).__name__
    metadata['scope'] = ('Only eta and u operators are free; thirteen saved operators and '
                         'support five are fixed. No negative full-joint or HN conclusion.')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=20000)
    parser.add_argument('--solver', choices=('cadical195', 'glucose3'), default='cadical195')
    parser.add_argument('--certificate', action='store_true')
    args = parser.parse_args()
    assert 1 <= args.budget <= 20000
    root = Path(__file__).resolve().parents[1]
    result = run(root, args.budget, args.solver)
    if args.certificate:
        filename = ('dyadic_eta_release.json' if args.solver == 'cadical195'
                    else 'dyadic_eta_release_proof_attempt.json')
        (root / 'certificates' / filename).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
