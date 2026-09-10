"""Produce the small additive character certificate for T080.

The character is explicit; this program performs no coloring search. The
independent checker reads the C015 directions without importing this producer.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json


def build(root):
    source = root/'certificates/cyclotomic_sparse_coupling.json'
    raw = source.read_bytes()
    records = json.loads(raw)['unit_vectors']
    weights = ((1, 0, -1, Q(3, 8)), (1, 0, 0, Q(3, 2)),
               (1, 0, 0, Q(3, 2)), (1, 0, 0, Q(11, 8)))
    evaluations = []
    for record in records:
        value = sum(Q(*a)*w for c, row in zip(record['coefficients'], weights)
                    for a, w in zip(c, row))
        evaluations.append(dict(label=record['label'],
                                value=[value.numerator, value.denominator]))
    return dict(schema=1, theorem='T080',
                source='certificates/cyclotomic_sparse_coupling.json',
                source_sha256=hashlib.sha256(raw).hexdigest(),
                coefficient_basis=['1', 'sqrt(3)', 'i', 'i*sqrt(3)'],
                powers=[0, 1, 2, 3],
                character_weights=[[[Q(w).numerator, Q(w).denominator] for w in row]
                                   for row in weights],
                generator_evaluations=evaluations,
                graph='Cayley(sum_Z D, plus_or_minus_D); listed directions only')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    path = root/'certificates/cyclotomic_direction_parity.json'
    data = build(root)
    path.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(dict(output=str(path), generators=len(data['generator_evaluations']))))
