"""Independent direct check of a negative column, never a joint certificate.

No SAT package or producer is imported. The actual induced geometry and the
maximal dyadic-u domain are rebuilt by existing independent algebra checkers.
"""

from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json

from verify_quintic_tau_union import verify as geometry
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping
from verify_quintic_core_probe import digest


def partition(word, indices):
    # Equivalence classes are canonicalized in order of first occurrence.
    first = {}
    answer = []
    for vertex in indices:
        color = word[vertex]
        if color not in first:
            first[color] = len(first)
        answer.append(first[color])
    return tuple(answer)


def _check_data(root, data, parent, context, mapping):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema'] == 1
    assert data['experiment'] == 'dyadic_joint_column_pricing_20260916'
    assert data['geometry'] == parent['geometry']
    assert len(mapping) == 29
    assert data['mapping'] == [list(pair) for pair in mapping]
    assert data['mapping_sha256'] == digest(mapping)
    files = ('quintic_multiword_joint.json', 'quintic_multiword_return_joint.json',
             'quintic_tau_union.json')
    assert len(data['source_files']) == 3
    words = []
    for index, name in enumerate(files):
        raw = (root / 'certificates' / name).read_bytes()
        source = json.loads(raw)
        assert source['geometry'] == parent['geometry']
        current = (source['result']['words'] if index < 2
                   else [source['result']['five_coloring']])
        assert len(current) == (5 if index < 2 else 1)
        assert data['source_files'][index] == dict(
            file=name, sha256=hashlib.sha256(raw).hexdigest(), count=len(current))
        words.extend(current)
    left, right = [i for i, j in mapping], [j for i, j in mapping]
    source_patterns = {partition(word, left) for word in words}
    image_patterns = {partition(word, right) for word in words}
    assert len(source_patterns) == 11 and len(image_patterns) == 10
    assert source_patterns.isdisjoint(image_patterns)
    assert data['pool_source_patterns'] == [list(p) for p in sorted(source_patterns)]
    assert data['pool_image_patterns'] == [list(p) for p in sorted(image_patterns)]
    values = [int(partition(w, left) in source_patterns)
              - int(partition(w, right) in source_patterns) for w in words]
    assert values == [1] * 11 and data['pool_cut_values'] == values
    result = data['result']
    assert isinstance(result, dict) and data['query']['status'] == 'SAT'
    word = result['word']
    for current in words + [word]:
        assert isinstance(current, str) and len(current) == len(context['points'])
        assert set(current) <= set('01234')
        assert all(current[i] != current[j] for i, j in context['edges'])
    new_source, new_image = partition(word, left), partition(word, right)
    assert new_source not in source_patterns and new_image in source_patterns
    assert result['source_pattern'] == list(new_source)
    assert result['image_pattern'] == list(new_image)
    assert result['cut_value'] == -1
    # Do not discard the new full-pattern row after killing the aggregate
    # cut. It occurs on the source side only in this twelve-column pool.
    assert new_source not in image_patterns and new_source != new_image
    new_row = [int(partition(w, left) == new_source)
               - int(partition(w, right) == new_source) for w in words + [word]]
    assert new_row == [0] * 11 + [1]
    # A strictly positive separator for the enlarged pool: the directed
    # pattern graph remains a DAG new_source -> old_sources -> old_images.
    def raised_potential(pat):
        return 2 if pat == new_source else int(pat in source_patterns)
    raised_values = [raised_potential(partition(w, left))
                     - raised_potential(partition(w, right)) for w in words + [word]]
    assert raised_values == [1] * 12
    # The difference of two indicators is always >= -1. The checked word
    # attains that value, proving the exact all-proper minimum of THIS cut.
    return dict(status='PASS', experiment=data['experiment'],
                geometry=parent['geometry'], complete_domain=29,
                proper_old_words=11, proper_new_words=1,
                checked_word_edges=12 * len(context['edges']),
                pool_source_patterns=11, pool_image_patterns=10,
                old_pool_cut_values=values, global_single_cut_minimum=-1,
                new_full_pattern_row=new_row,
                enlarged_pool_strict_cut_values=raised_values,
                scope=('All real reweightings of the specified eleven-word pool '
                       'fail dyadic-u invariance, but this one cut is invalid on '
                       'the full proper-coloring space. No full joint, convergence '
                       'of column generation, non-5 graph, or new HN bound.'))


