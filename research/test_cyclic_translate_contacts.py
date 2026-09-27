"""Independent finite calibrations of the cyclic translate algorithm.

The mathematical completeness proof is separate. Bounded brute force below
is only a cross-check; it is never substituted for the unbounded algorithm.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from cyclic_translate_contacts import contacts, solve_laurent


@dataclass(frozen=True)
class Gaussian:
    x: F = F(0)
    y: F = F(0)
    def __post_init__(self):
        object.__setattr__(self, 'x', F(self.x))
        object.__setattr__(self, 'y', F(self.y))
    @staticmethod
    def cast(other):
        return other if isinstance(other, Gaussian) else Gaussian(F(other))
    def __add__(self, other):
        o = self.cast(other); return Gaussian(self.x+o.x, self.y+o.y)
    __radd__ = __add__
    def __neg__(self): return Gaussian(-self.x, -self.y)
    def __sub__(self, other): return self+-self.cast(other)
    def __rsub__(self, other): return self.cast(other)+-self
    def __mul__(self, other):
        o = self.cast(other); return Gaussian(self.x*o.x-self.y*o.y, self.x*o.y+self.y*o.x)
    __rmul__ = __mul__
    def bar(self): return Gaussian(self.x, -self.y)
    def norm(self): return self.x*self.x+self.y*self.y
    def __truediv__(self, other):
        o = self.cast(other)
        if not o.norm(): raise ZeroDivisionError('zero Gaussian denominator')
        z = self*o.bar(); return Gaussian(z.x/o.norm(), z.y/o.norm())
    def __pow__(self, n):
        if type(n) is not int: raise ValueError('integer power required')
        x, out = (Gaussian(1)/self if n < 0 else self), Gaussian(1)
        n = abs(n)
        while n:
            if n & 1: out = out*x
            x = x*x; n >>= 1
        return out
    def serial(self): return [str(self.x), str(self.y)]


def order5(x):
    if not x: raise ValueError('valuation of zero')
    k = 0
    while x % 5 == 0: k += 1; x //= 5
    return k


def gaussian_division_order(z):
    """v_(2+i), by exact Gaussian-integer division, not by Hensel evaluation."""
    if z == Gaussian(): raise ValueError('valuation of zero')
    den = lcm(z.x.denominator, z.y.denominator)
    a, b, e = int(z.x*den), int(z.y*den), 0
    while (2*a+b) % 5 == 0 and (2*b-a) % 5 == 0:
        a, b, e = (2*a+b)//5, (2*b-a)//5, e+1
    return e-order5(den)


def hensel_order(z):
    """Independent v_(2+i): evaluate i at the 5-adic root i=3 modulo 5."""
    if z == Gaussian(): raise ValueError('valuation of zero')
    den = lcm(z.x.denominator, z.y.denominator)
    a, b = int(z.x*den), int(z.y*den)
    root, modulus, level = 3, 5, 1
    while True:
        image = (a+b*root) % modulus
        if image: return order5(image)-order5(den)
        digit = (-(root*root+1)//modulus*pow(2*root, -1, 5)) % 5
        root += modulus*digit; modulus *= 5; level += 1
        if (root*root+1) % modulus: raise AssertionError('incorrect Hensel lift')


def is_contact(a, b, t, u, n, m):
    return (a*u**n-t-b*u**m).norm() == 1


def contains(result, n, m):
    return (result['all_integer_pairs'] or [n, m] in result['points'] or
            any(A*n+B*m == C for A, B, C in result['lines']))


def automaton_tail_checks():
    """Cycle reachability versus exact N-step tails on every digraph of size <=3."""
    count = 0
    for n in range(1, 4):
        for mask in range(1 << (n*n)):
            adj = [[bool(mask & (1 << (i*n+j))) for j in range(n)] for i in range(n)]
            closure = [row[:] for row in adj]
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        closure[i][j] |= closure[i][k] and closure[k][j]
            cycles = {i for i in range(n) if closure[i][i]}
            from_cycle = {j for i in cycles for j in range(n) if closure[i][j]}
            to_cycle = {i for j in cycles for i in range(n) if closure[i][j]}
            ends = starts = set(range(n))
            for _ in range(n):
                ends = {j for i in ends for j in range(n) if adj[i][j]}
                starts = {i for j in starts for i in range(n) if adj[i][j]}
            assert ends == from_cycle and starts == to_cycle
            count += 1
    assert count == 530
    return count


def checks():
    if not __debug__: raise RuntimeError('verification requires assertions')
    u = Gaussian(F(3, 5), F(4, 5)); bar = lambda z: z.bar()
    assert gaussian_division_order(u) == hensel_order(u) == 1
    values = [Gaussian(x, y)/Gaussian(d) for x, y in product(range(-2, 3), repeat=2)
              for d in (1, 5) if x or y]
    for a in values:
        assert gaussian_division_order(a) == hensel_order(a)
        for b in values:
            assert gaussian_division_order(a*b) == gaussian_division_order(a)+gaussian_division_order(b)
    support = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]
    directions = {}; degree_budget = 0
    for p, q in combinations(support, 2):
        A, B = p[0]-q[0], p[1]-q[1]; g = gcd(A, B); A //= g; B //= g
        if A < 0 or A == 0 and B < 0: A, B = -A, -B
        e = [B*x-A*y for x,y in support]; degree = max(e)-min(e)
        degree_budget += degree
        row = directions.setdefault((A,B), dict(pairs=0, degree=degree)); row['pairs'] += 1
    assert degree_budget == 54
    seeds = [Gaussian(1), Gaussian(-1), Gaussian(2), Gaussian(0,1),
             Gaussian(F(1,2),F(1,2)), Gaussian(1,1)]
    cases = []
    window = range(-4, 5)
    for a, b, t in product(seeds, repeat=3):
        result = contacts(a,b,t,u,bar,gaussian_division_order)
        other = contacts(a,b,t,u,bar,hensel_order)
        assert result == other
        for n,m in product(window, repeat=2):
            assert contains(result,n,m) == is_contact(a,b,t,u,n,m)
        assert all(is_contact(a,b,t,u,n,m) for n,m in result['points'])
        cases.append(dict(a=a.serial(),b=b.serial(),t=t.serial(),result=result))
    late = []
    for N in (1, 7, 31, 101):
        t = u**N-Gaussian(2)
        result = contacts(Gaussian(1),Gaussian(1),t,u,bar,gaussian_division_order)
        assert [N,0] in result['points'] and not result['lines']
        assert is_contact(Gaussian(1),Gaussian(1),t,u,N,0)
        late.append(dict(N=N,points=result['points'],tested_lines=result['tested_lines'],
                         tested_parameters=result['tested_parameters']))
    # Complete zero-set edge cases, not contacts with zero translation/radius.
    one, zero = Gaussian(1), Gaussian()
    assert solve_laurent({},u,gaussian_division_order)['all_integer_pairs']
    assert solve_laurent({(0,0):one},u,gaussian_division_order)['points'] == []
    factored = solve_laurent({(1,1):one,(1,0):-one,(0,1):-one,(0,0):one},u,gaussian_division_order)
    assert factored['lines'] == [[0,1,0],[1,0,0]] and not factored['points']
    rejected=[]
    for name, run in [
        ('zero-translation', lambda: contacts(one,one,zero,u,bar,gaussian_division_order)),
        ('zero-radius', lambda: contacts(zero,one,one,u,bar,gaussian_division_order)),
        ('nonunit-rotation', lambda: contacts(one,one,one,Gaussian(2),bar,gaussian_division_order)),
        ('invisible-base', lambda: solve_laurent({(1,0):one},Gaussian(1),gaussian_division_order)),
        ('boolean-exponent', lambda: solve_laurent({(True,0):one},u,gaussian_division_order)),
        ('boolean-valuation', lambda: solve_laurent({(1,0):one},u,lambda _:True)),
    ]:
        try: run()
        except ValueError: rejected.append(name)
        else: raise AssertionError('accepted '+name)
    raw=json.dumps(cases,sort_keys=True,separators=(',',':')).encode()
    return dict(status='PASS',finite_automaton_graph_checks=automaton_tail_checks(),case_count=len(cases),brute_force_point_checks=len(cases)*len(window)**2,
                nonzero_test_values=len(values),valuation_multiplicativity_checks=len(values)**2,
                maximum_actual_exceptional_contacts=max(len(c['result']['points']) for c in cases),
                cases_with_infinite_families=sum(bool(c['result']['lines']) for c in cases),
                complete_case_table_sha256=hashlib.sha256(raw).hexdigest(),late_contacts=late,
                degree_bound=degree_budget,directions=[dict(normal=list(a),**v) for a,v in sorted(directions.items())],
                rejected_inputs=rejected,
                scope='Exact Q(i) finite calibration and complete symbolic output from the proved cyclic algorithm; not an HN coloring obstruction.')


if __name__ == '__main__':
    if not __debug__: raise RuntimeError('verification requires assertions')
    result=checks()
    child=subprocess.run([sys.executable,'-O',str(Path(__file__).resolve())],capture_output=True,text=True,timeout=10)
    assert child.returncode != 0 and 'requires assertions' in child.stderr
    result['optimized_mode_rejected']=True
    print(json.dumps(result,indent=2))
