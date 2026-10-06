"""Independent complete-cross-edge replay of Y union (1+Y), no search imports."""
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import json,gzip,sys,subprocess
from audit_full_law_preparation import reconstruct,unique_keys
from verify_quintic_core_probe import multiplication_twice,filter_map,product_twice,conjugate_twice,digest
from verify_anchored_eta import require


def geometry(data):
    den=data['denominator'];base=[tuple(p) for p in data['points']]
    moved=[(p[0]+den,*p[1:]) for p in base]
    A=set(base);B=set(moved);points=sorted(A|B);index={p:i for i,p in enumerate(points)}
    copies=[[index[p] for p in source] for source in (base,moved)]
    edges={tuple(sorted((copy[a],copy[b]))) for copy in copies for a,b in data['edges']}
    left=sorted(index[p] for p in A-B);right=sorted(index[p] for p in B-A)
    table=multiplication_twice();prime,images,bars=filter_map(table)
    require(den%prime!=0,'denominator prime')
    residual=[(sum(x*y for x,y in zip(p,images))%prime,sum(x*y for x,y in zip(p,bars))%prime) for p in points]
    buckets=defaultdict(list)
    for j in right:buckets[residual[j]].append(j)
    offsets=[(v,den*den*pow(v,-1,prime)%prime) for v in range(1,prime)]
    new=0;candidates=0
    # This enumerates possible right-hand residue buckets, unlike the
    # producer's NumPy elementwise scan over all cross pairs.
    for i in left:
        a,b=residual[i]
        for v,w in offsets:
            for j in buckets.get(((a-v)%prime,(b-w)%prime),()):
                candidates+=1;delta=[x-y for x,y in zip(points[i],points[j])]
                if product_twice(delta,conjugate_twice(delta),table)==[4*den*den]+[0]*31:
                    edges.add(tuple(sorted((i,j))));new+=1
    edges=sorted(edges)
    report=dict(vertices=len(points),overlap=len(A&B),induced_edges=len(edges),new_cross_edges=new,
                point_sha256=digest(points),edge_sha256=digest(edges),cross_pairs_examined=len(left)*len(right))
    return points,edges,report,candidates


def verify(c,data,summary,rebuilt=None):
    require(c['schema']=='actual-unit-translate-v1','schema')
    require(c['input_semantic_sha256']==summary['semantic_sha256'],'input hash')
    require(type(c['denominator']) is int and c['denominator']==data['denominator'],'denominator')
    t=c['translation'];require(t==[data['denominator']]+[0]*31 and all(type(x) is int for x in t),'exact unit translation')
    points,edges,g,candidates=geometry(data) if rebuilt is None else rebuilt
    require(c['geometry']==g and all(type(c['geometry'][k]) is type(v) for k,v in g.items()),'complete geometry')
    word=c['search'].get('word')
    require(type(word) is str and len(word)==len(points) and set(word)<=set('01234'),'word')
    require(all(word[a]!=word[b] for a,b in edges),'all actual edges')
    return dict(status='PASS',geometry=g,modular_candidates=candidates,proper_edge_checks=len(edges),
                contains_entire_Y=True,chromatic_number=5,
                scope='Exact induced graph Y union (1+Y). Lower bound inherits chi(Y)=5. No assertion about all translates or joint probability laws.')


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1];data,summary=reconstruct(root)
    c=json.loads(gzip.decompress((root/'certificates/unit_translate_Y.json.gz').read_bytes()),object_pairs_hook=unique_keys)
    rebuilt=geometry(data);report=verify(c,data,summary,rebuilt);refused=[]
    for name,mutation in [('input',lambda x:x.update(input_semantic_sha256='bad')),
                           ('shift',lambda x:x['translation'].__setitem__(1,1)),
                           ('shift_bool',lambda x:x['translation'].__setitem__(1,False)),
                           ('edge_count',lambda x:x['geometry'].update(induced_edges=0)),
                           ('geometry_hash',lambda x:x['geometry'].update(edge_sha256='0'*64)),
                           ('word',lambda x:x['search'].update(word='0'*len(x['search']['word']))),
                           ('truncated_word',lambda x:x['search'].update(word=x['search']['word'][:-1]))]:
        wrong=deepcopy(c);mutation(wrong)
        try:verify(wrong,data,summary,rebuilt)
        except (ValueError,AssertionError):refused.append(name)
        else:raise AssertionError('accepted mutation '+name)
    p=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True,timeout=20)
    require(p.returncode!=0 and 'requires assertions' in p.stderr,'optimized verification');refused.append('optimized')
    require(not any(x=='pysat' or x.startswith('pysat.') for x in sys.modules),'no solver imports')
    report['rejected_mutations']=refused;print(json.dumps(report,indent=2))

if __name__=='__main__':main()
