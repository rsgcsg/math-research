"""Generate T067's six-color target, RUP evidence, and a real two-shell probe.

Infinite completeness belongs to the written proof, not to this search program.
"""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

from parts_core import clauses

ROOT = Path(__file__).resolve().parents[1]
RAD = (1, 3, 11, 33, 5, 15, 55, 165, 2, 6, 22, 66, 10, 30, 110, 330)


def steps():
    result = {(x, y) for x, y in product(range(11), repeat=2) if (x*x+y*y) % 11 == 1}
    for m, n in product(range(-3, 4), repeat=2):
        norm = m*m+m*n+n*n
        if norm not in (3, 4):
            continue
        r = 7 if norm == 3 else 9
        for sign in (-1, 1):
            result.add(((n-sign*r*5*n*6) % 11, (3*m+2*n+sign*r*(2*m+n)*6) % 11))
    return sorted(result)


def target_edges():
    return sorted({tuple(sorted((11*x+y, 11*((x+a) % 11)+(y+b) % 11)))
                   for x, y in product(range(11), repeat=2) for a, b in steps()})


def rup_hints(initial, drup):
    """Search for propagation hints; existing independent LRAT checker validates them.

Deletion instructions may be ignored: keeping sound clauses is safe for RUP.
No RAT step is accepted by this converter.
"""
    database = [tuple(c) for c in initial]
    output = []
    for line in drup:
        fields = line.split()
        if not fields or fields[0] == 'd':
            continue
        values = list(map(int, fields))
        assert values[-1] == 0
        clause = values[:-1]
        assignment = {abs(lit): lit < 0 for lit in clause}
        hints = []
        contradiction = False
        while not contradiction:
            changed = False
            for identifier, old in enumerate(database, 1):
                if any(assignment.get(abs(lit)) == (lit > 0) for lit in old):
                    continue
                unset = [lit for lit in old if abs(lit) not in assignment]
                if len(unset) > 1:
                    continue
                hints.append(identifier)
                if not unset:
                    contradiction = True
                    break
                lit = unset[0]
                assignment[abs(lit)] = lit > 0
                changed = True
            if not changed and not contradiction:
                raise RuntimeError('Non-RUP step or insufficient propagation')
        identifier = len(database)+1
        output.append(' '.join(map(str, [identifier]+clause+[0]+hints+[0])))
        database.append(tuple(clause))
        if not clause:
            return output
    raise RuntimeError('No empty clause')


def probe_points(core):
    den = 13248
    labels = {tuple(tuple(138*a for a in axis)+ (0,)*8 for axis in p) for p in core['points']}
    for m, n in product(range(-3, 4), repeat=2):
        norm = m*m+m*n+n*n
        if norm not in (3, 4):
            continue
        for sign in (-1, 1):
            x, y = [0]*16, [0]*16
            if norm == 3:
                x[0], y[1] = -sign*3744*n, sign*1248*(2*m+n)
            else:
                x[1], y[0] = -sign*1008*n, sign*1008*(2*m+n)
            labels.add((tuple(x), tuple(y)))
    labels = sorted(labels)
    centers = [(m, n) for m, n in product(range(-1, 2), repeat=2)
               if max(abs(m), abs(n), abs(m+n)) <= 1]
    points = []
    for m, n in centers:
        for x, y in labels:
            x, y = list(x), list(y)
            x[13] += 576*(2*m+n)
            y[12] += 1728*n
            points.append((tuple(x), tuple(y)))
    return den, centers, labels, points


