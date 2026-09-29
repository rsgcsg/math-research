"""Independent complete two-terminal relation check, without SAT or search code.

The certificate consists solely of full proper five-color words. Bitsets cover
all nonedges exactly, and literal signatures distinguish every pair of points.
No probabilistic sampling, hash-only coverage or interpolation is used.
"""
from pathlib import Path
from itertools import product
from copy import deepcopy
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import time

from audit_full_law_preparation import reconstruct, canonical, unique_keys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def coverage(n, edges, words, colors=5):
    require(bool(words), 'empty portfolio')
    for w in words:
        require(type(w) is str and len(w)==n and set(w)<=set(map(str,range(colors))),
                'invalid full color word')
        require(all(w[i]!=w[j] for i,j in edges), 'not a proper actual-edge coloring')
    signatures = {''.join(w[i] for w in words) for i in range(n)}
    all_bits = (1<<n)-1
    pending = [all_bits ^ ((1<<(i+1))-1) for i in range(n)]
    for i,j in edges:
        a,b = min(i,j),max(i,j)
        pending[a] &= ~(1<<b)
    for w in words:
        groups = [0]*colors
        for i,c in enumerate(w):
            groups[int(c)] |= 1<<i
        for i,c in enumerate(w):
            pending[i] &= ~groups[int(c)]
    return dict(distinct_signatures=len(signatures),
                uncovered_nonedges=sum(row.bit_count() for row in pending))


def check(cert, data, summary):
    require(cert.get('schema')=='Y-two-terminal-portfolio-v1', 'schema')
    require(type(cert.get('colors')) is int and cert['colors']==5, 'color count')
    n = len(data['points'])
    require(type(cert.get('vertices')) is int and cert['vertices']==n, 'vertex count')
    require(type(cert.get('edges')) is int and cert['edges']==len(data['edges']), 'edge count')
    require(cert.get('input_semantic_sha256')==summary['semantic_sha256'], 'source binding')
    words = cert.get('words')
    require(type(words) is list and 1<=len(words)<=2000, 'word list size')
    result = coverage(n, data['edges'], words)
    require(result['distinct_signatures']==n, 'unseparated vertices')
    require(result['uncovered_nonedges']==0, 'nonedge without equality witness')
    return dict(**result, words=len(words), actual_edge_word_checks=len(words)*len(data['edges']),
                distinct_pairs=n*(n-1)//2, nonedges=n*(n-1)//2-len(data['edges']),
                word_list_sha256=hashlib.sha256(canonical(words)).hexdigest())


def finite_tests():
    count = 0
    pairs = [(i,j) for i in range(4) for j in range(i+1,4)]
    for mask in range(64):
        edges = [p for i,p in enumerate(pairs) if mask>>i&1]
        words = [''.join(map(str,c)) for c in product(range(3),repeat=4)
                 if all(c[i]!=c[j] for i,j in edges)]
        if not words:
            continue
        for selected in (words, words[:1], words[::2]):
            direct_equal = sum(not any(w[i]==w[j] for w in selected)
                               for i,j in pairs if (i,j) not in edges)
            direct_signatures = len({tuple(w[i] for w in selected) for i in range(4)})
            require(coverage(4,edges,selected,3)==dict(distinct_signatures=direct_signatures,
                    uncovered_nonedges=direct_equal), 'bitset/direct exhaustive disagreement')
            count += 1
    return count


def mutations(cert, data, summary):
    def first_bad_word(c):
        c['words'][0] = '0'*len(data['points'])
    tests = {
        'source': lambda c: c.__setitem__('input_semantic_sha256','0'*64),
        'boolean_colors': lambda c: c.__setitem__('colors',True),
        'float_vertices': lambda c: c.__setitem__('vertices',float(c['vertices'])),
        'edge_count': lambda c: c.__setitem__('edges',c['edges']-1),
        'improper_word': first_bad_word,
        'short_word': lambda c: c['words'].__setitem__(0,c['words'][0][:-1]),
        'one_proper_word': lambda c: c.__setitem__('words',c['words'][:1]),
        'lost_equality_coverage': lambda c: c.__setitem__('words',c['words'][:-1]),
    }
    for label, change in tests.items():
        altered = deepcopy(cert)
        change(altered)
        try:
            check(altered,data,summary)
        except ValueError:
            continue
        raise AssertionError('accepted mutation '+label)
    try:
        json.loads('{"a":1,"a":2}', object_pairs_hook=unique_keys)
    except ValueError:
        pass
    else:
        raise AssertionError('accepted duplicate JSON key')
    proc = subprocess.run([sys.executable,'-O',__file__],capture_output=True,text=True,timeout=10)
    require(proc.returncode != 0 and 'requires assertions' in proc.stderr, 'optimized mode accepted')
    return sorted(tests)+['duplicate_json','optimized_mode']


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path)
    parser.add_argument('--self-test',action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = args.certificate or root/'certificates/Y_pair_portfolio.json.gz'
    with gzip.open(path,'rb') as stream:
        raw = stream.read(32_000_001)
    require(len(raw)<=32_000_000,'certificate exceeds input budget')
    cert = json.loads(raw,object_pairs_hook=unique_keys)
    started = time.monotonic()
    data,summary = reconstruct(root)
    result = check(cert,data,summary)
    rejected = mutations(cert,data,summary) if args.self_test else []
    tests = finite_tests() if args.self_test else 0
    print(json.dumps(dict(status='PASS', input_semantic_sha256=summary['semantic_sha256'],
          **result, rejection_tests=rejected, small_graph_portfolios=tests,
          seconds=time.monotonic()-started,
          scope='Every locally proper assignment on at most two vertices of actual Y extends to a full five-coloring. '
                'Not a joint invariant probability law; not a claim about larger interfaces or larger hosts.'),indent=2))


if __name__ == '__main__':
    main()
