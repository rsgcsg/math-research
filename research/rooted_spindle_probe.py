#!/usr/bin/env python3
"""Finite rooted-list probe for the 7-vertex Moser spindle.

This is an exhaustive check over the 10^7 assignments of 3-lists from
{0,...,4}.  Triangle signatures are compressed, but the homogeneous flag is
kept as explicit metadata because it is part of the claimed singleton iff.
"""

from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path
import json

PALETTE = range(5)
LISTS = tuple(sum(1 << c for c in choice) for choice in combinations(PALETTE, 3))
ROOTS = tuple(LISTS)


def popcount(mask):
    return bin(mask).count("1")


def triangle_tip_mask(la, lb, lc, root_color):
    """Directly enumerate proper colors of triangle a-b-c after fixing o."""
    la &= ~(1 << root_color)
    lb &= ~(1 << root_color)
    tips = 0
    for ca in PALETTE:
        if not (la & (1 << ca)):
            continue
        for cb in PALETTE:
            if not (lb & (1 << cb)) or cb == ca:
                continue
            for cc in PALETTE:
                if lc & (1 << cc) and cc != ca and cc != cb:
                    tips |= 1 << cc
    return tips


def signature(triple):
    return tuple(triangle_tip_mask(*triple, x) for x in PALETTE)


def support_for(root_list, left_signature, right_signature):
    support = 0
    for x in PALETTE:
        if not (root_list & (1 << x)):
            continue
        left, right = left_signature[x], right_signature[x]
        # c-f is an edge: some c in left and a different f in right.
        if any((left & (1 << c)) and (right & ~(1 << c)) for c in PALETTE):
            support |= 1 << x
    return support


def main():
    # Compress the 10^3 ordered triangle-list triples by direct signatures.
    groups = defaultdict(list)
    for triple in product(LISTS, repeat=3):
        groups[signature(triple)].append(triple)

    # The iff needs this flag; assert compression did not erase it.
    homogeneous = {}
    for sig, triples in groups.items():
        flags = {triple[0] == triple[1] == triple[2] for triple in triples}
        assert len(flags) == 1, "homogeneous flag is not signature-invariant"
        homogeneous[sig] = flags.pop()

    print("triangle triples:", 10 ** 3)
    print("compressed signatures:", len(groups))
    print("homogeneous signatures:", sum(homogeneous.values()))

    support_sizes = Counter()
    singleton_checks = 0
    singleton_iff_failures = []
    homogeneous_support_failures = []
    total = 0

    for root_list in ROOTS:
        for left_sig, left_triples in groups.items():
            for right_sig, right_triples in groups.items():
                multiplicity = len(left_triples) * len(right_triples)
                total += multiplicity
                support = support_for(root_list, left_sig, right_sig)
                support_sizes[popcount(support)] += multiplicity
                if popcount(support) == 1:
                    singleton_checks += multiplicity
                left_h = homogeneous[left_sig]
                right_h = homogeneous[right_sig]
                # This is the conjectured right-hand side, evaluated on the
                # representative triples (and therefore on every member).
                la = left_triples[0][0]
                ld = right_triples[0][0]
                rhs = left_h and right_h and popcount(root_list & ~(la & ld)) == 1
                if (popcount(support) == 1) != rhs:
                    singleton_iff_failures.append((root_list, left_sig, right_sig))
                if left_h and right_h and support != (root_list & ~(la & ld)):
                    homogeneous_support_failures.append((root_list, la, ld))

    assert total == 10 ** 7
    assert not singleton_iff_failures
    assert not homogeneous_support_failures
    print("assignments checked:", total)
    print("support-size counts:", dict(sorted(support_sizes.items())))
    print("singleton assignments:", singleton_checks)
    print("singleton iff failures:", len(singleton_iff_failures))
    print("homogeneous support identity failures:", len(homogeneous_support_failures))

    # A concrete forcing instance: La=Lb=Lc={1,2,3},
    # Ld=Le=Lf={1,2,3}, Lo={0,1,2}; hence support={0}.
    forced = 0b00111
    triangle = (0b01110,) * 3
    support = support_for(forced, signature(triangle), signature(triangle))
    assert support == 1
    print("forcing example: Lo={0,1,2}, La=Lb=Lc=Ld=Le=Lf={1,2,3}")
    print("forcing example support:", [x for x in PALETTE if support & (1 << x)])
    certificate = {
        "schema": 1,
        "palette_size": 5,
        "list_size": 3,
        "groups": [{"signature": list(sig), "triples": [list(t) for t in triples]}
                   for sig, triples in sorted(groups.items())],
        "support_size_counts": dict(sorted(support_sizes.items())),
        "weighted_assignments": total,
        "compressed_cases": 10 * len(groups) ** 2,
        "forcing_lists": [forced] + [triangle[0]] * 6,
        "forcing_support": support,
    }
    target = Path(__file__).resolve().parents[1] / "certificates/rooted_spindle.json"
    target.write_text(json.dumps(certificate, indent=2) + "\n")


if __name__ == "__main__":
    main()
