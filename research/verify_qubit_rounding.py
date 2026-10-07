"""Exact finite samples for qubit rounding and the sharp triangle defect.

The arbitrary-graph and all-odd-cycle statements are proved in the document,
not inferred from this finite calibration. No floating point is used.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT/'certificates/qubit_rounding_calibration.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Quad:
    """Exact arithmetic in Q(sqrt(r)) for r=-1 or 3."""
    def __init__(self, r):
        self.r = Q(r)
        self.z = (Q(0),Q(0));self.o = (Q(1),Q(0))
        self.identity = ((self.o,self.z),(self.z,self.o))
        self.zero = ((self.z,self.z),(self.z,self.z))

    def add(self, x,y):
        return (x[0]+y[0],x[1]+y[1])

    def neg(self, x):
        return (-x[0],-x[1])

    def mul(self, x,y):
        return (x[0]*y[0]+self.r*x[1]*y[1],x[0]*y[1]+x[1]*y[0])

    def bar(self,x):
        return (x[0],-x[1]) if self.r == -1 else x

    def mm(self,a,b):
        return tuple(tuple(self.add(self.mul(a[i][0],b[0][j]),
                                    self.mul(a[i][1],b[1][j])) for j in range(2)) for i in range(2))

    def comp(self,a):
        return tuple(tuple(self.add(self.identity[i][j],self.neg(a[i][j]))
                           for j in range(2)) for i in range(2))

    def adj(self,a):
        return tuple(tuple(self.bar(a[j][i]) for j in range(2)) for i in range(2))

    def trace(self,a):
        return self.add(a[0][0],a[1][1])

    def valid(self,p):
        require(self.adj(p) == p and self.mm(p,p)==p, 'not an orthogonal projection')
        q = self.comp(p)
        require(self.mm(p,q)==self.zero==self.mm(q,p), 'complement not orthogonal')
        require(self.mm(q,q)==q, 'complement not idempotent')


def first_sign(n):
    return next(x>0 for x in n if x)


def bloch(n):
    x,y,z = n
    return (((Q(1,2)+z/2,Q(0)),(x/2,-y/2)),
            ((x/2,y/2),(Q(1,2)-z/2,Q(0))))


def rational_bloch_checks():
    field = Quad(-1)
    pars = [Q(-1),Q(-1,2),Q(0),Q(1,2),Q(1)]
    normals = set()
    for a,b in product(pars,repeat=2):
        d = 1+a*a+b*b
        n = (2*a/d,2*b/d,(1-a*a-b*b)/d)
        normals.add(n);normals.add(tuple(-x for x in n))
    normals = sorted(normals)
    require(any(n[1] for n in normals), 'sample missing complex off-diagonal entries')
    matrices = {n:bloch(n) for n in normals}
    for n,p in matrices.items():
        require(sum(x*x for x in n)==1, 'Bloch sphere equation')
        field.valid(p)
        require(field.comp(p)==matrices[tuple(-x for x in n)], 'Bloch complement')
    nonorthogonal = 0;orthogonal = 0;traces = 0
    for n,m in product(normals,repeat=2):
        pq = field.mm(matrices[n],matrices[m])
        trace = field.trace(pq)
        expected = (1+sum(x*y for x,y in zip(n,m)))/2
        require(trace==(expected,Q(0)), 'Bloch product trace formula')
        require(field.trace(field.mm(field.adj(pq),pq))==trace, 'Frobenius squared formula')
        require((pq==field.zero)==(m==tuple(-x for x in n)), 'orthogonality classification')
        if pq==field.zero:
            require(not(first_sign(n) and first_sign(m)), 'rounding selected orthogonal pair')
            orthogonal += 1
        if first_sign(n) and first_sign(m):
            require(pq!=field.zero, 'positive projectors have zero product')
            nonorthogonal += 1
        traces += 1
    measurements = 0
    for k in range(1,6):
        measurements += k  # One identity and k-1 zero projectors.
        for n in normals:
            for i in range(k):
                for j in range(i+1,k):
                    selected = [i if first_sign(n) else j]
                    require(len(selected)==1, 'not exactly one output')
                    measurements += 1
    rejected = 0
    for i,j in product(range(2),repeat=2):
        p = [list(row) for row in field.identity]
        p[i][j] = field.add(p[i][j],(Q(1,10),Q(0)))
        try:
            field.valid(tuple(map(tuple,p)))
        except ValueError:
            rejected += 1
        else:
            raise ValueError('corrupted projection accepted')
    return dict(bloch_vectors=len(normals), pair_trace_identities=traces,
                orthogonal_ordered_pairs=orthogonal,
                selected_nonorthogonal_pairs=nonorthogonal,
                labelled_measurements=measurements, mutations_rejected=rejected)


def triangle_checks():
    field = Quad(3)
    q = lambda a,b=0:(Q(a),Q(b))
    ps = [((q(1),q(0)),(q(0),q(0))),
          ((q(Q(1,4)),q(0,Q(1,4))),(q(0,Q(1,4)),q(Q(3,4)))),
          ((q(Q(1,4)),q(0,Q(-1,4))),(q(0,Q(-1,4)),q(Q(3,4))))]
    for p in ps:
        field.valid(p)
    products = 0
    for u,v in [(0,1),(1,2),(2,0)]:
        for complement in (False,True):
            p = field.comp(ps[u]) if complement else ps[u]
            t = field.comp(ps[v]) if complement else ps[v]
            prod = field.mm(p,t)
            require(field.trace(prod)==q(Q(1,4)), 'triangle overlap')
            require(field.trace(field.mm(field.adj(prod),prod))==q(Q(1,4)),
                    'triangle squared Frobenius error')
            products += 1
    # Universal arithmetic parity check is a finite calibration, not an odd-cycle proof.
    failures = 0
    for colors in product(range(2),repeat=3):
        require(any(colors[u]==colors[v] for u,v in [(0,1),(1,2),(2,0)]), 'triangle two-coloring')
        failures += 1
    return dict(field='Q(sqrt(3))', projections=[[[[str(a),str(b)] for a,b in row] for row in p] for p in ps],
                edge_label_products=products, squared_frobenius_defect='1/4',
                frobenius_defect='1/2', impossible_classical_assignments=failures,
                scope='Exact m=3 upper witness; the matching lower bound and arbitrary odd m are written proofs.')


def unique(pairs):
    result = {}
    for k,v in pairs:
        require(k not in result, 'duplicate JSON key')
        result[k]=v
    return result


def main():
    if not __debug__:
        raise RuntimeError('Qubit checks require non-optimized Python')
    result = dict(schema='hn-qubit-rounding-calibration-v1',status='PASS_FINITE_CALIBRATION',
                  rational_complex_samples=rational_bloch_checks(),triangle=triangle_checks(),
                  all_graphs_checked_by_enumeration=False, infinite_result_formalized=False,
                  scope='Rational complex projector samples and exact triangle witness only; full claims use docs/proofs/qubit_coloring_rounding.md.')
    if sys.argv[1:]==['--emit']:
        CERT.write_text(json.dumps(result,indent=2)+'\n')
    else:
        require(not sys.argv[1:], 'unsupported argument')
        require(json.loads(CERT.read_text(),object_pairs_hook=unique)==result,'certificate mismatch')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
