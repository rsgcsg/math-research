"""T020: maximal missing-residue cases suffice for arbitrary binary words.

Each layer is normalized at j=k-1; the central word at j=-1. Only local
increments remain. Enlarge two difference supports to Z3 and the remaining
one to a two-element set. Direct witnesses certify all 1536 resulting cases.
"""
from itertools import permutations, product
from pathlib import Path
import argparse
import json

ROOTS = [(-2,1),(-1,-1),(-1,2),(1,-2),(1,1),(2,-1)]


def run():
    frames = list(permutations(range(6)))
    rows = []
    for central in product((0,-1),repeat=4):
        s = {-1:0}
        for j,d in enumerate(central):
            s[j] = (s[j-1]+d)%3
        def central_color(m,n):
            return n%3 if m%2==0 else 3+(n+s[m//2])%3
        options = {}
        for k,d in product(range(4),(0,-1)):
            def layer_color(m,n):
                return n%3 if m%2==0 else 3+(n+(d if m//2==k else 0))%3
            options[k,d] = [p for p in frames if p[(-k)%3]==(-k)%3 and all(
                p[layer_color(2*k+m,-k+n)] != central_color(2*k+m,-k+n) for m,n in ROOTS)]
        for steps in product((0,-1),repeat=4):
            for interface in range(3):
                for omitted in range(3):
                    if omitted == (-steps[interface])%3:
                        continue  # This residue necessarily occurs at j=interface.
                    paths = {p:[p] for p in options[0,steps[0]]}
                    for k in range(3):
                        support = set(range(3))-{omitted} if k==interface else set(range(3))
                        pairs = [(i,i) for i in range(3)]+[
                            (3+i,3+(i+d)%3) for i in range(3) for d in support]
                        next_paths = {}
                        for q in options[k+1,steps[k+1]]:
                            for p,path in paths.items():
                                if all(p[i] != q[j] for i,j in pairs):
                                    next_paths[q] = path+[q]
                                    break
                        paths = next_paths
                    assert paths, (central,steps,interface,omitted)
                    rows.append(dict(central_steps=central, layer_steps=steps,
                                     relaxed_interface=interface, omitted_residue=omitted,
                                     frames=next(iter(paths.values()))))
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    rows = run()
    if args.output:
        # One certificate per line keeps this exhaustive table readable and compact.
        args.output.write_text('[\n'+',\n'.join(json.dumps(r,separators=(',',':')) for r in rows)+'\n]\n')
    print(json.dumps(dict(maximal_cases=len(rows), positive_witnesses=len(rows)),indent=2))
