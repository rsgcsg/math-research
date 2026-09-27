"""Fast independent exact verification of the 29-point T141 motion core.

No SAT solver, search producer, hint exporter, floating point arithmetic or
cached full-Y geometry is needed. The 406 point pairs and all 15 maximal
motion domains are rebuilt directly in the existing exact 32-dimensional
algebra. The comprehensive test additionally binds the points back to Y.
"""
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json
from verify_quintic_core_probe import (
    multiplication_twice, product_twice, conjugate_twice,
)
from verify_motion_packet import (
    CORE, BASE, require, read, pattern, full_law_domains, rebuild_singleton,
)
from verify_rup_lrat import check as check_rup


def actual_geometry(cert):
    points = cert['points']
    denominator = cert['coordinate_denominator']
    require(type(denominator) is int and denominator == 480, 'coordinate denominator')
    require(len(points) == 29 and all(isinstance(p, list) and len(p) == 32
            and all(type(x) is int for x in p) for p in points), 'exact coordinates')
    require(len(set(map(tuple, points))) == len(points), 'coincident vertices')
    table = multiplication_twice()
    target = [4*denominator*denominator]+[0]*31
    edges = []
    for a, b in combinations(range(len(points)), 2):
        delta = [x-y for x,y in zip(points[a], points[b])]
        if product_twice(delta, conjugate_twice(delta), table) == target:
            edges.append([a,b])
    require(cert['edges'] == edges and all(type(x) is int for e in cert['edges'] for x in e),
            'complete actual unit edges')
    zero = (Q(0),)*32
    one = (Q(1),)+zero[1:]
    eta = zero[:16]+one[:16]
    def vector(coeff):
        return tuple(coeff.get(j, Q(0)) for j in range(32))
    def mul(a,b):
        return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):
        return tuple(Q(x)/2 for x in conjugate_twice(a))
    def add(a,b):
        return tuple(x+y for x,y in zip(a,b))
    # Reconstruct the motion definitions, not the producer's cached mappings.
    z = vector({0: -Q(1,2), 9: -Q(1,6)})
    tau = vector({0: -Q(1,10), 10: Q(3,10)})
    nu = vector({0: Q(5,6), 10: Q(1,6)})
    omega = tuple(-2*x-3*y for x,y in zip(one,z))
    shift = add(one, mul(eta,z))
    definitions = [
        ('tau',tau,zero,False), ('nu',nu,zero,False),
        ('eta',eta,zero,False), ('omega',omega,zero,False),
        ('bar',one,zero,True),
        ('bridge',tuple(-x for x in eta),shift,False),
        ('translation_one',one,one,False), ('translation_z',one,z,False),
    ]
    power = one
    for exponent in range(1,5):
        power = mul(power,eta)
        definitions.append((f'one_plus_eta_{exponent}',one,add(one,power),False))
    require(mul(power,eta)==one and eta!=one, 'exact order-five rotation')
    u = vector({0: Q(1,8), 4: -Q(3,8), 9: -Q(1,8), 13: -Q(1,8)})
    definitions.extend([('bridge_shift',one,shift,False),
                        ('minus_bar',tuple(-x for x in one),zero,True),
                        ('dyadic_u',u,zero,False)])
    require(cert['motion_names']==[x[0] for x in definitions], 'motion names')
    physical = [tuple(Q(x,denominator) for x in p) for p in points]
    index = {p:i for i,p in enumerate(physical)}
    mappings = []
    for name,coefficient,offset,reflected in definitions:
        require(mul(coefficient,bar(coefficient)) == one, 'motion is not an isometry')
        mapping = []
        for i,p in enumerate(physical):
            image = add(mul(coefficient,bar(p) if reflected else p),offset)
            if image in index:
                mapping.append([i,index[image]])
        require(len({b for a,b in mapping})==len(mapping), 'noninjective motion')
        mappings.append(mapping)
    require(cert['mappings']==mappings and all(type(x) is int for mm in cert['mappings']
            for pair in mm for x in pair), 'complete maximal motion domains')
    return dict(points=points, edges=edges, mappings=mappings)


def word_checks(word, data, k):
    require(isinstance(word,str) and len(word)==len(data['points'])
            and set(word)<=set(map(str, range(k))), 'color word')
    require(all(word[a]!=word[b] for a,b in data['edges']), 'improper word')


