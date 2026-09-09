"""Independent finite-ring circle, character-cancellation and CRT checks.

Circle geometry is rebuilt by direct squaring, not the exporter's charts.
All small-ring primitive characters use exact cyclotomic coefficient counts.
No floating-point spectral claim and no inference of real-plane color bounds.
"""
from collections import defaultdict
from itertools import product
from pathlib import Path
import hashlib
import json


def verify(root):
    data=json.loads((root/'certificates/higher_residue_precision.json').read_text())
    assert data['schema'] == 1
    expected={(3,2,1),(3,3,1),(3,4,1),(7,2,1),(11,2,1),
              (131,2,1),(3,2,2),(3,3,2),(3,4,2),(7,2,2)}
    seen=set(); character_checks=0; symbolic_pairs=0; total_points=0
    saved_circles={}; report=[]
    for case in data['cases']:
        p,n,e=case['p'],case['precision'],case['ramification']
        assert (p,n,e) in expected-seen
        seen.add((p,n,e))
        mods=[p**n] if e == 1 else [p**((n+1)//2),p**(n//2)]
        elements=list(product(*(range(m) for m in mods)))
        assert len(elements) == case['ring_size'] == p**n
        def square(x):
            if e == 1:
                return (x[0]**2 % mods[0],)
            return ((x[0]**2+p*x[1]**2) % mods[0], 2*x[0]*x[1] % mods[1])
        roots=defaultdict(list)
        for x in elements:
            roots[square(x)].append(x)
        circle=[]
        for x in elements:
            xx=square(x)
            complement=tuple(((1 if j == 0 else 0)-a) % mods[j] for j,a in enumerate(xx))
            circle.extend((x,y) for y in roots[complement])
        circle.sort()
        assert len(circle) == case['circle_size'] == (p+1)*p**(n-1)
        assert hashlib.sha256(json.dumps(circle,separators=(',',':')).encode()).hexdigest() == case['circle_sha256']
        total_points += len(circle)
        if e == 1:
            saved_circles[p**n]=circle
        prevmods=[p**(n-1)] if e == 1 else [p**(n//2),p**((n-1)//2)]
        fibers=defaultdict(list)
        for x,y in circle:
            lower=tuple(tuple(a % m for a,m in zip(z,prevmods)) for z in (x,y))
            fibers[lower].append((x,y))
        assert len(fibers) == (p+1)*p**(n-2)
        assert all(len(v) == p for v in fibers.values())

        # Uniformizer^(n-1) is in coefficient 0 or 1, depending on parity.
        coefficient=0 if e == 1 else (n-1) % 2
        step=p**((n-1)//e)
        for points in fibers.values():
            anchor=points[0]
            base=tuple(z[0] % p for z in anchor)
            differences=[]
            for point in points:
                tangent=[]
                for z,z0 in zip(point,anchor):
                    delta=[(a-b) % m for a,b,m in zip(z,z0,mods)]
                    assert all(d == 0 for j,d in enumerate(delta) if j != coefficient)
                    assert delta[coefficient] % step == 0
                    tangent.append(delta[coefficient]//step)
                differences.append(tuple(tangent))
            expected_tangent={(u,v) for u,v in product(range(p),repeat=2)
                              if (base[0]*u+base[1]*v) % p == 0}
            assert set(differences) == expected_tangent and len(expected_tangent) == p

        primitive=0
        if p != 131:
            assert case['verification_mode'] == 'all_primitive_characters'
            period=mods[0]
            weights=[period//m for m in mods]
            stride=period//p
            for ax,ay in product(elements,repeat=2):
                leading=(ax[coefficient] % p,ay[coefficient] % p)
                if leading == (0,0):
                    continue
                primitive += 1
                canceled=[0]*period
                survivors=0
                for x,y in circle:
                    if (leading[0]*y[0]-leading[1]*x[0]) % p == 0:
                        survivors += 1
                    else:
                        phase=sum(w*(a*b+c*d) for w,a,b,c,d in zip(weights,ax,x,ay,y)) % period
                        canceled[phase] += 1
                # Exactly a multiple of Phi_(p^h), hence vanishes at a primitive
                # p^h-th root of unity. This is an integer identity, not a tolerance.
                assert all(len({canceled[r+j*stride] for j in range(p)}) == 1 for r in range(stride))
                assert survivors in (0,2*p**(n-1))
            assert primitive == p**(2*n)-p**(2*(n-1))
            character_checks += primitive
        else:
            assert case['verification_mode'] == 'symbolic_last_layer'
            base_circle={(x[0] % p,y[0] % p) for x,y in circle}
            assert len(base_circle) == p+1
            assert all({d*t % p for t in range(p)} == set(range(p)) for d in range(1,p))
            for a,b in product(range(p),repeat=2):
                if a == b == 0:
                    continue
                survivors=sum((a*y-b*x) % p == 0 for x,y in base_circle)
                assert survivors in (0,2)
                symbolic_pairs += len(base_circle)
        report.append(dict(p=p,precision=n,ramification=e,circle_points=len(circle),
                           primitive_characters_checked=primitive))
    assert seen == expected and character_checks == 32328
    assert symbolic_pairs == 2265120

    # Modulo prime powers, (-1, nilpotent) is not necessarily (-1,0).
    # Use TWO UNIT-DENOMINATOR CHARTS, not the field-only exceptional point.
    assert data['rational_crt_moduli'] == [9,49]
    charts=[]
    for modulus in (9,49):
        prime=3 if modulus == 9 else 7
        entries=[]
        for (x,),(y,) in saved_circles[modulus]:
            a,b=(1+x,y) if (1+x) % prime else (y,1-x)
            den=a*a+b*b
            assert den % prime
            assert (a*a-b*b)*pow(den,-1,modulus) % modulus == x
            assert 2*a*b*pow(den,-1,modulus) % modulus == y
            entries.append((a,b,x,y))
        charts.append(entries)
    pairs=0
    for (a,b,x,y),(c,d,u,v) in product(*charts):
        A=a+9*((c-a)*pow(9,-1,49) % 49)
        B=b+9*((d-b)*pow(9,-1,49) % 49)
        X,Y,D=A*A-B*B,2*A*B,A*A+B*B
        assert D and X*X+Y*Y == D*D
        assert all((X*pow(D,-1,m) % m,Y*pow(D,-1,m) % m) == target
                   for m,target in ((9,(x,y)),(49,(u,v))))
        pairs += 1
    assert pairs == data['rational_crt_direction_pairs'] == 672
    assert ((8,),(3,)) in saved_circles[9]
    return dict(status='VERIFIED_HIGHER_RESIDUE_PRECISION_CALIBRATION',
                local_ring_cases=len(report), circle_points=total_points,
                exact_primitive_character_checks=character_checks,
                symbolic_leading_frequency_point_checks=symbolic_pairs,
                prime_power_CRT_edge_lifts=pairs, cases=report,
                scope='Written T056/T057 prove arbitrary residue degree, ramification and finite precision; no real-plane lower bound')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
