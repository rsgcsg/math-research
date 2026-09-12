"""Independent E081 all-pair audit and small saved-law discrepancy checker.

The exact maximal domain of p -> -conjugate(p) is rebuilt directly with
Fractions.  No return-probe mapping or event-search algorithm is imported.
The conclusion concerns the saved E080 law only, never all proper words.
"""

from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json

from verify_quintic_core_probe import conjugate_twice, digest
from verify_quintic_tau_union import verify as geometry


def _pattern(word, indices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in indices)


def _prepare(root):
    parent, context = geometry(root, geometry_context=True)
    path = root / 'certificates/quintic_multiword_joint.json'
    data = json.loads(path.read_text())
    assert data['experiment'] == 'E080' and data['geometry'] == parent['geometry']
    words = data['result']['words']
    points = context['points']
    assert words and all(isinstance(w, str) and len(w) == len(points)
                         and set(w) <= set('01234') for w in words)
    assert all(w[i] != w[j] for w in words for i, j in context['edges'])
    lookup = {p: i for i, p in enumerate(points)}
    mapping = []
    for i, p in enumerate(points):
        target = tuple(-Q(x) / 2 for x in conjugate_twice(p))
        if target in lookup:
            mapping.append((i, lookup[target]))
    assert len(mapping) == 1866
    assert set(mapping) == {(j, i) for i, j in mapping}
    source, image = zip(*mapping)
    left = Counter(_pattern(w, source) for w in words)
    right = Counter(_pattern(w, image) for w in words)
    assert left != right
    provenance = dict(
        schema=1, experiment='E081', diagnostic='minus_bar_full_pair_and_event',
        source_experiment='E080', source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        geometry=parent['geometry'], motion='minus_bar', domain=len(mapping),
        mapping_sha256=digest(mapping), word_indices=len(words),
        full_partition_equal=False)
    return provenance, context, words, mapping, left, right


def _pair_audit(words, mapping):
    checked = mismatches = 0
    first = None
    for (i, j), (k, l) in combinations(mapping, 2):
        checked += 1
        counts = [sum(w[i] == w[k] for w in words),
                  sum(w[j] == w[l] for w in words)]
        if counts[0] != counts[1]:
            mismatches += 1
            if first is None:
                first = dict(pairs=[[i, j], [k, l]], same_counts=counts)
    assert checked == len(mapping) * (len(mapping) - 1) // 2
    return dict(checked=checked, mismatch_count=mismatches, first_mismatch=first)


def _event_counts(words, predicates):
    return [sum(all((word[p[side][0]] == word[p[side][1]]) == p['equal']
                    for p in predicates) for word in words)
            for side in ('source', 'image')]


def verify(root, certificate=None):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    root = Path(root)
    path = (Path(certificate) if certificate is not None
            else root / 'certificates/quintic_joint_return_witness.json')
    certificate_data = json.loads(path.read_text())
    provenance, context, words, mapping, _, _ = _prepare(root)
    assert certificate_data['provenance'] == provenance
    audit = _pair_audit(words, mapping)
    assert certificate_data['all_pairs'] == audit
    event = certificate_data['event']
    predicates = event['predicates']
    assert isinstance(predicates, list) and 1 <= len(predicates) <= len(words).bit_length()
    motion = dict(mapping)
    source_points, image_points = set(), set()
    for predicate in predicates:
        assert set(predicate) == {'source', 'image', 'equal'}
        assert type(predicate['equal']) is bool
        for side in ('source', 'image'):
            assert isinstance(predicate[side], list) and len(predicate[side]) == 2
            assert all(type(i) is int and 0 <= i < len(context['points'])
                       for i in predicate[side])
            assert predicate[side][0] != predicate[side][1]
        assert [motion[i] for i in predicate['source']] == predicate['image']
        source_points.update(predicate['source'])
        image_points.update(predicate['image'])
    assert len(source_points) == len(image_points) <= 2 * len(words).bit_length()
    counts = _event_counts(words, predicates)
    assert counts[0] != counts[1]
    assert event['counts'] == counts
    assert event['source_points'] == sorted(source_points)
    assert event['image_points'] == sorted(image_points)
    # Bind the listed indices to independent exact physical coordinates.
    expected_coordinates = [dict(index=i, coordinates=[str(x) for x in context['points'][i]])
                            for i in sorted(source_points | image_points)]
    assert event['point_coordinates'] == expected_coordinates

    repair_path = root / 'certificates/quintic_multiword_return_joint.json'
    repair = json.loads(repair_path.read_text())
    assert repair['experiment'] == 'E083' and repair['geometry'] == provenance['geometry']
    repair_words = repair['result']['words']
    assert repair_words and all(isinstance(w, str) and len(w) == len(context['points'])
                                and set(w) <= set('01234') for w in repair_words)
    assert all(w[i] != w[j] for w in repair_words for i, j in context['edges'])
    repair_counts = _event_counts(repair_words, predicates)
    assert repair_counts[0] == repair_counts[1]
    assert certificate_data['repair'] == dict(
        experiment='E083', source_sha256=hashlib.sha256(repair_path.read_bytes()).hexdigest(),
        event_counts=repair_counts, word_indices=len(repair_words))
    return dict(
        status='PASS', experiment='E081', domain=len(mapping), all_pairs=audit,
        event_predicates=predicates, event_counts=counts,
        source_event_points=len(source_points), image_event_points=len(image_points),
        union_event_points=len(source_points | image_points),
        repaired_E083_event_counts=repair_counts,
        scope=('A discrepancy of the saved E080 law, repaired by the saved E083 '
               'law; the point bound is per domain side, not their union; '
               'not an all-word obstruction or new HN bound'))


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
