"""Independent long-chain proof checker using global two-layer coordinates.

No import of long_chain.py. A certificate is a family of nonempty frame sets
closed downwards under all allowed forward images, so it certifies all lengths.
"""
from itertools import permutations, product
import json


def verify(path):
    data=json.loads(path.read_text())
    assert data['status']=='CLOSED_NONEMPTY_INVARIANT'
    frames=[(0,)+p for p in permutations(range(1,6))]
    types=list(product((0,-1),repeat=2))
    roots={(m,n) for m in range(-2,3) for n in range(-2,3) if m*m+m*n+n*n==3}
    def local_color(m,n,a):
        if m%2==0:
            return n%3
        s={-1:0,0:a}
        return 3+(n+s[(m-1)//2])%3
    domains={t:{i for i,p in enumerate(frames) if all(
        p[local_color(m,n,t[0])]!=local_color(m,n,t[1]) for m,n in roots)} for t in types}
    assert all(len(d)==53 for d in domains.values())
    transitions={}
    for t,nt in product(types,repeat=2):
        a,b=t
        aa,bb=nt
        # q is a canonical frame at layer 1. Convert it back to the common
        # physical/global palette and to the original layer-1 color indices.
        raw_next=[]
        for q in frames:
            p=[]
            for color in range(6):
                shifted=(color+1)%3 if color<3 else 3+(color-3+1)%3
                out=q[shifted]
                restored=(out-1)%3 if out<3 else 3+(out-3-1+b)%3
                p.append(restored)
            raw_next.append(p)
        # Validate the normalization at the actual shared point u=(2,-1)
        # and all six surrounding nonpublic seam contacts.
        physical_next=set()
        for qi,p in enumerate(raw_next):
            if p[2]!=2:
                continue
            ok=True
            for dm,dn in roots:
                m,n=2+dm,-1+dn
                if m%2==0:
                    layer_color=central_color=n%3
                else:
                    j=(m-1)//2
                    layer_color=3+(n+{0:0,1:aa}[j])%3
                    central_color=3+(n+{0:b,1:b+bb}[j])%3
                if p[layer_color]==central_color:
                    ok=False
            if ok:
                physical_next.add(qi)
        assert physical_next==domains[nt]
        for omitted in [-1]+[r for r in range(3) if r!=(-a)%3]:
            pairs=[(i,i) for i in range(3)]+[(3+i,3+j) for i,j in product(range(3),repeat=2)
                                                      if (j-i)%3!=omitted]
            transitions[t,nt,omitted]={i:{j for j in domains[nt] if all(
                frames[i][x]!=raw_next[j][y] for x,y in pairs)} for i in domains[t]}
    invariant={(t,f):[] for t in types for f in range(3)}
    for row in data['invariant']:
        key=tuple(row['node_type']),row['full_run']
        assert key in invariant
        states=set(row['frames'])
        assert states and len(states)==len(row['frames'])
        assert states<=domains[key[0]] and states not in invariant[key]
        invariant[key].append(states)
    assert all(invariant.values())
    assert all(any(s<=domains[t] for s in invariant[t,0]) for t in types)
    checked=0
    for (t,f),sets in invariant.items():
        for states in sets:
            for nt in types:
                for omitted in [-1]+[r for r in range(3) if r!=(-t[0])%3]:
                    if omitted==-1 and f==2:
                        continue
                    nf=f+1 if omitted==-1 else 0
                    image=set().union(*(transitions[t,nt,omitted][i] for i in states))
                    assert any(target<=image for target in invariant[nt,nf])
                    checked+=1
    # Stronger exact reset identities expose the mechanism behind the table.
    f1={t:{i for i in domains[t] if 1 not in frames[i][:3]} for t in types}
    f2={t:{i for i in f1[t] if 2 in frames[i][:3]} for t in types}
    reset={t:[domains[t]] for t in types}
    def image(states,t,nt,omitted):
        return set().union(*(transitions[t,nt,omitted][i] for i in states))
    for t,nt in product(types,repeat=2):
        assert len(f1[t])==39 and len(f2[t])==11
        assert image(domains[t],t,nt,-1)==f1[nt]
        assert image(f1[t],t,nt,-1)==f2[nt]
        assert not image(f2[t],t,nt,-1)
        for omitted in [r for r in range(3) if r!=(-t[0])%3]:
            assert image(f1[t],t,nt,omitted)==domains[nt]
            target=image(f2[t],t,nt,omitted)
            assert len(target)>=50
            if target not in reset[nt]:
                reset[nt].append(target)
    for t,nt in product(types,repeat=2):
        for states in reset[t]:
            assert image(states,t,nt,-1)==f1[nt]
            for omitted in [r for r in range(3) if r!=(-t[0])%3]:
                assert image(states,t,nt,omitted)==domains[nt]
    # T022 direct four-color formulas, independent of the external source.
    directions=[(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)]
    def layer_color(k,m,n):
        return (m+n)%2,(m-k)%2
    def center_color(m,n):
        return n%2,(m+n)%2
    for k,m,n in product(range(2),repeat=3):
        for dm,dn in directions:
            assert layer_color(k,m,n)!=layer_color(k,m+dm,n+dn)
        assert layer_color(k,m,n)!=layer_color(k+1,m,n)
    for m,n in product(range(2),repeat=2):
        for dm,dn in directions:
            assert center_color(m,n)!=center_color(m+dm,n+dn)
    for k in range(2):
        assert layer_color(k,2*k,-k)==center_color(2*k,-k)
        for p,q in roots:
            assert layer_color(k,2*k+p,-k+q)!=center_color(2*k+p,-k+q)
    from exact_geometry import field,cmul,add,induced_edges
    from fractions import Fraction as F
    origin=(field(0),field(0))
    one=(field(1),field(0))
    omega=(field(F(1,2)),field(0,F(1,2)))
    tip=(add(one[0],omega[0]),add(one[1],omega[1]))
    rho=(field(F(5,6)),field(0,0,F(1,6)))
    spindle=[origin,one,omega,tip]+[cmul(rho,p) for p in (one,omega,tip)]
    edges=induced_edges(spindle)
    assert edges==[(0,1),(0,2),(0,4),(0,5),(1,2),(1,3),(2,3),(3,6),(4,5),(4,6),(5,6)]
    assert not any(all(c[u]!=c[v] for u,v in edges) for c in product(range(3),repeat=7))
    return dict(status='PASS',long_chain_invariant_sets=sum(map(len,invariant.values())),
                closure_obligations=checked,domain_size=53,after_one_full=39,
                after_two_full=11,after_three_full=0,
                reset_sets_per_type=[len(reset[t]) for t in types],
                unrestricted_host_chromatic_number=4,spindle_tricolorings_checked=3**7)


if __name__=='__main__':
    import sys
    from pathlib import Path
    if not __debug__:
        sys.exit('Do not disable assertions in a proof checker.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]/'certificates/long_chain_invariant.json'),indent=2))
