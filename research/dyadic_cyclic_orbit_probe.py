"""Search the actual infinite u-orbit by a finite exponent sieve.

Exploratory producer. Positive periodic colorings require independent replay.
A failure of a finite period is not an obstruction to arbitrary coloring.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import json
import math
import time


def mul4(a, b, modulus):
    out = [0]*7
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j] += x*y
    for i in range(6,3,-1):
        out[i-4] -= out[i]
        out[i-3] -= out[i]
    return tuple(x % modulus for x in out[:4])


def poly4(coeff, a, modulus):
    out = (0,0,0,0)
    for c in reversed(coeff):
        out = mul4(out,a,modulus)
        out = ((out[0]+c) % modulus,)+out[1:]
    return out


def hensel(coeff, seed, bits):
    a = tuple((seed>>j)&1 for j in range(4))
    deriv = [j*coeff[j] for j in range(1,len(coeff))]
    d = poly4(deriv,a,2)
    inv = next(tuple((n>>j)&1 for j in range(4)) for n in range(1,16)
               if mul4(d,tuple((n>>j)&1 for j in range(4)),2)==(1,0,0,0))
    assert poly4(coeff,a,2)==(0,0,0,0)
    for j in range(1,bits):
        f = poly4(coeff,a,1<<(j+1))
        assert all(x % (1<<j)==0 for x in f)
        correction = mul4(tuple(x>>j for x in f),inv,2)
        a = tuple(x+(y<<j) for x,y in zip(a,correction))
    assert poly4(coeff,a,1<<bits)==(0,0,0,0)
    return a


def local_basis(bits, conjugated=False):
    mod = 1<<bits
    eta = hensel([1,1,1,1,1],8,bits)
    z = hensel([1,3,3],6,bits)
    nu = hensel([3,-5,3],6,bits)
    if conjugated:
        e2 = mul4(eta,eta,mod)
        eta = mul4(e2,e2,mod)
        z = tuple((-int(i==0)-v) % mod for i,v in enumerate(z))
        nu = tuple((5*pow(3,-1,mod)*int(i==0)-v) % mod for i,v in enumerate(nu))
    ep = [(1,0,0,0)]
    for _ in range(3):ep.append(mul4(ep[-1],eta,mod))
    out = ep+[mul4(z,e,mod) for e in ep]
    out += [mul4(nu,e,mod) for e in out[:]]
    return out


def evaluate(coeff, basis, bits, depth=2):
    mod = 1<<bits
    out = [0]*4
    for x,b in zip(coeff,basis):
        x *= 1<<depth
        assert x.denominator % 2
        a = x.numerator*pow(x.denominator,-1,mod) % mod
        for i,v in enumerate(b):out[i] += a*v
    return tuple(v % mod for v in out)


def v2(n):
    if not n: return 10**9
    return (n & -n).bit_length()-1


def digest(data):
    return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()


def run(root):
    import numpy as np
    from pysat.solvers import Solver
    from dyadic_mixed_return_joint import prepare
    from verify_quintic_core_probe import filter_map, product_twice, conjugate_twice
    start = time.monotonic()
    parent,c,old,algebra,mapping,definitions,maps = prepare(root)
    one,eta,z,u,bar,mul = algebra
    pts = c['points']; count = len(pts); zero = next(i for i,p in enumerate(pts) if not any(p))
    ring = c['ring']; table = ring['table']
    print('ORBIT_GEOMETRY '+json.dumps(parent['geometry']),flush=True)
    coeff = [ring['coordinates'](p) for p in pts]
    bits = 16; mod=1<<bits
    basis = local_basis(bits); basis_bar=local_basis(bits,True)
    ep = [evaluate(p,basis,bits) for p in coeff]
    eb = [evaluate(p,basis_bar,bits) for p in coeff]
    va = [min(map(v2,p))-2 for p in ep]
    vb = [min(map(v2,p))-2 for p in eb]
    assert all(va[i]<bits-2 and vb[i]<bits-2 for i in range(count) if i!=zero)
    uu = evaluate(ring['coordinates'](u),basis,bits)
    assert min(map(v2,uu))-2==-1
    nonzero=[i for i in range(count) if i!=zero]
    norms=[mul(p,bar(p)) for p in pts]
    norm_index={p:i for i,p in enumerate(set(norms))}
    zero_c_count=0
    # A residue-zero constant is checked exactly, never assigned a finite valuation.
    residues=[mul4(a,b,mod) for a,b in zip(ep,eb)]
    buckets={}
    for j,n in enumerate(residues):buckets.setdefault(n,[]).append(j)
    for i in nonzero:
        target=tuple((16*int(k==0)-a)%mod for k,a in enumerate(residues[i]))
        for j in buckets.get(target,[]):
            if j==zero:continue
            assert tuple(a+b-int(k==0) for k,(a,b) in enumerate(zip(norms[i],norms[j])))==(0,)*32, 'increase valuation precision'
            zero_c_count+=1
    B=max(va[i] for i in nonzero)-min(va[i] for i in nonzero)
    returns=[]; power=one
    for n in range(1,B+1):
        power=mul(power,u); pairs=mapping(power)
        returns.append(dict(power=n,mapping=pairs))
    print('ORBIT_VALUATIONS '+json.dumps(dict(first=sorted(Counter(va[i] for i in nonzero).items()),
        conjugate=sorted(Counter(vb[i] for i in nonzero).items()),all_return_bound=B,
        returns=[(r['power'],len(r['mapping'])) for r in returns],norms=len(norm_index),zero_constants=zero_c_count)),flush=True)
    prime,images,bars=filter_map(table)
    assert prime<10**9
    def ev(p,ims):return sum(x.numerator*pow(x.denominator,-1,prime)*im for x,im in zip(p,ims))%prime
    pe=np.array([ev(p,images) for p in pts],dtype=np.int64)
    pb=np.array([ev(p,bars) for p in pts],dtype=np.int64)
    ue=ev(u,images); ub=ev(u,bars); assert ue*ub%prime==1
    a=np.array(va,dtype=np.int64); b=np.array(vb,dtype=np.int64)
    rn=np.array(residues,dtype=np.int64)
    valuation_table=np.array([v2(x) if x else bits for x in range(mod)],dtype=np.int64)
    exponent_limit=2*max(max(abs(va[i]),abs(vb[i])) for i in nonzero)+bits+8
    up=np.array([pow(ue,n,prime) for n in range(-exponent_limit,exponent_limit+1)],dtype=np.int64)
    bp=np.array([pow(ub,n,prime) for n in range(-exponent_limit,exponent_limit+1)],dtype=np.int64)
    candidates=set()
    for lo in range(0,count,64):
        hi=min(lo+64,count)
        C=(rn[lo:hi,None,:]+rn[None,:,:]-np.array([16,0,0,0]))%mod
        vc=np.min(valuation_table[C],axis=2)-4
        present=np.any(C,axis=2)
        A=a[lo:hi,None]+b[None,:]
        BB=b[lo:hi,None]+a[None,:]
        for n,valid in (((A-BB)//2, (A-BB)%2==0),(A-vc,present),(vc-BB,present)):
            valid=valid.copy(); valid &= (n>=0)
            valid[:,zero]=False
            if lo<=zero<hi:valid[zero-lo,:]=False
            assert np.all(np.abs(n[valid])<=exponent_limit)
            safe=np.where(valid,n,0)+exponent_limit
            dx=(up[safe]*pe[lo:hi,None]-pe[None,:])%prime
            dy=(bp[safe]*pb[lo:hi,None]-pb[None,:])%prime
            hit=valid & ((dx*dy)%prime==1)
            rows,cols=np.nonzero(hit)
            for i,j in zip(rows.tolist(),cols.tolist()):
                nn=int(n[i,j]);ii=lo+i
                if nn==0 and ii>=j:continue
                candidates.add((nn,ii,j))
        if lo%1024==0:print('ORBIT_SIEVE '+json.dumps(dict(rows=hi,candidates=len(candidates))),flush=True)
    print('ORBIT_CANDIDATES '+json.dumps(dict(count=len(candidates),powers=sorted(Counter(n for n,i,j in candidates).items()))),flush=True)
    exact=[]; maxpower=max(n for n,i,j in candidates); power=one
    base_den=math.lcm(*(x.denominator for p in pts for x in p))
    ints=[tuple(int(x*base_den) for x in p) for p in pts]
    standard=[tuple(Q(int(i==j)) for i in range(32)) for j in range(32)]
    for n in range(maxpower+1):
        if n:power=mul(power,u)
        chosen=sorted((i,j) for nn,i,j in candidates if nn==n)
        if not chosen:continue
        columns=[mul(power,e) for e in standard]
        scale=math.lcm(*(x.denominator for col in columns for x in col))
        sparse=[[(i,int(x*scale)) for i,x in enumerate(col) if x] for col in columns]
        cache={}
        for i,j in chosen:
            if i not in cache:
                acc=[0]*32
                for value,col in zip(ints[i],sparse):
                    for k,co in col:acc[k]+=value*co
                cache[i]=acc
            d=[x-scale*y for x,y in zip(cache[i],ints[j])]
            if product_twice(d,conjugate_twice(d),table)==[4*(base_den*scale)**2]+[0]*31:
                exact.append((n,i,j))
        print('ORBIT_EXACT '+json.dumps(dict(power=n,candidates=len(chosen),edges=sum(nn==n for nn,i,j in exact))),flush=True)
    origin_neighbors=[i for i,n in enumerate(norms) if n==one]
    all_zero={(min(i,j),max(i,j)) for n,i,j in exact if n==0}
    all_zero.update((min(zero,j),max(zero,j)) for j in origin_neighbors)
    assert all_zero==set(c['edges'])
    def quotient(period):
        parent=list(range(count*period))
        def find(x):
            while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
            return x
        def union(x,y):
            x,y=find(x),find(y)
            if x!=y:parent[max(x,y)]=min(x,y)
        for t in range(period):union(zero,zero+count*t)
        for rr in returns:
            n=rr['power']
            for i,j in rr['mapping']:
                for t in range(period):union(i+count*((t+n)%period),j+count*t)
        roots=sorted({find(i) for i in range(count*period)})
        idx={r:j for j,r in enumerate(roots)}
        labels=[idx[find(i)] for i in range(count*period)]
        edges=set()
        for n,i,j in exact:
            for t in range(period):edges.add(tuple(sorted((labels[i+count*((t+n)%period)],labels[j+count*t]))))
        for j in origin_neighbors:
            for t in range(period):edges.add(tuple(sorted((labels[zero],labels[j+count*t]))))
        return roots,labels,sorted(edges)
    histories=[]; positive=None
    for period in (1,2,3,5):
        roots,labels,edges=quotient(period)
        entry=dict(period=period,vertices=len(roots),edges=len(edges))
        if any(i==j for i,j in edges):entry['status']='LOOP_RESTRICTED_PERIOD';histories.append(entry);continue
        clauses=[]
        for i in range(len(roots)):
            vv=[5*i+k+1 for k in range(5)];clauses.append(vv)
            clauses.extend([-vv[a],-vv[b]] for a in range(5) for b in range(a+1,5))
        clauses.extend([-5*i-k-1,-5*j-k-1] for i,j in edges for k in range(5))
        clauses.append([5*labels[zero]+1])
        with Solver(name='cadical195',bootstrap_with=clauses) as solver:
            solver.conf_budget(100000)
            answer=solver.solve_limited();entry['status']='SAT' if answer is True else 'UNKNOWN' if answer is None else 'UNSAT_RESTRICTED_PERIOD_UNCHECKED'
            entry['stats']=solver.accum_stats()
            if answer is True:
                model=set(v for v in solver.get_model() if v>0)
                word=''.join(str(next(k for k in range(5) if 5*i+k+1 in model)) for i in range(len(roots)))
                assert all(word[i]!=word[j] for i,j in edges)
                full=[''.join(word[labels[i+count*t]] for i in range(count)) for t in range(period)]
                positive=dict(period=period,words=full,quotient_vertices=len(roots),quotient_edges=len(edges))
        histories.append(entry);print('ORBIT_COLOR '+json.dumps(entry),flush=True)
        if positive:break
    out=dict(schema=1,experiment='E100_PRODUCER',source_sha='5cd6b56373e9e92d686101a87028e213747feaf2',geometry=parent['geometry'],
        bits=bits,valuation_first=va,valuation_conjugate=vb,return_bound=B,returns=returns,
        unit_cross_edges=exact,origin_neighbors=origin_neighbors,search=histories,result=positive,
        scope='Exploratory finite exponent sieve and periodic orbit coloring; independently verify before theorem use')
    raw=json.dumps(out,separators=(',',':')).encode()
    path=root/'certificates/dyadic_cyclic_orbit_probe.json.gz'
    path.write_bytes(gzip.compress(raw,mtime=0))
    summary=dict(geometry=parent['geometry'],bits=bits,return_bound=B,returns=[(r['power'],len(r['mapping'])) for r in returns],
        cross_edges=len(exact),cross_histogram=sorted(Counter(n for n,i,j in exact).items()),
        origin_neighbors=len(origin_neighbors),search=histories,result=bool(positive),
        certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start)
    (root/'certificates/dyadic_cyclic_orbit_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('ORBIT_FINAL '+json.dumps(summary),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    run(Path(__file__).resolve().parents[1])
