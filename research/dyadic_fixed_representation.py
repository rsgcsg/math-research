"""Quotient the Boolean color variables by E083's *fixed* old operators.

Words are free, but the fourteen saved word/color permutations are not.  This
is a strict submodel of the full joint problem, not a complete obstruction
search.  Positive output can be checked by verify_dyadic_mixed_return_joint;
UNSAT output is explicitly untrusted until a separate proof is checked.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from quintic_multiword_joint import MultiwordEncoding
from verify_quintic_core_probe import digest
from verify_quintic_multiword_joint import _definitions, _mapping
from verify_quintic_tau_union import verify as geometry
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping as new_mapping


class DisjointSet:
    def __init__(self, size):
        self.parent = list(range(size))
        self.size = [1] * size

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def join(self, x, y):
        x, y = self.find(x), self.find(y)
        if x == y:
            return
        if self.size[x] < self.size[y]:
            x, y = y, x
        self.parent[y] = x
        self.size[x] += self.size[y]


class QuotientEncoding(MultiwordEncoding):
    def __init__(self, n, m, classes):
        self.n, self.m, self.k = n, m, 5
        self.classes = classes
        self.top = max(classes)
        self.clauses = []
        self.witness_vars = []

    def color(self, a, i, c):
        return self.classes[(a * self.n + i) * self.k + c]


def run(root, budget=20000, solver_name='cadical195', new_domains=1):
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    source = root / 'certificates/quintic_multiword_return_joint.json'
    old = json.loads(source.read_text())['result']
    parent, context = geometry(root, geometry_context=True)
    points, edges = context['points'], context['edges']
    n, m, k = len(points), len(old['words']), 5
    lookup = {p: i for i, p in enumerate(points)}
    definitions = _definitions(context)
    mappings = [_mapping(points, lookup, context['ring']['mul'], d) for d in definitions]
    assert len(definitions) == 14 and old['motions'] == [d[0] for d in definitions]
    assert old['mapping_sha256'] == [digest(mapping) for mapping in mappings]
    assert all(len(w) == n and set(w) <= set('01234') for w in old['words'])
    assert all(w[i] != w[j] for w in old['words'] for i, j in edges)

    dsu = DisjointSet(n * m * k)
    variable = lambda a, i, c: (a * n + i) * k + c
    equalities = 0
    for t, mapping in enumerate(mappings):
        sigma, palettes = old['word_permutations'][t], old['color_permutations'][t]
        assert sorted(sigma) == list(range(m))
        assert all(sorted(pi) == list(range(k)) for pi in palettes)
        for a in range(m):
            for i, j in mapping:
                assert int(old['words'][sigma[a]][j]) == palettes[a][int(old['words'][a][i])]
                for c in range(k):
                    dsu.join(variable(a, i, c), variable(sigma[a], j, palettes[a][c]))
                    equalities += 1
    ids = {}
    classes = [ids.setdefault(dsu.find(v), len(ids) + 1) for v in range(n * m * k)]
    enc = QuotientEncoding(n, m, classes)
    clauses = set()

    def add(clause):
        values = set(clause)
        if not any(-v in values for v in values):
            clauses.add(tuple(sorted(values)))

    for a in range(m):
        for i in range(n):
            variables = [enc.color(a, i, c) for c in range(k)]
            add(variables)
            for c in range(k):
                for d in range(c):
                    add([-variables[c], -variables[d]])
        for i, j in edges:
            for c in range(k):
                add([-enc.color(a, i, c), -enc.color(a, j, c)])
    clauses = sorted(clauses)
    sample = {}
    for a, w in enumerate(old['words']):
        for i in range(n):
            for c in range(k):
                v, truth = enc.color(a, i, c), int(w[i]) == c
                assert sample.setdefault(v, truth) == truth
    assert all(any(sample[abs(v)] == (v > 0) for v in clause) for clause in clauses)
    summary = dict(original_color_variables=n*m*k, equality_equations=equalities,
                   quotient_color_variables=len(ids), base_clauses=len(clauses),
                   clause_lengths=dict(sorted(Counter(map(len, clauses)).items())),
                   classes_sha256=digest(classes), base_clauses_sha256=digest(clauses),
                   saved_E083_assignment_checks=True)
    print(json.dumps(dict(quotient=summary)), flush=True)
    from pysat.solvers import Solver
    history, positive, refutation = [], None, None
    full_formula = list(clauses)
    with Solver(name=solver_name, bootstrap_with=clauses, with_proof=True) as solver:
        okay, implied = solver.propagate()
        assert okay
        fixed = {abs(v) for v in implied}
        summary['reported_root_implied_variables'] = len(fixed)
        for definition in _new_definitions(context)[:new_domains]:
            mapping = new_mapping(context, definition)
            definitions.append(definition)
            mappings.append(mapping)
            extra = enc.add_motion(mapping)
            full_formula.extend(extra)
            solver.append_formula(extra)
            solver.conf_budget(budget)
            answer = solver.solve_limited()
            status = ('SAT' if answer is True else
                      'UNSAT_FIXED_REPRESENTATION_UNCERTIFIED' if answer is False else 'UNKNOWN')
            stage = dict(motion=definition[0], domain=len(mapping), variables=enc.top,
                         status=status, stats=solver.accum_stats())
            history.append(stage)
            print(json.dumps(stage), flush=True)
            if answer is False:
                from mixed_shell_stack import rup_hints
                # CaDiCaL's incremental trace through propagate()/append_formula
                # did not end in an empty clause.  Certify the identical frozen
                # formula with a one-shot proof-producing solver, no new model.
                with Solver(name='glucose3', bootstrap_with=full_formula,
                            with_proof=True) as certifier:
                    certifier.conf_budget(budget)
                    certified_answer = certifier.solve_limited()
                    proof_run = dict(solver='glucose3', budget=budget,
                                     answer=certified_answer, stats=certifier.accum_stats())
                    assert certified_answer is False, proof_run
                    drup = certifier.get_proof()
                lrat = rup_hints(full_formula, drup)
                refutation = dict(formula_sha256=digest(full_formula),
                                  initial_clauses=len(full_formula), variables=enc.top,
                                  lrat=lrat, proof_run=proof_run)
            if answer is not True:
                break
            decoded = enc.decode(solver.get_model())
            positive = dict(words=decoded['words'], status='SAT',
                            word_permutations=old['word_permutations'] + decoded['word_permutations'],
                            color_permutations=old['color_permutations'] + decoded['color_permutations'],
                            motions=[d[0] for d in definitions],
                            mapping_sha256=[digest(mm) for mm in mappings],
                            mappings=mappings)
    return dict(schema=1, experiment='E089', search_model='E083_fixed_operator_quotient',
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                geometry=parent['geometry'], support=m, quotient=summary,
                solver=solver_name, conflict_budget_per_query=budget,
                history=history, result=positive, refutation=refutation,
                scope='Fixed old14 operators only. UNKNOWN/UNSAT is not a full-joint obstruction.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=20000)
    parser.add_argument('--solver', default='cadical195')
    parser.add_argument('--new-domains', type=int, choices=(1, 2), default=1)
    parser.add_argument('--certificate', action='store_true',
                        help='Save the generated research artifact in certificates/')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = run(root, args.budget, args.solver, args.new_domains)
    if args.certificate:
        (root / 'certificates/dyadic_fixed_representation.json').write_text(
            json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