def _check_cycle_data(root, cycle, pricing, parent, mapping):
    """Refute only E086's prescribed last-column patterns, without a solver."""
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert cycle['schema'] == 1 and cycle['experiment'] == 'E086'
    assert cycle['geometry'] == parent['geometry']
    assert cycle['mapping'] == [list(pair) for pair in mapping]
    assert cycle['mapping_sha256'] == digest(mapping)
    raw = (root / 'certificates/dyadic_joint_column_pricing.json').read_bytes()
    assert cycle['pricing_source_sha256'] == hashlib.sha256(raw).hexdigest()
    assert cycle['query']['status'] == 'UNSAT_FIXED_CYCLE_UNCERTIFIED'
    assert cycle['result'] is None
    words = []
    for source in pricing['source_files']:
        raw = (root / 'certificates' / source['file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source['sha256']
        result = json.loads(raw)['result']
        words.extend(result['words'] if 'words' in result else [result['five_coloring']])
    left, right = [i for i, j in mapping], [j for i, j in mapping]
    priced = pricing['result']['word']
    middle = partition(priced, right)
    index = next(i for i, word in enumerate(words) if partition(word, left) == middle)
    assert index == cycle['old_pool_index'] == 8
    source_target = partition(words[index], right)
    image_target = partition(priced, left)
    assert len({source_target, image_target, middle}) == 3
    physical_pair = (2321, 3451)
    assert all(vertex in left and vertex in right for vertex in physical_pair)
    source_positions = [left.index(vertex) for vertex in physical_pair]
    image_positions = [right.index(vertex) for vertex in physical_pair]
    assert source_positions == [6, 9] and image_positions == [8, 20]
    source_blocks = [source_target[position] for position in source_positions]
    image_blocks = [image_target[position] for position in image_positions]
    assert source_blocks == [0, 3] and image_blocks == [0, 0]
    # The same two physical points must be different in the source target,
    # but equal in the image target. This refutes ANY coloring, even without
    # graph edges or a bound on its palette. SAT's negative status is unused.
    assert (source_blocks[0] == source_blocks[1]) != (image_blocks[0] == image_blocks[1])
    return dict(status='REFUTED_BY_OVERLAP_PARTITION', experiment='E086',
                old_pool_index=index, physical_pair=list(physical_pair),
                source_positions=source_positions, image_positions=image_positions,
                source_blocks=source_blocks, image_blocks=image_blocks,
                independent_of_unit_edges=True,
                scope=('Only the prescribed final column of the selected three-cycle '
                       'is impossible. Other cycles, other proper columns, all-word '
                       'joint feasibility and the HN bounds remain unproved.'))


def verify(root, mutation_checks=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    data = json.loads((root / 'certificates/dyadic_joint_column_pricing.json').read_text())
    parent, context = geometry(root, geometry_context=True)
    mapping = _mapping(context, _new_definitions(context)[0])
    report = _check_data(root, data, parent, context, mapping)
    cycle = json.loads((root / 'certificates/dyadic_joint_cycle_close.json').read_text())
    report['cycle_close'] = _check_cycle_data(root, cycle, data, parent, mapping)
    if mutation_checks:
        cases = []
        bad = deepcopy(data)
        edge = context['edges'][0]
        word = list(bad['result']['word'])
        word[edge[1]] = word[edge[0]]
        bad['result']['word'] = ''.join(word)
        cases.append(('monochromatic_actual_edge', bad))
        bad = deepcopy(data); bad['mapping'][0][1] += 1
        cases.append(('altered_mapping', bad))
        bad = deepcopy(data); bad['source_files'][0]['sha256'] = '0' * 64
        cases.append(('altered_pool_provenance', bad))
        bad = deepcopy(data); bad['result']['cut_value'] = 0
        cases.append(('altered_cut_value', bad))
        rejected = []
        for name, bad in cases:
            try:
                _check_data(root, bad, parent, context, mapping)
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
