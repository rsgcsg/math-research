"""Explore exact saturated sublattices of the T072 translation host.

All edge gains are retained before a deliberately restricted parity coloring
ansatz is tested. A negative solver return is NOT a host lower bound.
"""
from itertools import product
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
INVERSE = ((39, 52, -29, -25), (12, 16, -9, -8),
           (44, 59, -33, -28), (-36, -48, 27, 23))


def coordinates(v):
    return tuple(sum(a*b for a, b in zip(row, v)) for row in INVERSE)


def relations(data, selected, shifts):
    excluded = tuple(i for i in range(4) if i not in selected)
    shift_coords = [coordinates(s) for s in shifts]
    assert len({tuple(c[i] for i in excluded) for c in shift_coords}) == len(shifts)
    gains = {}
    for i, j, *d in data['contacts']:
        gains.setdefault(coordinates(d), []).append((i, j))
    for a, b in product(range(-1, 2), repeat=2):
        if a*a+a*b+b*b == 1:
            for d in ((a, b, 0, 0), (0, 0, a, b)):
                gains.setdefault(coordinates(d), []).extend((i, i) for i in range(509))
    result = []
    for s, x in enumerate(shift_coords):
        for t, y in enumerate(shift_coords):
            for d, pairs in gains.items():
                v = tuple(a+b-c for a, b, c in zip(x, d, y))
                if all(v[i] == 0 for i in excluded):
                    result.extend((s, t, i, j, *(v[k] for k in selected)) for i, j in pairs)
    return sorted(result)


def twisted_search(flip, permutation, budget, solver_name, output):
    """Try C[q + n*flip] followed by permutation**n, with n the V coordinate."""
    assert 0 <= flip < 8 and sorted(permutation) == list(range(5))
    from parts_core import clauses
    from pysat.solvers import Solver
    data = json.loads(gzip.decompress((ROOT/'certificates/resonant_translation_stack.json.gz').read_bytes()))
    rows = relations(data, (0, 1, 2, 3), [[0]*4])
    powers = [tuple(range(5))]
    while True:
        nxt = tuple(permutation[v] for v in powers[-1])
        if nxt == powers[0]:
            break
        powers.append(nxt)
    constraints = set()
    for _, _, i, j, a, b, n, d in rows:
        change = (4*(a % 2)+2*(b % 2)+d % 2) ^ (flip if n % 2 else 0)
        inverse = powers[-n % len(powers)]
        for q in range(8):
            u, v = 509*q+i, 509*(q ^ change)+j
            for c in range(5):
                constraints.add(tuple(sorted(set((-5*u-c-1, -5*v-inverse[c]-1)))))
    print(dict(mode='twisted', flip=flip, permutation=permutation,
               constraints=len(constraints)), flush=True)
    with Solver(name=solver_name, bootstrap_with=clauses(4072, [], 5)+sorted(constraints)) as solver:
        seed = json.loads((ROOT/'certificates/resonant_three_direction_w.json').read_text())['words']
        solver.set_phases([5*(509*q+i)+int(seed[q][i])+1 for q in range(8) for i in range(509)])
        solver.conf_budget(budget)
        status = solver.solve_limited()
        print(dict(flip=flip, status=status, statistics=solver.accum_stats()), flush=True)
        if status is True:
            model = set(solver.get_model())
            words = [''.join(str(next(c for c in range(5) if 5*(509*q+i)+c+1 in model))
                             for i in range(509)) for q in range(8)]
            result = dict(flip=flip, permutation=permutation, words=words,
                          scope='Candidate for full X; independent checking required')
            if output:
                Path(output).write_text(json.dumps(result, separators=(',', ':'))+'\n')
            return result


def search(selected, budget, solver_name, output, seed_file=None):
    assert selected in ((0, 1, 2), (0, 1, 3), (0, 1, 2, 3))
    from parts_core import clauses
    from pysat.solvers import Solver
    data = json.loads(gzip.decompress((ROOT/'certificates/resonant_translation_stack.json.gz').read_bytes()))
    shifts = data['cluster']['shifts'] if len(selected) < 4 else [[0]*4]
    phase = data['cluster']['phase_offsets'] if len(selected) < 4 else [0]
    rel = relations(data, selected, shifts)
    states = list(product(range(2), repeat=len(selected)))
    index = {v: i for i, v in enumerate(states)}
    constraints = set()
    for s, t, i, j, *gain in rel:
        delta = (phase[s]-phase[t]) % 5
        for q, state in enumerate(states):
            target = index[tuple((a+b) % 2 for a, b in zip(state, gain))]
            u, v = 509*q+i, 509*target+j
            constraints.update(tuple(sorted((-5*u-c-1, -5*v-(c+delta) % 5-1))) for c in range(5))
    print(dict(selected=selected, shifts=len(shifts), relations=len(rel),
               distinct_gains=len({r[4:] for r in rel}),
               largest_gain=max(abs(v) for r in rel for v in r[4:]),
               core_words=len(states), constraints=len(constraints)), flush=True)
    anchors = [[1]]
    if len(selected) == 4:
        # These four same-core states form the K4 coming from Lambda mod 2.
        # Any proper coloring can be globally renamed to satisfy these units.
        anchors = [[5*(509*q)+c+1] for q, c in ((0, 0), (8, 1), (2, 2), (10, 3))]
    with Solver(name=solver_name, bootstrap_with=clauses(509*len(states), [], 5)+sorted(constraints)+anchors) as solver:
        seed_data = json.loads(Path(seed_file).read_text()) if seed_file else None
        seed = seed_data['words'] if seed_data else data['cluster']['words']
        seed_axes = seed_data['selected'] if seed_data else [0, 1]
        seed_indices = [selected.index(k) for k in seed_axes]
        def seed_index(state):
            value = 0
            for k in seed_indices:
                value = 2*value+state[k]
            return value
        solver.set_phases([5*(509*q+i)+int(seed[seed_index(state)][i])+1
                           for q, state in enumerate(states) for i in range(509)])
        solver.conf_budget(budget)
        status = solver.solve_limited()
        print(dict(status=status, statistics=solver.accum_stats()), flush=True)
        if status is True:
            model = set(solver.get_model())
            words = [''.join(str(next(c for c in range(5) if 5*(509*q+i)+c+1 in model))
                             for i in range(509)) for q in range(len(states))]
            source = (ROOT/'certificates/resonant_translation_stack.json.gz').read_bytes()
            result = dict(schema=1, source_sha256=hashlib.sha256(source).hexdigest(),
                          selected=selected, shifts=shifts, phase_offsets=phase,
                          words=words, relation_count=len(rel),
                          relation_sha256=hashlib.sha256(json.dumps(rel, separators=(',', ':')).encode()).hexdigest(),
                          solver=solver_name, budget=budget,
                          scope='Complete stated three-direction induced host; not full X or plane')
            if output:
                Path(output).write_text(json.dumps(result, separators=(',', ':'))+'\n')
            return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directions', default='012')
    parser.add_argument('--budget', type=int, default=50000)
    parser.add_argument('--solver', default='cadical195')
    parser.add_argument('--output')
    parser.add_argument('--seed')
    parser.add_argument('--twist', help='Five images of a color permutation, e.g. 12340')
    parser.add_argument('--flip', type=int, default=0)
    args = parser.parse_args()
    if args.twist:
        twisted_search(args.flip, tuple(map(int, args.twist)), args.budget, args.solver, args.output)
    else:
        search(tuple(map(int, args.directions)), args.budget, args.solver, args.output, args.seed)
