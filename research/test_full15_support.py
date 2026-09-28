"""Standard-library semantic calibrations and independent six-case replay."""
from pathlib import Path
from itertools import product,combinations
from collections import Counter
from fractions import Fraction
from copy import deepcopy
import sys,json,subprocess
from audit_full_law_preparation import reconstruct,unique_keys
from full15_support_cnf import build,SPLIT_TYPES,UNIFORM_CASES
from verify_full15_support import verify,load_certificate,validate_header,validate_case,CASES
from closed_binary_proof import parse_binary
from ternary_mass_bound import check as mass_check


def partition(values):
    names={};return tuple(names.setdefault(v,len(names)) for v in values)


def small_sat(clauses,assumptions):
    """Tiny independent DPLL; used only on the small semantic truth tables."""
    def rec(rows,value):
        while True:
            reduced=[];units=[]
            for row in rows:
                if any(value.get(abs(x))==(x>0) for x in row):continue
                new=[x for x in row if abs(x) not in value]
                if not new:return False
                if len(new)==1:units.append(new[0])
                reduced.append(new)
            if not reduced:return True
            if not units:break
            for x in units:
                v=abs(x);sign=x>0
                if v in value and value[v]!=sign:return False
                value[v]=sign
            rows=reduced
        lit=min(reduced,key=len)[0]
        for sign in (lit>0,lit<0):
            vv=dict(value);vv[abs(lit)]=sign
            if rec(reduced,vv):return True
        return False
    value={}
    for x in assumptions:
        if abs(x) in value and value[abs(x)]!=(x>0):return False
        value[abs(x)]=x>0
    return rec(clauses,value)


def semantic_tests():
    splitting=0
    for a in product(range(3),repeat=3):
        for b in product(range(3),repeat=3):
            left=Counter({});right=Counter({})
            for i,w in enumerate((2,1,1)):left[a[i]]+=w;right[b[i]]+=w
            modes=any(all(a[i]==b[j] for i,j in edges) for edges in SPLIT_TYPES)
            assert modes==(left==right);splitting+=1
    table=[];words=list(product(range(2),repeat=3))
    for edge_set in ([],[[0,2]]):
        data=dict(points=[0,1,2],edges=edge_set,mappings=[[[0,1],[1,2]],[[0,0],[2,1]]])
        for kind,sigma,arcs in CASES:
            built=build(data,arcs,3,kind,symmetry=False,k=2,eta=0)
            clauses=list(built['clauses']);tested=sat=0
            for ws in product(words,repeat=3):
                proper=all(ws[s][a]!=ws[s][b] for s in range(3) for a,b in edge_set)
                eta_ok=all(ws[t][b]==ws[s][a] for s,t in arcs for a,b in data['mappings'][0])
                weights=[1,1,1] if kind=='uniform' else [2,1,1]
                left=Counter();right=Counter()
                for w,weight in zip(ws,weights):
                    left[partition(w[a] for a,b in data['mappings'][1])]+=weight
                    right[partition(w[b] for a,b in data['mappings'][1])]+=weight
                expected=proper and eta_ok and left==right
                assumptions=[2*built['components'][s*3+v]+ws[s][v]+1 for s in range(3) for v in range(3)]
                actual=small_sat(clauses,assumptions)
                assert actual==expected,(edge_set,kind,sigma,ws,expected,actual)
                tested+=1;sat+=int(actual)
            table.append(dict(edges=edge_set,kind=kind,eta_case=sigma,assignments=tested,positive=sat))
    rows=[r for r in product((-1,0,1),repeat=3) if any(r) and next(v for v in r if v)>0]
    types=set()
    for a,b in combinations(rows,2):
        v=tuple(a[(j+1)%3]*b[(j+2)%3]-a[(j+2)%3]*b[(j+1)%3] for j in range(3))
        if all(x>0 for x in v) or all(x<0 for x in v):types.add(tuple(Fraction(x,sum(v)) for x in v))
    expected={(Fraction(1,3),)*3}|{tuple(Fraction(1,2) if i==j else Fraction(1,4) for i in range(3)) for j in range(3)}
    assert types==expected
    return dict(weighted_transport_assignments=splitting,CNF_color_assignments=sum(r['assignments'] for r in table),tables=table,three_atom_weight_types=sorted([list(map(str,t)) for t in types]))


def parser_tests():
    assert parse_binary(b'a\x02\x05\x00a\x00')==['1 -2 0','0']
    rejected=0
    for raw in (b'a',b'a\x02',b'a\x80',b'a\x01\x00',b'x\x00',b'a\x80\x81',b'a'+b'\x80'*10,b'a\x00d'):
        try:parse_binary(raw)
        except ValueError:rejected+=1
        else:raise AssertionError('malformed proof accepted')
    try:json.loads('{"a":1,"a":2}',object_pairs_hook=unique_keys)
    except ValueError:rejected+=1
    else:raise AssertionError('duplicate JSON key')
    return rejected


def main():
    if not __debug__:raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    semantics=semantic_tests();mass=mass_check();parser_rejections=parser_tests()
    data,summary=reconstruct(root);cert=load_certificate(root)
    refused=[]
    def reject(name,call):
        try:call()
        except (ValueError,AssertionError,KeyError,TypeError):refused.append(name)
        else:raise AssertionError('accepted mutation '+name)
    for name,change in [
        ('schema',lambda c:c.update(schema='wrong')),
        ('geometry',lambda c:c.update(input_semantic_sha256='0'*64)),
        ('omit_weighted_split',lambda c:c['cases'].pop()),
        ('duplicate_case',lambda c:c['cases'].__setitem__(5,deepcopy(c['cases'][4]))),
        ('case_bool',lambda c:c['cases'][0]['eta_case'].__setitem__(0,False)),
        ('wrong_motion',lambda c:c['full_motions'].__setitem__(14,13)),
        ('overclaim',lambda c:c.update(conclusion='no unrestricted law'))]:
        c=deepcopy(cert);change(c);reject(name,lambda:validate_header(c,summary))
    def case_mutations(c,b,digest):
        prefix=c['kind']+':'+','.join(map(str,c['eta_case']))
        mutations=[('CNF_hash',lambda d:d.update(cnf_sha256='0'*64)),
                   ('variable_count',lambda d:d.update(nv=True)),
                   ('clause_count',lambda d:d.update(clauses=d['clauses']-1)),
                   ('initial_range',lambda d:d['initial_clause_ids'].__setitem__(0,0)),
                   ('initial_bool',lambda d:d['initial_clause_ids'].__setitem__(0,True)),
                   ('no_contradiction',lambda d:d['rup_clauses'].pop()),
                   ('premature_contradiction',lambda d:d.update(rup_clauses=[[]])),
                   ('new_variable',lambda d:d['rup_clauses'].__setitem__(0,[b['nv']+1])),
                   ('after_contradiction',lambda d:d['rup_clauses'].append([1]))]
        for name,change in mutations:
            d=deepcopy(c);change(d);reject(prefix+':'+name,lambda:validate_case(d,b,digest))
    report=verify(cert,data,summary,case_mutations)
    for name in ('test_full15_support.py','verify_full15_support.py','ternary_mass_bound.py'):
        r=subprocess.run([sys.executable,'-O',str(root/'research'/name)],capture_output=True,text=True,timeout=20)
        assert r.returncode!=0 and 'requires assertions' in r.stderr
        refused.append('optimized:'+name)
    assert not any(m=='pysat' or m.startswith('pysat.') for m in sys.modules)
    report.update(semantic_tests=semantics,mass_bound=mass,parser_rejections=parser_rejections,rejected_mutations=refused)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
