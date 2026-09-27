"""Exact adapter for the independently checked 16-dimensional field of Y.

Valuations are resolved by increasing 2-adic precision until a nonzero residue
is seen. Reaching an implementation limit raises an error, never 'no roots'.
The field and local embeddings are the pre-existing independent definitions.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from verify_dyadic_cyclic_orbit import algebra16, local_images, local_mul

TIMES9, BAR3, _, _ = algebra16()


@dataclass(frozen=True)
class Element:
    cs: tuple
    def __post_init__(self):
        if len(self.cs) != 16: raise ValueError('field dimension')
        object.__setattr__(self, 'cs', tuple(Q(c) for c in self.cs))
    @classmethod
    def scalar(cls, x): return cls((Q(x),)+(Q(0),)*15)
    @staticmethod
    def cast(x): return x if isinstance(x, Element) else Element.scalar(x)
    def __add__(self, y):
        y=self.cast(y); return Element(tuple(a+b for a,b in zip(self.cs,y.cs)))
    __radd__=__add__
    def __neg__(self): return Element(tuple(-a for a in self.cs))
    def __sub__(self,y): return self+-self.cast(y)
    def __rsub__(self,y): return self.cast(y)+-self
    def __mul__(self,y):
        y=self.cast(y); return Element(tuple(Q(a,9) for a in TIMES9(self.cs,y.cs)))
    __rmul__=__mul__
    def bar(self): return Element(tuple(Q(a,3) for a in BAR3(self.cs)))
    def __pow__(self,n):
        if type(n) is not int: raise ValueError('integer exponent')
        x=self; answer=Element.scalar(1)
        if n<0:
            x=self.bar()
            if x*self != answer: raise ValueError('negative powers implemented only for norm-one elements')
        n=abs(n)
        while n:
            if n&1: answer=answer*x
            x=x*x; n >>= 1
        return answer
    def serial(self): return [str(x) for x in self.cs]


U=Element(tuple(Q(x,2) for x in [1,0,0,0,0,0,-3,-3]+[0]*8))


def two_order(n):
    if type(n) is not int or not n: raise ValueError('nonzero integer required')
    return (abs(n)&-abs(n)).bit_length()-1


@lru_cache(maxsize=8)
def checked_basis(bits):
    basis=local_images(bits)[0]; M=1<<bits
    unit=[tuple(Q(int(i==j)) for j in range(16)) for i in range(16)]
    for i in range(16):
        for j in range(16):
            cs=[Q(x,9) for x in TIMES9(unit[i],unit[j])]
            image=tuple(sum(c.numerator*pow(c.denominator,-1,M)*basis[k][h]
                            for k,c in enumerate(cs))%M for h in range(4))
            if image != local_mul(basis[i],basis[j],M): raise AssertionError('local algebra mismatch')
    return basis


@lru_cache(maxsize=20000)
def valuation(x):
    if x==Element.scalar(0): raise ValueError('valuation of zero')
    clear=max(two_order(c.denominator) for c in x.cs)
    cs=[c*2**clear for c in x.cs]
    bits=8
    while bits<=4096:
        basis=checked_basis(bits); M=1<<bits
        residues=tuple(sum(c.numerator*pow(c.denominator,-1,M)*basis[i][j]
                           for i,c in enumerate(cs))%M for j in range(4))
        nonzero=[two_order(c) for c in residues if c]
        if nonzero: return min(nonzero)-clear
        bits*=2
    raise RuntimeError('valuation unresolved at resource limit; no mathematical verdict')
