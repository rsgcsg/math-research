"""Independent two-pin field formulas and rank-one escaped contact calibration.

The general field-lock statements use the written proof. The old all-pairs
escape checks certify completeness of the referenced unit-contact lists;
this checker independently rebuilds their algebraic rows, not their geometry.
"""
from fractions import Fraction as F
from itertools import combinations
from math import gcd
from pathlib import Path
import json


def verify(root):
    rad = (1,3,11,33,5,15,55,165)
    zero = (F(0),)*8
    def plus(a,b):
        return tuple(x+y for x,y in zip(a,b))
    def minus(a,b):
        return tuple(x-y for x,y in zip(a,b))
    def mult(a,b):
        out = [F(0)]*8
        for i,x in enumerate(a):
            for j,y in enumerate(b):
                g = gcd(rad[i],rad[j])
                out[rad.index(rad[i]*rad[j]//(g*g))] += g*x*y
        return tuple(out)
    def dot(p,q):
        return plus(mult(p[0],q[0]),mult(p[1],q[1]))
    def sub(p,q):
        return tuple(minus(a,b) for a,b in zip(p,q))
    def J(p):
        return tuple(-x for x in p[1]),p[0]
    def read(raw):
        return tuple(F(x) for x in raw)+(F(0),)*(8-len(raw))

    base = json.loads((root/'certificates/spindle_pair_gate.json').read_text())
    p = [tuple(read(a) for a in point) for point in base['points']]
    fan = json.loads((root/'certificates/repair_pair_fan.json').read_text())
    pose_count = point_checks = 0
    for record in fan['cases']:
        cert = record['certificate']; d=read(cert['squared_anchor_distance'])
        x,y = [p[i] for i in record['anchor_pair']]
        target = sub(y,x)
        for label,raw in zip(cert['labels'],cert['scaled_poses']):
            a,b,orientation = label
            v = sub(p[b],p[a]); jv = J(v); jw = J(target)
            assert dot(v,v) == d == dot(target,target) and d != zero
            for original,out in zip(p,raw):
                z=sub(original,p[a]); alpha,beta=dot(z,v),dot(z,jv)
                expected = tuple(plus(mult(d,x[k]),plus(mult(alpha,target[k]),
                                     tuple(orientation*t for t in mult(beta,jw[k])))) for k in range(2))
                assert tuple(read(axis) for axis in out) == expected
                point_checks += 1
            pose_count += 1
    assert pose_count == 24 and point_checks == 504

    data = json.loads((root/'certificates/pose_field_lock.json').read_text())
    core = json.loads((root/'certificates/parts509_core.json').read_text())
    escape = json.loads((root/'certificates/parts509_escape_rotations.json').read_text())
    assert data['schema'] == 1
    den=core['coordinate_denominator']; assert data['core_coordinate_denominator'] == den
    pts=[tuple(read(a) for a in point) for point in core['points']]
    expected={c['radicand']:c for c in escape['cases']}
    seen=set();summary=[]
    for case in data['cases']:
        d=case['radicand']; assert d in expected and d not in seen
        seen.add(d); old=expected[d]
        assert case['cosine'] == old['cosine']
        num,denom=case['cosine']
        assert [r['pair'] for r in case['contact_rows']] == old['cross_edges']
        rows=[]
        for row in case['contact_rows']:
            i,j=row['pair']; p,q=pts[i],pts[j]
            A=tuple(2*x for x in dot(p,q))
            B=tuple(2*x for x in dot(p,J(q)))
            C=list(plus(dot(p,p),dot(q,q))); C[0]-=den*den; C=tuple(C)
            assert (A,B,C) == tuple(read(row[name]) for name in ('A','B','C'))
            assert A != zero and B == zero
            assert tuple(num*x for x in A) == tuple(denom*x for x in C)
            rows.append((A,B,C))
        assert rows and case['coefficient_rank'] == case['augmented_rank'] == 1
        first=rows[0]
        for row in rows:
            for a,b in combinations(range(3),2):
                assert minus(mult(first[a],row[b]),mult(first[b],row[a])) == zero
        summary.append(dict(radicand=d,contacts=len(rows),rank=1))
    assert seen == {7,13,17,41} and sum(c['contacts'] for c in summary) == 58

    # A rank-two actual contact calibration with c=1/2,s=sqrt3/2 in K.
    one=(F(1),)+(F(0),)*7; sqrt3=(F(0),F(1))+(F(0),)*6
    q=(one,zero); p1=q
    p2=(tuple(F(3,2)*x for x in one),tuple(x/2 for x in sqrt3))
    A1,B1=dot(p1,q),dot(p1,J(q)); A2,B2=dot(p2,q),dot(p2,J(q))
    determinant=minus(mult(A1,B2),mult(A2,B1))
    assert determinant == tuple(x/2 for x in sqrt3) and determinant != zero
    rotated=(tuple(x/2 for x in one),tuple(x/2 for x in sqrt3))
    assert dot(sub(p1,rotated),sub(p1,rotated)) == one
    assert dot(sub(p2,rotated),sub(p2,rotated)) == one
    return dict(status='VERIFIED_POSE_FIELD_LOCK_CALIBRATION',two_pin_poses=pose_count,
                two_pin_point_formulas=point_checks,escaped_contact_rows=58,cases=summary,
                actual_rank_two_example=True,
                scope='General T051/T052 use written field proof; escape all-pairs coverage is E016')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
