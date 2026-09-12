"""Independent finite calibrations for the signed-support compression lemma.

The arbitrary-real-weight theorem has a written induction in the proof draft.
This checker validates finite instances and independently checks extracted events.
It does not turn a fixed-law mismatch into an all-proper-word obstruction.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations, product
import json
import random


def clean(items):
    out = defaultdict(Fraction)
    for atom, weight in items:
        out[tuple(atom)] += weight
    return {atom: weight for atom, weight in out.items() if weight}


def witness(measure):
    """Return a nonzero conjunction using logarithmically many coordinates."""
    current = clean(measure.items())
    assert current
    selected = []
    while True:
        total = sum(current.values(), Fraction())
        if total:
            return selected, total
        positive = [atom for atom, weight in current.items() if weight > 0]
        assert positive
        if len(positive) == 1:
            other = next(atom for atom, weight in current.items() if weight < 0)
            coordinate = next(i for i, (x, y) in enumerate(zip(positive[0], other)) if x != y)
        else:
            coordinate = next(i for i, (x, y) in enumerate(zip(positive[0], positive[1])) if x != y)
        slices = [{atom: weight for atom, weight in current.items() if atom[coordinate] == bit}
                  for bit in (0, 1)]
        totals = [sum(side.values(), Fraction()) for side in slices]
        if any(totals):
            bit = next(bit for bit in (0, 1) if totals[bit])
            return selected + [(coordinate, bit)], totals[bit]
        counts = [sum(weight > 0 for weight in side.values()) for side in slices]
        assert min(counts) > 0
        bit = min((0, 1), key=lambda b: counts[b])
        selected.append((coordinate, bit))
        current = slices[bit]


def check_witness(measure):
    measure = clean(measure.items())
    assert measure and sum(measure.values(), Fraction()) == 0
    positive = sum(w > 0 for w in measure.values())
    negative = sum(w < 0 for w in measure.values())
    # The extractor uses positive support. Flip signs to use the smaller side.
    if negative < positive:
        measure = {atom: -weight for atom, weight in measure.items()}
        positive = negative
    event, claimed = witness(measure)
    assert len(event) <= positive.bit_length()
    assert len({coordinate for coordinate, _ in event}) == len(event)
    actual = sum((weight for atom, weight in measure.items()
                  if all(atom[i] == bit for i, bit in event)), Fraction())
    assert actual == claimed and actual != 0
    return event


def marginal(measure, coordinates):
    return clean((tuple(atom[i] for i in coordinates), weight) for atom, weight in measure.items())


def pattern(values):
    labels = {}
    return tuple(labels.setdefault(value, len(labels)) for value in values)


def partition_bits(partition):
    return tuple(int(partition[i] == partition[j])
                 for i, j in combinations(range(len(partition)), 2))


def differing_pair(left, right):
    """Find a differing equality bit without constructing a quadratic bit vector."""
    assert len(left) == len(right)
    by_left, by_right = {}, {}
    for i, (a, b) in enumerate(zip(left, right)):
        if a in by_left and by_left[a][0] != b:
            return by_left[a][1], i
        if b in by_right and by_right[b][0] != a:
            return by_right[b][1], i
        by_left.setdefault(a, (b, i))
        by_right.setdefault(b, (a, i))
    raise ValueError('The two partitions are identical')


def partition_witness(measure):
    """Return ((point, point, equal-bit), ...) and its nonzero signed mass.

    Points are positions in the ordered common domain, not global vertex IDs.
    Input weights must be exact if the returned numerical mass is to be exact.
    """
    current = clean((pattern(atom), weight) for atom, weight in measure.items())
    assert current
    selected = []
    while True:
        total = sum(current.values(), Fraction())
        if total:
            return selected, total
        positive = [atom for atom, weight in current.items() if weight > 0]
        assert positive
        other = (positive[1] if len(positive) > 1 else
                 next(atom for atom, weight in current.items() if weight < 0))
        i, j = differing_pair(positive[0], other)
        slices = [{atom: weight for atom, weight in current.items()
                   if int(atom[i] == atom[j]) == bit} for bit in (0, 1)]
        totals = [sum(side.values(), Fraction()) for side in slices]
        if any(totals):
            bit = next(bit for bit in (0, 1) if totals[bit])
            return selected + [(i, j, bit)], totals[bit]
        counts = [sum(weight > 0 for weight in side.values()) for side in slices]
        assert min(counts) > 0
        bit = min((0, 1), key=lambda b: counts[b])
        selected.append((i, j, bit))
        current = slices[bit]


def parity(q):
    return {atom: Fraction((-1) ** sum(atom), 2 ** (q - 1))
            for atom in product((0, 1), repeat=q)}


def verify():
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    exhaustive = 0
    for n in range(1, 4):
        atoms = list(product((0, 1), repeat=n))
        for weights in product((-1, 0, 1), repeat=len(atoms)):
            if not any(weights) or sum(weights):
                continue
            measure = clean(zip(atoms, map(Fraction, weights)))
            check_witness(measure)
            positive = sum(weight > 0 for weight in measure.values())
            negative = sum(weight < 0 for weight in measure.values())
            for t in range(n + 1):
                if all(not marginal(measure, coordinates)
                       for size in range(t + 1)
                       for coordinates in combinations(range(n), size)):
                    assert min(positive, negative) >= 2 ** t
            exhaustive += 1

    parity_checks = []
    for q in range(1, 6):
        measure = parity(q)
        event = check_witness(measure)
        assert len(event) == q
        assert all(not marginal(measure, coordinates)
                   for coordinates in combinations(range(q), q - 1))
        parity_checks.append(dict(bits=q, positive_atoms=2 ** (q - 1), required_bits=q))

    # Independent merge switches: six points, four atoms on each side.
    # This sharp physical-point example needs up to six blocks, not five.
    partitions = []
    for bits, weight in parity(3).items():
        p = []
        for i, bit in enumerate(bits):
            p.extend((2 * i, 2 * i if bit else 2 * i + 1))
        partitions.append((pattern(p), weight))
    for size in range(6):
        for subset in combinations(range(6), size):
            assert not clean((pattern(p[i] for i in subset), w) for p, w in partitions)
    assert clean(partitions)

    rng = random.Random(20260912)
    weighted_checks = 0
    for n in (4, 6, 9):
        pairs = list(combinations(range(n), 2))
        for _ in range(100):
            laws = []
            for side in range(2):
                words = [pattern(rng.randrange(5) for _ in range(n)) for _ in range(5)]
                numerators = [rng.randrange(1, 12) for _ in words]
                denominator = sum(numerators)
                laws.append(list(zip(words, (Fraction(a, denominator) for a in numerators))))
            signed = clean((partition_bits(p), sign * w)
                           for sign, law in zip((1, -1), laws) for p, w in law)
            if not signed:
                continue
            event = check_witness(signed)
            physical = sorted({i for coordinate, _ in event for i in pairs[coordinate]})
            assert len(physical) <= 6
            restrictions = [clean((pattern(p[i] for i in physical), w) for p, w in law)
                            for law in laws]
            assert restrictions[0] != restrictions[1]
            signed_partitions = clean((p, sign * w)
                                      for sign, law in zip((1, -1), laws) for p, w in law)
            pair_event, claimed = partition_witness(signed_partitions)
            assert len(pair_event) <= 3
            actual = sum((w for p, w in signed_partitions.items()
                          if all(int(p[i] == p[j]) == bit for i, j, bit in pair_event)), Fraction())
            assert actual == claimed and actual
            assert len({i for pair in pair_event for i in pair[:2]}) <= 6
            weighted_checks += 1
    return dict(status='PASS', exhaustive_zero_mass_signed_inputs=exhaustive,
                parity_calibrations=parity_checks, six_point_partition_sharpness=True,
                unequal_weight_five_support_partition_checks=weighted_checks,
                scope='Fixed finite-law distinction only; not all-word bounded arity or an HN obstruction')


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
