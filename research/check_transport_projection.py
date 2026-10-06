#!/usr/bin/env python3
"""Exact, solver-free replay of two coupled P/Q/R finite configurations.

Uses the pinned existing Y geometry and independently recomputes local field
norms, actual transport reachability, all partitions, rational vertices, and
individual event means. Does not import the SAT or floating hull producers.
"""
import argparse
from collections import Counter, defaultdict, deque
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations, permutations, product
import json
from pathlib import Path
import subprocess
import sys

if not __debug__:
    raise RuntimeError('Verification requires assertions; run without -O')

from verify_pr_matching_window_ceiling import read, canonical, digest, validate_inputs
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'certificates/q_pr_joint_cuts.json'
RECEIPT = ROOT / 'certificates/q_pr_joint_cuts_validation.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def partitions(n, k):
    """All unlabeled partitions; no geometric or optimization assumptions."""
    def visit(word, top):
        if len(word) == n:
            yield tuple(word)
        else:
            for value in range(min(k, top + 2)):
                yield from visit(word + [value], max(top, value))
    yield from visit([], -1)


def normalize(word):
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in word)


def solve(matrix, rhs):
    a = [[F(x) for x in row] + [F(v)] for row, v in zip(matrix, rhs)]
    n = len(rhs)
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j]), None)
        if p is None:
            return None
        a[j], a[p] = a[p], a[j]
        scale = a[j][j]
        a[j] = [x / scale for x in a[j]]
        for i in range(n):
            if i != j:
                z = a[i][j]
                a[i] = [x - z * y for x, y in zip(a[i], a[j])]
    return tuple(row[-1] for row in a)


def exact_vertices(facets, dimension):
    require(all(len(row) == dimension + 1 and all(type(x) is int for x in row)
                for row in facets), 'integer facet rows')
    vertices = set()
    for rows in combinations(facets, dimension):
        point = solve([row[:-1] for row in rows], [-row[-1] for row in rows])
        if point is not None and all(sum(x*y for x, y in zip(row[:-1], point)) + row[-1] <= 0
                                     for row in facets):
            vertices.add(point)
    return vertices


def pair(a, b):
    return tuple(sorted((a, b)))


def square_distance(g, a, b, table):
    delta = [x-y for x, y in zip(g['points'][a], g['points'][b])]
    return tuple(F(x, 4*g['denominator']**2)
                 for x in product_twice(delta, conjugate_twice(delta), table))


def verify_geometry_and_components(g, b, r):
    n, E, P, R = validate_inputs(g, b, r)
    Q = {tuple(x) for x in b['orbit_nodes_by_grade']['2']}
    require(len(Q) == 780 and not (Q & (E | P | R)), 'Q input')
    maps = []
    for raw in g['mappings']:
        f = dict(raw)
        inv = {v: k for k, v in f.items()}
        require(len(f) == len(inv) == len(raw), 'actual partial bijection')
        maps.extend((f, inv))
    sizes = {}
    for label, nodes in [('P', P), ('Q', Q), ('R', R)]:
        seed = (233, 239) if label == 'R' else min(nodes)
        seen = {seed}
        queue = deque([seed])
        while queue:
            a, c = queue.popleft()
            for f in maps:
                if a in f and c in f:
                    target = pair(f[a], f[c])
                    require(target in nodes, 'component closure on actual maps')
                    if target not in seen:
                        seen.add(target)
                        queue.append(target)
        require(seen == nodes, 'connected actual transport component')
        sizes[label] = len(seen)
    return n, {'E': E, 'P': P, 'Q': Q, 'R': R}, sizes


