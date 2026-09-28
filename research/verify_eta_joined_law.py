"""Independent replay of a common full-Y three-word law.

The target is defined from exact Y, the five-point transport closure, seven
original maximal domains, and twelve explicit pair observations. No search
model, solver, unpublished proof checker or floating-point LP is imported.
"""
from collections import Counter, deque
from pathlib import Path
from itertools import combinations
import argparse
import hashlib
import json
from audit_full_law_preparation import reconstruct
from verify_anchored_eta import read, require, blocks, geometry_check, algebra_tests

FULL = [2,5,6,9,11,13,14]
SEED = (231,4641,5163,5412,7478)
BASE = '09926d59b176c1f649aa30f7ec397fb8fa9ef9fa'


def transport_kernel(data):
    transformations=[]
    for mm in data['mappings']:
        transformations.append(dict(mm))
        transformations.append({b:a for a,b in mm})
    seen={SEED};queue=deque([SEED])
    while queue:
        old=queue.popleft()
        for f in transformations:
            if all(x in f for x in old):
                new=tuple(f[x] for x in old)
                if new not in seen:
                    require(len(seen)<1000, 'unexpected transport size')
                    seen.add(new);queue.append(new)
    require(len(seen)==122, 'transport closure')
    kernel=sorted({v for row in seen for v in row})
    require(len(kernel)==129, 'kernel size')
    return kernel


def specifications(c,data):
    require(c['schema']=='eta-joined-gamma-three-law-v1' and c['base_commit']==BASE, 'provenance')
    kernel=transport_kernel(data)
    require(c['kernel_Y_indices']==kernel and all(type(i) is int for i in c['kernel_Y_indices']),
            'kernel definition')
    require(c['full_motions']==FULL and all(type(i) is int for i in c['full_motions']), 'full domains')
    events=c['pair_records']
    require(len(events)==12 and len({e[0] for e in events})==12, 'pair record count')
    inherited=read(Path(__file__).resolve().parents[1]/'certificates/shared_event_research.json.gz')
    require(events==[e for e in inherited['event_records'] if e[0]!=14], 'specified pair endpoints')
    # Their precise endpoints are part of the target, not an alleged universal
    # choice of representatives. Every record is tied to an actual motion.
    for e in events:
        require(len(e)==5 and all(type(v) is int for v in e), 'pair type')
        j,a,b,x,y=e
        require(0<=j<14 and a!=b, 'pair motion')
        mm=dict(data['mappings'][j])
        require(mm.get(a)==x and mm.get(b)==y, 'pair is not the actual motion')
    K=set(kernel)
    local=[[[a,b] for a,b in mm if a in K and b in K] for mm in data['mappings']]
    # For a positive result, check all 34 original requests separately. The
    # seven-domain requirements imply some of the weaker ones, but no join of
    # two separately requested distributions is silently added.
    requested=[('kernel:'+str(j),mm) for j,mm in enumerate(local)]
    requested += [('full:'+str(j),data['mappings'][j]) for j in FULL]
    requested += [('pair:'+str(j),[[a,x],[b,y]]) for j,a,b,x,y in events]
    return requested,local


