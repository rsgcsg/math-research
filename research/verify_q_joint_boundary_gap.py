#!/usr/bin/env python3
"""Exact color-class dual, saturated-face separator, and fractional-cover replay.

No optimization or search-output modules are imported. All event graphs are
reconstructed from pinned actual geometry and transport components. Complete
independent-set and restricted-growth enumerations serve distinct proof roles.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')

from check_transport_projection import (read, digest, require, pair,
    verify_geometry_and_components)
from verify_q_defect_lifting import geometry, literal_tree, WEIGHTS

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT/'certificates/q_joint_boundary_gap.json'
RECEIPT = ROOT/'certificates/q_joint_boundary_gap_validation.json'
PREVIOUS = '0e95de5517c615963e01aa900c67a12a14dfdccbf136b3575988dc28e1659ce6'
H = [229, 231, 233, 877, 887, 4641]


def independent_sets(adj):
    """Generate every independent mask exactly once, in increasing vertex order."""
    def visit(mask, remaining):
        yield mask
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            i = bit.bit_length()-1
            yield from visit(mask | bit, remaining & ~adj[i])
    yield from visit(0, (1 << len(adj))-1)


def class_dual(cert, previous, local):
    d = cert['color_class']
    V = previous['vertices']
    require(d == {'vertices':V,'distinguished':H,'constant':3,'coefficient':2},
            'fixed class dual')
    ix = {v:i for i,v in enumerate(V)}
    adj = [0]*len(V)
    for a,b in local['E']:
        if a in ix and b in ix:
            adj[ix[a]] |= 1 << ix[b]
            adj[ix[b]] |= 1 << ix[a]
    score = [((1 << ix[a]) | (1 << ix[b]), 1)
             for a,b in previous['score_realizations']]
    score += [((1 << ix[a]) | (1 << ix[b]), -w)
              for (a,b),w in zip(previous['Q_links'],WEIGHTS)]
    hm = sum(1 << ix[v] for v in H)
    seen = set()
    histogram = Counter()
    minimum = {}
    for mask in independent_sets(adj):
        require(mask not in seen, 'no duplicate independent sets')
        seen.add(mask)
        h = (mask & hm).bit_count()
        f = sum(w for e,w in score if mask & e == e)
        slack = f+3-2*h
        require(slack >= 0, 'color-class inequality')
        histogram[slack] += 1
        minimum[h] = min(f,minimum.get(h,f))
    # Independent exhaustive bit-DP over ALL subsets checks enumeration coverage.
    flags = bytearray(1 << len(V)); flags[0] = 1
    for mask in range(1, len(flags)):
        bit = mask & -mask
        rest = mask ^ bit
        flags[mask] = bool(flags[rest] and not rest & adj[bit.bit_length()-1])
        require(bool(flags[mask]) == (mask in seen), 'independent-set coverage')
    require(0 in seen and sum(flags) == 8232 and
            minimum == {0:-3,1:-1,2:1,3:3}, 'class count and sharp strata')
    return {'independent_sets':len(seen),'subsets_in_second_algorithm':len(flags),
            'tight_sets':histogram[0],
            'minima_by_H_occupancy':{str(k):v for k,v in sorted(minimum.items())}}


def check_cover(cover, V, local):
    require(cover['vertices'] == V and cover['mass'] == 5 and cover['means'] ==
            {'P':[1,27],'Q':[7,10],'R':[14,27]}, 'fractional cover targets')
    D = cover['denominator']; atoms = cover['atoms']
    require(type(D) is int and D > 0 and len(atoms) > 0, 'cover denominator')
    total = 0; diagonals = dict.fromkeys(V,0)
    moments = {k:dict.fromkeys(local[k],0) for k in ('P','Q','R')}
    seen = set()
    for atom in atoms:
        w = atom['numerator']; values = atom['vertices']
        require(type(w) is int and w > 0 and values == sorted(set(values)) and
                set(values) <= set(V), 'positive independent-set atom')
        A = set(values)
        require(tuple(values) not in seen, 'distinct independent-set atoms')
        seen.add(tuple(values))
        require(all(not (a in A and b in A) for a,b in local['E']),
                'independent on every actual unit edge')
        total += w
        for v in A: diagonals[v] += w
        for k in moments:
            for a,b in moments[k]:
                if a in A and b in A: moments[k][a,b] += w
    require(total == 5*D and all(x == D for x in diagonals.values()),
            'total mass five and individual vertex cover one')
    for k in moments:
        n,d = cover['means'][k]
        require(all(x*d == n*D for x in moments[k].values()),
                'each fractional '+k+' moment')
    return {'atoms':len(atoms),'denominator':D,'total_mass':5,
            'individual_vertex_covers':len(V),'individual_pair_moments':89}


def boundary_problem(boundary, local):
    V = boundary['vertices']; order = boundary['order']
    require(order and sorted(order) == V == sorted(set(V)), 'complete variable order')
    windows = boundary['saturated_windows']
    require(len(windows) == 7 and len({tuple(w) for w in windows}) == 7,
            'seven distinct windows')
    for w in windows:
        require(len(w) == 7 and w == sorted(set(w)) and set(w) <= set(V),
                'actual seven-point window')
        pairs = set(combinations(w,2))
        require(pairs <= set(local['E']) | set(local['P']) | set(local['R']) and
                [len(pairs & set(local[k])) for k in ('E','P','R')] == [6,12,3],
                'complete window with 6 E, 12 P, 3 R')
    a,o,b = boundary['PRR_triple']
    require(pair(a,b) in local['P'] and pair(a,o) in local['R'] and
            pair(b,o) in local['R'], 'actual PRR triple')
    terms = boundary['terms']
    for k in ('P','Q','R'):
        selected = [pair(*t['pair']) for t in terms if t['type'] == k]
        require(len(selected) == len(set(selected)) and set(selected) == set(local[k]),
                'all individual boundary '+k+' terms')
    require(len(terms) == 89 and all(type(t['coefficient']) is int for t in terms),
            'integer separator coefficients')
    sums = {k:sum(t['coefficient'] for t in terms if t['type'] == k)
            for k in ('P','Q','R')}
    rhs = boundary['rhs']
    require(type(rhs) is int and sums['Q'] > 0, 'integer upper separator')
    bound = (F(rhs)-F(sums['P'],27)-F(14*sums['R'],27))/sums['Q']
    positive_sum = sum(max(0,t['coefficient']) for t in terms)
    require(positive_sum == 1323 and positive_sum-rhs == 1321, 'safe global lifting penalty')
    require((2267+85*1321,501+19*1321,2-13*1321) ==
            (114552,25600,-17171), 'unconditional lifted inequality')
    require(500*(F(7,10)-bound) == F(115,27), 'strict fractional cover gap')
    require(boundary['q_upper'] == [bound.numerator,bound.denominator] and
            bound == F(1867,2700) < F(7,10), 'exact strict separation')
    require(12*F(1,27)+3*F(14,27) == 2 and
            2*F(14,27)-F(1,27) == 1, 'zero expectation of nonnegative slacks')
    ix = {v:i for i,v in enumerate(order)}
    unit_before = [0]*len(V)
    for a,b in local['E']:
        i,j = sorted((ix[a],ix[b])); unit_before[j] |= 1 << i
    cores = [sorted(ix[v] for v in w) for w in windows]
    memberships = [[t for t,w in enumerate(cores) if i in w] for i in range(len(V))]
    ends = [w[-1] for w in cores]
    tri = [ix[v] for v in boundary['PRR_triple']]
    costs = [[] for _ in V]
    for t in terms:
        a,b = sorted(ix[v] for v in t['pair'])
        costs[b].append((a,t['coefficient']))
    return unit_before, memberships, ends, tri, costs, rhs, sums


def enumerate_boundary(problem):
    """All proper canonical <=5-color words with each necessary slack zero.

