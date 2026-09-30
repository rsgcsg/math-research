#!/usr/bin/env python3
"""Solver-free checker for the one-word exact G14 pair-orbit face witness."""
if not __debug__:
    raise SystemExit('refusing optimized mode: verification dependencies require assertions')
import argparse, gzip, hashlib, json, sys, copy
from collections import defaultdict, deque
from fractions import Fraction
from itertools import combinations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT/'certificates'
sys.path.insert(0, str(ROOT / 'research'))
from audit_full_law_preparation import reconstruct, canonical, unique_keys
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice

def read(path):
    raw = Path(path).read_bytes()
    return (json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw, object_pairs_hook=unique_keys), raw)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def d2(p, q, table, den):
    v = [a - b for a, b in zip(p, q)]
    return tuple((Fraction(x, 4 * den * den) for x in product_twice(v, conjugate_twice(v), table)))

def check_forest_rows(forest, nodes):
    """Require a simple spanning tree in each claimed orbit component."""
    forest_by_grade = defaultdict(list)
    for row in forest:
        forest_by_grade[row['grade']].append(row)
    stats = {}
    for grade, grade_nodes in nodes.items():
        rows = forest_by_grade[grade]
        parent = {p: p for p in grade_nodes}
        rank = {p: 0 for p in grade_nodes}
        seen_edges = set()

        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v
        for row in rows:
            source = tuple(row['source'])
            target = tuple(row['target'])
            if source not in parent or target not in parent or source == target:
                raise AssertionError(('forest endpoint/loop', grade, source, target))
            edge = (min(source, target), max(source, target))
            if edge in seen_edges:
                raise AssertionError(('duplicate forest row', grade, edge))
            seen_edges.add(edge)
            a = find(source)
            b = find(target)
            if a == b:
                raise AssertionError(('forest cycle', grade, edge))
            if rank[a] < rank[b]:
                a, b = (b, a)
            parent[b] = a
            if rank[a] == rank[b]:
                rank[a] += 1
        components = len({find(v) for v in grade_nodes})
        if components != 1:
            raise AssertionError(('forest disconnected', grade, components))
        if len(rows) != len(grade_nodes) - 1:
            raise AssertionError(('forest rank', grade, len(rows), len(grade_nodes)))
        stats[grade] = {'nodes': len(grade_nodes), 'edges': len(rows), 'components': components}
    if set(forest_by_grade) != set(nodes):
        raise AssertionError(('forest grade keys', sorted(forest_by_grade), sorted(nodes)))
    return stats

def check_quotient(data,nodes,word):
    parent=list(range(len(word)))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x
    for a,b in nodes['2']:
        parent[find(a)]=find(b)
    def edges(pairs):
        return {tuple(sorted((find(a),find(b)))) for a,b in pairs}
    unit=edges(data['edges']);extra=edges(nodes['1/sqrt3'])
    conflicts=unit|extra
    if any(a==b or word[a]==word[b] for a,b in conflicts):
        raise ValueError('quotient loop or invalid coloring')
    if not all(word[v]==word[find(v)] for v in range(len(word))):
        raise ValueError('word does not descend to quotient')
    classes={find(v) for v in range(len(word))}
    stats=dict(vertices=len(classes),unit_conflicts=len(unit),extra_conflicts=len(extra),
               overlap=len(unit&extra),conflict_edges=len(conflicts),loops=0,
               color_class_counts=[sum(word[v]==str(c) for v in classes) for c in range(5)])
    if stats!=dict(vertices=9577,unit_conflicts=48706,extra_conflicts=780,overlap=0,
                   conflict_edges=49486,loops=0,color_class_counts=[1994,1958,1872,1918,1835]):
        raise ValueError(('quotient statistics changed',stats))
    return stats