def restrict(data, keep):
    labels = {v:i for i,v in enumerate(keep)}
    return dict(points=[data['points'][v] for v in keep],
        edges=sorted([labels[a],labels[b]] for a,b in data['edges'] if a in labels and b in labels),
        mappings=[[[labels[a],labels[b]] for a,b in mm if a in labels and b in labels]
                  for mm in data['mappings']])


def normalized_cnf(data, q):
    edge = q['normalization_edge']
    require(isinstance(edge,list) and len(edge)==2 and all(type(v) is int for v in edge)
            and edge in data['edges'] and q['normalization_colors']==[0,1]
            and all(type(v) is int for v in q['normalization_colors']), 'safe edge normalization')
    built = rebuild_singleton(len(data['points']),data['edges'],5,
                              [data['mappings'][j] for j in CORE])
    # A global palette renaming normalizes any proper coloring on this actual
    # edge. All existential motion permutations are conjugated, never fixed.
    built['clauses'] += [[5*edge[0]+1],[5*edge[1]+2]]
    raw = (f"p cnf {built['nv']} {len(built['clauses'])}\n"+
           ''.join(' '.join(map(str,c))+' 0\n' for c in built['clauses'])).encode()
    built['cnf_sha256'] = hashlib.sha256(raw).hexdigest()
    return built


