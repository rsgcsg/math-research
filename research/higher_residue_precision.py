"""Export finite local-ring calibration using two projective circle charts.

The general proof is in docs/proofs/higher_residue_precision.md. This exporter
does not search for colorings or estimate floating-point eigenvalues.
"""
import hashlib
import json
from itertools import product
from pathlib import Path


def ring(p, n, e):
    # e=1: Z/p^n; e=2: Z[sqrt(p)]/(sqrt(p)^n).
    moduli = (p**n,) if e == 1 else (p**((n+1)//2), p**(n//2))
    elements = list(product(*(range(m) for m in moduli)))
    def add(x, y):
        return tuple((a+b) % m for a,b,m in zip(x,y,moduli))
    def neg(x):
        return tuple(-a % m for a,m in zip(x,moduli))
    def mul(x, y):
        if e == 1:
            return (x[0]*y[0] % moduli[0],)
        a,b=x; c,d=y
        return ((a*c+p*b*d) % moduli[0], (a*d+b*c) % moduli[1])
    def inv(x):
        if e == 1:
            return (pow(x[0],-1,moduli[0]),)
        a,b=x
        norm_inv=pow(a*a-p*b*b,-1,moduli[0])
        return (a*norm_inv % moduli[0], -b*norm_inv % moduli[1])
    one=(1,)+(0,)*(e-1)
    circle=[]
    # [1:t] for all t, then [s:1] only for s in the maximal ideal.
    for a,b in [(one,t) for t in elements]+[(s,one) for s in elements if s[0] % p == 0]:
        aa,bb=mul(a,a),mul(b,b)
        den=inv(add(aa,bb))
        circle.append((mul(add(aa,neg(bb)),den),mul(add(mul(a,b),mul(a,b)),den)))
    return sorted(circle)


def digest(circle):
    return hashlib.sha256(json.dumps(circle,separators=(',',':')).encode()).hexdigest()


def run():
    cases=[]
    specifications=[(3,2,1),(3,3,1),(3,4,1),(7,2,1),(11,2,1),
                    (131,2,1),(3,2,2),(3,3,2),(3,4,2),(7,2,2)]
    for p,n,e in specifications:
        circle=ring(p,n,e)
        assert len(circle) == len(set(circle)) == (p+1)*p**(n-1)
        cases.append(dict(p=p, precision=n, ramification=e, ring_size=p**n,
                          circle_size=len(circle), circle_sha256=digest(circle),
                          verification_mode='symbolic_last_layer' if p == 131 else 'all_primitive_characters'))
    return dict(schema=1, cases=cases, rational_crt_moduli=[9,49],
                rational_crt_direction_pairs=672,
                scope='Finite mixed-characteristic calibrations; general q and arbitrary precision follow from the written tangent-cancellation proof')


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    data=run()
    (root/'certificates/higher_residue_precision.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(cases=len(data['cases']),circle_points=sum(c['circle_size'] for c in data['cases']))))
