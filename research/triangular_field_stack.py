"""Positive search and finite probes for T064/T065's triangular sheet lift.

This is a generator, not a proof checker. Infinite completeness is in the proof.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

from parts_core import clauses

ROOT = Path(__file__).resolve().parents[1]
EXTRA = ((1, 3), (3, 1), (4, 4), (7, 7), (8, 10), (10, 8))


def generators():
    return sorted({(x, y) for x, y in product(range(11), repeat=2)
                   if (x*x+y*y) % 11 == 1} | set(EXTRA))


def target_edges():
    return sorted({tuple(sorted((11*x+y, 11*((x+a) % 11)+(y+b) % 11)))
                   for x, y in product(range(11), repeat=2)
                   for a, b in generators()})


def shear(r):
    r = min(r, 11-r)
    if r == 2:
        return [3, 5, 3, 9]
    if r == 4:
        return [1, 5, 7, 6]
    a = next(a for a in range(11) if (a*a+r*r) % 11 == 1)
    return [a, 6*a % 11, 0, 8*a % 11]


def mixed_shell_boundary():
    steps = generators()
    directions = [(m, n) for m, n in product(range(-3, 4), repeat=2)
                  if m*m+m*n+n*n in (3, 4)]
    accepted = []
    for a, b, c, d in product(range(11), repeat=4):
        valid = True
        for m, n in directions:
            norm = m*m+m*n+n*n
            factor = 7 if norm == 3 else 9  # (13/23)/sqrt(3), (7/23)/2.
            for sign in (-1, 1):
                z = ((a*m+b*n-sign*factor*5*n*6) % 11,
                     (c*m+d*n+sign*factor*(2*m+n)*6) % 11)
                if z not in steps:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            accepted.append([a, b, c, d])
    assert not accepted
    return dict(beta=[120, 529], t3=[13, 23], t4=[7, 23],
                matrix_count=11**4, accepted_matrices=accepted,
                scope='Only affine residue shears into this fixed 121-point target are excluded')


def finite_probe(word, shell):
    raw = (ROOT/'certificates/parts509_core.json').read_bytes()
    core = json.loads(raw)
    # A common denominator 288 covers Parts and both escaped translations.
    points = [tuple(tuple(3*a for a in axis) for axis in p) for p in core['points']]
    if shell == 1:
        points = [(tuple(-a for a in y), x) for x, y in points]
    ids = {p: i for i, p in enumerate(points)}
    centers = [(m, n) for m, n in product(range(-1, 2), repeat=2)
               if max(abs(m), abs(n), abs(m+n)) <= 1]
    edges = {(509*k+a, 509*k+b) for k in range(len(centers))
             for a, b in core['induced_edges']}
    interfaces = []
    for i, j in combinations(range(len(centers)), 2):
        dm, dn = (b-a for a, b in zip(centers[i], centers[j]))
        if dm*dm+dm*dn+dn*dn != shell:
            continue
        count = 0
        for q, (x, y) in enumerate(points):
            for sign in (-1, 1):
                dx, dy = list(x), list(y)
                if shell == 1:
                    dx[1] -= sign*48*dn
                    dy[0] += sign*48*(2*dm+dn)
                else:
                    dx[0] -= sign*48*dn
                    dy[1] += sign*16*(2*dm+dn)
                other = ids.get((tuple(dx), tuple(dy)))
                if other is not None:
                    edges.add((509*i+q, 509*j+other))
                    count += 1
        interfaces.append([i, j, count])
    images = (1, 5, 0, 0, 4, 9, 0, 0)
    colors = []
    for m, n in centers:
        if shell == 1:
            a, b = m, n
        else:
            coset = (m-n) % 3
            a, b = (2*m-2*coset+n)//3, (n-m+coset)//3
            assert (m-coset, n) == (a-b, a+2*b)
        for p in points:
            x, y = (sum(c*d for c, d in zip(axis, images))*pow(288, -1, 11) % 11
                    for axis in p)
            if shell == 3:
                # R_{-pi/6}; sqrt(3) -> 5, so cos -> 8, sin -> -6.
                x, y = (8*x+6*y) % 11, (5*x+8*y) % 11
            x, y = (x+a+5*b) % 11, (y+7*a+6*b) % 11
            colors.append(int(word[11*x+y]))
    assert all(colors[a] != colors[b] for a, b in edges)
    edges = sorted(edges)
    return dict(shell=shell, alpha='2sqrt(2)/3' if shell == 1 else '2sqrt(6)/9',
                core_rotation='quarter_turn' if shell == 1 else 'identity',
                core_sha256=hashlib.sha256(raw).hexdigest(), centers=centers,
                vertices=len(colors), edges=len(edges), interfaces=interfaces,
                word=''.join(map(str, colors)),
                edge_sha256=hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest())


def build():
    from pysat.solvers import Solver
    edges = target_edges()
    cnf = clauses(121, edges, 5)+[[1], [5*11+2], [5*74+3]]
    with Solver(name='cadical195', bootstrap_with=cnf) as solver:
        solver.conf_budget(30000)
        status = solver.solve_limited()
        if status is not True:
            raise RuntimeError('Positive witness not obtained; no negative claim')
        model = set(solver.get_model())
        word = ''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(121))
    data = dict(schema=1, prime=11, target_generators=generators(), target_edges=len(edges),
                word=word, solver='cadical195', conflict_budget=30000, status='SAT_CANDIDATE',
                shears=[dict(residue=r, matrix=shear(r)) for r in range(11)],
                nonsquare_shells={str(b): [n for n in (1, 3) if (1-n*b) % 11 in {x*x % 11 for x in range(11)}]
                                   for b in (2, 6, 7, 8, 10)},
                scope='Entire triangular translated K^2 sheets under written T064/T065 hypotheses; not K(sqrt(2))^2 or the plane')
    data['finite_probes'] = [finite_probe(word, shell) for shell in (1, 3)]
    data['mixed_shell_boundary'] = mixed_shell_boundary()
    return data


if __name__ == '__main__':
    data = build()
    (ROOT/'certificates/triangular_field_stack.json').write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps({k: v for k, v in data.items() if k not in ('word', 'finite_probes')}, indent=2))
    print(json.dumps([{k: v for k, v in p.items() if k != 'word'} for p in data['finite_probes']], indent=2))
