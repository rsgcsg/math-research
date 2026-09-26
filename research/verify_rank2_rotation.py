"""Independent stdlib replay of the complete <eta,u,tau>Y unit graph.

Uses 16-dimensional integer algebra (not the producer's 32-dimensional
algebra), different modular embeddings, all finite-place bounds, complete
orbit reconstruction, and direct checks of the saved infinite coloring.
No producer, cache, SAT solver, or numerical library is imported.
"""
from collections import Counter, defaultdict, deque
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from itertools import product
import argparse
import gzip
import hashlib
import json
import math
import subprocess
import sys
import time
from verify_quintic_tau_union import verify as source_geometry
from verify_dyadic_cyclic_orbit import algebra16, local_images, local_mul

SOURCE_SHA = '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1'
POINT_SHA = '6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1'
VAL5_SHA = '3bafba7ce838135f01a5ce3ff8076138df6b254dde67764a85c86b065df6d1c0'

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def digest(x):
    return hashlib.sha256(json.dumps(x, separators=(',', ':')).encode()).hexdigest()

def unique_keys(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError('duplicate JSON key: '+k)
        d[k] = v
    return d

def read(path):
    b = Path(path).read_bytes()
    if b[:2] == b'\x1f\x8b': b = gzip.decompress(b)
    return json.loads(b, object_pairs_hook=unique_keys)

def _finite_bounds(coefficients, times9, bar3):
    """Reconstruct exact paired 2- and 5-adic orders, with nonzero witnesses."""
    bits, N = 12, 4
    M, modulus = 1 << bits, 5**N
    bases2 = local_images(bits)
    one = [Q(1)] + [Q(0)]*15
    u = [Q(v, 2) for v in [1,0,0,0,0,0,-3,-3]+[0]*8]
    tau = [Q(-8,5)]+[Q(0)]*7+[Q(9,5)]+[Q(0)]*7
    eta = [Q(0),Q(1)]+[Q(0)]*14
    def image2(cs, basis):
        vals = [Q(c).numerator*pow(Q(c).denominator,-1,M)%M for c in cs]
        return tuple(sum(c*b[k] for c,b in zip(vals,basis))%M for k in range(4))
    # Check the defining algebra against both local embeddings on every basis product.
    units = [[Q(int(i==j)) for j in range(16)] for i in range(16)]
    for basis in bases2:
        for i,j in product(range(16), repeat=2):
            got = image2([Q(v,9) for v in times9(units[i],units[j])],basis)
            assert got == local_mul(basis[i],basis[j],M)
    def vals2(cs, clear=2):
        ans=[]
        for basis in bases2:
            res=image2([Q(c)*2**clear for c in cs],basis)
            v=min((x & -x).bit_length()-1 if x else bits for x in res)
            assert v<bits, 'unresolved 2-adic zero: increase precision'
            ans.append(v-clear)
        return ans
    roots=[]
    for initial in (2,4):
        w,level=initial,5
        while level<modulus:
            choices=[w+level*j for j in range(5)
                     if ((w+level*j)**2-(w+level*j)+3)%(5*level)==0]
            assert len(choices)==1
            w,level=choices[0],5*level
        roots.append(w)
    assert roots==[217,409]
    nu=[(w+2)*pow(3,-1,modulus)%modulus for w in roots]
    def order5(x):
        if not x:return N
        v=0
        while x%5==0:v+=1;x//=5
        return v
    def vals5(cs):
        d=0
        for c in cs:
            den=Q(c).denominator;e=0
            while den%5==0:den//=5;e+=1
            d=max(d,e)
        rs=[]
        for c in cs:
            c=Q(c)*5**d
            assert c.denominator%5
            rs.append(c.numerator*pow(c.denominator,-1,modulus)%modulus)
        result=[]
        for v in nu:
            # Binomial expansion eta^e=(1+pi)^e, independent of the branch's Horner code.
            polynomials=[[sum(math.comb(e,j)*(rs[4*b+e]+v*rs[8+4*b+e])
                              for e in range(j,4))%modulus for j in range(4)] for b in range(2)]
            minimum=min(4*min(order5(polynomials[0][j]),order5(polynomials[1][j]))+j
                        for j in range(4))
            assert minimum<4*N, 'unresolved 5-adic zero: increase precision'
            result.append(minimum-4*d)
        return result
    assert vals2(u)==[-1,1] and vals2(tau)==[0,0] and vals2(eta)==[0,0]
    assert vals5(u)==[0,0] and vals5(tau)==[-4,4] and vals5(eta)==[0,0]
    rows2=[];rows5=[]
    for i,c in enumerate(coefficients):
        if not any(c):
            assert i==4641
            continue
        a,b=vals2(c),vals5(c)
        conjugate=[Q(v,3) for v in bar3(c)]
        assert vals2(conjugate)==list(reversed(a))
        assert vals5(conjugate)==list(reversed(b))
        rows2.append([i,*a]);rows5.append([i,*b])
    assert len(rows2)==len(rows5)==10076 and digest(rows5)==VAL5_SHA
    values={}
    for label,rows,scale,edge_bound,eq_bound in [('u',rows2,1,9,6),('tau',rows5,4,4,2)]:
        types=set((x,y) for _,x,y in rows)
        for xp,yp in types:
            for xq,yq in types:
                a,b=yp+xq,xp+yq;low=min(xp+yp,xq+yq,0)
                assert a-min(b,low)<=scale*edge_bound
                assert b-min(a,low)<=scale*edge_bound
                assert abs(xp-xq)<=scale*eq_bound
        values[label]=dict(types=len(types),unit_bound=edge_bound,equality_bound=eq_bound,
                           rows_sha256=digest(rows))
    return values

def _prime_images(times9,bar3,start):
    p=start
    while True:
        if p%30==1 and not any(p%d==0 for d in range(2,math.isqrt(p)+1)) and pow(-11,(p-1)//2,p)==1:break
        p+=1
    square_root=[-1]*p
    for j in range(p):square_root[j*j%p]=j
    e=next(pow(j,(p-1)//5,p) for j in range(2,p) if pow(j,(p-1)//5,p)!=1)
    z=(-3+square_root[-3%p])*pow(6,-1,p)%p
    v=(5-square_root[-11%p])*pow(6,-1,p)%p
    assert sum(pow(e,j,p) for j in range(5))%p==0
    assert (3*z*z+3*z+1)%p==(3*v*v-5*v+3)%p==0
    images=[pow(e,i%4,p)*pow(z,(i//4)%2,p)*pow(v,i//8,p)%p for i in range(16)]
    bars=[]
    unit=[[int(i==j) for j in range(16)] for i in range(16)]
    for b in unit:bars.append(sum(c*x for c,x in zip(bar3(b),images))*pow(3,-1,p)%p)
    for i,j in product(range(16),repeat=2):
        assert sum(c*x for c,x in zip(times9(unit[i],unit[j]),images))%p==9*images[i]*images[j]%p
    inverse=[0,1]+[0]*(p-2)
    for j in range(2,p):inverse[j]=p-(p//j)*inverse[p%j]%p
    return p,images,bars,square_root,inverse

def _gains(times9,bar3):
    one=(Q(1),)+(Q(0),)*15
    eta=(Q(0),Q(1))+(Q(0),)*14
    u=tuple(Q(x,2) for x in [1,0,0,0,0,0,-3,-3]+[0]*8)
    tau=(Q(-8,5),)+(Q(0),)*7+(Q(9,5),)+(Q(0),)*7
    mul=lambda a,b:tuple(Q(c,9) for c in times9(a,b))
    def powers(x,limit):
        bar=tuple(Q(c,3) for c in bar3(x));assert mul(x,bar)==one
        out={0:one}
        for i in range(1,limit+1):out[i]=mul(x,out[i-1]);out[-i]=mul(bar,out[1-i])
        return out
    e=powers(eta,5);a=powers(tau,4);b=powers(u,9)
    assert e[5]==one and len({e[j] for j in range(5)})==5
    g={(h,n,k):mul(e[h],mul(a[k],b[n])) for h in range(5) for n in range(-9,10) for k in range(-4,5)}
    assert len(g)==len(set(g.values()))==855
    ints={}
    for key,cs in g.items():
        den=math.lcm(*(c.denominator for c in cs));ints[key]=(tuple(int(c*den) for c in cs),den)
    return g,ints

def _canon(i,j,h,n,k):
    return min((i,j,h%5,n,k),(j,i,(-h)%5,-n,-k))

def rebuild(root,progress=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    root=Path(root)
    assert hashlib.sha256((root/'certificates/quintic_tau_union.json').read_bytes()).hexdigest()==SOURCE_SHA
    source,ctx=source_geometry(root,geometry_context=True)
    assert source['geometry']['point_sha256']==POINT_SHA
    coefficients=[tuple(ctx['ring']['coordinates'](p)) for p in ctx['points']]
    times9,bar3,norm27,_=algebra16()
    bounds=_finite_bounds(coefficients,times9,bar3)
    denominator=math.lcm(*(c.denominator for p in coefficients for c in p))
    points=[tuple(int(c*denominator) for c in p) for p in coefficients]
    assert len(set(points))==10077 and points[4641]==(0,)*16
    gains,integer_gains=_gains(times9,bar3)
    maps=[_prime_images(times9,bar3,s) for s in (300001,500001)]
    factors=[];residues=[]
    for prime,images,bars,_,_ in maps:
        def ev(cs,basis):return sum(c.numerator*pow(c.denominator,-1,prime)*x for c,x in zip(cs,basis))%prime
        factors.append({g:(ev(v,images),ev(v,bars)) for g,v in gains.items()})
        residues.append([(sum(v*x for v,x in zip(p,images))*pow(denominator,-1,prime)%prime,
                          sum(v*x for v,x in zip(p,bars))*pow(denominator,-1,prime)%prime) for p in points])
        assert all(a*b%prime==1 for a,b in factors[-1].values())
    prime=maps[0][0];index=defaultdict(list)
    for i,z in enumerate(residues[0]):
        if i!=4641:index[z].append(i)
    adjacency=defaultdict(list);records=[]
    # Unlike the producer's union/find, recover connected components and group coordinates by BFS.
    for (h,n,k),(a,b) in factors[0].items():
        if abs(n)>6 or abs(k)>2:continue
        cs,d=integer_gains[h,n,k]
        for i,(x,y) in enumerate(residues[0]):
            if i==4641:continue
            targets=index.get((a*x%prime,b*y%prime),())
            if not targets:continue
            transformed=times9(cs,points[i])
            for j in targets:
                if transformed==[9*d*v for v in points[j]]:
                    records.append([i,j,h,n,k]);adjacency[i].append((j,h,n,k))
    coords=[None]*len(points);representatives=[]
    for i in range(len(points)):
        if i==4641 or coords[i] is not None:continue
        representatives.append(i);coords[i]=[i,0,0,0];queue=deque([i])
        while queue:
            j=queue.popleft();r,h,n,k=coords[j]
            for to,dh,dn,dk in adjacency[j]:
                want=[r,(h+dh)%5,n+dn,k+dk]
                if coords[to] is None:coords[to]=want;queue.append(to)
                else:assert coords[to]==want
    assert len(records)==sum(c*c for c in Counter(v[0] for v in coords if v is not None).values())
    # Every source point is explicitly equal to the claimed representative position.
    for i,v in enumerate(coords):
        if v is None:assert i==4641;continue
        r,h,n,k=v;cs,d=integer_gains[h,n,k]
        assert times9(cs,points[r])==[9*d*x for x in points[i]]
    if progress:print('Independent rank2 orbits:',len(representatives),flush=True)
    # Complete root sieve over every unordered representative pair, at different primes.
    prime,_,_,sqrt,inv=maps[0];prime2=maps[1][0]
    rp=[residues[0][i] for i in representatives];rp2=[residues[1][i] for i in representatives]
    norms=[a*b%prime for a,b in rp]
    labels=defaultdict(list)
    for key,(g,_) in factors[0].items():labels[g].append(key)
    contacts=set();transformed={};exact=0;degenerate=0
    for i,(x,xb) in enumerate(rp):
        for j in range(i,len(rp)):
            y,yb=rp[j];a=xb*y%prime;b=x*yb%prime;c=(norms[i]+norms[j]-1)%prime
            if a:
                s=sqrt[(c*c-4*a*b)%prime]
                roots=() if s<0 else {(c+s)*inv[2*a%prime]%prime,(c-s)*inv[2*a%prime]%prime}
                possible=[key for r in roots for key in labels.get(r,())]
            elif c:possible=labels.get(b*inv[c]%prime,())
            elif b:possible=()
            else:possible=gains.keys();degenerate+=1
            for h,n,k in possible:
                edge=_canon(i,j,h,n,k)
                if edge in contacts:continue
                xx,xbb=rp2[i];yy,ybb=rp2[j];g,gb=factors[1][h,n,k]
                if ((xx-g*yy)*(xbb-gb*ybb)-1)%prime2:continue
                cs,d=integer_gains[h,n,k];key=(j,h,n,k)
                if key not in transformed:transformed[key]=times9(cs,points[representatives[j]])
                diff=[9*d*z-t for z,t in zip(points[representatives[i]],transformed[key])]
                exact+=1
                if norm27(diff)==[27*(9*d*denominator)**2]+[0]*15:contacts.add(edge)
        if progress and i%600==0:print('Independent rank2 contacts:',i,len(contacts),flush=True)
    contacts=[list(c) for c in sorted(contacts)]
    origin=[i for i,r in enumerate(representatives) if norm27(points[r])==[27*denominator**2]+[0]*15]
    ri={r:i for i,r in enumerate(representatives)};edge_set=set(map(tuple,contacts))
    for a,b in ctx['edges']:
        if 4641 in (a,b):assert ri[coords[b if a==4641 else a][0]] in origin
        else:
            r,h,n,k=coords[a];s,hh,nn,kk=coords[b]
            assert _canon(ri[r],ri[s],hh-h,nn-n,kk-k) in edge_set
    graph=dict(geometry=source['geometry'],representatives=representatives,coordinates=coords,
               contacts=contacts,origin_neighbors=origin,returns_count=len(records),
               returns_sha256=digest(sorted(records)),contact_sha256=digest(contacts))
    details=dict(bounds=bounds,primes=[m[0] for m in maps],algebra_dimension=16,
                 unordered_representative_pairs=len(representatives)*(len(representatives)+1)//2,
                 exact_contact_checks=exact,degenerate_polynomials=degenerate,
                 nonzero_returns=len(records),source_edge_checks=len(ctx['edges']))
    return graph,details

def check_data(data,expected):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    assert set(data)=={'schema','source_commit','canonical_result','graph','coloring'}
    assert data['schema']=='rank2-rotation-coloring-v1'
    assert data['source_commit']=='482b53020f36900ab2fcceff801ee2eb84893d94'
    assert data['canonical_result']=='T138/E110'
    assert canonical(data['graph'])==canonical(expected)
    c=data['coloring'];assert set(c)=={'word','eta','u','tau','origin'}
    assert canonical([c['eta'],c['tau'],c['u']])==canonical([list(range(5)),list(range(5)),[0,2,3,1,4]])
    assert type(c['origin']) is int and c['origin']==0
    word=c['word'];assert isinstance(word,str) and len(word)==len(expected['representatives'])
    assert set(word)<=set('01234')
    U=c['u'];powers=[list(range(5))]
    for _ in range(3):powers.append([U[x] for x in powers[-1]])
    assert powers[3]==powers[0]
    assert all(word[i]!='0' for i in expected['origin_neighbors'])
    assert all(int(word[i])!=powers[n%3][int(word[j])] for i,j,h,n,k in expected['contacts'])
    self_edges=[e for e in expected['contacts'] if e[0]==e[1]]
    assert self_edges and all(h==k==0 and abs(n)==2 for i,j,h,n,k in self_edges)
    return dict(nonzero_orbits=len(word),unit_contact_orbits=len(expected['contacts']),
                origin_neighbor_orbits=len(expected['origin_neighbors']),self_contacts=self_edges,
                certified_upper_bound=5,minimal_positive_u_label_period=3,
                eta_and_tau_label_invariant=True,lower_bound_source='Y contains the separately certified Parts509 graph')

def mutations(data,expected):
    changes={
        'removed_edge':lambda x:x['graph']['contacts'].pop(),
        'wrong_gain':lambda x:x['graph']['contacts'][0].__setitem__(4,9),
        'missing_origin_neighbor':lambda x:x['graph']['origin_neighbors'].pop(),
        'wrong_point_coordinate':lambda x:x['graph']['coordinates'][0].__setitem__(2,10),
        'wrong_returns':lambda x:x['graph'].__setitem__('returns_count',0),
        'wrong_contact_hash':lambda x:x['graph'].__setitem__('contact_sha256','0'*64),
        'wrong_source':lambda x:x.__setitem__('source_commit','0'*40),
        'constant_coloring':lambda x:x['coloring'].__setitem__('word','0'*len(x['coloring']['word'])),
        'short_coloring':lambda x:x['coloring'].__setitem__('word',x['coloring']['word'][:-1]),
        'bad_color':lambda x:x['coloring'].__setitem__('word','5'+x['coloring']['word'][1:]),
        'identity_u':lambda x:x['coloring'].__setitem__('u',list(range(5))),
        'wrong_origin':lambda x:x['coloring'].__setitem__('origin',True),
        'boolean_edge_index':lambda x:x['graph']['contacts'][0].__setitem__(0,False),
        'boolean_palette':lambda x:x['coloring']['eta'].__setitem__(0,False),
        'float_palette':lambda x:x['coloring']['tau'].__setitem__(1,1.0),
    }
    for name,f in changes.items():
        bad=deepcopy(data);f(bad)
        try:check_data(bad,expected)
        except (AssertionError,ValueError,IndexError,KeyError):continue
        raise AssertionError('accepted mutation: '+name)
    try:json.loads('{"x":1,"x":2}',object_pairs_hook=unique_keys)
    except ValueError:pass
    else:raise AssertionError('duplicate keys accepted')
    p=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True,timeout=20)
    assert p.returncode and 'requires assertions' in p.stderr
    return sorted(changes)+['duplicate_keys','optimized_mode']

def verify(root,mutation_tests=False,progress=False):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    started=time.monotonic();data=read(Path(root)/'certificates/rank2_rotation_coloring.json.gz')
    graph,details=rebuild(root,progress)
    report=check_data(data,graph)
    rejected=mutations(data,graph) if mutation_tests else []
    return dict(status='PASS',canonical_result='T138/E110',**report,independent_rebuild=details,
                mutation_rejections=rejected,seconds=round(time.monotonic()-started,3),
                scope='Entire induced <eta,u,tau>Y orbit graph, not the fifteen-domain full joint or the plane.')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Verification requires assertions')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mutation-tests',action='store_true');parser.add_argument('--progress',action='store_true')
    a=parser.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parents[1],a.mutation_tests,a.progress),indent=2))
