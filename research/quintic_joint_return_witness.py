"""Find a small discrepancy of the saved E080 law; not an obstruction search.

The separate verifier rebuilds geometry, audits every pair, and directly
counts the final event without relying on this extraction algorithm.
"""

from itertools import combinations
from pathlib import Path
import hashlib
import json

from verify_quintic_joint_return import _prepare, _pair_audit, _event_counts


def _compress(signed, trail=()):
    """Halve positive support until a Boolean cylinder has nonzero mass."""
    assert signed and sum(signed.values()) == 0
    atoms = sorted(signed)
    positive_support = sum(weight > 0 for weight in signed.values())
    for i, j in combinations(range(len(atoms[0])), 2):
        values = {atom[i] == atom[j] for atom in atoms}
        if len(values) > 1:
            break
    else:
        raise AssertionError('Distinct normalized partitions have a separating pair')
    slices = [{atom: weight for atom, weight in signed.items()
               if (atom[i] == atom[j]) == value} for value in (False, True)]
    for value, part in zip((False, True), slices):
        if sum(part.values()):
            return trail + ((i, j, value),)
    choice = min(range(2), key=lambda value: sum(w > 0 for w in slices[value].values()))
    next_signed = slices[choice]
    assert 0 < sum(weight > 0 for weight in next_signed.values()) <= positive_support // 2
    return _compress(next_signed, trail + ((i, j, bool(choice)),))


def run(root):
    provenance, context, words, mapping, left, right = _prepare(root)
    audit = _pair_audit(words, mapping)
    if audit['first_mismatch'] is not None:
        first, second = audit['first_mismatch']['pairs']
        predicates = [dict(source=[first[0], second[0]],
                           image=[first[1], second[1]], equal=True)]
    else:
        signed = {atom: left[atom] - right[atom] for atom in left.keys() | right.keys()
                  if left[atom] != right[atom]}
        compressed = _compress(signed)
        assert len(compressed) <= len(words).bit_length()
        predicates = [dict(source=[mapping[i][0], mapping[j][0]],
                           image=[mapping[i][1], mapping[j][1]], equal=value)
                      for i, j, value in compressed]
    counts = _event_counts(words, predicates)
    assert counts[0] != counts[1]
    source = sorted({i for p in predicates for i in p['source']})
    image = sorted({i for p in predicates for i in p['image']})
    coordinates = [dict(index=i, coordinates=[str(x) for x in context['points'][i]])
                   for i in sorted(set(source) | set(image))]
    repair_path = root / 'certificates/quintic_multiword_return_joint.json'
    repair_words = json.loads(repair_path.read_text())['result']['words']
    repair_counts = _event_counts(repair_words, predicates)
    assert repair_counts[0] == repair_counts[1]
    return dict(
        provenance=provenance, all_pairs=audit,
        event=dict(predicates=predicates, counts=counts, source_points=source,
                   image_points=image, point_coordinates=coordinates),
        repair=dict(experiment='E083',
                    source_sha256=hashlib.sha256(repair_path.read_bytes()).hexdigest(),
                    event_counts=repair_counts, word_indices=len(repair_words)),
        scope='Saved-law discrepancy and its later repair only; not an all-word obstruction')


if __name__ == '__main__':
    print(json.dumps(run(Path(__file__).resolve().parents[1]), indent=2))
