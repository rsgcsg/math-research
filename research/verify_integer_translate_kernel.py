"""Complete standard-library contact reconstruction of union_(n in Z) (Y+n).

The kernel replay alone is not a coloring result. The separate formula replay
checks every contact type and then gives a positive infinite coloring.
No negative periodic search is interpreted as a lower bound.
"""
from pathlib import Path
from array import array
from collections import Counter
from copy import deepcopy
import sys,json,gzip,math,subprocess
from audit_full_law_preparation import reconstruct,unique_keys
from verify_quintic_core_probe import RAD,multiplication_twice,conjugate_twice,product_twice,digest
from verify_anchored_eta import require


def prime(n):
    return type(n) is int and n>2 and n%2 and all(n%d for d in range(3,math.isqrt(n)+1,2))


def replay(c,data,summary):
    require(c['schema']=='integer-translate-kernel-v1','schema')
    require(c['input_semantic_sha256']==summary['semantic_sha256'],'input binding')
    d=data['denominator'];require(c['denominator']==d and type(c['denominator']) is int,'denominator')
    Q=sorted({(p[0]%d,*p[1:]) for p in data['points']});N=len(Q)
    B=max((sum(abs(x)*(math.isqrt(RAD[j%8])+(math.isqrt(RAD[j%8])**2<RAD[j%8])) for j,x in enumerate(q))+d-1)//d for q in Q)
    M=2*B+1
    require(all(type(c[k]) is int for k in ('N','bound','offset_bound')) and c['N']==N and c['bound']==B and c['offset_bound']==M and c['q_sha256']==digest(Q),'representatives and rigorous bound')
    require(isinstance(c['gains'],list) and all(isinstance(row,list) and len(row)==3 and all(type(x) is int for x in row) for row in c['gains']),'gain types')
    p=c['prime'];require(prime(p) and p>2*M and d%p,'validated prime')
    im=c['images'];bars=c['bars'];require(len(im)==32 and all(type(x) is int and 0<=x<p for x in im) and im[0]==1,'unital residue images')
    tab=multiplication_twice();require(all(sum(z*im[k] for k,z in row)%p==2*im[i]*im[j]%p for (i,j),row in tab.items()),'all basis products')
    actual_bars=[sum(x*y for x,y in zip(conjugate_twice([int(i==j) for j in range(32)]),im))*pow(2,-1,p)%p for i in range(32)]
    require(bars==actual_bars and all(type(x) is int for x in bars),'conjugate residue images')
    residues=[(sum(x*y for x,y in zip(q,im))%p,sum(x*y for x,y in zip(q,bars))%p) for q in Q]
    roots=array('i',[-1])*p
    for x in range((p+1)//2):roots[x*x%p]=x
    inverse=pow(2*d,-1,p);target=[4*d*d]+[0]*31;gains={(i,i,1) for i in range(N)};candidates=0
    # Scalar integer loop, unlike the NumPy production path.
    for i,(a,b) in enumerate(residues):
        for j in range(i+1,N):
            aa,bb=residues[j];dx=a-aa;dy=b-bb
            rr=roots[((dx-dy)**2+4*d*d)%p]
            if rr<0:continue
            for r in (rr,-rr):
                n=((dx+dy+r)*inverse)%p
                if 2*n>p:n-=p
                if abs(n)>M:continue
                candidates+=1;v=[x-y for x,y in zip(Q[i],Q[j])];v[0]-=n*d
                if product_twice(v,conjugate_twice(v),tab)==target:gains.add((i,j,n))
    gains=sorted(gains)
    # Independent calibration: every original Y edge must have a gain.
    where={q:i for i,q in enumerate(Q)};gainset=set(gains)
    for a,b in data['edges']:
        x,y=data['points'][a],data['points'][b]
        qa=(x[0]%d,*x[1:]);qb=(y[0]%d,*y[1:])
        i,j=where[qa],where[qb];shift=(y[0]-qb[0]-x[0]+qa[0])//d
        if i>j:i,j,shift=j,i,-shift
        if i==j:shift=abs(shift)
        require((i,j,shift) in gainset,'original Y edge absent from the kernel')
    # Check the quadratic sign against direct modular norm evaluation.
    calibrated=0
    for i,j in [(a,b) for a in range(6) for b in range(a+1,8)]:
        dx=residues[i][0]-residues[j][0];dy=residues[i][1]-residues[j][1]
        rr=roots[((dx-dy)**2+4*d*d)%p]
        computed=set()
        if rr>=0:
            for r in (rr,-rr):
                value=((dx+dy+r)*inverse)%p
                if 2*value>p:value-=p
                if abs(value)<=M:computed.add(value)
        brute={n for n in range(-M,M+1) if ((dx-n*d)*(dy-n*d)-d*d)%p==0}
        require(computed==brute,'quadratic integer-root calibration');calibrated+=1
    require(c['gains']==[list(e) for e in gains] and c['gain_sha256']==digest(gains),'complete gain list')
    return dict(status='PASS',representatives=N,rigorous_search_offset=M,largest_actual_offset=max(abs(g[2]) for g in gains),
                complete_contacts=len(gains),offset_histogram=dict(sorted(Counter(e[2] for e in gains).items())),q_sha256=digest(Q),gain_sha256=digest(gains),
                exact_modular_candidates=candidates,original_edge_checks=len(data['edges']),quadratic_calibrations=calibrated,chromatic_number=None,
                scope='All integer translates of this Y: complete exact unit contacts. No chromatic conclusion is inferred from failed periodic searches.')


def formula_replay(c,data,kernel):
    require(c['schema']=='integer-translate-five-coloring-v1','formula schema')
    require(c['gain_sha256']==kernel['gain_sha256'] and c['q_sha256']==kernel['q_sha256'],'formula kernel binding')
    require(type(c['color_shift']) is int and c['color_shift']==1,'color shift')
    w=c['word'];require(type(w) is str and len(w)==kernel['N'] and set(w)<=set('01234'),'formula word')
    import hashlib
    require(hashlib.sha256(w.encode()).hexdigest()==c['word_sha256'],'word digest')
    require(all(int(w[a])!=(int(w[b])+n)%5 for a,b,n in kernel['gains']),'all infinite-contact types')
    from collections import defaultdict
    d=data['denominator'];Q=sorted({(p[0]%d,*p[1:]) for p in data['points']});index={p:i for i,p in enumerate(Q)}
    windows=[]
    for copies in [1,2,3,5]:
        points=sorted({(p[0]+r*d,*p[1:]) for p in data['points'] for r in range(copies)})
        fibers=defaultdict(dict);colors=[]
        for pos,p in enumerate(points):
            q=(p[0]%d,*p[1:]);i=index[q];t=(p[0]-q[0])//d
            fibers[i][t]=pos;colors.append((int(w[i])+t)%5)
        edges=set()
        for a,b,n in kernel['gains']:
            for t,v in fibers[a].items():
                if t+n in fibers[b]:edges.add(tuple(sorted((v,fibers[b][t+n]))))
        edges=sorted(edges);require(all(colors[a]!=colors[b] for a,b in edges),'window coloring')
        record=dict(copies=copies,vertices=len(points),induced_edges=len(edges),point_sha256=digest(points),edge_sha256=digest(edges))
        if copies==1:
            require(edges==list(map(tuple,data['edges'])),'induced original Y equality')
        if copies==2:
            old=json.loads(gzip.decompress((Path(__file__).resolve().parents[1]/'certificates/unit_translate_Y.json.gz').read_bytes()))['geometry']
            require(all(record[k]==old[k] for k in ['vertices','induced_edges','point_sha256','edge_sha256']),'independent two-translate calibration')
        windows.append(record)
    return dict(status='PASS',whole_integer_translate_host_chromatic_number=5,contact_color_checks=len(kernel['gains']),formula='c(q_i+n)=(a_i+n) mod 5',color_label_period=5,finite_windows=windows,
        scope='The entire union of all integer translates of this Y. Lower bound inherits chi(Y)=5. No planar HN bound, minimum period, or full15 probability law is asserted.')


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1];data,summary=reconstruct(root)
    cert=json.loads(gzip.decompress((root/'certificates/integer_translate_kernel.json.gz').read_bytes()),object_pairs_hook=unique_keys)
    report=replay(cert,data,summary)
    formula=json.loads((root/'certificates/integer_translate_five_coloring.json').read_text(),object_pairs_hook=unique_keys)
    report['coloring']=formula_replay(formula,data,cert)
    for key,value in [('word','0'),('color_shift',True),('gain_sha256','bad'),('word_sha256','bad')]:
        wrong=dict(formula);wrong[key]=value
        try:formula_replay(wrong,data,cert)
        except (ValueError,AssertionError):pass
        else:raise AssertionError('accepted formula mutation '+key)
    for key,value in [('schema','bad'),('input_semantic_sha256','bad'),('offset_bound',0),('q_sha256','bad'),('prime',15)]:
        c=deepcopy(cert);c[key]=value
        try:replay(c,data,summary)
        except (ValueError,AssertionError):pass
        else:raise AssertionError('accepted mutation '+key)
    result=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True,timeout=20)
    require(result.returncode!=0 and 'requires assertions' in result.stderr,'optimized mode')
    report['rejected_mutations']=10
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
