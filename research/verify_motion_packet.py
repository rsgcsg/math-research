"""Independent replay of T141/E113: a two-atom law but no invariant single atom.

Reconstructs Y and all maximal domains, then checks words and a hinted RUP
proof against an independently rebuilt one-word CNF. It does not import the
packet producer, a solver, a numerical library, or the hint exporter.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import gzip
import hashlib
import json
from audit_full_law_preparation import reconstruct
from verify_rup_lrat import check as check_rup

CORE = [5, 6, 9, 11, 13, 14]
BASE = 'ed4cfb044164b5d88413a2d53c7e030274d04bb8'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    raw = Path(path).read_bytes()
    if raw.startswith(b'\x1f\x8b'):
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=unique)


def pattern(word, ids):
    blocks = {}
    for position, vertex in enumerate(ids):
        blocks.setdefault(word[vertex], []).append(position)
    return tuple(sorted(tuple(b) for b in blocks.values()))


def verify_word(word, data):
    require(isinstance(word, str) and len(word)==len(data['points'])
            and set(word)<=set('01234'), 'word shape')
    require(all(word[a]!=word[b] for a,b in data['edges']), 'improper coloring')


def full_law_domains(words, weights, mappings):
    require(len(words)==len(weights) and all(w>=0 for w in weights) and sum(weights)==1, 'probability weights')
    passed = []
    details = []
    for j, mapping in enumerate(mappings):
        source, target = Counter(), Counter()
        for word, weight in zip(words, weights):
            source[pattern(word, [a for a,b in mapping])] += weight
            target[pattern(word, [b for a,b in mapping])] += weight
        same = source==target
        if same:
            passed.append(j)
        details.append(dict(motion=j, domain_size=len(mapping), complete_law=same))
    return passed, details


def rebuild_singleton(n, edges, k, mappings):
    """Independent enumeration, not a call to motion_packet_cnf."""
    require(type(n) is int and n>0 and type(k) is int and 2<=k<=10, 'dimensions')
    result = []
    def append(clause):
        distinct = []
        seen = set()
        for literal in clause:
            if -literal in seen:
                return  # logically true; no restriction is discarded
            if literal not in seen:
                seen.add(literal)
                distinct.append(literal)
        require(bool(distinct), 'unexpected empty initial clause')
        result.append(distinct)
    def one(variables):
        append(variables)
        for left in range(len(variables)):
            for right in range(left+1, len(variables)):
                append([-variables[left], -variables[right]])
    def x(v, c):
        return 1+k*v+c
    for v in range(n):
        one([x(v,c) for c in range(k)])
    last_edge = None
    for a,b in edges:
        require(type(a) is int and type(b) is int and 0<=a<b<n, 'edge')
        require(last_edge is None or last_edge<(a,b), 'edge order/duplicate')
        last_edge = (a,b)
        for c in range(k):
            append([-x(a,c), -x(b,c)])
    top = n*k
    for mapping in mappings:
        require(len({a for a,b in mapping})==len(mapping)
                and len({b for a,b in mapping})==len(mapping), 'partial bijection')
        for a,b in mapping:
            require(type(a) is int and type(b) is int and 0<=a<n and 0<=b<n, 'map vertex')
        # Read the variables row-major, without reusing the producer's builder.
        start = top+1
        top += k*k
        for c in range(k):
            one([start+c*k+d for d in range(k)])
        for d in range(k):
            one([start+c*k+d for c in range(k)])
        for a,b in mapping:
            for c in range(k):
                for d in range(k):
                    append([-x(a,c), -(start+c*k+d), x(b,d)])
    header = f'p cnf {top} {len(result)}\n'
    raw = (header+''.join(' '.join(map(str,c))+' 0\n' for c in result)).encode()
    return dict(nv=top, clauses=result, cnf_sha256=hashlib.sha256(raw).hexdigest())


def fast_checks(cert, data, summary):
    require(cert.get('schema')=='two-atom-motion-packet-v1', 'schema')
    require(cert.get('base_commit')==BASE, 'base provenance')
    require(cert.get('input_semantic_sha256')==summary['semantic_sha256'], 'geometry binding')
    require(cert.get('motions')==CORE and all(type(j) is int for j in cert['motions']), 'motion scope')
    words = cert['two_word_law']['words']
    require(len(words)==2 and cert['two_word_law']['weights']==['1/2','1/2'], 'two-atom weights')
    for word in words:
        verify_word(word, data)
    require(pattern(words[0], range(len(words[0])))!=pattern(words[1], range(len(words[1]))),
            'two words are not distinct partitions')
    passed, detail = full_law_domains(words, [Fraction(1,2)]*2, data['mappings'])
    require(passed==CORE, 'unexpected or missing full-domain law')
    singles = []
    for word in words:
        ok, _ = full_law_domains([word], [Fraction(1)], data['mappings'])
        require(not set(CORE)<=set(ok), 'an alleged refuted singleton exists')
        singles.append(ok)
    drop = cert['omit_one_motion']
    require(len(drop)==len(CORE) and [c['omitted'] for c in drop]==CORE
            and all(type(c['omitted']) is int for c in drop), 'deletion-witness scope')
    for item in drop:
        verify_word(item['word'], data)
        ok, _ = full_law_domains([item['word']], [Fraction(1)], data['mappings'])
        require(set(CORE)-{item['omitted']}<=set(ok) and item['omitted'] not in ok,
                'invalid omit-one-motion witness')
    q = cert['one_word_denial']
    require(q['status']=='VERIFIED_NO_SINGLETON' and q['motions']==CORE
            and all(type(j) is int for j in q['motions']), 'negative scope')
    require(q['proof'] and isinstance(q['proof'], list) and
            all(isinstance(line,str) for line in q['proof']), 'proof shape')
    return dict(full_domain_checks=detail, singleton_passed=singles,
                two_word_edge_checks=2*len(data['edges']), omit_one_edge_checks=6*len(data['edges']))


def check(cert, data, summary, rebuilt=None):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    report = fast_checks(cert, data, summary)
    if rebuilt is None:
        rebuilt = rebuild_singleton(len(data['points']), data['edges'], 5,
                                    [data['mappings'][j] for j in CORE])
    q = cert['one_word_denial']
    require(type(q['nv']) is int and type(q['clauses']) is int and
            q['cnf_sha256']==rebuilt['cnf_sha256'] and q['nv']==rebuilt['nv']
            and q['clauses']==len(rebuilt['clauses']), 'CNF binding')
    ids = q['initial_clause_ids']
    require(isinstance(ids,list) and ids and all(type(i) is int for i in ids)
            and ids==sorted(set(ids)) and 1<=ids[0]<=ids[-1]<=len(rebuilt['clauses']),
            'selected initial clauses')
    selected = [rebuilt['clauses'][i-1] for i in ids]
    raw = (f"p cnf {rebuilt['nv']} {len(selected)}\n"+
           ''.join(' '.join(map(str,c))+' 0\n' for c in selected)).encode()
    require(q['selected_cnf_sha256']==hashlib.sha256(raw).hexdigest(), 'selected CNF binding')
    proof = check_rup(selected, q['proof'])
    return dict(status='PASS', result='MINIMUM_PARTITION_SUPPORT_EXACTLY_TWO',
                maximum_atom_mass='1/2', motions=CORE, input_semantic_sha256=summary['semantic_sha256'],
                negative_proof=proof, **report, full_fifteen_domain_law=False,
                scope='The specified six-motion subsystem only. Each deletion permits a singleton. '
                      'The atom-mass statement additionally uses the written majority-atom proof; no new HN bound.')


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    root = Path(__file__).resolve().parents[1]
    data, summary = reconstruct(root)
    cert = read(root/'certificates/two_atom_motion_packet.json.gz')
    print(json.dumps(check(cert, data, summary), indent=2))


if __name__=='__main__':
    main()
