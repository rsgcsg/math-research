"""Independent exact checker of a fixed 22-point boundary; no search libraries."""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
import argparse,copy,gzip,hashlib,json,sys,time

def require(ok,message):
    if not ok: raise ValueError(message)
def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def positives(cert,geometry,prior):
    require(cert['schema']=='exact-local-pr-boundary-interval-v1','schema')
    vertices=cert['order']; require(vertices==prior['boundary']['order'],'vertex order')
    require(cert['terms']==[dict(pair=t['pair'],type=t['type']) for t in prior['boundary']['terms']],'all individual events')
    require(cert['windows']==prior['boundary']['saturated_windows'],'window set')
    require(cert['PRR_triple']==prior['boundary']['PRR_triple'],'triple')
    index={v:i for i,v in enumerate(vertices)}
    edges=[(index[a],index[b]) for a,b in geometry['edges'] if a in index and b in index]
    require(len(vertices)==22 and len(edges)==34,'actual graph')
    pairs=[tuple(index[v] for v in t['pair']) for t in cert['terms']]
    require(len(pairs)==89,'pair count')
    windows=[[index[v] for v in w] for w in cert['windows']]
    kind={frozenset(t['pair']):t['type'] for t in cert['terms']}
    tr=cert['PRR_triple'];o=next(o for o in tr if all(kind[frozenset((o,v))]=='R' for v in tr if v!=o))
    a,b=sorted(set(tr)-{o});triple=[index[a],index[o],index[b]]
    require(len(cert['endpoints'])==2,'endpoints')
    for ep,sense in zip(cert['endpoints'],[-1,1]):
        require(ep['sense']==sense,'orientation')
        q=Fraction(*ep['q']); den=ep['denominator']; atoms=ep['atoms']
        require(type(den) is int and den>0 and atoms,'denominator')
        require(all(type(a['numerator']) is int and a['numerator']>0 for a in atoms),'positive integer weights')
        require(sum(a['numerator'] for a in atoms)==den,'normalization')
        for atom in atoms:
            w=atom['word']
            require(len(w)==22 and all(type(c) is int and 0<=c<5 for c in w),'five colors')
            require(all(w[a]!=w[b] for a,b in edges),'unit edge')
            require(all(sum(w[a]==w[b] for a,b in combinations(vs,2))==2 for vs in windows),'window equality')
            a,o,b=triple
            require(int(w[a]==w[o])+int(w[b]==w[o])-int(w[a]==w[b])==1,'triangle equality')
        for term,(a,b) in zip(cert['terms'],pairs):
            wanted=Fraction(1,27) if term['type']=='P' else Fraction(14,27) if term['type']=='R' else q
            actual=Fraction(sum(atom['numerator'] for atom in atoms if atom['word'][a]==atom['word'][b]),den)
            require(actual==wanted,'individual '+term['type']+' mean')
        cf=ep['coefficients']; rhs=ep['rhs']
        require(len(cf)==89 and all(type(x) is int for x in cf) and type(rhs) is int,'integer dual')
        sums={s:sum(c for c,t in zip(cf,cert['terms']) if t['type']==s) for s in 'PQR'}
        require(sums==ep['coefficient_sums'],'coefficient sums')
        require(sums['Q']>0 if sense==-1 else sums['Q']<0,'Q coefficient orientation')
        require(Fraction(sums['P'],27)+Fraction(14*sums['R'],27)+sums['Q']*q==rhs,'primal dual equality')
    require(Fraction(*cert['endpoints'][1]['q'])<=Fraction(*cert['endpoints'][0]['q']),'interval order')
    return vertices,edges,pairs,windows,triple

