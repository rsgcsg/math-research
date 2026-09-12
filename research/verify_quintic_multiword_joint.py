"""Independent E080/E083 finite multiword full-domain positive-law checker.

Every word is checked on the independently rebuilt actual induced unit graph.
For each listed motion g, the certificate supplies bijections sigma of word
indices and pi[a] of colors satisfying

    words[sigma[a]][g(p)] = pi[a][words[a][p]]

on the complete maximal domain.  Uniformly sampling a word index and then an
independent global S5 relabeling therefore gives a common probability law.
No compatibility of the supplied bijections outside these domains is assumed.
This checks only a positive sufficient witness, never finite-support exhaustion.
The geometry and algebra dependencies below are independent checkers, not the
E080 producer.  Normal entry points always rebuild and check the geometry.
"""

from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import sys

from verify_quintic_core_probe import conjugate_twice, digest
from verify_quintic_tau_union import verify as geometry


def _definitions(context):
    """The fourteen physical motions, in the prescribed prefix order."""
    ring = context['ring']
    mul = ring['mul']
    one = (Q(1),) + (Q(0),) * 31
    zero = (Q(0),) * 32
    eta = zero[:16] + one[:16]
    z = ring['blocks'][0][64]
    nu = tuple(Q(5, 6) if i == 0 else Q(1, 6) if i == 10 else Q(0)
               for i in range(32))
    omega = tuple(-2 * x - 3 * y for x, y in zip(one, z))
    shift = tuple(x + y for x, y in zip(one, mul(eta, z)))
    definitions = [
        ('tau', ring['tau'], zero, False),
        ('nu', nu, zero, False),
        ('eta', eta, zero, False),
        ('omega', omega, zero, False),
        ('bar', one, zero, True),
        ('bridge', tuple(-x for x in eta), shift, False),
        ('translation_one', one, one, False),
        ('translation_z', one, z, False),
    ]
    power = one
    for j in range(1, 5):
        power = mul(power, eta)
        definitions.append((f'one_plus_eta_{j}', one,
                            tuple(x + y for x, y in zip(one, power)), False))
    definitions.append(('bridge_shift', one, shift, False))
    definitions.append(('minus_bar', tuple(-x for x in one), zero, True))
    # These are actual planar isometries, including the reflected fifth map.
    for _, a, _, _ in definitions:
        bar_a = tuple(Q(x) / 2 for x in conjugate_twice(a))
        assert mul(a, bar_a) == one
    return definitions


def _mapping(points, lookup, mul, definition):
    _, a, shift, reflection = definition
    mapping = []
    for i, p in enumerate(points):
        source = (tuple(Q(x) / 2 for x in conjugate_twice(p))
                  if reflection else p)
        target = tuple(x + y for x, y in zip(mul(a, source), shift))
        if target in lookup:
            mapping.append((i, lookup[target]))
    assert len({j for _, j in mapping}) == len(mapping)
    return mapping


def _permutation(values, size):
    assert isinstance(values, list) and len(values) == size
    assert all(type(value) is int for value in values)
    assert sorted(values) == list(range(size))


def _pattern(word, indices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in indices)


def _same_partition_law(words, mapping):
    source = [i for i, _ in mapping]
    image = [j for _, j in mapping]
    assert Counter(_pattern(word, source) for word in words) == Counter(
        _pattern(word, image) for word in words)


