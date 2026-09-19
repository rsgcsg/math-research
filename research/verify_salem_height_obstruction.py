#!/usr/bin/env python3
"""Exact 13-direction height obstruction and 12-direction colouring.

The passage from a three-colouring to height periods is proved in the
accompanying note. This checks its finite integer certificate, not that theorem.
Python 3.10+ standard library; no SAT solver or floating-point arithmetic.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = (1, 0, -1, -1, -1, 0, 1)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def convolve(a: list[int], b: tuple[int, ...]) -> list[int]:
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return out


def verify(path: Path) -> dict[str, object]:
    require(__debug__, 'run without -O or -OO')
    data = json.loads(path.read_text(encoding='utf-8'))
    require(data['schema'] == 'salem-sextic-height-v1', 'unknown schema')
    require(data['polynomial'] == list(P), 'wrong polynomial')
    rows = data['separators']
    require(type(rows) is list and len(rows) == 10, 'expected ten separators')
    require(all(type(r) is list and len(r) == 7 and
                all(type(x) is int for x in r) for r in rows), 'invalid separator')
    norms = [sum(map(abs, convolve(r, P))) for r in rows]
    require(norms == data['l1_norms'], 'wrong relation norms')
    signs = list(itertools.product((-1, 1), repeat=7))
    minimum_margin = min(max(abs(3*sum(b*s for b, s in zip(row, sign)))-norm
                             for row, norm in zip(rows, norms)) for sign in signs)
    require(minimum_margin > 0, 'a period sign pattern survives')
    slope = data['linear_coloring_basis']
    require(type(slope) is list and len(slope) == 6 and
            all(type(x) is int for x in slope), 'invalid linear colouring')
    a = [1, 0, 0, 0, 0, 0]
    colours = []
    for _ in range(13):
        colours.append(sum(x*y for x, y in zip(a, slope)) % 3)
        lead = a[-1]
        a = [0] + a[:-1]
        for j in range(6):
            a[j] -= lead*P[j]
    require(all(colours[:12]), 'linear three-colouring fails before direction 13')
    require(colours == data['direction_colors_mod3'], 'wrong direction colours')
    require(colours[12] == 0, 'expected failure at the thirteenth direction')
    # The five-cycle relation has five distinct partial sums: its polynomials
    # have degree at most four, below the irreducible field degree six.
    require(sum(map(abs, P)) == 5 and sum(P) % 2 == 1, 'wrong odd relation')
    return {'status': 'PASS', 'sign_patterns': len(signs), 'separators': len(rows),
            'minimum_strict_margin': minimum_margin, 'relation_norms': norms,
            'direction_colors_mod3': colours,
            'scope': 'finite certificate for the proved 12/13-direction threshold'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', nargs='?', type=Path,
                        default=ROOT/'certificates/salem_sextic_height.json')
    args = parser.parse_args()
    try:
        result = verify(args.certificate)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as exc:
        raise SystemExit(f'FAIL: {exc}') from exc
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
