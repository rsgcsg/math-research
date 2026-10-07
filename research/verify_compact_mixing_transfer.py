"""Exact finite calibration for R158-M/K, not a proof of their infinite claims.

Only fractions and finite enumerations are used.  The all-order mixing proof
uses the independently stated ESS theorem; this script does not verify ESS.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'certificates/compact_mixing_calibration.json'
ZERO = (Q(0),) * 6


def require(ok, message):
    if not ok:
        raise ValueError(message)


def basis(j):
    return tuple(Q(int(i == j)) for i in range(6))


ONE, I, A, IA, A2, IA2 = (basis(j) for j in range(6))


def add(x, y):
    return tuple(a+b for a, b in zip(x, y))


def scale(q, x):
    return tuple(Q(q)*v for v in x)


def mul(x, y):
    # Q(i, a), a^3=2; basis (1,i,a,ia,a^2,ia^2).
    result = list(ZERO)
    for j, a in enumerate(x):
        for k, b in enumerate(y):
            degree = j//2 + k//2
            ipower = j % 2 + k % 2
            sign = -1 if ipower == 2 else 1
            factor = 2 if degree >= 3 else 1
            result[2*(degree % 3)+(ipower % 2)] += sign*factor*a*b
    return tuple(result)


def conjugate(x):
    return tuple(v if j % 2 == 0 else -v for j, v in enumerate(x))


def inverse(x):
    columns = [mul(x, basis(j)) for j in range(6)]
    rows = [[columns[j][i] for j in range(6)] + [ONE[i]] for i in range(6)]
    for j in range(6):
        pivot = next((r for r in range(j, 6) if rows[r][j]), None)
        require(pivot is not None, 'singular field element')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [v/divisor for v in rows[j]]
        for r in range(6):
            if r != j:
                factor = rows[r][j]
                rows[r] = [v-factor*w for v, w in zip(rows[r], rows[j])]
    answer = tuple(row[-1] for row in rows)
    require(mul(x, answer) == ONE == mul(answer, x), 'inverse product')
    return answer


def in_m(x):
    return all(x[j] == 0 for j in (0, 1, 4, 5))


def in_n(x):
    return all(x[j] == 0 for j in (2, 3, 4, 5))


def quotient(x):
    return tuple(x[j] for j in (0, 1, 4, 5))


def escape(t):
    z = scale(t, IA)
    return mul(add(ONE, z), inverse(add(ONE, scale(-1, z))))


def validate_escape(row):
    require(set(row) == {'t', 'u'}, 'escape record fields')
    t = Q(row['t'])
    require(t != 0 and len(row['u']) == 6, 'invalid escape input')
    u = tuple(Q(v) for v in row['u'])
    # Check the defining identity rather than trusting stored search output.
    require(mul(u, add(ONE, scale(-t, IA))) == add(ONE, scale(t, IA)),
            'Cayley identity')
    require(mul(u, conjugate(u)) == ONE, 'unit norm')
    require(not in_n(u), 'rotation remained in N')
    require(in_m(A) and not in_m(mul(u, A)), 'subspace not exposed')


def spectral_samples():
    require(mul(mul(A, A), A) == scale(2, ONE), 'cubic equation')
    require(mul(I, I) == scale(-1, ONE), 'imaginary equation')
    samples = [ZERO, ONE, I, A, IA, A2, IA2, add(ONE, A), add(I, IA),
               add(A, A2), add(ONE, A2), add(I, scale(2, A2))]
    tags = sorted({quotient(x) for x in samples})
    incidence = [[int(quotient(x) == t) for t in tags] for x in samples]
    gram = [[int(in_m(add(x, scale(-1, y)))) for y in samples] for x in samples]
    require(gram == [[sum(a*b for a, b in zip(x, y)) for y in incidence]
                    for x in incidence], 'coset Gram factorization')
    h = add(scale(Q(3, 5), ONE), scale(Q(4, 5), I))
    require(mul(h, conjugate(h)) == ONE, 'old rotation norm')
    powers = {0: ONE}
    for n in range(1, 7):
        powers[n] = mul(powers[n-1], h)
        powers[-n] = conjugate(powers[n])
    require(len(set(powers.values())) == 13, 'sample powers collided')
    invariance = 0
    for rot in powers.values():
        for i, x in enumerate(samples):
            for j, y in enumerate(samples):
                require(int(in_m(mul(rot, add(x, scale(-1, y))))) == gram[i][j],
                        'old rotation invariance')
                invariance += 1
    nonzero_classes = [x for x in samples if not in_m(x)]
    mixing = 0
    for x, y in product(nonzero_classes, repeat=2):
        hits = [n for n, rot in powers.items()
                if in_m(add(x, scale(-1, mul(rot, y))))]
        require(len(hits) <= 1, 'more than one correlation exception')
        mixing += 1
    # Joint Fourier moments on (1,i,1+i), including their additive relation.
    moments = 0
    for a, b, c in product(range(-3, 4), repeat=3):
        z = add(scale(a+c, ONE), scale(b+c, I))
        require(int(in_m(z)) == int(z == ZERO), 'Haar marginal sample')
        moments += 1
    witnesses = [dict(t=str(t), u=[str(v) for v in escape(t)])
                 for t in (Q(1), Q(1, 10), Q(1, 100), Q(1, 1000))]
    for row in witnesses:
        validate_escape(row)
    rejected = 0
    for i in range(6):
        row = dict(witnesses[0]);row['u'] = list(row['u'])
        row['u'][i] = str(Q(row['u'][i])+Q(1, 7))
        try:
            validate_escape(row)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('corrupted escape accepted')
    return dict(field='Q(i,a), a>0 and a^3=2', basis=['1','i','a','ia','a^2','ia^2'],
                sample_points=len(samples), distinct_cosets=len(tags),
                gram_rank=len(tags), invariance_checks=invariance,
                mixing_character_pairs=mixing, joint_moments=moments,
                escape_witnesses=witnesses, mutated_escapes_rejected=rejected)


def net_samples():
    # A finite compact model: the mechanism is verified with exact distances.
    space = [Q(i, 24) for i in range(25)]
    net = [Q(i, 4) for i in range(5)]
    eps = Q(1, 8)
    rounding = {x: min(net, key=lambda a: (abs(a-x), a)) for x in space}
    require(max(abs(x-rounding[x]) for x in space) <= eps, 'not an epsilon net')
    checked = 0
    for threshold in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
        relation = [(x, y) for x, y in product(space, repeat=2)
                    if abs(x-y) >= threshold]
        fat = {(a, b) for a, b in product(net, repeat=2)
               if min(max(abs(a-x), abs(b-y)) for x, y in relation) <= eps}
        for x, y in relation:
            require((rounding[x], rounding[y]) in fat, 'finite target rounding lost relation')
            checked += 1
        require(all((b,a) in fat for a,b in fat), 'thickening not symmetric')
    # This fixed sequence illustrates the nonclosed counterexample; proof is in text.
    prefix = 0
    for m in range(1, 33):
        point = Q(1, m+1)
        for n in range(1, m+1):
            require(0 < point <= Q(1,n), 'finite nonclosed prefix')
            prefix += 1
    return dict(net_size=5, fine_space_size=25, epsilon=str(eps),
                rounded_allowed_pairs=checked, nonclosed_prefix_checks=prefix)


def matmul(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2))
                 for i in range(2))


def projector_samples():
    identity = ((Q(1), Q(0)), (Q(0), Q(1)))
    zero = ((Q(0), Q(0)), (Q(0), Q(0)))
    def comp(p):
        return tuple(tuple(identity[i][j]-p[i][j] for j in range(2)) for i in range(2))
    def valid(p):
        require(p == tuple(zip(*p)) and matmul(p,p) == p, 'invalid projection')
        q = comp(p)
        require(matmul(q,q) == q and matmul(p,q) == zero == matmul(q,p), 'PVM axioms')
    vectors = [(Q(1), Q(0)), (Q(0), Q(1)), (Q(3,5), Q(4,5)),
               (Q(4,5), Q(3,5)), (Q(5,13), Q(12,13))]
    projections = {tuple(tuple(x*y for y in v) for x in v) for v in vectors}
    projections.add(((Q(1,2),Q(1,2)),(Q(1,2),Q(1,2))))
    projections |= {comp(p) for p in list(projections)}
    projections = sorted(projections)
    for p in projections:
        valid(p)
    relation_count = 0
    for p, q in product(projections, repeat=2):
        allowed = matmul(p,q) == zero and matmul(comp(p),comp(q)) == zero
        reverse = matmul(q,p) == zero and matmul(comp(q),comp(p)) == zero
        require(allowed == reverse, 'projector relation not symmetric')
        require(allowed == (q == comp(p)), 'rank-one two-label relation')
        relation_count += 1
    rejects = 0
    for i, j in product(range(2), repeat=2):
        p = [list(r) for r in identity];p[i][j] += Q(1,10)
        try:
            valid(tuple(map(tuple,p)))
        except ValueError:
            rejects += 1
        else:
            raise ValueError('invalid projector accepted')
    scalar = 0
    for k in range(1, 6):
        labels = [row for row in product((0,1), repeat=k) if sum(row)==1]
        require(len(labels)==k, 'one-dimensional labels')
        for a, b in product(labels, repeat=2):
            require(all(x*y==0 for x,y in zip(a,b)) == (a!=b), 'd=1 is not classical')
            scalar += 1
    return dict(rational_projection_tuples=len(projections),
                tuple_pair_relations=relation_count, scalar_classical_pairs=scalar,
                mutated_projectors_rejected=rejects)



def v2(q):
    q = Q(q)
    require(q != 0, 'v2 zero has no finite value')
    def power(a):
        a = abs(a)
        return (a & -a).bit_length()-1
    return power(q.numerator)-power(q.denominator)


def binary_remainder(q):
    q = Q(q)
    denominator = q.denominator
    s = (denominator & -denominator).bit_length()-1
    if not s:
        return Q(0)
    modulus = 1 << s
    odd = denominator // modulus
    return Q((q.numerator * pow(odd, -1, modulus)) % modulus, modulus)


def color_bit(q):
    z = Q(q)-binary_remainder(q)
    require(z.denominator % 2 == 1, 'principal part did not remove denominator')
    return z.numerator % 2


def odd_radical_samples():
    records = []
    for n in (1, 3, 5, 7):
        one = (Q(1),)+(Q(0),)*(n-1)
        zero = (Q(0),)*n
        def fadd(x,y):
            return tuple(a+b for a,b in zip(x,y))
        def fscale(a,x):
            return tuple(a*b for b in x)
        def fmul(x,y):
            out=[Q(0)]*n
            for j,a in enumerate(x):
                for k,b in enumerate(y):
                    out[(j+k)%n] += a*b*(2 if j+k >= n else 1)
            return tuple(out)
        def finv(x):
            basis_n=[tuple(Q(int(j==k)) for j in range(n)) for k in range(n)]
            columns=[fmul(x,b) for b in basis_n]
            rows=[[columns[k][j] for k in range(n)]+[one[j]] for j in range(n)]
            for j in range(n):
                pivot=next((k for k in range(j,n) if rows[k][j]),None)
                require(pivot is not None, 'nonzero real field inverse failed')
                rows[j],rows[pivot]=rows[pivot],rows[j]
                d=rows[j][j];rows[j]=[a/d for a in rows[j]]
                for k in range(n):
                    if j!=k:
                        d=rows[k][j];rows[k]=[a-d*b for a,b in zip(rows[k],rows[j])]
            ans=tuple(row[-1] for row in rows)
            require(fmul(x,ans)==one,'real inverse failed')
            return ans
        def valuation(x):
            return min((n*v2(a)+j for j,a in enumerate(x) if a), default=None)
        points=sorted({tuple(Q(((r+1)*(j+2))%11-5, (2**(r%3))*(2*(j%3)+1))
                             for j in range(n)) for r in range(18)} | {one,zero})
        products=0
        for x,y in product(points,repeat=2):
            if x!=zero and y!=zero:
                require(valuation(fmul(x,y))==valuation(x)+valuation(y),'valuation multiplicativity')
                products+=1
        units=[]
        for t in points:
            tt=fmul(t,t);d=finv(fadd(one,tt))
            x=fmul(fadd(one,fscale(-1,tt)),d)
            y=fmul(fscale(2,t),d)
            require(fadd(fmul(x,x),fmul(y,y))==one,'unit norm failed')
            require(all(a==0 or v2(a)>=0 for a in x+y),'unit vector not integral')
            require((color_bit(x[0])+color_bit(y[0]))%2==1,'unit residual sum')
            units.append((x,y))
        edge_checks=0
        for x,y in units:
            for a,b in zip(points,reversed(points)):
                before=(color_bit(a[0])+color_bit(b[0]))%2
                after=(color_bit(a[0]+x[0])+color_bit(b[0]+y[0]))%2
                require(before!=after,'explicit coloring failed a genuine unit edge')
                edge_checks+=1
        if n==3:
            alpha=(Q(0),Q(1),Q(0))
            for t in (Q(1),Q(1,10),Q(1,100),Q(1,1000)):
                v=fscale(t,alpha);vv=fmul(v,v);den=finv(fadd(one,vv))
                re=fmul(fadd(one,fscale(-1,vv)),den);im=fmul(fscale(2,v),den)
                combined=tuple(z for pair in zip(re,im) for z in pair)
                require(combined==escape(t),'cubic escape and real unit parametrization differ')
        records.append(dict(degree=n,field_samples=len(points),
                            valuation_products=products,unit_directions=len(units),
                            translated_unit_edges=edge_checks))
    require(color_bit(0)!=color_bit(1),'one-color lower edge')
    # Even-degree counterexample to this valuation lemma/formula, not to all two-colorings.
    xx=(Q(0),Q(1,2))  # sqrt(2)/2
    norm=(2*2*xx[1]**2, Q(0))
    require(norm==(Q(1),Q(0)) and color_bit(xx[0])==0, 'even-degree calibration')
    return dict(fields=records,exact_cubic_escape_comparisons=4,
                even_degree_formula_counterexample_checked=True,
                scope='Finite calibration of the uniform odd-degree proof and explicit coloring; not extrapolation from these degrees.')

def unique_keys(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def main():
    if not __debug__:
        raise RuntimeError('Exact calibration requires non-optimized Python')
    report = dict(schema='hn-compact-mixing-calibration-v1', status='PASS_FINITE_CALIBRATION',
                  spectral=spectral_samples(), compact_nets=net_samples(),
                  projection_templates=projector_samples(), odd_radical_coloring=odd_radical_samples(),
                  infinite_theorems_formalized=False, new_plane_bound=False,
                  scope='Exact finite algebra and finite template mechanisms only. Infinite R158-M/K/D use written proofs; all-order mixing uses ESS; compact transfer depends on R158-C.')
    if sys.argv[1:] == ['--emit']:
        CERT.write_text(json.dumps(report, indent=2)+'\n')
    else:
        require(not sys.argv[1:], 'unsupported arguments')
        saved = json.loads(CERT.read_text(), object_pairs_hook=unique_keys)
        require(saved == report, 'saved calibration differs from independent recomputation')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
