"""Exact geometric premises and optional full-Y seven-domain positive law.

No solver, search encoder, floating point arithmetic or unpublished checker
is imported. The generic normal-form theorem is proved in the companion
text; this program verifies its concrete finite premises and witnesses.
"""
from collections import Counter
from copy import deepcopy
from itertools import permutations, product
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import lzma
import random
import subprocess
import sys
from audit_full_law_preparation import reconstruct
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice

BASE = '09926d59b176c1f649aa30f7ec397fb8fa9ef9fa'
TARGET = [2, 5, 6, 9, 11, 13, 14]


def require(test, message):
    if not test:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            require(key not in obj, 'duplicate JSON key')
            obj[key] = value
        return obj
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    elif raw[:6] == b'\xfd7zXZ\x00':
        raw = lzma.decompress(raw)
    return json.loads(raw, object_pairs_hook=unique)


def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def inverse(p):
    return tuple(p.index(i) for i in range(len(p)))


def normalizing_gauges(sigma, palettes):
    require(isinstance(sigma, (list, tuple)) and len(sigma)>0, 'support shape')
    m = len(sigma)
    require(all(type(x) is int for x in sigma) and sorted(sigma)==list(range(m)),
            'support permutation')
    require(len(palettes)==m and len(palettes[0])>0, 'palette count')
    k = len(palettes[0])
    require(all(len(p)==k and all(type(x) is int for x in p)
                and sorted(p)==list(range(k)) for p in palettes), 'palette permutation')
    answer = [None]*m
    for a in range(m):
        if answer[a] is not None:
            continue
        answer[a] = tuple(range(k))
        i = a
        while True:
            j = sigma[i]
            value = compose(answer[i], inverse(tuple(palettes[i])))
            if answer[j] is not None:
                require(answer[j]==value, 'nontrivial holonomy')
                break
            answer[j] = value
            i = j
    return answer


def blocks(word, ids):
    result = {}
    for pos, i in enumerate(ids):
        result.setdefault(word[i], []).append(pos)
    return tuple(sorted(tuple(x) for x in result.values()))


def geometry_check(c, data):
    require(c['schema']=='anchored-eta-normalization-v1' and c['base_commit']==BASE,
            'geometry provenance')
    require(c['point_sha256']==data['geometry']['point_sha256'], 'point binding')
    require(type(c['denominator']) is int and c['denominator']==data['denominator']==480,
            'coordinate denominator')
    require(type(c['rotation_order']) is int and c['rotation_order']==5
            and type(c['color_count']) is int and c['color_count']==5, 'theorem parameters')
    ids = c['closed_Y_indices']
    require(len(ids)==36 and all(type(i) is int and 0<=i<len(data['points']) for i in ids)
            and ids==sorted(set(ids)), 'closed indices')
    pts = c['closed_coordinates']
    require(len(pts)==36 and all(len(p)==32 and all(type(x) is int for x in p) for p in pts)
            and pts==[data['points'][i] for i in ids], 'actual closed coordinates')
    anchor = c['origin_Y_index']
    require(type(anchor) is int and anchor==4641 and anchor in ids
            and data['points'][anchor]==[0]*32, 'fixed origin')
    perm = c['eta_on_closed']
    require(len(perm)==36 and all(type(i) is int for i in perm)
            and sorted(perm)==list(range(36)), 'closed rotation permutation')
    table = multiplication_twice()
    eta = [0]*32
    eta[16] = 1
    for j, p in enumerate(pts):
        require(product_twice(p, eta, table)==[2*x for x in pts[perm[j]]],
                'actual eta image')
        q = j
        for _ in range(5):
            q = perm[q]
        require(q==j, 'order-five closed orbit')
    require(perm[ids.index(anchor)]==ids.index(anchor) and any(perm[j]!=j for j in range(36)),
            'order and anchor')
    spindle = c['spindle_Y_indices']
    require(spindle==[70,545,547,5805,497,503,3200], 'spindle binding')
    require(set(spindle)<=set(ids), 'spindle not closed')
    expected = [[0,1],[0,2],[0,4],[0,5],[1,2],[1,3],[2,3],[3,6],[4,5],[4,6],[5,6]]
    require(c['spindle_edges']==expected and all(type(v) is int for e in c['spindle_edges'] for v in e),
            'spindle edges')
    for a,b in expected:
        delta = [x-y for x,y in zip(data['points'][spindle[a]],data['points'][spindle[b]])]
        require(product_twice(delta,conjugate_twice(delta),table)==[4*480*480]+[0]*31,
                'nonunit spindle edge')
    bad = sum(all(w[a]!=w[b] for a,b in expected) for w in product(range(3),repeat=7))
    require(bad==0, 'three-color counterexample')
    w = c['spindle_four_colors']
    require(len(w)==7 and all(type(x) is int and 0<=x<4 for x in w)
            and all(w[a]!=w[b] for a,b in expected), 'four-color witness')
    return dict(closed_points=36, listed_unit_edges=11, rejected_three_color_assignments=2187)