def check(cert, full_data=None, full_summary=None):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    require(cert['schema']=='localized-motion-packet-v1' and cert['base_commit']==BASE, 'provenance')
    require(cert['motions']==CORE and all(type(x) is int for x in cert['motions']), 'six-motion scope')
    ids = cert['vertices_in_Y']
    require(len(ids)==29 and all(type(v) is int and 0<=v<10077 for v in ids)
            and ids==sorted(set(ids)), 'Y vertex identifiers')
    data = actual_geometry(cert)
    if full_data is not None:
        require(full_summary is not None and cert['input_semantic_sha256']==full_summary['semantic_sha256'],
                'Y input binding')
        require(data==restrict(full_data,ids), 'localized embedding into Y')
    words = cert['two_word_law']['words']
    require(cert['two_word_law']['motions']==list(range(15)) and
            cert['two_word_law']['weights']==['1/2','1/2'] and len(words)==2, 'all15 two-word scope')
    for w in words:
        word_checks(w,data,5)
    require(pattern(words[0],range(29))!=pattern(words[1],range(29)), 'distinct complete partitions')
    passed,detail = full_law_domains(words,[Q(1,2)]*2,data['mappings'])
    require(passed==list(range(15)), 'missing full local domain law')
    triple = cert['three_word_extreme_law']
    require(triple['motions']==list(range(15)) and triple['weights']==['1/3']*3
            and len(triple['words'])==3, 'three-atom law scope')
    for word in triple['words']:
        word_checks(word,data,5)
    require(len({pattern(w,range(29)) for w in triple['words']})==3, 'distinct three atoms')
    three_passed,_ = full_law_domains(triple['words'],[Q(1,3)]*3,data['mappings'])
    require(three_passed==list(range(15)), 'three-atom complete joint law')
    rank_rows = triple['rank_rows']
    require(len(rank_rows)==2, 'rank witness shape')
    coefficients = []
    for witness in rank_rows:
        j = witness['motion']
        require(type(j) is int and 0<=j<15, 'rank witness motion')
        blocks = witness['blocks']
        require(all(type(v) is int for block in blocks for v in block), 'rank pattern indices')
        chosen = tuple(tuple(b) for b in blocks)
        mm = data['mappings'][j]
        sources = [pattern(w,[a for a,b in mm]) for w in triple['words']]
        targets = [pattern(w,[b for a,b in mm]) for w in triple['words']]
        require(chosen in sources+targets, 'nonexistent complete pattern')
        row = [int(a==chosen)-int(b==chosen) for a,b in zip(sources,targets)]
        require(row==witness['coefficients'] and all(type(x) is int for x in witness['coefficients']),
                'rank coefficients')
        coefficients.append(row)
    a,b = coefficients
    det = a[0]*(b[1]-b[2])-a[1]*(b[0]-b[2])+a[2]*(b[0]-b[1])
    require(det!=0 and type(triple['augmented_determinant']) is int
            and triple['augmented_determinant']==det, 'extremality determinant')
    eta_map = data['mappings'][2]
    aa = [pattern(w,[a for a,b in eta_map]) for w in triple['words']]
    bb = [pattern(w,[b for a,b in eta_map]) for w in triple['words']]
    matching = [list(p) for p in permutations(range(3)) if all(aa[i]==bb[p[i]] for i in range(3))]
    require(len(matching)==1 and matching[0]==triple['eta_unique_support_matching']
            and sorted(matching[0])==[0,1,2] and all(matching[0][i]!=i for i in range(3)),
            'unique three-cycle on the order-five local rotation')
    for i in range(3):
        five = i
        for _ in range(5):
            five = matching[0][five]
        require(five!=i, 'support order does not divide five')
    q = cert['one_word_denial']
    require(q['status']=='VERIFIED_NO_SINGLETON' and q['motions']==CORE, 'singleton denial scope')
    built = normalized_cnf(data,q)
    require(type(q['nv']) is int and type(q['clauses']) is int and q['nv']==built['nv']
            and q['clauses']==len(built['clauses']) and q['cnf_sha256']==built['cnf_sha256'], 'CNF identity')
    proof = check_rup(built['clauses'],q['proof'])
    deletion = cert['omit_one_motion']
    require([x['omitted'] for x in deletion]==CORE and all(type(x['omitted']) is int for x in deletion),
            'motion deletion indices')
    for item in deletion:
        word_checks(item['word'],data,5)
        ok,_ = full_law_domains([item['word']],[Q(1)],data['mappings'])
        require(set(CORE)-{item['omitted']}<=set(ok) and item['omitted'] not in ok, 'motion deletion witness')
    vertex = cert['omit_one_vertex']
    require([x['removed'] for x in vertex]==list(range(29)) and
            all(type(x['removed']) is int for x in vertex), 'vertex deletion indices')
    for item in vertex:
        local = restrict(data,[v for v in range(29) if v!=item['removed']])
        word_checks(item['word'],local,5)
        ok,_ = full_law_domains([item['word']],[Q(1)],local['mappings'])
        require(set(CORE)<=set(ok), 'vertex deletion singleton witness')
    ordinary = cert['ordinary_coloring']
    require(type(ordinary['k']) is int and ordinary['k']==3, 'ordinary color count')
    word_checks(ordinary['word'],data,3)
    cycle = ordinary['odd_cycle']
    require(isinstance(cycle,list) and len(cycle)>=3 and len(cycle)%2==1
            and len(set(cycle))==len(cycle) and all(type(v) is int and 0<=v<29 for v in cycle), 'odd cycle')
    ee = set(map(tuple,data['edges']))
    require(all(tuple(sorted((a,b))) in ee for a,b in zip(cycle,cycle[1:]+cycle[:1])), 'nonedge in odd cycle')
    six = cert['singleton_six_coloring']
    require(six['colors']==6 and type(six['colors']) is int and six['motions']==list(range(15)), 'six-color scope')
    word_checks(six['word'],data,6)
    ok,_ = full_law_domains([six['word']],[Q(1)],data['mappings'])
    require(ok==list(range(15)), 'six-color singleton is not invariant')
    return dict(status='PASS', vertices=29, actual_pairs=406, induced_edges=len(data['edges']),
        ordinary_chromatic_number=3, invariant_single_partition_colors=6,
        minimum_five_color_partition_support=2, full_local_domains_passed=passed,
        local_domain_sizes=[len(mm) for mm in data['mappings']],
        three_atom_extreme_law=True, extremality_determinant=det,
        three_atom_full_domains=three_passed, eta_unique_support_matching=matching[0],
        two_atom_hull_counterexample=True, order_five_support_lift_counterexample=True,
        six_motion_vertex_deletion_witnesses=29, six_motion_deletion_witnesses=6,
        negative_proof=proof, embedded_in_full_Y=full_data is not None,
        scope='The explicit 29-point induced subconfiguration and its own maximal domains. '
              'Vertex/motion criticality is relative to the six-motion singleton-five-color requirement. '
              'All15 here does not mean all15 on the original 10077-point Y. No minimum-size or HN claim.')


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    root = Path(__file__).resolve().parents[1]
    cert = read(root/'certificates/localized_motion_packet.json')
    print(json.dumps(check(cert),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
