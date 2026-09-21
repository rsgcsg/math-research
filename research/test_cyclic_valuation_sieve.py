"""Independent Q(i) calibration for the general cyclic-orbit valuation lemma.

All arithmetic is rational. This small file is not a substitute for the actual
10077-point certificate verifier or the general proof.
"""
from fractions import Fraction as Q
from itertools import product
import json

ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0))


def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def bar(a):return (a[0],-a[1])
def norm(a):return a[0]*a[0]+a[1]*a[1]
def inv(a):
    nn=norm(a);assert nn
    return (a[0]/nn,-a[1]/nn)
def power(a,n):
    if n<0:return power(inv(a),-n)
    out=ONE
    while n:
        if n&1:out=mul(out,a)
        a=mul(a,a);n//=2
    return out


def v_pi(z):
    """Valuation at pi=2+i; pi has valuation one, rational 5 also one."""
    if z==ZERO:return None
    from math import lcm
    D=lcm(z[0].denominator,z[1].denominator)
    A=int(z[0]*D);B=int(z[1]*D);value=0
    while (2*A+B)%5==0 and (2*B-A)%5==0:
        A,B=(2*A+B)//5,(2*B-A)//5;value+=1
    while D%5==0:D//=5;value-=1
    return value


def candidates(p,q,u):
    assert p!=ZERO and q!=ZERO
    a=v_pi(mul(p,bar(q)));b=v_pi(mul(bar(p),q))
    c=v_pi((norm(p)+norm(q)-1,Q(0)));s=v_pi(u);assert s
    if c is None or 2*c>=a+b:
        numerators=[(b-a,2*s)]
    else:numerators=[(c-a,s),(b-c,s)]
    return {a//b for a,b in numerators if a%b==0}


def run():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    u=(Q(3,5),Q(4,5));assert norm(u)==1 and v_pi(u)==1
    pool=[(Q(a,5),Q(b,5)) for a,b in product(range(-2,3),repeat=2) if a or b]
    pool += [power(u,n) for n in range(-3,4)]
    checks=0;hits=0;maximum=0
    for p,q in product(pool,repeat=2):
        ns=candidates(p,q,u);assert len(ns)<=2;maximum=max(maximum,len(ns))
        for n in range(-12,13):
            edge=norm(add(mul(power(u,n),p),neg(q)))==1
            if edge:assert n in ns;hits+=1
            checks+=1
        for n in ns:
            assert isinstance(n,int)
    distant=[]
    for h in (1,2,17,101):
        p=inv(add(ONE,neg(power(u,h))))
        ns=candidates(p,p,u)
        assert ns=={-h,h}
        assert norm(add(mul(power(u,h),p),neg(p)))==1
        distant.append(dict(lag=h,candidates=sorted(ns)))
    # For h=2, actual edge shifts are +/-2. The infinite graph is bipartite,
    # but periods 1 and 2 collapse an edge; period 4 has a binary coloring.
    h=2;word='0011'
    assert all(word[n%4]!=word[(n+h)%4] for n in range(4))
    for period in (1,2):assert h%period==0
    return dict(status='PASS',exact_pair_power_checks=checks,detected_edges=hits,
                maximum_candidate_count=maximum,distant_lag_examples=distant,
                two_color_period_four=word,scope='General-lemma calibration in Q(i), not the Y orbit certificate')


if __name__=='__main__':print(json.dumps(run(),indent=2))