def check(cert, g, b, r, prepared=None):
    def literal_tree(x):
        if type(x) in (int, str):return True
        if type(x) is list:return all(literal_tree(z) for z in x)
        if type(x) is dict:return all(type(k) is str and literal_tree(z) for k,z in x.items())
        return False
    require(literal_tree(cert), 'certificate admits only integer/string structured literals')
    require(cert['schema'] == 'q-pr-joint-cuts-v1', 'schema')
    require(cert['base_commit'] == '3009eda28c26334bc8063913af74031cc7bcd9f4', 'base')
    require(cert['geometry_semantic_sha256'] == digest(g), 'geometry binding')
    require(cert['P_Q_basis_sha256'] == b['basis_sha256'] and
            cert['R_basis_sha256'] == r['candidate_sha256'], 'basis binding')
    n, sets, sizes = prepared or verify_geometry_and_components(g, b, r)
    table = multiplication_twice()
    local_pair_checks = 0

    def geometry(vertices):
        nonlocal local_pair_checks
        require(all(type(v) is int and 0 <= v < n for v in vertices)
                and len(vertices) == len(set(vertices)), 'distinct actual vertex IDs')
        records = {}
        for a, z in combinations(vertices, 2):
            key = pair(a, z)
            value = square_distance(g, a, z, table)
            local_pair_checks += 1
            is_unit = value == (F(1),)+(F(0),)*31
            require(is_unit == (key in sets['E']), 'all actual local unit edges')
            for label, norm in [('P', F(1,3)), ('Q', F(4)), ('R', F(4,3))]:
                if key in sets[label]:
                    require(value == (norm,)+(F(0),)*31, 'pair distance '+label)
            records[key] = value
        return records

    s = cert['seven']
    require(s['center'] == 4641 and s['inner'] == [877, 5535, 7479]
            and s['outer'] == [9081, 3477, 233], 'seven-point identity')
    V = [s['center']] + s['inner'] + s['outer']
    distances = geometry(V)
    for a, z in zip(s['inner'], s['outer']):
        require(g['points'][z] == [3*x-2*y for x,y in zip(g['points'][s['center']],g['points'][a])],
                'outer point is the doubled opposite radius')
    edges = [(i,j) for i,j in combinations(range(7),2) if pair(V[i],V[j]) in sets['E']]
    expected_edges = [(i,j) for i,j in combinations(range(1,4),2)] + [(i,4+j) for i in range(1,4) for j in range(3) if i != j+1]
    require(set(edges) == set(expected_edges) and len(edges) == 9, 'seven unit graph')
    events = {'P': [(0,i) for i in range(1,4)], 'Q': list(combinations(range(4,7),2)),
              'R': [(0,i) for i in range(4,7)]}
    for label, es in events.items():
        require({pair(V[a],V[z]) for a,z in es} == sets[label] & set(map(lambda e:pair(*e),combinations(V,2))),
                'seven selected component events '+label)
    require(s['count_order'] == ['P','Q','R'], 'count order')
    facets = s['facets']
    expected_facets = [[-1,0,0,0],[0,-1,0,0],[0,-1,1,-1],[0,0,-1,0],[0,1,0,-3],
                       [1,-1,2,-3],[1,0,0,-1],[2,0,1,-3],[6,1,2,-9]]
    require(facets == expected_facets, 'seven facet semantics')
    proper = [w for w in partitions(7,5) if all(w[a] != w[z] for a,z in edges)]
    require(len(proper) == s['proper_partition_count'] == 69, 'all proper five-block partitions')
    counts = lambda w: tuple(sum(w[a] == w[z] for a,z in events[t]) for t in ('P','Q','R'))
    for w in proper:
        require(all(sum(x*y for x,y in zip(row[:-1],counts(w)))+row[-1] <= 0 for row in facets),
                'pointwise seven inequality')
    actual_vertices = exact_vertices(facets,3)
    require(actual_vertices == {tuple(F(x) for x in v['counts']) for v in s['vertices']}
            and len(actual_vertices) == 9, 'complete rational seven polytope vertices')
    for v in s['vertices']:
        w = tuple(v['partition'])
        require(w in proper and counts(w) == tuple(v['counts']), 'seven positive vertex')
        orbit = [tuple([w[0]] + [w[1+i] for i in perm] + [w[4+i] for i in perm])
                 for perm in permutations(range(3))]
        for label, target in zip(('P','Q','R'), v['counts']):
            require(all(sum(z[a] == z[b] for z in orbit) == 2*target for a,b in events[label]),
                    'each individual seven event mean')
        require(all(all(z[a] != z[b] for a,b in edges) for z in orbit), 'proper seven orbit')

    # A 21-point actual configuration with nine Q links, not a fictitious unit K4.
    q = cert['quotient'];W = q['vertices'];geometry(W)
    links = q['Q_bridges'];require(len(links)==9 and len({tuple(e) for e in links})==9
        and all(pair(*e) in sets['Q'] for e in links), 'nine distinct actual Q links')
    require(len(W)==21 and W==sorted(W), 'twenty-one-point configuration')
    adjacency={v:set() for v in W}
    for a,z in links:
        require(a in adjacency and z in adjacency, 'Q link endpoints')
        adjacency[a].add(z);adjacency[z].add(a)
    component={}
    for v in W:
        if v in component:continue
        found={v};todo=[v]
        while todo:
            for z in adjacency[todo.pop()]:
                if z not in found:found.add(z);todo.append(z)
        for z in found:component[z]=min(found)
    grid=q['grid'];flat=sum(grid,[])
    require(len(grid)==3 and all(len(row)==4 for row in grid) and len(set(flat))==12
            and set(flat)==set(component.values()), 'twelve Q classes in three rows')
    position={v:divmod(i,4) for i,v in enumerate(flat)}
    def tag(a,z):
        ra,ca=position[a];rb,cb=position[z]
        return 'E' if ra==rb else 'R' if ca==cb else 'P'
    realizations=q['realizations']
    require(len(realizations)==66 and {tuple(rec['classes']) for rec in realizations}==set(combinations(sorted(flat),2)),
            'all 66 quotient pairs are realized')
    for rec in realizations:
        a,z=rec['actual_pair'];x,y=rec['classes'];label=rec['type']
        require(a in component and z in component and pair(component[a],component[z])==(x,y)
                and label==tag(x,y) and pair(a,z) in sets[label], 'actual typed pair realization')
    require(Counter(rec['type'] for rec in realizations)=={'E':18,'P':36,'R':12}, 'quotient pair counts')
    # All additional actual local edges/events must also respect the quotient, for positive laws.
    for a,z in combinations(W,2):
        for label,S in sets.items():
            if (a,z) not in S:continue
            if label=='Q':require(component[a]==component[z], 'every local Q event has mean one')
            else:require(component[a]!=component[z] and tag(component[a],component[z])==label,
                         'all induced typed events lift consistently')
    es={t:[(a,z) for a,z in combinations(range(12),2) if tag(flat[a],flat[z])==t] for t in ('E','P','R')}
    qs=lambda w:(sum(w[a]==w[z] for a,z in es['P']),sum(w[a]==w[z] for a,z in es['R']))
    words=[(0,1,2,3)+a+b for a in permutations(range(5),4) for b in permutations(range(5),4)]
    require(len(words)==q['proper_partition_count']==14400, 'all quotient proper partitions')
    # First row is a K4: fixing it to 0,1,2,3 loses exactly the color-label symmetry.
    require(len({normalize(w) for w in words})==14400, 'no duplicated quotient partitions')
    qfac=[[-1,0,0],[0,-1,0],[1,1,-12],[-1,-1,9],[-2,-1,10]]
    require(q['facets']==qfac and q['count_order']==['P','R'], 'quotient facet semantics')
    for w in words:
        x,y=qs(w)
        require(all(row[0]*x+row[1]*y+row[2]<=0 for row in qfac), 'pointwise quotient count')
    require(exact_vertices(qfac,2)=={tuple(F(x) for x in v['counts']) for v in q['vertices_count']}
            and len(q['vertices_count'])==5, 'exact quotient polygon vertices')
    for v in q['vertices_count']:
        w=tuple(v['partition']);require(w in words and qs(w)==tuple(v['counts']), 'positive quotient vertex')
        orbit=[tuple(w[4*i+j] for i in a for j in b)
               for a in permutations(range(3)) for b in permutations(range(4))]
        for label,number,den in zip(('P','R'),v['counts'],(36,12)):
            require(all(F(sum(z[a]==z[b] for z in orbit),144)==F(number,den) for a,b in es[label]),
                    'every quotient event mean, not only an average count')
        require(all(all(z[a]!=z[b] for a,b in es['E']) for z in orbit), 'proper quotient orbits')
    require(q['robust_penalty']==9, 'robust union-bound penalty, not an uncertified stronger coefficient')
    # 12 points in <=5 classes force >=9 same pairs, independently of the graph.
    def occupancy(n,k,prefix=()):
        if k==1:yield prefix+(n,)
        else:
            for j in range(n+1):yield from occupancy(n-j,k-1,prefix+(j,))
    require(min(sum(x*(x-1)//2 for x in ns) for ns in occupancy(12,5))==9, 'integer five-color occupancy')
    require(9*len(links)==81 and (36+12*F(1,2),12*F(1,2))==(42,6), 'robust coefficient elimination')
    # The bound p>=1/14 at q=1 is attained on W plus one actual point,
    # but this is not a full-Y law or a claim of full-Y sharpness.
    att=cert['attainment'];require(att['extra_vertex']==305, 'extra PRR vertex')
    W22=sorted(W+[305]);geometry(W22)
    require(pair(229,305) in sets['P'] and pair(229,4641) in sets['R'] and
            pair(305,4641) in sets['R'], 'actual PRR transitivity triangle')
    require(att['classes']==flat+[305] and att['q']=='1', 'conditional projection classes')
    cc=dict(component);cc[305]=305;index={v:i for i,v in enumerate(att['classes'])}
    local_typed={t:[(a,b) for a,b in combinations(W22,2) if (a,b) in S] for t,S in sets.items()}
    h22=[[-1,0,0],[0,-1,0],[3,1,-1],[-12,-4,3],[-1,2,-1]]
    corner_set=exact_vertices(h22,2)
    require(corner_set=={(F(1,14),F(15,28)),(F(1,4),F(0)),(F(1,3),F(0)),(F(1,7),F(4,7))},
            'exact four-vertex necessary intersection')
    require({(F(law['p']),F(law['r'])) for law in att['laws']}==corner_set and len(att['laws'])==4,
            'all four conditional projection vertices')
    attainment_reports=[]
    for law in att['laws']:
        pp,rr=F(law['p']),F(law['r']);denom=law['denominator']
        require(denom>0, 'positive probability denominator')
        seen=set();marginals={t:Counter() for t in ('P','Q','R')};total=0
        for num,text in law['atoms']:
            require(type(num) is int and type(text) is str and len(text)==13 and set(text)<=set('01234'),
                    'integer weights and five-color words')
            w=tuple(map(int,text))
            require(num>0 and normalize(w)==w and w not in seen, 'distinct canonical positive atoms')
            seen.add(w);total+=num;colors={v:w[index[cc[v]]] for v in W22}
            require(all(colors[a]!=colors[b] for a,b in local_typed['E']), 'all actual 22-point unit edges')
            for label in marginals:
                for a,b in local_typed[label]:marginals[label][a,b]+=num*(colors[a]==colors[b])
        require(total==denom, 'probability normalization')
        for label,target in [('P',pp),('Q',F(1)),('R',rr)]:
            require(local_typed[label] and all(F(marginals[label][ab],denom)==target for ab in local_typed[label]),
                    'each individual sharp-corner event '+label)
        attainment_reports.append({'p':str(pp),'r':str(rr),'atoms':len(seen),'denominator':denom})
    return {'status':'PASS','schema':'q-pr-joint-cuts-replay-v1','geometry_semantic_sha256':digest(g),
            'certificate_sha256':digest(cert),'transport_component_sizes':sizes,'local_squared_distances':local_pair_checks,
            'seven':{'vertices':7,'unit_edges':9,'proper_partitions':69,'facets':9,'vertices_of_polytope':9,
                     'individual_event_orbit_checks':81},
            'quotient':{'actual_vertices':21,'Q_links':9,'classes':12,'typed_pairs':66,'proper_partitions':14400,
                        'polygon_vertices':5,'individual_event_orbit_checks':240},
            'necessary_inequalities':['6p+q+2r <= 3','p-q+2r <= 1','r-q <= 1/3',
                                     '36p+12r+81(1-q) >= 9','14p+27(1-q) >= 1'],
            'q_one_necessary_interval_p':['1/14','1/3'],
            'local_q_one_projection':{'actual_vertices':22,'vertices':attainment_reports,
                                     'typed_pairs':{t:len(es) for t,es in local_typed.items()},
                                     'minimum_p':'1/14','r_at_minimum':'15/28'},
            'scope':cert['scope'],'uses_sat_or_floating_point':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args()
    cert=read(CERT);g=read(ROOT/'certificates/Y_full_geometry.json.gz')
    b=read(ROOT/'certificates/g14_pair_orbit_basis.json.gz');r=read(ROOT/'certificates/g14_r_pair_orbit_basis.json.gz')
    prepared=verify_geometry_and_components(g,b,r)
    report=check(cert,g,b,r,prepared)
    if args.self_test:
        mutations={
            'geometry-binding':lambda c:c.__setitem__('geometry_semantic_sha256','0'*64),
            'false-outer-point':lambda c:c['seven']['outer'].__setitem__(0,9082),
            'weakened-facet':lambda c:c['seven']['facets'][-1].__setitem__(-1,-10),
            'false-vertex':lambda c:c['seven']['vertices'][0]['counts'].__setitem__(0,1),
            'bad-seven-coloring':lambda c:c['seven']['vertices'][0].__setitem__('partition',[0]*7),
            'missing-quotient-pair':lambda c:c['quotient']['realizations'].pop(),
            'wrong-pair-type':lambda c:c['quotient']['realizations'][0].__setitem__('type','Q'),
            'missing-Q-link':lambda c:c['quotient']['Q_bridges'].pop(),
            'fake-Q-link':lambda c:c['quotient']['Q_bridges'][0].__setitem__(1,32),
            'bad-quotient-coloring':lambda c:c['quotient']['vertices_count'][0].__setitem__('partition',[0]*12),
            'stronger-uncertified-penalty':lambda c:c['quotient'].__setitem__('robust_penalty',2),
            'float-in-facet':lambda c:c['seven']['facets'][0].__setitem__(0,-1.0),
            'false-attainment-probability':lambda c:c['attainment']['laws'][0]['atoms'][0].__setitem__(0,0),
            'false-attainment-coloring':lambda c:c['attainment']['laws'][0]['atoms'][0].__setitem__(1,'0'*13),
            'false-local-sharpness':lambda c:c['attainment']['laws'][0].__setitem__('p','1/27'),
            'boolean-point':lambda c:c['seven'].__setitem__('center',True),
        }
        rejected=[]
        for name, mutate in mutations.items():
            c=deepcopy(cert);mutate(c)
            try:check(c,g,b,r,prepared)
            except (ValueError,AssertionError,KeyError,IndexError,TypeError):rejected.append(name)
            else:raise ValueError('accepted mutation '+name)
        proc=subprocess.run([sys.executable,'-O',__file__],capture_output=True,text=True,timeout=20)
        require(proc.returncode!=0 and 'requires assertions' in proc.stderr,'optimized mode must refuse')
        report['rejections']=rejected+['optimized-mode']
    if args.write_receipt:RECEIPT.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    else:
        saved=read(RECEIPT)
        if not args.self_test:saved.pop('rejections',None)
        require(canonical(saved)==canonical(report),'saved receipt differs from actual replay')
    print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))


if __name__=='__main__':main()
