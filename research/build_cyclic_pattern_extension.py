"""Optional bounded search for the sharp order-five extension witness.

Search and independent checking are separate. Uses the already saved local
three-atom pattern set, rather than claiming all three-atom laws behave alike.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import argparse
import hashlib
import json
import math
from run_event_pricing import load
from motion_packet_cnf import singleton_formula
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice


def build(local, local_raw, data, budget):
    try:
        from pysat.solvers import Solver
    except ModuleNotFoundError as error:
        raise RuntimeError('Optional search needs requirements-packet-search.txt') from error
    table = multiplication_twice()
    eta = [0]*32
    eta[16] = 1
    def multiply(a,b):
        return tuple(Q(x)/2 for x in product_twice(a,b,table))
    layers = [[tuple(Q(x,local['coordinate_denominator']) for x in p) for p in local['points']]]
    for _ in range(4):
        layers.append([multiply(eta,p) for p in layers[-1]])
    points = sorted(set(p for row in layers for p in row))
    index = {p:i for i,p in enumerate(points)}
    copies = [[index[p] for p in row] for row in layers]
    den = math.lcm(*(x.denominator for p in points for x in p))
    integers = [[int(x*den) for x in p] for p in points]
    target = [4*den*den]+[0]*31
    edges = []
    for a,b in combinations(range(len(points)),2):
        delta = [x-y for x,y in zip(integers[a],integers[b])]
        if product_twice(delta,conjugate_twice(delta),table)==target:
            edges.append([a,b])
    triple = local['three_word_extreme_law']
    matching = triple['eta_unique_support_matching']
    successor = [matching.index(i) for i in range(3)]
    witness = None
    for start in range(3):
        built = singleton_formula(len(points),edges,5,[])
        clauses,top = built['clauses'],built['nv']
        indices = [start]
        for _ in range(3):
            indices.append(successor[indices[-1]])
        for copy,word_index in zip(copies,indices):
            pi = [[top+1+5*a+b for b in range(5)] for a in range(5)]
            top += 25
            for row in pi+list(map(list,zip(*pi))):
                clauses.append(row)
                clauses.extend([[-x,-y] for x,y in combinations(row,2)])
            for v,color in zip(copy,triple['words'][word_index]):
                for new_color in range(5):
                    clauses.append([-pi[int(color)][new_color],5*v+new_color+1])
        with Solver(name='cadical195',bootstrap_with=clauses) as solver:
            solver.conf_budget(budget)
            answer = solver.solve_limited()
            if answer is True:
                model = {v for v in solver.get_model() if v>0}
                witness = ''.join(str(next(c for c in range(5) if 5*v+c+1 in model))
                                  for v in range(len(points)))
                break
    if witness is None:
        raise RuntimeError('No positive witness found within fixed budgets; no negative claim or certificate')
    yids = {tuple(Q(x,data['denominator']) for x in p):i for i,p in enumerate(data['points'])}
    cert = dict(schema='cyclic-pattern-extension-v1',base_commit=local['base_commit'],
        local_certificate_sha256=hashlib.sha256(local_raw).hexdigest(),rotation_order=5,pattern_cycle_length=3,
        points=integers,coordinate_denominator=den,edges=edges,copies=copies,
        vertices_in_Y_or_null=[yids.get(p) for p in points],proper_five_coloring=witness,
        expected_hits=4,bound='4/5',scope='Sharp finite cyclic extension witness; no original-Y full15 decision.')
    from verify_cyclic_pattern_extension import check
    check(cert,local,local_raw,data)
    return cert


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--budget',type=int,default=20000)
    args = parser.parse_args()
    if not 1<=args.budget<=100000:
        raise ValueError('budget outside 1..100000')
    root = Path(__file__).resolve().parents[1]
    path = root/'certificates/localized_motion_packet.json'
    raw = path.read_bytes()
    local = json.loads(raw)
    data = load(args.cache)
    digest = hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    if digest!=local['input_semantic_sha256']:
        raise ValueError('full-Y cache mismatch')
    cert = build(local,raw,data,args.budget)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(cert,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status='INDEPENDENTLY_ACCEPTED',vertices=len(cert['points']),
                         edges=len(cert['edges']),sharp_mass=cert['bound'])))


if __name__=='__main__':
    main()
