"""Independent stdlib replay of the complete infinite dyadic rotation orbit.

No producer, NumPy, SAT solver, or producer valuation routines are imported.
Uses a 16-dimensional integer multiplication table and a different unramified
2-adic defining polynomial with Newton (not bitwise) root lifting.
"""
from array import array
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse
import copy
import subprocess
import sys
import gzip
import hashlib
import json
import math
import time


def algebra16():
    def eta(e):
        e %= 5
        return [(j,-1) for j in range(4)] if e==4 else [(e,1)]
    table={}
    for i,j in product(range(16),repeat=2):
        ei,bi,ci=i%4,(i//4)%2,i//8
        ej,bj,cj=j%4,(j//4)%2,j//8
        zz=[(bi+bj,Q(1))] if bi+bj<2 else [(0,-Q(1,3)),(1,-Q(1))]
        vv=[(ci+cj,Q(1))] if ci+cj<2 else [(0,-Q(1)),(1,Q(5,3))]
        terms={}
        for (e,a),(b,z),(c,v) in product(eta(ei+ej),zz,vv):
            k=e+4*b+8*c; terms[k]=terms.get(k,0)+9*a*z*v
        assert all(x.denominator==1 for x in terms.values())
        table[i,j]=[(k,int(x)) for k,x in terms.items() if x]
    def times9(a,b):
        out=[0]*16
        for i,x in enumerate(a):
            if x:
                for j,y in enumerate(b):
                    if y:
                        for k,c in table[i,j]:out[k]+=x*y*c
        return out
    def times(a,b):return [Q(x,9) for x in times9(a,b)]
    one=[1]+[0]*15
    zbar=[-1]+[0]*3+[-1]+[0]*11
    nbar=[Q(5,3)]+[0]*7+[-1]+[0]*7
    bc=[]
    for i in range(16):
        e,b,c=i%4,(i//4)%2,i//8
        v=[0]*16
        for k,x in eta(-e):v[k]=x
        if b:v=times(v,zbar)
        if c:v=times(v,nbar)
        assert all((3*x).denominator==1 if isinstance(x,Q) else True for x in v)
        bc.append([(j,int(3*x)) for j,x in enumerate(v) if x])
    def bar3(a):
        out=[0]*16
        for i,x in enumerate(a):
            if x:
                for j,c in bc[i]:out[j]+=c*x
        return out
    def norm27(a):return times9(a,bar3(a))
    U=[1,0,0,0,0,0,-3,-3]+[0]*8
    cols=[]
    for i in range(16):
        v=times9(U,[int(i==j) for j in range(16)])
        assert all(x%9==0 for x in v)
        cols.append([(j,x//9) for j,x in enumerate(v) if x])
    def apply(a):
        out=[0]*16
        for i,x in enumerate(a):
            if x:
                for j,c in cols[i]:out[j]+=c*x
        return tuple(out)
    assert norm27(U)==[108]+[0]*15
    return times9,bar3,norm27,apply


# Alternate local field: T^4+T^3+1, instead of the producer's T^4+T+1.
def local_mul(a,b,M):
    out=[0]*7
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    for i in range(6,3,-1):
        out[i-4]-=out[i];out[i-1]-=out[i]
    return tuple(x%M for x in out[:4])


def local_poly(cs,x,M):
    out=(0,0,0,0)
    for c in reversed(cs):
        out=local_mul(out,x,M)
        out=((out[0]+c)%M,)+out[1:]
    return out


def local_inverse(a,bits):
    inv=next(tuple((j>>i)&1 for i in range(4)) for j in range(1,16)
             if local_mul(a,tuple((j>>i)&1 for i in range(4)),2)==(1,0,0,0))
    n=1
    while n<bits:
        n=min(2*n,bits);M=1<<n
        ab=local_mul(a,inv,M)
        inv=local_mul(inv,tuple((2*int(i==0)-x)%M for i,x in enumerate(ab)),M)
    assert local_mul(a,inv,1<<bits)==(1,0,0,0)
    return inv


def newton_root(cs,seed,bits):
    x=seed;n=1;der=[i*cs[i] for i in range(1,len(cs))]
    assert local_poly(cs,x,2)==(0,0,0,0)
    while n<bits:
        n=min(2*n,bits);M=1<<n
        correction=local_mul(local_poly(cs,x,M),local_inverse(local_poly(der,x,M),n),M)
        x=tuple((a-b)%M for a,b in zip(x,correction))
    assert local_poly(cs,x,1<<bits)==(0,0,0,0)
    return x


def local_images(bits):
    elements=[tuple((j>>i)&1 for i in range(4)) for j in range(16)]
    es=next(x for x in elements if local_poly([1]*5,x,2)==(0,0,0,0))
    zseeds=[x for x in elements if local_poly([1,1,1],x,2)==(0,0,0,0)]
    e2=local_mul(es,es,2);e3=local_mul(e2,es,2)
    h=tuple((a+b)%2 for a,b in zip(e2,e3))
    zs=next(x for x in zseeds if local_mul(h,x,2)!=(1,0,0,0))
    e=newton_root([1]*5,es,bits)
    z=newton_root([1,3,3],zs,bits)
    v=newton_root([3,-5,3],zs,bits)
    M=1<<bits
    def basis(e,z,v):
        powers=[(1,0,0,0)]
        for _ in range(3):powers.append(local_mul(powers[-1],e,M))
        values=powers+[local_mul(z,x,M) for x in powers]
        return values+[local_mul(v,x,M) for x in values]
    em=local_mul(local_mul(e,e,M),local_mul(e,e,M),M)
    zm=tuple((-int(i==0)-x)%M for i,x in enumerate(z))
    vm=tuple((5*pow(3,-1,M)*int(i==0)-x)%M for i,x in enumerate(v))
    return basis(e,z,v),basis(em,zm,vm)


def order2(x):
    if not x:return 10**9
    return (x & -x).bit_length()-1


def split_images():
    for p in range(10051,200000,60):
        if any(p%d==0 for d in range(2,math.isqrt(p)+1)):continue
        if pow(-11,(p-1)//2,p)==1:break
    else:raise AssertionError('split prime missing')
    e=next(pow(x,(p-1)//5,p) for x in range(2,p) if pow(x,(p-1)//5,p)!=1)
    z=(-3+pow(-3,(p+1)//4,p))*pow(6,-1,p)%p
    v=(5+pow(-11,(p+1)//4,p))*pow(6,-1,p)%p
    assert sum(pow(e,i,p) for i in range(5))%p==0
    assert (3*z*z+3*z+1)%p==0 and (3*v*v-5*v+3)%p==0
    def basis(e,z,v):return [pow(e,a,p)*pow(z,b,p)*pow(v,c,p)%p for c in range(2) for b in range(2) for a in range(4)]
    return p,basis(e,z,v),basis(pow(e,-1,p),-1-z,5*pow(3,-1,p)-v)


def pattern(word,indices):
    names={}
    return tuple(names.setdefault(word[i],len(names)) for i in indices)



def quotient_counts(N,zero,returns,edges,origin,period):
    parent=list(range(N*period))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    def join(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    for t in range(period):join(zero,zero+N*t)
    for rr in returns:
        for i,j in rr['mapping']:
            for t in range(period):join(i+N*((t+rr['power'])%period),j+N*t)
    labels=[find(i) for i in range(N*period)]
    ee=set()
    for n,i,j in edges:
        for t in range(period):
            ee.add(tuple(sorted((labels[i+N*((t+n)%period)],labels[j+N*t]))))
    for j in origin:
        for t in range(period):ee.add(tuple(sorted((labels[zero],labels[j+N*t]))))
    return len(set(labels)),len(ee),sum(i==j for i,j in ee)


def check_payload(data,model):
    """Validate untrusted payload against independently rebuilt finite geometry."""
    assert data['schema']==1 and data['experiment']=='E100_PRODUCER'
    assert data['source_sha']=='5cd6b56373e9e92d686101a87028e213747feaf2'
    assert data['bits']==16
    for field in ('geometry','valuation_first','valuation_conjugate','return_bound',
                  'returns','unit_cross_edges','origin_neighbors'):
        assert data[field]==model[field],field
    result=data['result'];assert isinstance(result,dict)
    period=result['period'];words=result['words'];N=model['geometry']['vertices'];zero=model['zero']
    assert type(period) is int and 1<=period<=100 and len(words)==period
    assert all(isinstance(w,str) and len(w)==N and set(w)<=set('01234') for w in words)
    assert len({w[zero] for w in words})==1
    for rr in model['returns']:
        for i,j in rr['mapping']:
            assert all(words[(t+rr['power'])%period][i]==words[t][j] for t in range(period))
    for n,i,j in model['unit_cross_edges']:
        assert all(words[(t+n)%period][i]!=words[t][j] for t in range(period))
    assert all(words[t][j]!=words[0][zero] for j in model['origin_neighbors'] for t in range(period))
    vertices,edges,loops=quotient_counts(N,zero,model['returns'],model['unit_cross_edges'],
                                       model['origin_neighbors'],period)
    assert not loops
    assert vertices==result['quotient_vertices'] and edges==result['quotient_edges']
    return vertices,edges


def mutation_checks(data,model):
    def mutate_word(d,t,i,color):
        w=d['result']['words'][t];d['result']['words'][t]=w[:i]+color+w[i+1:]
    n,i,j=next(e for e in model['unit_cross_edges'] if e[0]==4)
    u,v=next((i,j) for n,i,j in model['unit_cross_edges'] if n==0)
    def alter_return(d):d['returns'][0]['mapping'][0][1]=(d['returns'][0]['mapping'][0][1]+1)%model['geometry']['vertices']
    cases=[
        ('source',lambda d:d.__setitem__('source_sha','0'*40)),
        ('geometry',lambda d:d['geometry'].__setitem__('point_sha256','0'*64)),
        ('valuation',lambda d:d['valuation_first'].__setitem__(0,d['valuation_first'][0]+1)),
        ('return-bound',lambda d:d.__setitem__('return_bound',d['return_bound']-1)),
        ('missing-return',lambda d:d['returns'][1]['mapping'].pop()),
        ('false-return',alter_return),
        ('missing-fourth-layer-edge',lambda d:d['unit_cross_edges'].remove([n,i,j])),
        ('invented-fifth-layer-edge',lambda d:d['unit_cross_edges'].append([5,i,j])),
        ('missing-origin-edge',lambda d:d['origin_neighbors'].pop()),
        ('changed-fixed-origin',lambda d:mutate_word(d,1,model['zero'],str((int(d['result']['words'][0][model['zero']])+1)%5))),
        ('monochromatic-unit-edge',lambda d:mutate_word(d,0,u,d['result']['words'][0][v])),
        ('sixth-color',lambda d:mutate_word(d,0,u,'5')),
        ('quotient-size',lambda d:d['result'].__setitem__('quotient_vertices',d['result']['quotient_vertices']+1)),
        ('false-period',lambda d:d['result'].__setitem__('period',2)),
    ]
    rejected=[]
    for name,alter in cases:
        bad=copy.deepcopy(data);alter(bad)
        try:check_payload(bad,model)
        except (AssertionError,ValueError,KeyError,IndexError,TypeError):rejected.append(name)
        else:raise AssertionError('accepted mutation: '+name)
    return rejected

def verify(root,certificate=None):
    if not __debug__:raise RuntimeError('Verification requires assertions')
    from verify_quintic_tau_union import verify as geometry
    from verify_quintic_multiword_joint import _definitions
    start=time.monotonic()
    path=certificate or root/'certificates/dyadic_cyclic_orbit_probe.json.gz'
    data=json.loads(gzip.decompress(path.read_bytes()))
    assert data['schema']==1 and data['experiment']=='E100_PRODUCER'
    assert data['source_sha']=='5cd6b56373e9e92d686101a87028e213747feaf2'
    report,c=geometry(root,geometry_context=True)
    assert report['geometry']==data['geometry']
    r=c['ring'];pts=c['points'];N=len(pts)
    coeff=[r['coordinates'](p) for p in pts]
    D=math.lcm(*(x.denominator for p in coeff for x in p))
    points=[tuple(int(x*D) for x in p) for p in coeff]
    zero=next(i for i,p in enumerate(points) if not any(p))
    times9,bar3,norm27,apply=algebra16()
    norms=[tuple(norm27(p)) for p in points]
    unit=(27*D*D,)+(0,)*15
    origin_neighbors=[i for i,n in enumerate(norms) if n==unit]
    assert origin_neighbors==data['origin_neighbors']
    bits=24;M=1<<bits;depth=order2(D);odd=D>>depth; invodd=pow(odd,-1,M)
    ims,bms=local_images(bits)
    def ev(p,bs):return tuple(sum(x*b[j] for x,b in zip(p,bs))*invodd%M for j in range(4))
    U=[1,0,0,0,0,0,-3,-3]+[0]*8
    local_U=tuple(sum(x*b[j] for x,b in zip(U,ims))%M for j in range(4))
    assert min(map(order2,local_U))==0  # v(2u)=0, hence v(u)=-1.
    ep=[ev(p,ims) for p in points];eb=[ev(p,bms) for p in points]
    va=[min(map(order2,p))-depth for p in ep]
    vb=[min(map(order2,p))-depth for p in eb]
    va[zero]=vb[zero]=10**9-2 # canonical infinity sentinel of the producer
    assert all(max(va[i],vb[i])<bits-depth for i in range(N) if i!=zero)
    assert va==data['valuation_first'] and vb==data['valuation_conjugate']
    nz=[i for i in range(N) if i!=zero]
    B=max(va[i] for i in nz)-min(va[i] for i in nz)
    assert B==data['return_bound']
    result=data['result'];assert result is not None
    period=result['period'];words=result['words']
    assert type(period) is int and 1<=period<=100 and len(words)==period
    assert all(isinstance(w,str) and len(w)==N and set(w)<=set('01234') for w in words)
    assert len({w[zero] for w in words})==1
    lookup={p:i for i,p in enumerate(points)}
    returns=[];powerpoints=points
    for n in range(1,B+1):
        powerpoints=[apply(p) for p in powerpoints];scale=1<<n
        mm=[]
        for i,p in enumerate(powerpoints):
            if any(x%scale for x in p):continue
            j=lookup.get(tuple(x//scale for x in p))
            if j is not None:mm.append([i,j])
        returns.append({'power':n,'mapping':mm})
        for i,j in mm:
            assert all(words[(t+n)%period][i]==words[t][j] for t in range(period))
    assert returns==data['returns']
    norm_ids={};reps=[];ids=[]
    rn=[local_mul(a,b,M) for a,b in zip(ep,eb)]
    for i,x in enumerate(norms):
        if x not in norm_ids:norm_ids[x]=len(reps);reps.append(i)
        ids.append(norm_ids[x])
    INF=127;cv=[];zero_constants=0
    for i in reps:
        row=array('b')
        for j in reps:
            x=tuple((a+b-(1<<(2*depth))*int(k==0))%M for k,(a,b) in enumerate(zip(rn[i],rn[j])))
            if not any(x):
                assert tuple(a+b for a,b in zip(norms[i],norms[j]))==unit
                row.append(INF);zero_constants+=1
            else:
                v=min(map(order2,x))-2*depth
                assert -128<v<INF;row.append(v)
        cv.append(row)
    prime,fi,fb=split_images();invD=pow(D,-1,prime)
    pe=[sum(x*y for x,y in zip(p,fi))*invD%prime for p in points]
    pb=[sum(x*y for x,y in zip(p,fb))*invD%prime for p in points]
    ue=(1-3*fi[6]-3*fi[7])*pow(2,-1,prime)%prime
    ub=(1-3*fb[6]-3*fb[7])*pow(2,-1,prime)%prime
    assert ue*ub%prime==1
    bound=2*max(max(abs(va[i]),abs(vb[i])) for i in nz)+bits+2*depth+8
    up=[pow(ue,n,prime) for n in range(bound+1)]
    bp=[pow(ub,n,prime) for n in range(bound+1)]
    candidates=set()
    # Independent, strict Newton polygon: at most TWO, not three, exponent values.
    for i in nz:
        ai,bi,pi,qi=va[i],vb[i],pe[i],pb[i]
        row=cv[ids[i]]
        for j in nz:
            A=ai+vb[j];BB=bi+va[j];C=row[ids[j]]
            if C!=INF and 2*C<A+BB:
                ns=(A-C,C-BB)
            elif (A-BB)%2==0:
                ns=((A-BB)//2,)
            else:continue
            for n in ns:
                if n<0 or (n==0 and i>=j):continue
                assert n<=bound
                if ((pi*up[n]-pe[j])*(qi*bp[n]-pb[j])-1)%prime==0:candidates.add((n,i,j))
        if i%2000==0:print('VERIFY_ORBIT_SIEVE '+json.dumps(dict(row=i,candidates=len(candidates))),flush=True)
    maxpower=max(n for n,i,j in candidates)
    exact=[];powerpoints=points
    for n in range(maxpower+1):
        if n:powerpoints=[apply(p) for p in powerpoints]
        scale=1<<n;target=[27*(D*scale)**2]+[0]*15
        for nn,i,j in sorted(candidates):
            if nn!=n:continue
            d=[x-scale*y for x,y in zip(powerpoints[i],points[j])]
            if norm27(d)==target:exact.append([n,i,j])
    assert exact==data['unit_cross_edges']
    zero_edges={tuple(sorted((i,j))) for n,i,j in exact if n==0}
    zero_edges.update(tuple(sorted((zero,j))) for j in origin_neighbors)
    assert zero_edges==set(c['edges'])
    for n,i,j in exact:
        assert all(words[(t+n)%period][i]!=words[t][j] for t in range(period))
    assert all(words[t][j]!=words[0][zero] for j in origin_neighbors for t in range(period))
    model=dict(geometry=report['geometry'],zero=zero,valuation_first=va,valuation_conjugate=vb,
        return_bound=B,returns=returns,unit_cross_edges=exact,origin_neighbors=origin_neighbors)
    quotient_vertices,quotient_edges=check_payload(data,model)
    rejected=mutation_checks(data,model)
    optimized=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True)
    assert optimized.returncode!=0 and 'Verification requires assertions' in optimized.stderr
    self_edges=[(n,i) for n,i,j in exact if n>0 and i==j]
    period_two_witness=next((n,i) for n,i in self_edges if n%2==0)
    n,i=period_two_witness
    # One actual edge inside a single orbit excludes all periods dividing n.
    witness=dict(power=n,point_index=i,coordinates=[str(x) for x in coeff[i]])
    # Audit old obligations separately, without asserting that a u-invariant law
    # is invariant under unrelated motions.
    def transform_map(a,t,reflected):
        aa=r['coordinates'](a);tt=r['coordinates'](t)
        columns=[]
        for j in range(16):
            e=[Q(int(j==k)) for k in range(16)]
            if reflected:e=[Q(x,3) for x in bar3(e)]
            columns.append([Q(x,9) for x in times9(aa,e)])
        sc=math.lcm(*(x.denominator for col in columns for x in col),*((D*x).denominator for x in tt))
        cc=[[(k,int(x*sc)) for k,x in enumerate(col) if x] for col in columns]
        shift=[int(D*x*sc) for x in tt];mm=[]
        for i,p in enumerate(points):
            out=shift[:]
            for x,col in zip(p,cc):
                if x:
                    for k,y in col:out[k]+=x*y
            if any(x%sc for x in out):continue
            j=lookup.get(tuple(x//sc for x in out))
            if j is not None:mm.append((i,j))
        return mm
    old_audit=[]
    for name,a,t,refl in _definitions(c):
        mm=transform_map(a,t,refl)
        left=Counter(pattern(w,[i for i,j in mm]) for w in words)
        right=Counter(pattern(w,[j for i,j in mm]) for w in words)
        old_audit.append(dict(motion=name,domain=len(mm),full_partition_law_equal=left==right))
    result_report=dict(status='PASS',scope='Entire actual union over all integer u powers; no old-14 common-law or plane claim',
        certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        geometry=report['geometry'],local_bits=bits,local_polynomial=[1,0,0,1,1],split_prime=prime,
        return_bound=B,complete_returns=[(r['power'],len(r['mapping'])) for r in returns],
        cross_edges=len(exact),cross_histogram=sorted(Counter(n for n,i,j in exact).items()),
        origin_neighbors=len(origin_neighbors),period=period,minimum_period_witness=witness,
        quotient_vertices=quotient_vertices,quotient_edges=quotient_edges,
        mutations_rejected=rejected,optimized_mode_rejections=1,
        edge_color_checks=period*(len(exact)+len(origin_neighbors)),old_14_audit=old_audit,
        elapsed_seconds=time.monotonic()-start)
    return result_report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('certificate',nargs='?');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    result=verify(root,Path(args.certificate) if args.certificate else None)
    (root/'certificates/dyadic_cyclic_orbit_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
