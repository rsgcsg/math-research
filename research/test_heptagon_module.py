"""Positive replay and deliberately corrupted heptagon certificates."""
from copy import deepcopy
from pathlib import Path
import json

from verify_heptagon_module import verify, verify_extensions, verify_three_tree, phi_mask
from fractions import Fraction


def main():
    if not __debug__:
        raise RuntimeError('assertions required')
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'certificates/heptagon_module.json').read_text())
    result = verify(data)
    assert phi_mask((Fraction(1,7), Fraction(-3,7))) == 3
    try:
        phi_mask((Fraction(1,2),))
    except ValueError:
        pass
    else:
        raise AssertionError('even denominator accepted')
    mutants = []

    def changed(path, value):
        copy = deepcopy(data)
        at = copy
        for key in path[:-1]:
            at = at[key]
        at[path[-1]] = value
        mutants.append(copy)

    changed(['field', 'rational_r', 0, 0], 3)
    changed(['field', 'basis_order', 0], 'w^0z^0')
    changed(['geometry_check', 'unordered_unit_pairs'], 41)
    changed(['geometry_check', 'nonunit_pair_norms', 0, 'norm', 0, 0], 2)
    changed(['geometry_check', 'nonunit_pair_norms', 0, 'pair'], [['P', 0], ['P', 1]])
    changed(['directions', 0, 'mod2_mask'], 0)
    changed(['directions', 0, 'exact_norm', 0, 0], 2)
    changed(['directions', 0], data['directions'][1])
    changed(['search', 'stages', 1, 'successful_first_functional_count'], 125)
    changed(['search', 'stages', 1, 'successful_first_functionals_and_representative_second', 0, 'second_mask'], 0)
    changed(['search', 'stages', 1, 'successful_first_functionals_and_representative_second', 0, 'second_solution_nullity'], 2)
    changed(['search', 'stages', 2, 'linear_map_exists'], True)
    changed(['search', 'stages', 2, 'reduced_direction_count'], 62)
    changed(['search', 'stages', 2, 'first_functionals_examined'], 4095)
    for i, mutant in enumerate(mutants):
        try:
            verify(mutant)
        except (AssertionError, ValueError, KeyError, IndexError):
            continue
        raise AssertionError(f'mutation {i} accepted')
    extension = json.loads((root/'certificates/heptagon_table_extensions.json').read_text())
    extended = verify_extensions(extension)
    for i in range(6):
        bad = deepcopy(extension)
        bad['extensions'][i]['masks'][0] ^= 1
        try:
            verify_extensions(bad)
        except AssertionError:
            continue
        raise AssertionError('bad extension accepted')
    tree = json.loads((root/'certificates/heptagon_three_tree.json').read_text())
    lower = verify_three_tree(tree)
    tree_mutants = []
    bad = deepcopy(tree)
    bad['root_palette'][1][1] = 0
    tree_mutants.append(bad)
    bad = deepcopy(tree)
    bad['nodes']['children'].pop(next(iter(bad['nodes']['children'])))
    tree_mutants.append(bad)
    bad = deepcopy(tree)
    bad['nodes'] = {'blocked_vertex': 1}
    tree_mutants.append(bad)
    bad = deepcopy(tree)
    bad['edges'].pop()
    tree_mutants.append(bad)
    for bad in tree_mutants:
        try:
            verify_three_tree(bad)
        except AssertionError:
            continue
        raise AssertionError('bad tree accepted')
    print(json.dumps(dict(heptagon_module=result, extensions=extended, lower=lower,
                          mutation_rejections=len(mutants)+6+len(tree_mutants)), sort_keys=True))


if __name__ == '__main__':
    main()