def enumerate_boundaries(cert,problem):
    vertices,edges,pairs,windows,triple=problem
    before=[set() for _ in vertices]
    for a,b in edges:
        a,b=sorted((a,b)); before[b].add(a)
    members=[[j for j,w in enumerate(windows) if i in w] for i in range(22)]
    last=[max(w) for w in windows]; tri_last=max(triple)
    costs=[[] for _ in vertices]
    e0,e1=cert['endpoints']
    for j,(a,b) in enumerate(pairs):
        a,b=sorted((a,b)); costs[b].append((a,e0['coefficients'][j],e1['coefficients'][j]))
    color=[-1]*22;counts=[[0]*5 for _ in windows];equal_pairs=[0]*len(windows)
    nodes=leaves=0; maxima=[None,None]
    def visit(i,used,s0,s1):
        nonlocal nodes,leaves
        nodes+=1
        if i==22:
            leaves+=1
            require(s0<=e0['rhs'] and s1<=e1['rhs'],'a proper partition violates the claimed dual')
            maxima[0]=s0 if maxima[0] is None else max(maxima[0],s0)
            maxima[1]=s1 if maxima[1] is None else max(maxima[1],s1)
            return
        forbidden={color[j] for j in before[i]}
        for c in range(min(used+1,5)):
            if c in forbidden: continue
            color[i]=c
            if i==tri_last:
                a,o,b=triple
                if int(color[a]==color[o])+int(color[b]==color[o])-int(color[a]==color[b])!=1:continue
            if any(equal_pairs[t]+counts[t][c]>2 or last[t]==i and equal_pairs[t]+counts[t][c]!=2 for t in members[i]):continue
            for t in members[i]:equal_pairs[t]+=counts[t][c];counts[t][c]+=1
            n0,n1=s0,s1
            for j,u,v in costs[i]:
                if color[j]==c:n0+=u;n1+=v
            visit(i+1,max(used,c+1),n0,n1)
            for t in members[i]:counts[t][c]-=1;equal_pairs[t]-=counts[t][c]
            color[i]=-1
    visit(0,0,0,0)
    require(leaves==5648160,'complete finite enumeration count')
    require(maxima==[e0['rhs'],e1['rhs']],'tight dual bounds')
    return dict(nodes=nodes,leaves=leaves,maxima=maxima)

def main():
    require(__debug__,'checker requires assertions enabled')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    cert=read(root/'certificates/exact_local_pr_boundary_interval.json')
    gp=root/'certificates/Y_full_geometry.json.gz';pp=root/'certificates/q_joint_boundary_gap.json'
    require(cert['geometry_sha256']==digest(gp),'geometry source hash')
    require(cert['prior_certificate_sha256']==digest(pp),'prior exact instance hash')
    geometry=read(gp);prior=read(pp)
    start=time.monotonic();problem=positives(cert,geometry,prior);rejected=[]
    if args.self_test:
        changes={
            'word':lambda d:d['endpoints'][0]['atoms'][0]['word'].__setitem__(0,5),
            'mass':lambda d:d['endpoints'][0]['atoms'][0].__setitem__('numerator',0),
            'endpoint':lambda d:d['endpoints'][0].__setitem__('q',[1,1]),
            'dual':lambda d:d['endpoints'][0].__setitem__('rhs',d['endpoints'][0]['rhs']-1),
            'window':lambda d:d['windows'].pop(),
            'event':lambda d:d['terms'].pop(),
            'denominator':lambda d:d['endpoints'][0].__setitem__('denominator',True),
            'coefficient':lambda d:d['endpoints'][0]['coefficients'].__setitem__(0,0.5),
        }
        for name,mutate in changes.items():
            bad=copy.deepcopy(cert);mutate(bad)
            try:positives(bad,geometry,prior)
            except (ValueError,KeyError,IndexError,ZeroDivisionError):rejected.append(name)
            else:raise ValueError('accepted mutation '+name)
    enumeration=enumerate_boundaries(cert,problem)
    print(json.dumps(dict(status='PASS',q_interval=[str(Fraction(*e['q'])) for e in reversed(cert['endpoints'])],enumeration=enumeration,rejected=rejected,elapsed_seconds=round(time.monotonic()-start,3),scope=cert['scope']),indent=2))
if __name__=='__main__':main()
