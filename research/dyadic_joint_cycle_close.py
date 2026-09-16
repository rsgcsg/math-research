"""Close the witnessed u-pattern path by one unrestricted proper-coloring query.

This searches one full-domain circulation, not the old fourteen-domain joint.
Negative solver states are never treated as all-word obstruction certificates.
"""
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import argparse
import hashlib
import json

from quintic_multiword_joint import MultiwordEncoding
from verify_quintic_tau_union import verify as geometry
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping
from verify_quintic_core_probe import digest


def pattern(word, positions):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in positions)


def run(root, budget):
    from pysat.solvers import Solver
    parent, context = geometry(root, geometry_context=True)
    pairs = _mapping(context, _new_definitions(context)[0])
    left, right = [i for i, _ in pairs], [j for _, j in pairs]
    pricing_path = root / 'certificates/dyadic_joint_column_pricing.json'
    raw = pricing_path.read_bytes()
    pricing = json.loads(raw)
    assert parent['geometry'] == pricing['geometry']
    assert digest(pairs) == pricing['mapping_sha256']
    words = []
    for source in pricing['source_files']:
        source_raw = (root / 'certificates' / source['file']).read_bytes()
        assert hashlib.sha256(source_raw).hexdigest() == source['sha256']
        result = json.loads(source_raw)['result']
        words.extend(result['words'] if 'words' in result else [result['five_coloring']])
    priced = pricing['result']['word']
    middle = pattern(priced, right)
    old_index = next(i for i, word in enumerate(words) if pattern(word, left) == middle)
    old = words[old_index]
    target_source = pattern(old, right)
    target_image = pattern(priced, left)
    assert len({middle, target_source, target_image}) == 3
    for word in (old, priced):
        assert all(word[i] != word[j] for i, j in context['edges'])
    enc = MultiwordEncoding(len(context['points']), context['edges'], 1)
    for index, color in zip(left, target_source):
        enc.clauses.append([enc.color(0, index, color)])
    choices = []
    for palette in permutations(range(5), max(target_image) + 1):
        selector = enc.fresh()
        choices.append(selector)
        for index, block in zip(right, target_image):
            enc.clauses.append([-selector, enc.color(0, index, palette[block])])
    enc.clauses.append(choices)
    print(json.dumps(dict(progress='cycle_formula_ready', vertices=len(context['points']),
                          old_index=old_index, variables=enc.top, clauses=len(enc.clauses))), flush=True)
    with Solver(name='cadical195', bootstrap_with=enc.clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        status = 'SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_FIXED_CYCLE_UNCERTIFIED'
        witness = None
        if answer is True:
            model = {v for v in solver.get_model() if v > 0}
            word = ''.join(str(next(c for c in range(5) if enc.color(0, i, c) in model))
                           for i in range(len(context['points'])))
            assert pattern(word, left) == target_source
            assert pattern(word, right) == target_image
            assert all(word[i] != word[j] for i, j in context['edges'])
            witness = dict(words=[priced, old, word], weights=['1/3'] * 3,
                           pattern_cycle=[target_image, middle, target_source])
        stats = solver.accum_stats()
    return dict(schema=1, experiment='E086',
                pricing_source_sha256=hashlib.sha256(raw).hexdigest(),
                geometry=parent['geometry'], mapping=pairs, mapping_sha256=digest(pairs),
                old_pool_index=old_index,
                query=dict(status=status, conflict_budget=budget, stats=stats),
                result=witness,
                scope='Only the complete u domain; no assertion about the old fourteen domains or HN.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=20000)
    args = parser.parse_args()
    assert 1 <= args.budget <= 20000
    result = run(Path(__file__).resolve().parents[1], args.budget)
    print('CYCLE_FINAL_JSON=' + json.dumps(result, separators=(',', ':')), flush=True)
