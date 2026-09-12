"""Independent E084 old-fourteen plus dyadic-return positive-law checker.

Only independent geometry/algebra and the frozen independent old-motion
definitions are reused.  The producer and its motion matrices are not imported.
The two new motions are reconstructed from rational ambient coefficients and
cross-checked against their eta/z expression.  A successful certificate is a
uniform word-index law with global S5 averaging on exactly the listed domains.
"""

from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json

from verify_quintic_core_probe import conjugate_twice, digest
from verify_quintic_multiword_joint import _definitions as old_definitions
from verify_quintic_tau_union import verify as geometry


def _new_definitions(context):
    mul = context['ring']['mul']
    zero = (Q(0),) * 32
    one = (Q(1),) + zero[1:]
    eta = zero[:16] + one[:16]
    z = tuple(-Q(1, 2) if i == 0 else -Q(1, 6) if i == 9 else Q(0)
              for i in range(32))
    tau = tuple(-Q(1, 10) if i == 0 else Q(3, 10) if i == 10 else Q(0)
                for i in range(32))
    u = tuple({0: Q(1, 8), 4: -Q(3, 8), 9: -Q(1, 8), 13: -Q(1, 8)}.get(i, Q(0))
              for i in range(32))
    bar_eta = tuple(Q(x) / 2 for x in conjugate_twice(eta))
    h_plus_one = tuple(a + b + c for a, b, c in zip(eta, bar_eta, one))
    expression = tuple((a + 3 * b) / 2 for a, b in zip(one, mul(h_plus_one, z)))
    assert u == expression
    assert z == context['ring']['blocks'][0][64]
    assert tau == context['ring']['tau']
    for a in (u, tau):
        bar_a = tuple(Q(x) / 2 for x in conjugate_twice(a))
        assert mul(a, bar_a) == one
    assert mul(u, tau) == mul(tau, u)
    return [('dyadic_u', u, zero, False),
            ('dyadic_u_tau_bar', mul(u, tau), zero, True)]


def _mapping(context, definition):
    points = context['points']
    lookup = {point: i for i, point in enumerate(points)}
    mul = context['ring']['mul']
    _, coefficient, shift, reflection = definition
    result = []
    for i, point in enumerate(points):
        argument = (tuple(Q(x) / 2 for x in conjugate_twice(point))
                    if reflection else point)
        image = tuple(x + y for x, y in zip(mul(coefficient, argument), shift))
        if image in lookup:
            result.append((i, lookup[image]))
    assert len({j for _, j in result}) == len(result)
    return result


def _permutation(values, size):
    assert isinstance(values, list) and len(values) == size
    assert all(type(value) is int for value in values)
    assert sorted(values) == list(range(size))


def _pattern(word, indices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in indices)


def _check_data(root, data, parent, context):
    """Private payload check; parent/context must come from geometry()."""
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema'] == 1 and data['experiment'] == 'E084'
    assert data['geometry'] == parent['geometry']
    source_path = root / 'certificates/quintic_multiword_return_joint.json'
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == data['source_sha256']
    previous = json.loads(source_path.read_text())
    assert previous['experiment'] == 'E083'
    assert previous['geometry'] == parent['geometry']
    result = data['result']
    assert isinstance(result, dict)
    if 'status' in result:
        assert result['status'] == 'SAT'
    words = result['words']
    assert isinstance(words, list) and words
    assert type(data['support']) is int and data['support'] == len(words)
    for word in words:
        assert isinstance(word, str) and len(word) == len(context['points'])
        assert set(word) <= set('01234')
        assert all(word[i] != word[j] for i, j in context['edges'])

    old = old_definitions(context)
    assert len(old) == 14
    assert previous['result']['motions'] == [definition[0] for definition in old]
    definitions = old + _new_definitions(context)
    names = result['motions']
    assert isinstance(names, list) and len(names) in (15, 16)
    assert names == [definition[0] for definition in definitions[:len(names)]]
    for key in ('mapping_sha256', 'mappings', 'word_permutations', 'color_permutations'):
        assert isinstance(result[key], list) and len(result[key]) == len(names)
    domains = []
    for index, definition in enumerate(definitions[:len(names)]):
        mapping = _mapping(context, definition)
        assert [list(pair) for pair in mapping] == result['mappings'][index]
        assert digest(mapping) == result['mapping_sha256'][index]
        if index < 14:
            assert digest(mapping) == previous['result']['mapping_sha256'][index]
        else:
            assert len(mapping) == (29 if index == 14 else 33)
        sigma = result['word_permutations'][index]
        palettes = result['color_permutations'][index]
        _permutation(sigma, len(words))
        assert isinstance(palettes, list) and len(palettes) == len(words)
        for atom, pi in enumerate(palettes):
            _permutation(pi, 5)
            assert all(int(words[sigma[atom]][j]) == pi[int(words[atom][i])]
                       for i, j in mapping)
        source, image = [i for i, _ in mapping], [j for _, j in mapping]
        assert Counter(_pattern(word, source) for word in words) == Counter(
            _pattern(word, image) for word in words)
        domains.append(dict(motion=definition[0], domain=len(mapping)))
    return dict(
        status='PASS', experiment='E084', geometry=parent['geometry'],
        proper_words=len(words), checked_word_edges=len(words) * len(context['edges']),
        full_domains=domains, retained_E083_full_domains=14,
        direct_full_partition_multisets=True,
        scope=('The saved proper multiword law repairs exactly the listed fifteen '
               'or sixteen complete domains; preserves the old fourteen on the '
               'same physical Y; not all motions, a host coloring, or a new HN bound'))


