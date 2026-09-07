"""Complete frame search for the two uniform slopes on the five-lattice host.

Positive witnesses are independently checked. Negative cases have the T018
palette proof; a zero dynamic-programming count is not their sole evidence.
"""
from itertools import permutations, product
from pathlib import Path
import argparse
import json

ROOTS = [(-2,1),(-1,-1),(-1,2),(1,-2),(1,1),(2,-1)]


def color(v, slope):
    m,n = v
    return n%3 if m%2 == 0 else 3+(n-slope*(m//2))%3


def run():
    frames = list(permutations(range(6)))
    rows = []
    for central, slopes in product(range(2), product(range(2),repeat=4)):
        options = []
        for k,slope in enumerate(slopes):
            u = (2*k,-k)
            ports = [(u[0]+m,u[1]+n) for m,n in ROOTS]
            options.append([p for p in frames
                            if p[color(u,slope)] == color(u,central)
                            and all(p[color(v,slope)] != color(v,central) for v in ports)])
        paths = {p:[p] for p in options[0]}
        for k in range(3):
            pairs = [(i,i) for i in range(6)] if slopes[k] == slopes[k+1] else (
                [(i,i) for i in range(3)] + list(product(range(3,6),repeat=2)))
            next_paths = {}
            for q in options[k+1]:
                for p,path in paths.items():
                    if all(p[i] != q[j] for i,j in pairs):
                        next_paths[q] = path+[q]
                        break
            paths = next_paths
        rows.append(dict(central_slope=central, layer_slopes=slopes,
                         status='SAT' if paths else 'PROVED_INCOMPATIBLE_T018',
                         witness=next(iter(paths.values())) if paths else None))
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = run()
    if args.output:
        args.output.write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(dict(cases=len(rows), positive=sum(r['status']=='SAT' for r in rows),
                          proved_incompatible=sum(r['status']!='SAT' for r in rows)),indent=2))