def check_domain_mismatches(data,word):
    witnesses=[]
    for j,pairs in enumerate(data['mappings']):
        mapping=dict(pairs)
        for a,b in combinations(sorted(mapping),2):
            x,y=sorted((mapping[a],mapping[b]))
            left=word[a]==word[b];right=word[x]==word[y]
            if left!=right:
                witnesses.append(dict(motion=j,name=data['motions'][j],source=[a,b],image=[x,y],
                                      source_equal=left,image_equal=right))
                break
        else:
            raise ValueError(('expected full-domain mismatch was absent',j))
    return witnesses

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',action='store_true')
    args=parser.parse_args()
    data, summary = reconstruct(ROOT)
    semantic = summary['semantic_sha256']
    if not semantic == '90674956a11ac0b6627fb12c6bc108f1c4ddf2ca037c39a9271cf6ba896c0957':
        raise AssertionError('checker assertion failed')
    basis, braw = read(EXP / 'g14_pair_orbit_basis.json.gz')
    basis_sha = basis.pop('basis_sha256')
    if not basis_sha == hashlib.sha256(canonical(basis)).hexdigest():
        raise AssertionError('checker assertion failed')
    basis['basis_sha256'] = basis_sha
    if not (basis['geometry_semantic_sha256'] == semantic and basis['motion_names'] == data['motions']):
        raise AssertionError('checker assertion failed')
    g14, graw = read(EXP / 'g14_port_or_certificate.json')
    # The search used the original G14 certificate before an explicit semantic
    # metadata field was added for publication. Reproduce those exact old bytes;
    # the geometry itself and every mathematical field are unchanged.
    if g14['actual_Y_embedding']['semantic_sha256'] != semantic:
        raise ValueError('published G14 geometry semantic binding')
    legacy=copy.deepcopy(g14)
    del legacy['actual_Y_embedding']['semantic_sha256']
    legacy_raw=(json.dumps(legacy,sort_keys=True,indent=2)+'\n').encode()
    if not basis['source_g14_certificate_sha256'] == sha(legacy_raw):
        raise AssertionError('checker assertion failed')
    result, rraw = read(EXP / 'g14_pair_orbit_word.json')
    if not (result['schema'] == 'g14-orbit-extreme-face-v1' and result['status'] == 'SAT_WITNESS'):
        raise AssertionError('checker assertion failed')
    if not (result['geometry_semantic_sha256'] == semantic and result['basis_sha256'] == basis_sha):
        raise AssertionError('checker assertion failed')
    if not (result['p_orbit_pairs'] == 1860 and result['q_orbit_pairs'] == 780):
        raise AssertionError('checker assertion failed')
    word = result['word']
    if not (len(word) == len(data['points']) and set(word) <= set('01234')):
        raise AssertionError('checker assertion failed')
    if not sha(word.encode()) == result['word_sha256']:
        raise AssertionError('checker assertion failed')
    if not (len(data['edges']) == 49858 and result['actual_edge_checks'] == 49858):
        raise AssertionError('checker assertion failed')
    if not all((word[a] != word[b] for a, b in data['edges'])):
        raise AssertionError('checker assertion failed')
    nodes = {g: {tuple(p) for p in pp} for g, pp in basis['orbit_nodes_by_grade'].items()}
    if not {g: len(v) for g, v in nodes.items()} == {'1/sqrt3': 1860, '2': 780}:
        raise AssertionError('checker assertion failed')
    for g, pairs in basis['orbit_nodes_by_grade'].items():
        if len(pairs)!=len(nodes[g]) or not all(0<=a<b<len(word) for a,b in pairs):
            raise ValueError('invalid or duplicate pair indices')
    map_events = g14['actual_Y_embedding']['vertex_indices']
    seeds = defaultdict(set)
    for e in g14['independent_check']['virtual_pairs']:
        seeds[e['distance']].add(tuple(sorted((map_events[e['u']], map_events[e['v']]))))
    if not {g: len(p) for g, p in seeds.items()} == {'1/sqrt3': 27, '2': 5}:
        raise AssertionError('checker assertion failed')
    if not all((seeds[g] <= nodes[g] for g in seeds)):
        raise AssertionError('checker assertion failed')
    tab = multiplication_twice()
    den = data['denominator']
    target = {'1/sqrt3': (Fraction(1, 3),) + (Fraction(0),) * 31, '2': (Fraction(4),) + (Fraction(0),) * 31}
    for g, ps in nodes.items():
        for a, b in ps:
            if not d2(data['points'][a], data['points'][b], tab, den) == target[g]:
                raise AssertionError('checker assertion failed')
    fwd = []
    rev = []
    for pairs in data['mappings']:
        f = dict(pairs)
        r = {v: k for k, v in f.items()}
        if not len(f) == len(r):
            raise AssertionError('checker assertion failed')
        fwd.append(f)
        rev.append(r)
    comps = {}
    transitions = 0
    for g, ps in nodes.items():
        adj = {p: set() for p in ps}
        for a, b in ps:
            for j in range(15):
                f, r = (fwd[j], rev[j])
                if a in f and b in f:
                    t = tuple(sorted((f[a], f[b])))
                    if not t in ps:
                        raise AssertionError('checker assertion failed')
                    adj[a, b].add(t)
                    adj[t].add((a, b))
                    transitions += 1
                if a in r and b in r:
                    t = tuple(sorted((r[a], r[b])))
                    if not t in ps:
                        raise AssertionError('checker assertion failed')
                    adj[a, b].add(t)
                    adj[t].add((a, b))
                    transitions += 1
        visited = set()
        parts = []
        while len(visited) < len(ps):
            seed = min(ps - visited)
            todo = [seed]
            visited.add(seed)
            part = []
            while todo:
                v = todo.pop()
                part.append(v)
                for t in adj[v]:
                    if t not in visited:
                        visited.add(t)
                        todo.append(t)
            parts.append(part)
        if not (len(parts) == 1 and len(set(parts[0]) & seeds[g]) == len(seeds[g])):
            raise AssertionError('checker assertion failed')
        comps[g] = dict(nodes=len(ps), components=len(parts), seed_nodes=len(seeds[g]))
    n = len(data['points'])
    k = 5
    clauses = []

    def col(v, c):
        return v * k + c + 1
    for v in range(n):
        vv = [col(v, c) for c in range(k)]
        clauses.append(vv)
        clauses.extend([[-a, -b] for a, b in combinations(vv, 2)])
    for a, b in data['edges']:
        clauses.extend([[-col(a, c), -col(b, c)] for c in range(k)])
    for a, b in basis['orbit_nodes_by_grade']['1/sqrt3']:
        for c in range(k):
            clauses.append([-col(a, c), -col(b, c)])
    for a, b in basis['orbit_nodes_by_grade']['2']:
        for c in range(k):
            clauses.extend([[-col(a, c), col(b, c)], [-col(b, c), col(a, c)]])
    dimacs = ('p cnf %d %d\n' % (n * k, len(clauses)) + ''.join((' '.join(map(str, c)) + ' 0\n' for c in clauses))).encode()
    if not (len(clauses) == result['clauses'] and sha(dimacs) == result['cnf_sha256']):
        raise AssertionError('checker assertion failed')
    p_same = sum((word[a] == word[b] for a, b in nodes['1/sqrt3']))
    q_same = sum((word[a] == word[b] for a, b in nodes['2']))
    if not (p_same, q_same) == (0, 780) == (result['exact_counts']['d2_1_3_same'], result['exact_counts']['d2_4_same']):
        raise AssertionError('checker assertion failed')
    forest = basis['forest_edges']
    if not len(forest) == 2638:
        raise AssertionError('checker assertion failed')
    counts = defaultdict(int)
    for row in forest:
        j = row['motion']
        a, b = row['source']
        x, y = row['target']
        mapping = fwd[j]
        if not tuple(sorted((mapping[a], mapping[b]))) == tuple(row['target']):
            raise AssertionError('checker assertion failed')
        g = row['grade']
        if not (tuple(sorted((a, b))) in nodes[g] and tuple(sorted((x, y))) in nodes[g]):
            raise AssertionError('checker assertion failed')
        if not int(word[a] == word[b]) - int(word[x] == word[y]) == 0:
            raise AssertionError('checker assertion failed')
        counts[g] += 1
    if not dict(counts) == {'1/sqrt3': 1859, '2': 779}:
        raise AssertionError('checker assertion failed')
    check_forest_rows(forest, nodes)
    report = dict(status='PASS_SOLVER_FREE_G14_PAIR_ORBIT_LAW', geometry_semantic_sha256=semantic, basis_sha256=basis_sha, source_g14_certificate_sha256=sha(graw), word_sha256=result['word_sha256'], vertices=n, actual_Y_edges=len(data['edges']), edge_checks=len(data['edges']), exact_squared_distance_basis='32-coefficient Q(eta,sqrt(3),sqrt(5),sqrt(11),i); recomputed with checker-side doubled multiplication and conjugation', orbit_components=comps, actual_map_transitions_checked=transitions, forest_rows=dict(counts), forest_total=len(forest), pair_event_counts={'d2_1_3_same': p_same, 'd2_4_same': q_same}, forest_balance='Every source-target equality-event row is exactly 0 on this one coloring; the full 1,860-node d2=1/3 orbit has all events false and the 780-node d2=4 orbit has all events true.', independently_rebuilt_cnf_sha256=sha(dimacs), clauses=len(clauses), scope='One-atom law for only these two selected pair-event motion-orbit components. Not a joint law balancing complete patterns on any of the original 15 domains and not an HN bound.')
    report['source_g14_legacy_sha256']=sha(legacy_raw)
    report['source_g14_rebinding']='Legacy bytes reproduced by removing only actual_Y_embedding.semantic_sha256 from the independently bound published certificate and serializing sorted/indented JSON.'
    report['quotient']=check_quotient(data, nodes, word)
    report['full_domain_mismatch_witnesses']=check_domain_mismatches(data,word)
    out = EXP / 'g14_pair_orbit_verification.json'
    if args.write_certificate:
        out.write_text(json.dumps(report,indent=2)+'\n')
    elif canonical(read(out)[0])!=canonical(report):
        raise ValueError('saved pair-orbit receipt differs from independent replay')
    print(json.dumps(report, indent=2))
if __name__ == '__main__':
    main()
