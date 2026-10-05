#!/usr/bin/env python3
"""Solver-free replay of T162's weighted Q lifting and T163's local positive law.

Search producers are not imported. The verifier rebuilds each of 512 equality
cases from pinned geometry, enumerates all canonical partitions needed to rule
out violations, and checks sharpness and positive laws using integer arithmetic.
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

from check_transport_projection import (read, canonical, digest, require, pair,
    normalize, partitions, verify_geometry_and_components, square_distance,
    multiplication_twice)

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'certificates/q_defect_lifting.json'
RECEIPT = ROOT / 'certificates/q_defect_lifting_validation.json'
BASE = 'c7dd21efe99cf18884a62b21f34a27de23eec550'
PREVIOUS = '5753d18f691eab2b5b04e54d21762f063e8478daff72c013558535144b44d056'
WEIGHTS = [2, 1, 1, 1, 1, 2, 2, 0, 2]
CORE = [877, 887, 3483, 4641, 5535, 7479, 7489]


def literal_tree(x):
    if type(x) in (int, str):
        return True
    if type(x) is list:
        return all(literal_tree(z) for z in x)
    if type(x) is dict:
        return all(type(k) is str and literal_tree(v) for k, v in x.items())
    return False


def geometry(g, sets, vertices):
    table = multiplication_twice()
    require(vertices == sorted(set(vertices)) and all(type(v) is int and
            0 <= v < len(g['points']) for v in vertices), 'actual vertices')
    all_pairs = set(combinations(vertices, 2))
    for a, b in all_pairs:
        value = square_distance(g, a, b, table)
        require((value == (F(1),) + (F(0),)*31) == ((a,b) in sets['E']),
                'complete induced unit graph')
        for label, norm in [('P', F(1,3)), ('Q', F(4)), ('R', F(4,3))]:
            if (a,b) in sets[label]:
                require(value == (norm,) + (F(0),)*31, 'local field norm '+label)
    return {label: sorted(es & all_pairs) for label, es in sets.items()}


def legal_word(vertices, edges, word):
    require(type(word) is list and len(word) == len(vertices) and
            all(type(c) is int and 0 <= c < 5 for c in word) and
            tuple(word) == normalize(word), 'canonical at-most-five-block word')
    c = dict(zip(vertices, word))
    require(all(c[a] != c[b] for a,b in edges), 'all actual unit edges proper')
    return c


def rebuild_case(vertices, edges, scored, links, mask):
    """Contract exactly the unbroken links; never contract a broken link."""
    parent = {v: v for v in vertices}
    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v
    for i, (a,b) in enumerate(links):
        if not mask >> i & 1:
            x,y = root(a),root(b)
            parent[max(x,y)] = min(x,y)
    image = {v:root(v) for v in vertices}
    unit = {pair(image[a],image[b]) for a,b in edges}
    unit.update(pair(image[a],image[b]) for i,(a,b) in enumerate(links)
                if mask >> i & 1)
    if any(a == b for a,b in unit):
        return None
    score = Counter(pair(image[a],image[b]) for a,b in scored)
    constant = sum(w for (a,b),w in score.items() if a == b)
    score = Counter({e:w for e,w in score.items() if e[0] != e[1]})
    # Connected variable order affects runtime only, not the searched partitions.
    left = set(image.values())
    order = []
    while left:
        v = max(left, key=lambda v: (
            3*sum(pair(u,v) in unit for u in order) +
            sum(score[pair(u,v)] for u in order),
            sum(v in e for e in unit), -v))
        order.append(v)
        left.remove(v)
    index = {v:i for i,v in enumerate(order)}
    before = [[] for _ in order]
    costs = [[] for _ in order]
    for a,b in unit:
        i,j = sorted((index[a],index[b]))
        before[j].append(i)
    for (a,b),w in score.items():
        i,j = sorted((index[a],index[b]))
        costs[j].append((i,w))
    return before, costs, constant


def no_violation(case, target):
    """Complete restricted-growth enumeration, pruned only by nonnegative cost."""
    before, costs, constant = case
    colors = [-1]*len(before)
    nodes = 0
    def visit(i, top, score):
        nonlocal nodes
        nodes += 1
        if score >= target:
            return
        require(i < len(colors), 'pointwise lifting violation: '+repr(colors))
        for value in range(min(5, top+2)):
            if any(colors[j] == value for j in before[i]):
                continue
            increment = sum(w for j,w in costs[i] if colors[j] == value)
            colors[i] = value
            visit(i+1, max(top,value), score+increment)
    visit(0, -1, constant)
    return nodes


def verify_finite_evidence(cert, old, local):
    require(literal_tree(cert), 'only exact integer/string structured literals')
    require(cert['schema'] == 'q-defect-lifting-v1' and cert['research_base'] == BASE,
            'schema and research base')
    require(cert['previous_certificate_sha256'] == PREVIOUS == digest(old),
            'fixed previous certificate')
    for key in ['geometry_semantic_sha256', 'P_Q_basis_sha256', 'R_basis_sha256']:
        require(cert[key] == old[key], 'input source binding '+key)
    q = old['quotient']
    vertices = cert['vertices']
    links = cert['Q_links']
    scored = cert['score_realizations']
    require(vertices == q['vertices'], 'fixed W21')
    require(links == q['Q_bridges'], 'fixed nine Q links and order')
    require(scored == [r['actual_pair'] for r in q['realizations']
                      if r['type'] in ('P','R')], 'fixed 48 actual score realizations')
    require(cert['weights'] == WEIGHTS and cert['threshold'] == 9, 'lifting constants')
    require(len(scored) == len(set(map(tuple,scored))) == 48 and
            all(pair(*e) in set(local['P']) | set(local['R']) for e in scored),
            '48 distinct actual P/R pairs')
    require(sum(pair(*e) in local['P'] for e in scored) == 36 and
            sum(pair(*e) in local['R'] for e in scored) == 12, '36 P and 12 R')
    require(all(pair(*e) in local['Q'] for e in links), 'actual Q membership')
    edges21 = [e for e in local['E'] if set(e) <= set(vertices)]
    sharp = cert['singleton_sharpness']
    require(len(sharp) == 9 and [s['broken_link'] for s in sharp] == list(range(9)),
            'complete singleton sharpness coverage')
    for i, row in enumerate(sharp):
        c = legal_word(vertices, edges21, row['partition'])
        require([j for j,(a,b) in enumerate(links) if c[a] != c[b]] == [i],
                'exact singleton defect')
        s = sum(c[a] == c[b] for a,b in scored)
        require(s == row['score'] == 9-WEIGHTS[i], 'sharp singleton score')

    law = cert['local_22_law']
    V = sorted(vertices + [305])
    require(law['vertices'] == V and law['means'] ==
            {'P':[1,27], 'Q':[1,3], 'R':[14,27]}, 'local law target and vertices')
    require({k:len(v) for k,v in local.items()} == {'E':34,'P':47,'Q':11,'R':31},
            'all 22-point local event counts')
    D = law['denominator']
    atoms = law['atoms']
    require(type(D) is int and D > 0 and 0 < len(atoms) and
            all(type(row['weight']) is int and row['weight'] > 0 for row in atoms),
            'strictly positive integer atom weights and denominator')
    require(sum(row['weight'] for row in atoms) == D, 'probability normalization')
    require(len({tuple(row['partition']) for row in atoms}) == len(atoms),
            'distinct atoms')
    means = {k:[0]*len(local[k]) for k in ('P','Q','R')}
    for row in atoms:
        c = legal_word(V, local['E'], row['partition'])
        for k in means:
            for i,(a,b) in enumerate(local[k]):
                if c[a] == c[b]:
                    means[k][i] += row['weight']
    for k, values in means.items():
        num,den = law['means'][k]
        require(all(v*den == num*D for v in values), 'each individual '+k+' mean')

    # Certify the exact local source of p >= 1/27, not a borrowed global claim.
    core_pairs = set(combinations(CORE,2))
    require(core_pairs <= set(local['E']) | set(local['P']) | set(local['R']) and
            [len(core_pairs & set(local[k])) for k in ('E','P','R')] == [6,12,3],
            'seven-point occupancy window')
    require((229,305) in local['P'] and (229,4641) in local['R'] and
            (305,4641) in local['R'], 'actual PRR triple')
    for w in partitions(7,5):
        require(sum(w[a] == w[b] for a,b in combinations(range(7),2)) >= 2,
                'seven in at most five blocks')
    for w in partitions(3,3):
        require((w[0] == w[2]) + (w[1] == w[2]) - (w[0] == w[1]) <= 1,
                'transitivity bound')
    require(F(1,27) == (2*F(2)-3)/27 and
            14*F(1,27)+4*(1-F(95,108)) == 1, 'exact elimination arithmetic')
    return {'atoms':len(atoms), 'denominator':D, 'unit_edge_checks':len(atoms)*34,
            'individual_event_means':89, 'singleton_witnesses':9}


def replay_cases(cert, local):
    vertices = cert['vertices']
    edges = [e for e in local['E'] if set(e) <= set(vertices)]
    nodes = nontrivial = inconsistent = 0
    for mask in range(1 << 9):
        target = 9 - sum(w for i,w in enumerate(WEIGHTS) if mask >> i & 1)
        if target <= 0:
            continue  # S is a sum of nonnegative indicators.
        nontrivial += 1
        case = rebuild_case(vertices, edges, cert['score_realizations'],
                            cert['Q_links'], mask)
        if case is None:
            inconsistent += 1
        else:
            nodes += no_violation(case, target)
    return {'patterns':512, 'nontrivial_patterns':nontrivial,
            'trivial_by_nonnegativity':512-nontrivial,
            'inconsistent_patterns':inconsistent, 'enumeration_nodes':nodes}


def self_test(cert, old, local):
    mutants = []
    for i in range(9):
        c = deepcopy(cert); c['weights'][i] -= 1; mutants.append(c)
    c = deepcopy(cert); c['weights'][7] = 1; mutants.append(c)
    c = deepcopy(cert); c['Q_links'].pop(); mutants.append(c)
    c = deepcopy(cert); c['score_realizations'].pop(); mutants.append(c)
    c = deepcopy(cert); c['singleton_sharpness'][0]['partition'][0] = 5; mutants.append(c)
    c = deepcopy(cert); c['singleton_sharpness'][0]['score'] += 1; mutants.append(c)
    c = deepcopy(cert); c['previous_certificate_sha256'] = '0'*64; mutants.append(c)
    c = deepcopy(cert); c['local_22_law']['atoms'][0]['weight'] += 1; mutants.append(c)
    c = deepcopy(cert); c['local_22_law']['denominator'] += 1; mutants.append(c)
    c = deepcopy(cert); c['local_22_law']['means']['Q'] = [2,3]; mutants.append(c)
    c = deepcopy(cert); c['local_22_law']['atoms'][0]['partition'] = [0]*22; mutants.append(c)
    c = deepcopy(cert); c['weights'][0] = 2.0; mutants.append(c)
    c = deepcopy(cert); c['threshold'] = True; mutants.append(c)
    for c in mutants:
        try:
            verify_finite_evidence(c, old, local)
        except (ValueError, KeyError, TypeError, IndexError):
            pass
        else:
            raise ValueError('mutation accepted')
    # A genuine counterexample must reach a rejecting leaf, not be a timeout.
    try:
        no_violation(([[],[]],[[],[]],0), 1)
    except ValueError:
        pass
    else:
        raise ValueError('enumeration failed to reject a false inequality')
    require(no_violation(([[],[0]],[[],[(0,1)]],0),0) == 1, 'zero-target pruning')
    proc = subprocess.run([sys.executable,'-O','-S',str(Path(__file__).resolve()),
                           '--optimization-probe'], capture_output=True, text=True)
    require(proc.returncode != 0 and 'run without -O' in proc.stderr,
            'optimization mode rejection')
    return len(mutants)+3


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test',action='store_true')
    ap.add_argument('--write-receipt',action='store_true')
    args = ap.parse_args()
    old = read(ROOT/'certificates/q_pr_joint_cuts.json')
    cert = read(CERT)
    require(digest(old) == PREVIOUS, 'prior certificate is pinned before use')
    g = read(ROOT/'certificates/Y_full_geometry.json.gz')
    b = read(ROOT/'certificates/g14_pair_orbit_basis.json.gz')
    r = read(ROOT/'certificates/g14_r_pair_orbit_basis.json.gz')
    _,sets,sizes = verify_geometry_and_components(g,b,r)
    local = geometry(g,sets,sorted(old['quotient']['vertices']+[305]))
    finite = verify_finite_evidence(cert,old,local)
    enumeration = replay_cases(cert,local)
    report = {'schema':'q-defect-lifting-validation-v1','status':'PASS',
              'certificate_sha256':digest(cert),'base':BASE,'transport_components':sizes,
              'local_exact_pair_checks':231,'finite_evidence':finite,
              'case_replay':enumeration,'scope':cert['scope']}
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    else:
        require(read(RECEIPT) == report, 'deterministic replay receipt')
    if args.self_test:
        print('self_tests_passed',self_test(cert,old,local))
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))


if __name__ == '__main__':
    main()
