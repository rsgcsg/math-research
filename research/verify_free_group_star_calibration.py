#!/usr/bin/env python3
"""Finite calibration of a labeled F_2 orientation CSP, not a coloring result.

The analytic extension and mass-transport proofs are in
docs/proofs/full15_joint_event_theory.md. This exhaustive 4^5 calculation
only checks the local allowed patterns and their constant row potential.
"""
import itertools
import json
import sys

if not __debug__:
    sys.exit("Run without -O: this calibration requires assertions")


def main():
    # Directions a,A,b,B; x[0] labels the root and x[s+1] its s-neighbor.
    inverse = (1, 0, 3, 2)
    allowed = []
    for x in itertools.product(range(4), repeat=5):
        if all((x[0] == s) != (x[s + 1] == inverse[s]) for s in range(4)):
            incoming = sum(x[s + 1] == inverse[s] for s in range(4))
            outgoing = sum(x[0] == inverse[s] for s in range(4))
            assert (incoming, outgoing, incoming - outgoing) == (3, 1, 2)
            # The chosen neighbor continues away from root. This two-edge
            # nonbacktracking ray extends to an end of the infinite tree.
            assert x[x[0] + 1] != inverse[x[0]]
            allowed.append(x)
    assert len(allowed) == 12
    assert all(sum(x[0] == s for x in allowed) == 3 for s in range(4))
    print(json.dumps({"status": "PASS", "assignments_examined": 1024,
                      "allowed_patterns": 12, "constant_potential": 2,
                      "scope": "Finite labeled orientation CSP calibration; no unit-distance or HN claim"}, indent=2))


if __name__ == "__main__":
    main()