def finite_probe(word):
    from pysat.solvers import Solver
    raw = (ROOT/'certificates/parts509_core.json').read_bytes()
    den, centers, labels, points = probe_points(json.loads(raw))
    # Algebraic modular filtering, followed by bit-mask multiquadratic products.
    prime = 1031  # All four defining radicands have roots here; checked below.
    roots = {a*a % prime: a for a in range(prime)}
    assert all(r in roots for r in (2, 3, 5, 11))
    images = []
    for r in RAD:
        z = 1
        for p in (2, 3, 5, 11):
            if r % p == 0:
                z = z*roots[p] % prime
        images.append(z)
    projected = [tuple(sum(a*b for a, b in zip(ax, images)) % prime for ax in p) for p in points]
    edges = []
    for i, j in combinations(range(len(points)), 2):
        if sum((a-b)**2 for a, b in zip(projected[i], projected[j])) % prime != den*den % prime:
            continue
        norm = [0]*16
        for ax, bx in zip(points[i], points[j]):
            nz = [(k, a-b) for k, (a, b) in enumerate(zip(ax, bx)) if a != b]
            for k, a in nz:
                for l, b in nz:
                    norm[k ^ l] += a*b*RAD[k & l]
        if norm == [den*den]+[0]*15:
            edges.append((i, j))
    images11 = (1, 5, 0, 0, 4, 9, 0, 0)+(0,)*8
    colors = []
    for m, n in centers:
        for point in labels:
            x, y = (sum(a*b for a, b in zip(ax, images11))*pow(den, -1, 11) % 11 for ax in point)
            colors.append(int(word[11*((x+n) % 11)+(y+3*m+2*n) % 11]))
    assert all(colors[a] != colors[b] for a, b in edges)
    count = {3: 0, 4: 0}
    for i, j in edges:
        if i//len(labels) != j//len(labels):
            m, n = (b-a for a, b in zip(centers[i//len(labels)], centers[j//len(labels)]))
            count[m*m+m*n+n*n] += 1
    with Solver(name='cadical195', bootstrap_with=clauses(len(points), edges, 5)+[[1]]) as solver:
        solver.conf_budget(20000)
        assert solver.solve_limited() is True, 'Finite five-color probe unresolved; no lower bound'
        model = set(solver.get_model())
        five_word = ''.join(str(next(c for c in range(5) if 5*i+c+1 in model)) for i in range(len(points)))
    return dict(core_sha256=hashlib.sha256(raw).hexdigest(), denominator=den,
                centers=centers, labels_per_center=len(labels), vertices=len(points), edges=len(edges),
                cross_edges_by_shell=count, word=''.join(map(str, colors)), five_word=five_word,
                edge_sha256=hashlib.sha256(json.dumps(edges, separators=(',', ':')).encode()).hexdigest())


def build():
    from pysat.solvers import Solver
    edges = target_edges()
    # Scalar target is K_11 minus the cycle with step 4: pair consecutive cycle vertices.
    word = ''.join(str((3*(x+y) % 11)//2) for x, y in product(range(11), repeat=2))
    assert all(word[a] != word[b] for a, b in edges)
    initial = clauses(121, edges, 5)+[[1], [57], [373]]
    with Solver(name='glucose3', bootstrap_with=initial, with_proof=True) as solver:
        solver.conf_budget(10000)
        assert solver.solve_limited() is False
        proof = rup_hints(initial, solver.get_proof())
    return dict(schema=1, beta=[120, 529], matrix=[0, 1, 3, 2],
                generators=steps(), edges=len(edges), word=word,
                coloring_formula='floor(((3*(x+y)) mod 11)/2)',
                scalar_word=''.join(str((3*z % 11)//2) for z in range(11)),
                refutation_solver='glucose3', conflict_budget=10000,
                five_color_lrat=proof, finite_probe=finite_probe(word),
                scope='Finite target exactly six; real infinite host only between five and six')


if __name__ == '__main__':
    data = build()
    (ROOT/'certificates/mixed_shell_stack.json').write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps({k: v for k, v in data.items() if k not in ('five_color_lrat', 'finite_probe')}, indent=2))
    print('RUP additions:', len(data['five_color_lrat']))
    print(json.dumps({k: v for k, v in data['finite_probe'].items() if k != 'word'}, indent=2))