def _check_data(root, data, parent, context):
    """Check a payload after geometry() returned this parent/context pair.

    This private helper permits mutation tests to reuse already independently
    verified geometry.  Passing a producer cache here is not a verification;
    the public verify() entry point intentionally has no unchecked cache input.
    """
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    experiment = data['experiment']
    assert experiment in ('E080', 'E083')
    if 'schema' in data:
        assert type(data['schema']) is int and data['schema'] == 1
    assert data['geometry'] == parent['geometry']
    result = data['result']
    if 'status' in result:
        assert result['status'] == 'SAT'
    words = result['words']
    assert isinstance(words, list) and words
    if 'support' in data:
        assert type(data['support']) is int and data['support'] == len(words)
    points = context['points']
    edges = context['edges']
    for word in words:
        assert isinstance(word, str) and len(word) == len(points)
        assert set(word) <= set('01234')
        assert all(word[i] != word[j] for i, j in edges)

    definitions = _definitions(context)
    names = result['motions']
    assert isinstance(names, list)
    if experiment == 'E080':
        assert 9 <= len(names) <= 13
    else:
        assert len(names) == 14
    assert names == [definition[0] for definition in definitions[:len(names)]]
    for key in ('mapping_sha256', 'word_permutations', 'color_permutations'):
        assert isinstance(result[key], list) and len(result[key]) == len(names)

    lookup = {p: i for i, p in enumerate(points)}
    mul = context['ring']['mul']
    # All fourteen are independently extracted: the unused suffix is needed
    # to authenticate the old obligations, not to claim it is satisfied.
    maps = {definition[0]: _mapping(points, lookup, mul, definition)
            for definition in definitions}
    domains = []
    for idx, name in enumerate(names):
        mapping = maps[name]
        assert digest(mapping) == result['mapping_sha256'][idx]
        sigma = result['word_permutations'][idx]
        permutations = result['color_permutations'][idx]
        _permutation(sigma, len(words))
        assert isinstance(permutations, list) and len(permutations) == len(words)
        for atom, pi in enumerate(permutations):
            _permutation(pi, 5)
            source_word, image_word = words[atom], words[sigma[atom]]
            assert all(int(image_word[j]) == pi[int(source_word[i])]
                       for i, j in mapping)
        # This direct full-partition multiset check does not rely on the
        # certificate's proposed word and color permutations.
        _same_partition_law(words, mapping)
        domains.append(dict(motion=name, domain=len(mapping)))

    old = json.loads((root / 'certificates/quintic_full_translation_laws.json').read_text())
    assert old['schema'] == 1 and old['experiment'] == 'E065'
    old_names = ['eta', 'conjugate', 'bridge', 'translation_one', 'translation_z',
                 'one_plus_eta_1', 'one_plus_eta_2', 'one_plus_eta_3',
                 'one_plus_eta_4', 'bridge_shift']
    assert [motion['name'] for motion in old['motions']] == old_names
    old_points = context['ring']['points']
    old_ids = [lookup[p] for p in old_points]
    reverse_old = {new_id: old_id for old_id, new_id in enumerate(old_ids)}
    retained, missing = [], []
    for motion in old['motions']:
        name = 'bar' if motion['name'] == 'conjugate' else motion['name']
        expected = [[reverse_old[i], reverse_old[j]] for i, j in maps[name]
                    if i in reverse_old and j in reverse_old]
        # This is an equality with the independently extracted complete old-X
        # domain, not a subset claim based on an unverified historical list.
        assert expected == motion['mapping']
        if name in names:
            lifted = [(old_ids[i], old_ids[j]) for i, j in expected]
            _same_partition_law(words, lifted)
            retained.append(motion['name'])
        else:
            missing.append(motion['name'])

    event_path = root / 'certificates/joint_column_pricing.json'
    assert hashlib.sha256(event_path.read_bytes()).hexdigest() == old['event_source_sha256']
    events = json.loads(event_path.read_text())['events']
    assert len(events) == 18
    map_sets = {name: set(mapping) for name, mapping in maps.items()}
    retained_events, missing_events = [], []
    for event_index, event in enumerate(events):
        name = (event['motion'] if event['translation'] is None
                else event['translation_label'])
        name = 'bar' if name == 'conjugate' else name
        pairs = event['pairs']
        assert isinstance(pairs, list) and len(pairs) == 4
        assert all(isinstance(pair, list) and len(pair) == 2
                   and all(type(i) is int and 0 <= i < len(old_ids) for i in pair)
                   for pair in pairs)
        assert len({i for i, _ in pairs}) == len({j for _, j in pairs}) == 4
        lifted = [(old_ids[i], old_ids[j]) for i, j in pairs]
        assert all(pair in map_sets[name] for pair in lifted)
        if name in names:
            _same_partition_law(words, lifted)
            retained_events.append(event_index)
        else:
            missing_events.append(event_index)
    retained_prefix = min(len(names), 13)
    assert len(retained) == retained_prefix - 3
    assert len(retained_events) == 3 * (retained_prefix - 7)
    if len(names) >= 13:
        assert not missing and not missing_events
        assert len(retained) == 10 and len(retained_events) == 18

    return dict(
        status='PASS', experiment=experiment, geometry=parent['geometry'],
        proper_words=len(words), checked_word_edges=len(words) * len(edges),
        full_domains=domains, direct_full_partition_multisets=True,
        retained_E065_maps=retained, missing_E065_maps=missing,
        retained_E063_quartets=len(retained_events),
        retained_E063_event_indices=retained_events,
        missing_E063_event_indices=missing_events,
        scope=('Uniform word-index law with global S5 averaging on the listed '
               'complete domains only; not all integral motions, arbitrary '
               'support exhaustion, a field coloring, or a new HN bound'))


def verify(root, certificate=None, geometry_context=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    path = (Path(certificate) if certificate is not None
            else root / 'certificates/quintic_multiword_joint.json')
    data = json.loads(path.read_text())
    parent, context = geometry(root, geometry_context=True)
    report = _check_data(root, data, parent, context)
    return (report, context) if geometry_context else report


if __name__ == '__main__':
    assert len(sys.argv) <= 2
    certificate = Path(sys.argv[1]) if len(sys.argv) == 2 else None
    print(json.dumps(verify(Path(__file__).resolve().parents[1], certificate), indent=2))
