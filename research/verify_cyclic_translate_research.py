"""Independent unbounded T140/E112 contact replay in the actual field of Y.

Does not import cyclic_translate_contacts or its producer. It chooses different
integer origins and forms restricted polynomials as a three-term product with
its conjugate. Existing independent geometry and field definitions are reused.
"""
from copy import deepcopy
from itertools import combinations
from math import gcd
from pathlib import Path
import json
import subprocess
import sys
from cyclic_translate_field16 import Element, U, valuation
from verify_quintic_tau_union import verify as geometry


PAIRS=[(233,239),(5557,238),(31,193),(32,36),(0,2),(119,161),
       (230,232),(467,468),(3533,3535),(4,5),(31,118),(232,900)]
ZERO, ONE = Element.scalar(0), Element.scalar(1)


def polynomial_product(terms):
    """|sum_e terms[e] u^(e dot z)|^2 - 1, by direct multiplication."""
    result={}
    for a,x in terms.items():
        for b,y in terms.items():
            e=tuple(i-j for i,j in zip(a,b))
            result[e]=result.get(e,ZERO)+x*y.bar()
    origin=(0,)*len(next(iter(terms)))
    result[origin]=result.get(origin,ZERO)-ONE
    return {e:c for e,c in result.items() if c!=ZERO}


def independent_contacts(a,b,t):
    poly=polynomial_product({(1,0):a,(0,1):-b,(0,0):-t})
    assert len(poly) in (6,7)
    d=valuation(U); assert d==-1
    lines=set()
    for (e,x),(f,y) in combinations(sorted(poly.items()),2):
        A,B,C=d*(e[0]-f[0]),d*(e[1]-f[1]),valuation(y)-valuation(x)
        g=gcd(A,B)
        if C%g: continue
        A,B,C=A//g,B//g,C//g
        if A<0 or A==0 and B<0: A,B,C=-A,-B,-C
        lines.add((A,B,C))
    whole=set(); points=set(); roots_checked=0
    for A,B,C in sorted(lines):
        if B==0: n,m,r,s=C,0,0,1
        elif A==0: n,m,r,s=0,C,1,0
        else:
            n=(C*pow(A,-1,abs(B)))%abs(B) if abs(B)>1 else 0
            m=(C-A*n)//B; r,s=B,-A
        assert A*n+B*m==C and A*r+B*s==0 and gcd(r,s)==1
        terms={}
        for e,x in [(r,a*U**n),(s,-b*U**m),(0,-t)]:
            terms[(e,)]=terms.get((e,),ZERO)+x
        restricted=polynomial_product(terms)
        if not restricted:
            whole.add((A,B,C)); continue
        assert max(e[0] for e in restricted)-min(e[0] for e in restricted)<=4
        candidates=set()
        for (e,x),(f,y) in combinations(restricted.items(),2):
            num,den=valuation(y)-valuation(x),d*(e[0]-f[0])
            if num%den==0: candidates.add(num//den)
        for j in candidates:
            nn,mm=n+r*j,m+s*j
            z=a*U**nn-t-b*U**mm; roots_checked+=1
            if z*z.bar()==ONE: points.add((nn,mm))
    for A,B,C in whole:
        if (A,B)==(1,0): assert a*U**C==t and b*b.bar()==ONE
        elif (A,B)==(0,1): assert b*U**C==-t and a*a.bar()==ONE
        elif (A,B)==(1,-1): assert a*U**C==b and t*t.bar()==ONE
        else: raise AssertionError('non-geometric infinite component')
    points={p for p in points if not any(A*p[0]+B*p[1]==C for A,B,C in whole)}
    assert len(points)<=54
    return dict(points=[list(p) for p in sorted(points)],lines=[list(x) for x in sorted(whole)],
                all_integer_pairs=False),roots_checked


def validate(data,report,ctx):
    if not __debug__: raise RuntimeError('verification requires assertions')
    assert data['schema']=='cyclic-translate-research-v1' and data['experiment']=='E112'
    assert data['base_commit']=='ed4cfb044164b5d88413a2d53c7e030274d04bb8'
    assert data['geometry']==report['geometry'] and data['u']==U.serial()
    assert type(data['valuation_u']) is int and data['valuation_u']==valuation(U)==-1
    assert len(data['cases'])==24
    coordinates=ctx['ring']['coordinates'];results=[]
    for pos,(i,j) in enumerate(PAIRS):
        a=Element(tuple(coordinates(ctx['points'][i])));b=Element(tuple(coordinates(ctx['points'][j])))
        for mode in range(2):
            row=data['cases'][2*pos+mode]
            assert row['source_indices']==[i,j] and all(type(v) is int for v in row['source_indices'])
            if mode==0:
                assert row['kind']=='unit_translation';t=ONE
            else:
                N=(1,2,7,37)[pos%4]
                assert row['kind']=='forced_one_contact' and type(row['power']) is int and row['power']==N
                t=a*U**N-b-ONE
            assert t!=ZERO and row['translation']==t.serial()
            result,count=independent_contacts(a,b,t)
            expected=row['result']
            assert set(expected)=={'all_integer_pairs','lines','points','tested_lines','tested_parameters','root_degree_budget'}
            assert type(expected['all_integer_pairs']) is bool
            for field in ('points','lines'):
                assert all(type(v) is int for r in expected[field] for v in r)
            for key in ('tested_lines','tested_parameters','root_degree_budget'):
                assert type(expected[key]) is int and expected[key]>=0
            assert expected['tested_lines']<=21 and expected['tested_parameters']<=441 and expected['root_degree_budget']<=54
            for key in result: assert expected[key]==result[key],(pos,mode,key)
            if mode:
                assert [N,0] in result['points'] or any(A*N==C for A,B,C in result['lines'])
            results.append(dict(source_indices=[i,j],kind=row['kind'],points=result['points'],lines=result['lines'],
                                independent_parameter_checks=count))
    return dict(status='PASS',geometry=report['geometry'],cases=results,
                checked_cases=len(results),unit_translation_empty=sum(not r['points'] and not r['lines'] for r in results[::2]),
                guided_exceptional_contacts=sum(len(r['points']) for r in results[1::2]),
                scope='Twenty-four complete single-u, two-track contact sets. No claim about all Y pairs, H-prime, colorability, or ordinary HN bounds.')


def main():
    if not __debug__: raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'certificates/cyclic_translate_research.json').read_text())
    report,ctx=geometry(root,geometry_context=True)
    result=validate(data,report,ctx)
    mutations={
        'wrong-geometry':lambda c:c['geometry'].__setitem__('point_sha256','0'*64),
        'missing-case':lambda c:c['cases'].pop(),
        'missing-contact':lambda c:c['cases'][1]['result']['points'].pop(),
        'fake-line':lambda c:c['cases'][0]['result']['lines'].append([1,1,0]),
        'wrong-translation':lambda c:c['cases'][1]['translation'].__setitem__(0,'123'),
        'boolean-power':lambda c:c['cases'][1].__setitem__('power',True),
        'boolean-point-index':lambda c:c['cases'][0]['source_indices'].__setitem__(0,True),
        'wrong-base-valuation':lambda c:c.__setitem__('valuation_u',1),
    }
    rejected=[]
    for name,mutate in mutations.items():
        changed=deepcopy(data);mutate(changed)
        try: validate(changed,report,ctx)
        except (AssertionError,ValueError,IndexError,KeyError):rejected.append(name)
        else:raise AssertionError('accepted '+name)
    p=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True,timeout=10)
    assert p.returncode!=0 and 'requires assertions' in p.stderr
    rejected.append('optimized-mode');result['rejection_tests']=rejected
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