def expand_compact(c, data, summary):
    """Decode a small witness, then require a direct full-graph replay.

    The transport equalities only compress the positive witness. No result is
    inferred from their consistency without the independent checks below.
    """
    require(c['schema']=='eta-joined-three-word-compact-v1', 'compact schema')
    require(c['input_semantic_sha256']==summary['semantic_sha256'], 'compact input')
    require(type(c['equal_words']) is int and c['equal_words']==3, 'compact states')
    converted=dict(c, schema='eta-joined-gamma-three-law-v1')
    _,local=specifications(converted,data)
    obs=[data['mappings'][j] if j in FULL else local[j] for j in range(15)]
    obs += [[[a,x],[b,y]] for j,a,b,x,y in c['pair_records'] if j not in FULL]
    require(len(c['matches'])==len(obs)==22, 'compact observation count')
    m=3;n=len(data['points']);adj=[[] for _ in range(m*n)]
    for mm,match in zip(obs,c['matches']):
        sigma=match['support'];palettes=match['palettes']
        require(len(sigma)==m and all(type(x) is int for x in sigma)
                and sorted(sigma)==list(range(m)), 'compact support permutation')
        require(len(palettes)==m and all(len(pi)==5 and all(type(x) is int for x in pi)
                and sorted(pi)==list(range(5)) for pi in palettes), 'compact palette')
        for state in range(m):
            pi=tuple(palettes[state]);inv=tuple(pi.index(x) for x in range(5))
            for a,b in mm:
                x=state*n+a;y=sigma[state]*n+b
                adj[x].append((y,pi));adj[y].append((x,inv))
    roots=c['root_colors']
    require(isinstance(roots,str) and set(roots)<=set('01234'), 'compact root colors')
    values=[-1]*(m*n);used=0
    for start in range(m*n):
        if values[start]>=0:continue
        require(used<len(roots), 'missing compact root')
        values[start]=int(roots[used]);used+=1;stack=[start]
        while stack:
            x=stack.pop()
            for y,pi in adj[x]:
                value=pi[values[x]]
                if values[y]<0:values[y]=value;stack.append(y)
                else:require(values[y]==value, 'inconsistent compact cycle')
    require(used==len(roots), 'extra compact roots')
    words=[''.join(map(str,values[i*n:(i+1)*n])) for i in range(m)]
    require([hashlib.sha256(w.encode()).hexdigest() for w in words]==c['word_sha256'],
            'expanded word digest')
    converted['words']=words
    return converted


def check(c,data,summary):
    require(c['input_semantic_sha256']==summary['semantic_sha256'], 'geometry hash')
    requests,local=specifications(c,data)
    words=c['words']
    require(len(words)==3 and c['weights']==['1/3']*3, 'three uniform weights')
    for w in words:
        require(isinstance(w,str) and len(w)==len(data['points']) and set(w)<=set('01234'), 'word')
        require(all(w[a]!=w[b] for a,b in data['edges']), 'improper full-Y word')
    require(len({blocks(w,range(len(w))) for w in words})==3, 'duplicate partitions')
    reports=[]
    for name,mm in requests:
        left=Counter(blocks(w,[a for a,b in mm]) for w in words)
        right=Counter(blocks(w,[b for a,b in mm]) for w in words)
        require(left==right, 'failed complete law '+name)
        reports.append(dict(observation=name,size=len(mm)))
    all_passed=[]
    for j,mm in enumerate(data['mappings']):
        left=Counter(blocks(w,[a for a,b in mm]) for w in words)
        right=Counter(blocks(w,[b for a,b in mm]) for w in words)
        if left==right:all_passed.append(j)
    require(all_passed==FULL, 'full-domain scope')
    def named_pattern(word, ids):
        names={}
        return ''.join(str(names.setdefault(word[v],len(names))) for v in ids)
    extreme_rows=[]
    for pat in ['01102201340110220134101010214302130210101034012210013401221001333',
                '01230144100123014410010113140214014020010110440123011044012301020']:
        a=[x for x,y in local[0]];b=[y for x,y in local[0]]
        extreme_rows.append([int(named_pattern(w,a)==pat)-int(named_pattern(w,b)==pat) for w in words])
    require(extreme_rows==[[1,-1,0],[0,1,-1]], 'extreme-law balance rows')

    require(all(w[a]==w[b] for w in words for a,b in data['mappings'][2]), 'eta normal form')
    return dict(status='PASS',whole_Y_words=3,proper_edge_checks=3*len(data['edges']),
                checked_observations=len(requests),observations=reports,extreme_support_determinant=3,
                complete_original_domains_passed=all_passed,full_fifteen_domain_law=False,
                scope='A positive law for F union Gamma union the full eta domain. Minimal support is not asserted by this positive checker.')


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    data,summary=reconstruct(root)
    cert=expand_compact(read(root/'certificates/eta_joined_three_compact.json.gz'),data,summary)
    geometry=geometry_check(read(root/'certificates/eta_gauge_geometry.json'),data)
    report=check(cert,data,summary)
    report['normalization_premises']=geometry
    report['finite_algebra_tests']=algebra_tests()
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
