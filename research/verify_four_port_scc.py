#!/usr/bin/env python3
"""Replay four exact four-port pattern-transition SCC certificates.

Reads the audited full-law geometry cache and existing whole-Y witnesses.
Run after check-y-full-geometry for independent geometry reconstruction.
By default replays and compares the saved receipt; --write-certificate emits it. A strongly connected witnessed subgraph spanning
all locally legal partitions is enough; no missing-arc UNSAT is used.
"""
import argparse, gzip, hashlib, itertools, json, sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/'certificates'
CACHE=EXP/'Y_full_geometry.json.gz'
from audit_full_law_preparation import unique_keys
if not __debug__:
    raise RuntimeError('Verification requires assertions')

def load_json(path, zipped=False):
    opener=gzip.open if zipped else open
    with opener(path,'rt',encoding='utf-8') as f: return json.load(f,object_pairs_hook=unique_keys)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

def rgs_patterns(n):
    out=[]
    def visit(prefix,top):
        if len(prefix)==n:
            out.append(''.join(map(str,prefix))); return
        for x in range(top+2): visit(prefix+[x],max(top,x))
    visit([0],0)
    return out

def pattern(word, ids):
    labels={}
    return ''.join(str(labels.setdefault(word[i],len(labels))) for i in ids)

def sccs(states, arcs):
    adjacency={s:set() for s in states}
    for a,b in arcs: adjacency[a].add(b)
    reach={s:{s} for s in states}
    changed=True
    while changed:
        changed=False
        for a in states:
            new=set().union(*(reach[b] for b in adjacency[a])) if adjacency[a] else set()
            if not new<=reach[a]: reach[a]|=new; changed=True
    comps=[]; unseen=set(states)
    while unseen:
        a=next(iter(unseen))
        c={b for b in states if b in reach[a] and a in reach[b]}
        unseen-=c; comps.append(sorted(c))
    return comps

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',action='store_true')
    args=parser.parse_args()
    data=load_json(CACHE,True)
    semantic=digest(canonical(data))
    receipt=load_json(ROOT/'certificates/full_law_preparation_audit.json')
    assert semantic==receipt['independent_inputs']['semantic_sha256']
    from verify_g14_unique_event_y import check_geometry_binding
    check_geometry_binding(data,receipt)
    assert len(data['points'])==10077 and len(data['edges'])==49858 and len(data['mappings'])==15
    compact=load_json(ROOT/'certificates/eta_joined_three_compact.json.gz',True)
    portfolio=load_json(ROOT/'certificates/Y_pair_portfolio.json.gz',True)
    e111=load_json(ROOT/'certificates/shared_event_research.json.gz',True)
    e115=load_json(ROOT/'certificates/joined_seed_negative_probe.json')
    e115_run=load_json(ROOT/'certificates/joined_seed_pricing.json.gz',True)
    assert portfolio['vertices']==10077 and portfolio['edges']==49858 and portfolio['input_semantic_sha256']==semantic
    assert e111['input_semantic_sha256']==semantic and e115['cache_semantic_sha256']==semantic
    word_sources=[]
    for source, words in [('branch56',portfolio['words']),('E083',data['words']),
                          ('E111',[e111['positive_word']]),('E115_negative_price',[e115['word']])]:
        for ix,word in enumerate(words):
            assert type(word) is str and len(word)==10077 and set(word)<=set('01234')
            assert all(word[a]!=word[b] for a,b in data['edges'])
            word_sources.append(dict(source=source,index=ix,sha256=digest(word.encode()),word=word))
    sys.path.insert(0,str(ROOT/'research'))
    from verify_eta_joined_law import expand_compact
    seen_words={record['word'] for record in word_sources}
    extra=[('S3',expand_compact(compact,data,receipt['independent_inputs'])['words']),
           ('E115_pool',e115_run['run']['words'])]
    for source,items in extra:
        for ix,word in enumerate(items):
            if word in seen_words: continue
            assert type(word) is str and len(word)==10077 and set(word)<=set('01234')
            assert all(word[a]!=word[b] for a,b in data['edges'])
            word_sources.append(dict(source=source,index=ix,sha256=digest(word.encode()),word=word))
            seen_words.add(word)
    edges={tuple(e) for e in data['edges']}
    adj=[set() for _ in data['points']]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    maps=data['mappings']; domains=[{a for a,b in m} for m in maps]
    exterior=[0,1,3,4,7,8,10,12]
    kernel=set(compact['kernel_Y_indices'])
    candidates=[
      dict(role='one_plus_eta_1 five-neighbor star',j=8,center=4385,T=[3604,3817,4114,4641]),
      dict(role='translation_z five-neighbor star',j=7,center=5645,T=[3484,6700,7219,9104]),
      dict(role='omega five-neighbor star',j=3,center=4264,T=[3748,3797,4513,5158]),
      dict(role='dyadic_u mismatch pair plus tau/bar unit edge',j=14,center=None,T=[233,239,9425,9951]),
    ]
    words=[record['word'] for record in word_sources]
    candidates_out=[]
    for row in candidates:
        j=row['j']; center=row['center']; T=row['T']; mapping=dict(maps[j])
        if center is not None:
            assert center not in domains[j] and len(adj[center]&domains[j])>=5
            assert set(T)<=adj[center]&domains[j]
        assert set(T)<=domains[j] and len(set(T))==4
        image=[mapping[x] for x in T]
        assert len(set(image))==4
        induced_edges=[[i,k] for i,k in itertools.combinations(range(4),2)
                       if tuple(sorted((T[i],T[k]))) in edges]
        states=[p for p in rgs_patterns(4) if all(not(p[i]==p[k] and [i,k] in induced_edges)
                                                   for i,k in itertools.combinations(range(4),2))]
        arcs={}; witness_count=defaultdict(int)
        for word_id,word in enumerate(words):
            a,b=pattern(word,T),pattern(word,image)
            assert a in states and b in states
            arcs.setdefault((a,b),word_id); witness_count[a,b]+=1
        graph_arcs=[[a,b,arcs[a,b]] for a,b in sorted(arcs)]
        components=sccs(states,arcs)
        other_domains=sorted({l for x in T for l in exterior if l!=j and x in domains[l]})
        out=dict(role=row['role'],motion_index=j,motion=data['motions'][j],
                 center=center,center_in_kernel=(center in kernel if center is not None else None),
                 center_outside_source_domain=(center not in domains[j] if center is not None else None),source_T=T,image_T=image,
                 source_in_kernel=[x in kernel for x in T],
                 source_in_domain=True,star_degree_in_source_domain=(len(adj[center]&domains[j]) if center is not None else None),
                 source_induced_edges=induced_edges,locally_legal_patterns=states,
                 legal_pattern_count=len(states),witnessed_arc_count=len(arcs),
                 arc_witnesses=graph_arcs,sccs=components,scc_count=len(components),
                 largest_scc=max(map(len,components)),
                 other_exterior_domains_touched=other_domains,
                 word_count=len(words),edge_checks_per_word=len(edges),
                 scope=('Witnessed subgraph is strongly connected on every internally legal '
                        '4-port partition; full proper-color transition graph is therefore '
                        'strongly connected too. The individual-motion SCC potential is zero.'))
        assert len(components)==1 and len(components[0])==len(states)
        candidates_out.append(out)
    word_meta=[dict(word_id=i,**{k:v for k,v in r.items() if k!='word'})
               for i,r in enumerate(word_sources)]
    source_paths={
        'branch56':'certificates/Y_pair_portfolio.json.gz',
        'E083':'certificates/full_law_pricing.json.gz',
        'E111':'certificates/shared_event_research.json.gz',
        'E115_negative_price':'certificates/joined_seed_negative_probe.json',
        'S3':'certificates/eta_joined_three_compact.json.gz',
        'E115_pool':'certificates/joined_seed_pricing.json.gz',
    }
    source_hashes={name:digest((ROOT/path).read_bytes()) for name,path in source_paths.items()}
    result=dict(schema='four-port-witnessed-scc-v1',date='2026-09-30',
        input_semantic_sha256=semantic,geometry=data['geometry'],
        source_certificate_paths=source_paths,source_certificate_sha256=source_hashes,
        word_sources=word_meta,candidates=candidates_out,
        positive_word_edge_checks=len(words)*len(edges),
        theorem_scope=('For each named single motion and port separately, any nonnegative '
                       'SCC-condensation potential is trivial because a witnessed subgraph '
                       'already strongly connects all internally legal port patterns. This '
                       'does not rule out signed potentials coupling distinct motions, any '
                       'full15 separator, or an ordinary Hadwiger–Nelson bound.'))
    star_counts=[]
    max_external=[]
    for domain in domains:
        counts=[len(adj[v]&domain) for v in range(len(adj)) if v not in domain]
        star_counts.append(sum(x>=5 for x in counts))
        max_external.append(max(counts,default=0))
    assert star_counts==[0,0,312,300,504,0,95,57,6,0,0,0,0,0,0]
    assert max_external[14]==2
    result['external_five_neighbor_centers']=star_counts
    result['u_max_external_neighbors']=max_external[14]
    target=EXP/'four_port_witnessed_scc.json'
    if args.write_certificate:
        target.write_text(json.dumps(result,separators=(',',':'))+'\n')
    else:
        assert canonical(load_json(target))==canonical(result), 'SCC receipt differs from fresh replay'
    print(json.dumps(dict(status='PASS',certificate=str(target),
          words=len(words),whole_edge_checks=len(words)*len(edges),
          candidates=[dict(motion=c['motion'],T=c['source_T'],image=c['image_T'],
                           legal=c['legal_pattern_count'],arcs=c['witnessed_arc_count'],
                           sccs=c['scc_count'],other_domains=c['other_exterior_domains_touched'])
                      for c in candidates_out]),indent=2))

if __name__=='__main__': main()