def _check_probe_data(root, data, parent, context):
    """Check only the two proposed new domains and their old-law events."""
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    assert data['schema'] == 1 and data['experiment'] == 'E084'
    assert data['geometry'] == parent['geometry']
    source = root / 'certificates/quintic_multiword_return_joint.json'
    assert data['source_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    previous = json.loads(source.read_text())
    assert previous['experiment'] == 'E083' and previous['geometry'] == parent['geometry']
    words = previous['result']['words']
    assert words and all(isinstance(word, str) and len(word) == len(context['points'])
                         and set(word) <= set('01234') for word in words)
    assert all(word[i] != word[j] for word in words for i, j in context['edges'])
    definitions = _new_definitions(context)
    assert data['unit'] == dict(coordinates=[str(x) for x in definitions[0][1]],
                                norm_squared='1', commutes_with_tau=True)
    records = data['probes']
    assert len({record['motion'] for record in records}) == len(records)
    by_name = {record['motion']: record for record in records}
    verified = []
    for definition, expected_size in zip(definitions, (29, 33)):
        mapping = _mapping(context, definition)
        assert len(mapping) == expected_size
        record = by_name[definition[0]]
        assert record['domain'] == len(mapping)
        assert record['mapping'] == [list(pair) for pair in mapping]
        assert record['mapping_sha256'] == digest(mapping)
        sources, images = [i for i, _ in mapping], [j for _, j in mapping]
        left = Counter(_pattern(word, sources) for word in words)
        right = Counter(_pattern(word, images) for word in words)
        assert left != right and record['full_partition_equal'] is False
        event = record['event']
        assert isinstance(event, dict) and event['predicates']
        motion = dict(mapping)
        for predicate in event['predicates']:
            assert set(predicate) == {'source', 'image', 'equal'}
            assert type(predicate['equal']) is bool
            for side in ('source', 'image'):
                assert isinstance(predicate[side], list) and len(predicate[side]) == 2
                assert all(type(i) is int and 0 <= i < len(context['points'])
                           for i in predicate[side])
                assert predicate[side][0] != predicate[side][1]
            assert [motion[i] for i in predicate['source']] == predicate['image']
        counts = [sum(all((word[p[side][0]] == word[p[side][1]]) == p['equal']
                          for p in event['predicates']) for word in words)
                  for side in ('source', 'image')]
        assert counts == event['counts'] and counts[0] != counts[1]
        verified.append(dict(motion=definition[0], full_domain=len(mapping),
                             predicates=event['predicates'], old_E083_counts=counts))
    return dict(
        status='PASS', experiment='E084', geometry=parent['geometry'],
        verified_old_law_diagnostics=verified,
        proper_source_words=len(words),
        scope=('Only the two independently reconstructed dyadic_u and '
               'dyadic_u_tau_bar domains and saved-E083 discrepancies; other '
               'probe records, common paths and fiber summaries are not audited '
               'by this entry point; not failure of all proper laws'))


def verify(root, certificate=None, geometry_context=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    path = (Path(certificate) if certificate is not None
            else root / 'certificates/dyadic_mixed_return_joint.json')
    data = json.loads(path.read_text())
    parent, context = geometry(root, geometry_context=True)
    report = _check_data(root, data, parent, context)
    return (report, context) if geometry_context else report


def verify_probe(root, certificate=None, geometry_context=False):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    path = (Path(certificate) if certificate is not None
            else root / 'certificates/dyadic_mixed_return_probe.json')
    data = json.loads(path.read_text())
    parent, context = geometry(root, geometry_context=True)
    report = _check_probe_data(root, data, parent, context)
    return (report, context) if geometry_context else report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--probe', action='store_true',
                        help='Verify the two saved-law diagnostics, not a positive joint law')
    args = parser.parse_args()
    entry = verify_probe if args.probe else verify
    print(json.dumps(entry(Path(__file__).resolve().parents[1]), indent=2))