def word_check(c, data, summary):
    require(c['schema']=='eta-gamma-two-word-law-v1' and c['base_commit']==BASE,
            'law provenance')
    require(c['input_semantic_sha256']==summary['semantic_sha256'], 'law geometry')
    require(c['motions']==TARGET and all(type(j) is int for j in c['motions']), 'motion scope')
    words = c['words']
    require(len(words)==2 and c['weights']==['1/2','1/2'], 'two-word weights')
    for w in words:
        require(isinstance(w,str) and len(w)==len(data['points']) and set(w)<=set('01234'),
                'word alphabet/length')
        require(all(w[a]!=w[b] for a,b in data['edges']), 'improper full-Y word')
    require(blocks(words[0],range(len(words[0])))!=blocks(words[1],range(len(words[1]))),
            'duplicate full partition')
    passed = []
    for j,mm in enumerate(data['mappings']):
        left = Counter(blocks(w,[a for a,b in mm]) for w in words)
        right = Counter(blocks(w,[b for a,b in mm]) for w in words)
        if left==right:
            passed.append(j)
    require(passed==TARGET, 'missing law or stale reported scope')
    require(all(w[a]==w[b] for w in words for a,b in data['mappings'][2]),
            'eta identity normal form')
    return dict(proper_edge_checks=2*len(data['edges']), complete_domains_passed=passed,
                complete_domain_sizes=[len(data['mappings'][j]) for j in passed],
                all_fifteen_domains_passed=False)


def algebra_tests():
    count = 0
    for p in permutations(range(5)):
        power = tuple(range(5))
        for _ in range(5):
            power = compose(p,power)
        if any(p[i]==i for i in range(5)):
            require([i for i in range(5) if power[i]==i]==[i for i in range(5) if p[i]==i],
                    'anchored fifth power')
            if sum(power[i]==i for i in range(5))>=4:
                require(p==tuple(range(5)), 'nontrivial allowed holonomy')
            count += 1
    rng = random.Random(20260928)
    gauge_cases = 0
    for m in [1,2,3,4,5,7,8,11,15,31]:
        for _ in range(12):
            sigma = list(range(m)); rng.shuffle(sigma)
            original = []
            for i in range(m):
                p = list(range(5)); rng.shuffle(p); original.append(tuple(p))
            pi = [compose(inverse(original[sigma[i]]),original[i]) for i in range(m)]
            q = normalizing_gauges(sigma,pi)
            require(all(compose(compose(q[sigma[i]],pi[i]),inverse(q[i]))==tuple(range(5))
                        for i in range(m)), 'gauge equation')
            gauge_cases += 1
    for sigma, palettes in [([0],[[1,2,3,4,0]]),([0],[[1,2,0,3,4]]),([0],[[1,0,2,3,4]])]:
        try:
            normalizing_gauges(sigma,palettes)
        except ValueError:
            pass
        else:
            raise ValueError('accepted nontrivial holonomy')
    return dict(anchored_S5_permutations=count, gauge_cases=gauge_cases,
                nontrivial_holonomies_rejected=3)


def mutations(gc, wc, data, summary):
    gs = {
      'origin': lambda d:d.__setitem__('origin_Y_index',0),
      'coordinate': lambda d:d['closed_coordinates'][0].__setitem__(0,d['closed_coordinates'][0][0]+1),
      'eta_image': lambda d:d['eta_on_closed'].__setitem__(0,0),
      'order': lambda d:d.__setitem__('rotation_order',10),
      'spindle_edge': lambda d:d['spindle_edges'].pop(),
      'four_colors': lambda d:d.__setitem__('spindle_four_colors',[0]*7),
      'boolean_denominator': lambda d:d.__setitem__('denominator',True),
    }
    ws = {
      'word': lambda d:d['words'].__setitem__(0,'0'*len(d['words'][0])),
      'weights': lambda d:d.__setitem__('weights',['1/3','2/3']),
      'full_law_claim': lambda d:d.__setitem__('motions',list(range(15))),
      'geometry_hash': lambda d:d.__setitem__('input_semantic_sha256','0'*64),
      'duplicate_word': lambda d:d['words'].__setitem__(1,d['words'][0]),
    }
    rejected = []
    cases=[('geometry',gc,gs,lambda d:geometry_check(d,data))]
    if wc is not None:
        cases.append(('law',wc,ws,lambda d:word_check(d,data,summary)))
    for prefix, original, tests, fn in cases:
        for name, mutate in tests.items():
            c = deepcopy(original); mutate(c)
            try:
                fn(c)
            except ValueError:
                rejected.append(prefix+':'+name)
            else:
                raise ValueError('accepted mutation '+name)
    proc = subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],
                          capture_output=True,text=True,timeout=20)
    require(proc.returncode!=0 and 'requires assertions' in proc.stderr, 'optimized checker accepted')
    return rejected+['optimized-mode']


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--two-word-certificate',type=Path,help='Optional intermediate positive certificate')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    data, summary = reconstruct(root)
    gc = read(root/'certificates/eta_gauge_geometry.json')
    wc = read(args.two_word_certificate) if args.two_word_certificate else None
    result = dict(status='PASS',geometry=geometry_check(gc,data),
                  algebra=algebra_tests(),source_file_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Geometric premises and one seven-domain positive law; not a full fifteen-domain law.')
    if wc is not None:
        result['optional_two_word_law']=word_check(wc,data,summary)
    if args.self_test:
        result['rejected_mutations'] = mutations(gc,wc,data,summary)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
