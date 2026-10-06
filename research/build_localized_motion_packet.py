"""Optional bounded re-search of the fixed 29-point configuration (not a checker).

Uses the separately bound full-Y cache to recover coordinates and domains.
The certificate is emitted only after the separate exact checker accepts it.
No unproved minimality inference is taken from a solver's unsatisfiable core.
"""
from pathlib import Path
import argparse
import hashlib
import json
from itertools import permutations
from motion_packet_cnf import singleton_formula
from search_motion_packet import run
from run_event_pricing import load

VERTICES = [34,231,232,878,888,899,900,3503,3533,3660,3661,3666,4109,4641,
            4655,5163,5412,7468,7469,7478,7488,7507,8646,8651,8807,8986,9052,9055,9070]
CORE = [5,6,9,11,13,14]
BASE = 'ed4cfb044164b5d88413a2d53c7e030274d04bb8'


def subset(data, keep):
    ids = {v:i for i,v in enumerate(keep)}
    return dict(points=[data['points'][v] for v in keep],
        edges=sorted([ids[a],ids[b]] for a,b in data['edges'] if a in ids and b in ids),
        mappings=[[[ids[a],ids[b]] for a,b in mm if a in ids and b in ids] for mm in data['mappings']])


def search_one(data, k, motions, budget, denial=False):
    from pysat.solvers import Solver
    b = singleton_formula(len(data['points']),data['edges'],k,[data['mappings'][j] for j in motions])
    origin = next((v for v,p in enumerate(data['points']) if not any(p)),None)
    edge = next((e for e in data['edges'] if origin in e),data['edges'][0])
    b['clauses'] += [[k*edge[0]+1],[k*edge[1]+2]]
    raw = (f"p cnf {b['nv']} {len(b['clauses'])}\n"+
           ''.join(' '.join(map(str,c))+' 0\n' for c in b['clauses'])).encode()
    with Solver(name='glucose3' if denial else 'cadical195',bootstrap_with=b['clauses'],with_proof=denial) as s:
        s.conf_budget(budget)
        answer = s.solve_limited()
        if answer is None:
            raise RuntimeError('UNKNOWN fixed-model query; no new certificate written')
        if denial:
            if answer:
                raise RuntimeError('Unexpected singleton solution; inspect geometry and original certificate')
            from rup_hint_export import export
            proof = export(b['clauses'],s.get_proof())
            return dict(status='VERIFIED_NO_SINGLETON', motions=motions,nv=b['nv'],clauses=len(b['clauses']),
                cnf_sha256=hashlib.sha256(raw).hexdigest(),normalization_edge=edge,
                normalization_colors=[0,1],proof=proof)
        if not answer:
            raise RuntimeError('UNSAT_UNCERTIFIED positive-witness search; no certificate written')
        model = {x for x in s.get_model() if x>0}
        word = ''.join(str(next(c for c in range(k) if k*v+c+1 in model)) for v in range(len(data['points'])))
        return word


def build(data, digest, budget):
    local = subset(data,VERTICES)
    q = search_one(local,5,CORE,budget,True)
    two = run(local,list(range(15)),2,budget)
    if two['status']!='POSITIVE_PACKET':
        raise RuntimeError(two['status']+' in full local two-word query')
    three = run(local,list(range(15)),3,budget)
    if three['status']!='POSITIVE_PACKET':
        raise RuntimeError(three['status']+' in full local three-word query')
    def partition(word, indices):
        classes = {}
        for pos,v in enumerate(indices):
            classes.setdefault(word[v],[]).append(pos)
        return sorted(classes.values())
    candidates = []
    for j,mm in enumerate(local['mappings']):
        aa = [partition(w,[a for a,b in mm]) for w in three['words']]
        bb = [partition(w,[b for a,b in mm]) for w in three['words']]
        for pattern in aa+bb:
            row = [int(a==pattern)-int(b==pattern) for a,b in zip(aa,bb)]
            if any(row):
                candidates.append(dict(motion=j,blocks=pattern,coefficients=row))
    def determinant(a,b):
        return a[0]*(b[1]-b[2])-a[1]*(b[0]-b[2])+a[2]*(b[0]-b[1])
    ranks = next(((a,b,determinant(a['coefficients'],b['coefficients'])) for a in candidates
                  for b in candidates if determinant(a['coefficients'],b['coefficients'])),None)
    if ranks is None:
        raise RuntimeError('Three-word candidate is not the required extreme-point witness')
    mm = local['mappings'][2]
    aa = [partition(w,[a for a,b in mm]) for w in three['words']]
    bb = [partition(w,[b for a,b in mm]) for w in three['words']]
    matches = [list(p) for p in permutations(range(3)) if all(aa[i]==bb[p[i]] for i in range(3))]
    if len(matches)!=1 or any(matches[0][i]==i for i in range(3)):
        raise RuntimeError('This new three-word law does not reproduce the order-mismatch witness')
    extreme = dict(words=three['words'],weights=['1/3']*3,motions=list(range(15)),
        rank_rows=list(ranks[:2]),augmented_determinant=ranks[2],eta_unique_support_matching=matches[0])
    ordinary = search_one(local,3,[],budget)
    six = search_one(local,6,list(range(15)),budget)
    vertex = [dict(removed=v,word=search_one(subset(local,[w for w in range(29) if w!=v]),5,CORE,budget))
              for v in range(29)]
    motion = [dict(omitted=j,word=search_one(local,5,[i for i in CORE if i!=j],budget)) for j in CORE]
    cert = dict(schema='localized-motion-packet-v1',base_commit=BASE,input_semantic_sha256=digest,
        vertices_in_Y=VERTICES,coordinate_denominator=data['denominator'],points=local['points'],
        edges=local['edges'],motion_names=data['motions'],mappings=local['mappings'],motions=CORE,
        one_word_denial=q,three_word_extreme_law=extreme,two_word_law=dict(words=two['words'],weights=['1/2','1/2'],motions=list(range(15))),
        ordinary_coloring=dict(k=3,word=ordinary,odd_cycle=[5,10,13,6,21]),
        singleton_six_coloring=dict(colors=6,motions=list(range(15)),word=six),
        omit_one_motion=motion,omit_one_vertex=vertex,
        scope='Fixed 29-point local system; no full-Y15-law or global minimum-cardinality claim.')
    # The result status is not trusted until the independent re-constructor accepts it.
    from verify_localized_motion_packet import check
    check(cert, data, dict(semantic_sha256=digest))
    return cert


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--budget',type=int,default=100000)
    args = parser.parse_args()
    if not 1<=args.budget<=100000:
        raise ValueError('budget must be between 1 and 100000')
    root = Path(__file__).resolve().parents[1]
    data = load(args.cache)
    digest = hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    expected = load(root/'certificates/full_law_preparation_audit.json')['independent_inputs']['semantic_sha256']
    if digest!=expected:
        raise ValueError('cache identity mismatch')
    cert = build(data,digest,args.budget)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(cert,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status='INDEPENDENTLY_ACCEPTED',vertices=29,ordinary_colors=3,
                          singleton_colors=6,local_five_color_support=2)))


if __name__=='__main__':
    main()
