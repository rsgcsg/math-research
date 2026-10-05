#!/usr/bin/env python3
"""Independently reconcile Q-defect penalty optima 13 and 12.

The former uses only the 18 selected unit realizations. The latter uses the
complete induced 34-edge graph. Never transfer a positive coloring between
these two models without checking the omitted actual edges.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

if not __debug__:
    raise RuntimeError('Verification requires normal Python, not -O')

from check_q_defect_lift import (
    prepare, build_case, exclude_lower_score, literal_tree,
)
from check_transport_projection import require
from verify_pr_matching_window_ceiling import read, digest

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'certificates/q_defect_scope_audit.json'
RECEIPT = ROOT / 'certificates/q_defect_scope_audit_validation.json'


def verify(cert, parent, lift, prepared, negative=True):
    require(literal_tree(cert), 'scope certificate exact literals')
    require(cert['schema'] == 'q-defect-model-scope-audit-v1', 'schema')
    require(cert['relation_parent_sha256'] == digest(parent), 'fixed relation binding')
    require(cert['induced_witness_source_sha256'] == digest(lift), 'fixed full-graph witness source')
    vertices, edges, pairs, links, _, _ = prepared
    selected = [tuple(x['actual_pair']) for x in parent['quotient']['realizations'] if x['type'] == 'E']
    require(len(set(selected)) == len(selected) == 18 and len(edges) == 34, 'two distinct edge models')
    require(set(selected) < set(edges), 'selected edges are a strict subset of the induced graph')
    omitted = sorted(set(edges) - set(selected))
    require(cert['omitted_unit_edges'] == [list(x) for x in omitted], 'all 16 omitted actual edges')
    a, b = cert['selected_weights'], cert['induced_weights']
    require(a == [2,1,1,1,1,2,2,1,2] and b == [2,1,1,1,1,2,2,0,2], '13 and 12 weights')
    rows = cert['rows']
    require(len(rows) == 6, 'six selected-model optimality witnesses')
    defects = [2,4,3,4,4,3]
    coefficient_twice = [0]*9
    violation_counts = []
    induced_twelve_failures = 0
    for k, row in enumerate(rows):
        text = row['word']
        require(type(text) is str and len(text) == 21 and set(text) <= set('01234'), 'full word')
        colors = dict(zip(vertices, map(int, text)))
        require(all(colors[x] != colors[y] for x,y in selected), 'proper on selected 18 edges')
        score = sum(colors[x] == colors[y] for x,y in pairs)
        broken = [j for j,(x,y) in enumerate(links) if colors[x] != colors[y]]
        violations = [list(e) for e in edges if colors[e[0]] == colors[e[1]]]
        require(score == row['score'] == 9-defects[k] and broken == row['broken'], 'exact score and pattern')
        require(violations == row['violated_actual_unit_edges'] and len(violations) > 0,
                'each selected witness violates omitted actual edges')
        value = score + sum(b[j] for j in broken)
        require(value == row['penalty_12_score'], 'score with the induced-model weights')
        induced_twelve_failures += value < 9
        violation_counts.append(len(violations))
        multiplier_twice = 2 if k < 2 else 1
        for j in broken:
            coefficient_twice[j] += multiplier_twice
    require(coefficient_twice == [2]*9 and sum(2*x if i<2 else x for i,x in enumerate(defects)) == 26,
            'six half-integral dual multipliers prove sum of penalties at least 13')
    require(induced_twelve_failures == 2, 'two genuine counterexamples to weight 12 on the 18-edge relaxation')
    # The nine full-graph singleton words separately force every coefficient
    # to be at least b_j. No assertion about their global Y extension follows.
    for j in range(9):
        row = lift['cases'][1 << j]
        text = row['word']
        require(type(text) is str and len(text) == 21 and set(text) <= set('01234'), 'full-graph five-color word')
        colors = dict(zip(vertices, map(int, text)))
        require(all(colors[x] != colors[y] for x,y in edges), 'proper full-graph singleton word')
        broken = [i for i,(x,y) in enumerate(links) if colors[x] != colors[y]]
        score = sum(colors[x] == colors[y] for x,y in pairs)
        require(broken == [j] and score == 9-b[j], 'full-graph coordinatewise lower bound')
    nodes = {}
    if negative:
        for label, graph, weights in [('selected_18', selected, a), ('induced_34', edges, b)]:
            count = 0
            for mask in range(512):
                threshold = 9 - sum(w for j,w in enumerate(weights) if (mask >> j) & 1)
                count += exclude_lower_score(*build_case(vertices, graph, pairs, links, mask), threshold)
            nodes[label] = count
    return {'schema':'q-defect-model-scope-replay-v1', 'status':'PASS',
            'certificate_sha256':digest(cert), 'relation_parent_sha256':digest(parent),
            'induced_optimality_witness_source_sha256':digest(lift),
            'selected_edges':18, 'induced_edges':34, 'omitted_actual_edges':16,
            'selected_model_minimum_penalty_sum':13,
            'induced_model_minimum_penalty_sum':12,
            'integer_branch_cover_nodes':nodes, 'case_patterns_per_model':512,
            'selected_model_optimality_words':6,
            'actual_unit_violations_in_each_selected_word':violation_counts,
            'counterexamples_to_penalty_12_in_selected_model':induced_twelve_failures,
            'full_graph_singleton_optimality_words':9,
            'scope':cert['scope']}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-receipt',action='store_true')
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    cert=read(CERT);parent=read(ROOT/'certificates/q_pr_joint_cuts.json')
    lift=read(ROOT/'certificates/q_defect_lift.json')
    g=read(ROOT/'certificates/Y_full_geometry.json.gz')
    b=read(ROOT/'certificates/g14_pair_orbit_basis.json.gz')
    r=read(ROOT/'certificates/g14_r_pair_orbit_basis.json.gz')
    prepared=prepare(parent,g,b,r)
    report=verify(cert,parent,lift,prepared)
    if args.self_test:
        mutations={
            'wrong-schema': lambda c:c.__setitem__('schema','wrong'),
            'wrong-lift-binding': lambda c:c.__setitem__('induced_witness_source_sha256','0'*64),
            'wrong-relation': lambda c:c.__setitem__('relation_parent_sha256','0'*64),
            'missing-edge': lambda c:c['omitted_unit_edges'].pop(),
            'wrong-weights': lambda c:c['induced_weights'].__setitem__(7,1),
            'missing-word': lambda c:c['rows'].pop(),
            'bad-word': lambda c:c['rows'][0].__setitem__('word','0'*21),
            'wrong-score': lambda c:c['rows'][0].__setitem__('score',8),
            'wrong-pattern': lambda c:c['rows'][0].__setitem__('broken',[7]),
            'missing-violation': lambda c:c['rows'][0].__setitem__('violated_actual_unit_edges',[]),
            'wrong-counterexample-score': lambda c:c['rows'][4].__setitem__('penalty_12_score',9),
        }
        for name, mutate in mutations.items():
            damaged=deepcopy(cert);mutate(damaged)
            try: verify(damaged,parent,lift,prepared,negative=False)
            except (ValueError,KeyError,IndexError,TypeError): continue
            raise ValueError('mutation not rejected: '+name)
        proc=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True)
        require(proc.returncode != 0 and 'not -O' in proc.stderr, 'optimized Python rejected')
        print(json.dumps({'self_test':'PASS','certificate_mutations_rejected':len(mutations),'optimized_mode_rejected':True}))
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    else: require(read(RECEIPT)==report,'saved scope receipt matches independent replay')
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=='__main__':main()