Unlike the producer, use color-class bit masks and per-window color counts,
not scans of prior vertices to maintain equality counts. No numerical pruning.
"""
    before, members, ends, tri, costs, rhs, sums = problem
    n = len(before); colors = [-1]*n; classes = [0]*5
    counts = [[0]*5 for _ in ends]; pairs = [0]*len(ends)
    tri_end = max(tri)
    nodes = leaves = 0; maximum = None
    def visit(i, top, value):
        nonlocal nodes,leaves,maximum
        nodes += 1
        if i == n:
            leaves += 1
            require(value <= rhs, 'boundary separator violation: '+repr(colors))
            maximum = value if maximum is None else max(maximum,value)
            return
        for color in range(min(5,top+2)):
            if before[i] & classes[color]: continue
            colors[i] = color
            if i == tri_end:
                a,o,b = tri
                if (colors[a] == colors[o])+(colors[b] == colors[o])-(colors[a] == colors[b]) != 1:
                    continue
            touched = members[i]
            if any(pairs[t]+counts[t][color] > 2 or
                   (ends[t] == i and pairs[t]+counts[t][color] != 2) for t in touched):
                continue
            for t in touched:
                pairs[t] += counts[t][color]; counts[t][color] += 1
            classes[color] |= 1 << i
            inc = sum(w for j,w in costs[i] if colors[j] == color)
            visit(i+1,max(top,color),value+inc)
            classes[color] ^= 1 << i
            for t in touched:
                counts[t][color] -= 1; pairs[t] -= counts[t][color]
    visit(0,-1,0)
    require(leaves > 0, 'nonempty boundary enumeration')
    return {'nodes':nodes,'proper_saturated_partitions':leaves,
            'maximum_integer_score':maximum,'bound_rhs':rhs,'coefficient_sums':sums}


def self_tests(cert, previous, local):
    # Positivity, vertex coverage, pair means, actual edges, and separation are
    # checked by real evaluators, not by accepting a stored PASS flag.
    count = 0
    for edit in ('weight','denominator','target','edge'):
        cover = deepcopy(cert['fractional_cover'])
        if edit == 'weight': cover['atoms'][0]['numerator'] += 1
        elif edit == 'denominator': cover['denominator'] += 1
        elif edit == 'target': cover['means']['Q'] = [1,3]
        else: cover['atoms'][0]['vertices'] = sorted(local['E'][0])
        try: check_cover(cover,cert['boundary']['vertices'],local)
        except (ValueError,KeyError,TypeError): count += 1
        else: raise ValueError('invalid cover accepted')
    for edit in ('coefficient','type','window','bound'):
        b = deepcopy(cert['boundary'])
        if edit == 'coefficient': b['terms'][0]['coefficient'] = 0.5
        elif edit == 'type': b['terms'][0]['type'] = 'Q'
        elif edit == 'window': b['saturated_windows'][0][0] = 305
        else: b['q_upper'] = [7,10]
        try: boundary_problem(b,local)
        except (ValueError,KeyError,TypeError): count += 1
        else: raise ValueError('invalid boundary input accepted')
    # A one-vertex synthetic problem reaches and rejects a violating leaf.
    try: enumerate_boundary(([0], [[]], [], [0,0,0], [[]], -1, {}))
    except ValueError: count += 1
    else: raise ValueError('false pointwise inequality accepted')
    proc = subprocess.run([sys.executable,'-O','-S',str(Path(__file__).resolve()),
                           '--optimization-probe'],capture_output=True,text=True)
    require(proc.returncode != 0 and 'run without -O' in proc.stderr, 'reject -O')
    problem = boundary_problem(cert['boundary'],local)
    ix = {v:i for i,v in enumerate(cert['boundary']['order'])}
    require(problem[3] == [ix[v] for v in cert['boundary']['PRR_triple']],
            'PRR endpoints survive later edge-loop variables')
    return count+2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt',action='store_true')
    ap.add_argument('--self-test',action='store_true')
    args = ap.parse_args()
    cert = read(CERT); previous = read(ROOT/'certificates/q_defect_lifting.json')
    require(literal_tree(cert) and cert['schema'] == 'q-joint-boundary-gap-v1' and
            cert['previous_certificate_sha256'] == PREVIOUS == digest(previous),
            'exact certificate and pinned prior input')
    g = read(ROOT/'certificates/Y_full_geometry.json.gz')
    b = read(ROOT/'certificates/g14_pair_orbit_basis.json.gz')
    r = read(ROOT/'certificates/g14_r_pair_orbit_basis.json.gz')
    _,sets,sizes = verify_geometry_and_components(g,b,r)
    V = cert['boundary']['vertices']
    require(V == sorted(previous['vertices']+[305]), 'fixed W22')
    local = geometry(g,sets,V)
    cd = class_dual(cert,previous,local)
    cov = check_cover(cert['fractional_cover'],V,local)
    problem = boundary_problem(cert['boundary'],local)
    bd = enumerate_boundary(problem)
    report = {'schema':'q-joint-boundary-validation-v1','status':'PASS',
              'certificate_sha256':digest(cert),'transport_components':sizes,
              'color_class':cd,'boundary':bd,'fractional_cover':cov,'scope':cert['scope']}
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    else: require(read(RECEIPT) == report, 'deterministic replay receipt')
    if args.self_test: print('self_tests_passed',self_tests(cert,previous,local))
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))

if __name__ == '__main__': main()
