"""Exact algebra calibration for the nu-stable localized translation module."""
from fractions import Fraction as Q
import json
from pathlib import Path
from verify_quintic_core_probe import multiplication_twice,product_twice,conjugate_twice


def verify():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    table=multiplication_twice()
    def mul(a,b):return tuple(Q(x)/2 for x in product_twice(a,b,table))
    def bar(a):return tuple(Q(x)/2 for x in conjugate_twice(a))
    one=(Q(1),)+(Q(0),)*31;eta=(Q(0),)*16+one[:16]
    z=tuple(-Q(1,2) if i==0 else -Q(1,6) if i==9 else Q(0) for i in range(32))
    nu=tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
    assert mul(nu,bar(nu))==one
    assert tuple(x+y for x,y in zip(nu,bar(nu)))==tuple(Q(5,3)*x for x in one)
    assert mul(nu,nu)==tuple(Q(5,3)*x-y for x,y in zip(nu,one))
    powers=[one]
    for _ in range(3):powers.append(mul(eta,powers[-1]))
    basis=powers+[mul(z,p) for p in powers]
    basis+= [mul(nu,p) for p in basis[:]]
    rows=[]
    for vector in basis:
        row=list(vector)
        for pivot,old in rows:
            factor=row[pivot];row=[x-factor*y for x,y in zip(row,old)]
        assert any(row)
        pivot=next(i for i,x in enumerate(row) if x);scale=row[pivot]
        rows.append((pivot,[x/scale for x in row]))
    assert len(rows)==16
    # Formal a+nu*b coordinates over Z[1/3], reduced modulo five.
    chars=[(1,2),(2,3),(2,0)]
    def value(j,lam,v):
        a,b,c,d=v;u,w=chars[j]
        return (u*a+w*b+lam*(u*c+w*d))%5
    inv3=2
    def rotate(v):
        a,b,c,d=v
        return (-c,-d,a+5*inv3*c,b+5*inv3*d)
    def omega(v):
        a,b,c,d=v
        return (-2*a+b,-3*a+b,-2*c+d,-3*c+d)
    def reflect(v):
        a,b,c,d=v
        return (a-b+5*inv3*(c-d),-b-5*inv3*d,-c+d,d)
    for j in range(3):
        for lam in (2,3):
            for i in range(4):
                v=tuple(int(i==k) for k in range(4))
                assert value(j,lam,rotate(v))==lam*value(j,lam,v)%5
                assert value(j,lam,omega(v))==value((j+1)%3,lam,v)
                assert value(j,lam,reflect(v))==value((-j)%3,(-lam)%5,v)
    alpha=tuple(Q(1,6) if i==3 else -Q(1,6) if i==9 else Q(0) for i in range(32))
    assert mul(alpha,bar(alpha))==one and mul(alpha,alpha)==bar(nu)
    assert alpha==tuple(-2*a-4*b+3*c+6*d for a,b,c,d in zip(one,z,nu,mul(nu,z)))
    root=Path(__file__).resolve().parents[1]
    parts=json.loads((root/'certificates/parts509_core.json').read_text())['points']
    def point(i):return tuple(Q(x,96) for x in sum(parts[i],[])+[0]*16)
    assert not any(point(0))
    om=tuple(-2*a-3*b for a,b in zip(one,z))
    unit=alpha;formal=(-2,-4,3,6)
    for k,index in enumerate((154,170,162)):
        assert point(index)==unit and mul(unit,bar(unit))==one
        j=(-k)%3
        assert all(value(j,lam,formal)==0 for lam in (2,3))
        unit=mul(om,unit);formal=omega(formal)
    return dict(status='PASS',rational_rank=16,localization_prime=3,
                characters=6,nu_scalars=[2,3],reflection_swaps_scalars=True,
                killed_characters=6,unit_root_indices=[154,170,162],
                scope='Six specified affine characters each kill an actual unit edge; not an unrestricted joint obstruction')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
