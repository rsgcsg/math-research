"""Bounded two-layer character coupling; failure is not a joint obstruction.

Geometry is first rebuilt by the independent E077 checker. This exploratory
producer is not its own checker for any new positive joint certificate.
"""
from fractions import Fraction as Q
from itertools import permutations,product
from pathlib import Path
import json
from verify_quintic_tau_union import verify
from verify_quintic_core_probe import conjugate_twice,digest


def run(root):
    report,c=verify(root,geometry_context=True)
    r=c['ring'];mul=r['mul'];points=c['points'];lookup={p:i for i,p in enumerate(points)}
    bar=lambda p:tuple(Q(x)/2 for x in conjugate_twice(p))
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    z=r['blocks'][0][64];omega=tuple(-2*a-3*b for a,b in zip(one,z))
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    maps={}
    for name,a in [('tau',r['tau']),('nu',nu),('eta',eta),('omega',omega),('bar',None)]:
        maps[name]=[(i,lookup[q]) for i,p in enumerate(points)
                    if (q:=bar(p) if a is None else mul(a,p)) in lookup]
    def pattern(word,ids):
        labels={};return tuple(labels.setdefault(word[i],len(labels)) for i in ids)
    probes=[]
    for name,m in maps.items():
        left,right=zip(*m)
        probes.append(dict(motion=name,domain=len(m),mapping_sha256=digest(m),
                           saved_word_partition_equal=pattern(c['word'],left)==pattern(c['word'],right)))
    print(json.dumps(dict(probes=probes)),flush=True)
    # The twelve proper characters are checked independently in T108.
    chars=[(1,0,1,2),(1,0,2,3),(1,0,3,2),(1,0,4,3),
           (1,2,1,0),(1,2,1,4),(1,2,4,0),(1,2,4,1),
           (1,4,1,2),(1,4,2,0),(1,4,3,0),(1,4,4,3)]
    X=r['points'];first=[lookup[p] for p in X];second=[lookup[mul(r['tau'],p)] for p in X]
    values=[r['residue'](p) for p in X]
    words=[[sum(a*b for a,b in zip(ch,v))%5 for v in values] for ch in chars]
    index0={v:i for i,v in enumerate(first)};index1={v:i for i,v in enumerate(second)}
    overlap=sorted(set(first)&set(second))
    cross=[(i,j) for i,j in c['edges'] if not (i in index0 and j in index0 or i in index1 and j in index1)]
    neighbors={v:[] for v in index1 if v not in index0}
    for u,v in c['edges']:
        if u in index0 and v in neighbors:neighbors[v].append(u)
        if v in index0 and u in neighbors:neighbors[u].append(v)
    stars=[]
    for a,w in enumerate(words):
        witness=None
        for v,ns in sorted(neighbors.items()):
            by_color={w[index0[u]]:u for u in ns}
            if len(by_color)==5:
                witness=dict(character=a,center=v,neighbors=[by_color[k] for k in range(5)]);break
        stars.append(witness)
    print(json.dumps(dict(saturated_stars=stars)),flush=True)
    candidates=[]
    overlap_compatible=0
    for a,b in product(range(12),repeat=2):
        for pi in permutations(range(5)):
            if any(words[a][index0[v]]!=pi[words[b][index1[v]]] for v in overlap):continue
            overlap_compatible+=1
            word=[words[a][index0[v]] if v in index0 else pi[words[b][index1[v]]] for v in range(len(points))]
            if any(word[i]==word[j] for i,j in cross):continue
            assert all(word[i]!=word[j] for i,j in c['edges'])
            candidates.append((a,b,pi,word))
    print(json.dumps(dict(proper_gluings=len(candidates),character_pairs=len({(a,b) for a,b,_,_ in candidates}))),flush=True)
    # Perfect matching ensures the marginal law on each whole X copy is T109's.
    match={}
    def augment(a,seen):
        for idx,(aa,b,pi,word) in enumerate(candidates):
            if aa!=a or b in seen:continue
            seen.add(b)
            if b not in match or augment(candidates[match[b]][0],seen):match[b]=idx;return True
        return False
    size=sum(augment(a,set()) for a in range(12))
    chosen=[candidates[i] for i in sorted(match.values())]
    checks={}
    if size==12:
        for name,m in maps.items():
            left,right=zip(*m)
            checks[name]=sorted(pattern(w,left) for _,_,_,w in chosen)==sorted(pattern(w,right) for _,_,_,w in chosen)
    return dict(experiment='E078',probes=probes,saturated_stars=stars,overlap_compatible=overlap_compatible,proper_gluings=len(candidates),
                character_pairs=len({(a,b) for a,b,_,_ in candidates}),matching_size=size,
                selected_joint_checks=checks,
                selected=[dict(left=a,right=b,permutation=pi,word=''.join(map(str,w))) for a,b,pi,w in chosen],
                scope='Finite two-layer character template only; no unrestricted joint negative conclusion')


if __name__=='__main__':
    import sys
    result=run(Path(__file__).resolve().parents[1])
    # JSON is emitted to stdout; callers retain it as a replay log.
    print(json.dumps(result,indent=2))
