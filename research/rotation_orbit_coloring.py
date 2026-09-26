"""Bounded positive-certificate searches on the complete rotation graph.

All restrictions are explicit. UNKNOWN or restricted UNSAT is never NON5.
"""
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import time

from verify_quintic_core_probe import digest


def perm_power(p, n):
    result = list(range(len(p)))
    for _ in range(n % 12):
        result = [p[x] for x in result]
    return result


def equivariant(root, cycle, budget=20000):
    from pysat.solvers import Solver
    path = root/'certificates/rotation_orbit_contacts.json'
    data = json.loads(path.read_text())
    count = data['representative_count']
    p = [0,2,3,1,4] if cycle == 3 else [0,2,3,4,1]
    assert cycle in (3,4) and p[0] == 0
    var = lambda i,c: 5*i+c+1
    clauses = []
    for i in range(count):
        clauses.append([var(i,c) for c in range(5)])
        clauses.extend([-var(i,a),-var(i,b)] for a,b in combinations(range(5),2))
    for i in data['origin_neighbors']:
        clauses.append([-var(i,0)])
    for i,j,h,n in data['contacts']:
        power = perm_power(p,n)
        clauses.extend([-var(i,power[c]),-var(j,c)] for c in range(5))
    metadata = dict(kind='rotation_graph_palette_equivariant_search',
                    eta_color_permutation=list(range(5)),u_color_permutation=p,
                    vertices=count,clauses=len(clauses),formula_sha256=digest(clauses),
                    contact_certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    conflict_budget=budget,solver='cadical195',
                    scope='Positive witnesses cover all H-orbit points; failure only concerns this fixed global palette action.')
    start = time.monotonic()
    with Solver(name='cadical195',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        metadata['status'] = 'SAT' if answer is True else 'UNKNOWN' if answer is None else 'RESTRICTED_UNSAT_UNCERTIFIED'
        metadata['stats'] = solver.accum_stats()
        if answer is True:
            positive = set(x for x in solver.get_model() if x > 0)
            word = [next(c for c in range(5) if var(i,c) in positive) for i in range(count)]
            assert all(word[i] != 0 for i in data['origin_neighbors'])
            assert all(word[i] != perm_power(p,n)[word[j]] for i,j,h,n in data['contacts'])
            metadata['word'] = ''.join(map(str,word))
    metadata['seconds'] = round(time.monotonic()-start,3)
    return metadata


def periodic(root, period, colors=5, budget=20000):
    from pysat.solvers import Solver
    path = root/'certificates/rotation_orbit_contacts.json'
    data = json.loads(path.read_text())
    size = data['representative_count']
    # All eta phases and time phases are free, not color-permutation equivariant.
    vertex = lambda i,h,t: (t*5+h)*size+i
    origin = 5*period*size
    edges = set()
    for t in range(period):
        for a in range(5):
            for i,j,h,n in data['contacts']:
                edges.add(tuple(sorted((vertex(i,a,t),vertex(j,(a+h)%5,(t+n)%period)))))
            for i in data['origin_neighbors']:
                edges.add((vertex(i,a,t),origin))
    edges = sorted(edges)
    metadata = dict(kind='rotation_graph_free_periodic_search',period=period,colors=colors,
                    vertices=origin+1,edges=len(edges),edge_sha256=digest(edges),
                    contact_certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    conflict_budget=budget,solver='cadical195',
                    scope='A proper quotient word lifts to the entire H-orbit graph; failure at one period is not an infinite obstruction.')
    loops = [list(e) for e in edges if e[0] == e[1]]
    if loops:
        return dict(**metadata,status='PERIOD_IDENTIFICATION_LOOP',loops=loops)
    var = lambda i,c: colors*i+c+1
    clauses = []
    for i in range(origin+1):
        clauses.append([var(i,c) for c in range(colors)])
        clauses.extend([-var(i,a),-var(i,b)] for a,b in combinations(range(colors),2))
    clauses.append([var(origin,0)])
    for i,j in edges:
        clauses.extend([-var(i,c),-var(j,c)] for c in range(colors))
    metadata['clauses'] = len(clauses)
    metadata['formula_sha256'] = digest(clauses)
    print(json.dumps(dict(stage='periodic_formula',**metadata)),flush=True)
    start = time.monotonic()
    with Solver(name='cadical195',bootstrap_with=clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        metadata['status'] = 'SAT' if answer is True else 'UNKNOWN' if answer is None else 'RESTRICTED_UNSAT_UNCERTIFIED'
        metadata['stats'] = solver.accum_stats()
        if answer is True:
            positive = set(x for x in solver.get_model() if x > 0)
            word = [next(c for c in range(colors) if var(i,c) in positive) for i in range(origin+1)]
            assert all(word[i] != word[j] for i,j in edges)
            metadata['word'] = ''.join(map(str,word))
    metadata['seconds'] = round(time.monotonic()-start,3)
    return metadata


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Do not use -O')
    parser = argparse.ArgumentParser()
    parser.add_argument('--cycle',type=int,choices=(3,4))
    parser.add_argument('--period',type=int)
    parser.add_argument('--colors',type=int,default=5)
    parser.add_argument('--budget',type=int,default=20000)
    args = parser.parse_args()
    assert 1 <= args.budget <= 20000
    assert (args.cycle is None) != (args.period is None)
    root = Path(__file__).resolve().parents[1]
    result = equivariant(root,args.cycle,args.budget) if args.cycle else periodic(root,args.period,args.colors,args.budget)
    print('ROTATION_COLORING_JSON='+json.dumps(result,separators=(',',':')),flush=True)
