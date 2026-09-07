"""Independent direct checker; does not import translated_seam search code."""
from itertools import permutations, product, combinations
from fractions import Fraction as F
import json
from exact_geometry import field, cmul, add, sub, distance_squared, ONE


def verify(path):
    records = json.loads(path.read_text())
    roots = {(m,n) for m in range(-2,3) for n in range(-2,3) if m*m+m*n+n*n == 3}
    assert len(records) == 6
    assert {tuple(r['translation_root']) for r in records} == roots
    checked = 0
    for r in records:
        ux, uy = r['translation_root']
        shifted = {(m+ux,n+uy) for m,n in roots}
        ports = roots | shifted | {(0,0), (ux,uy)}
        assert sorted(ports) == [tuple(v) for v in r['ports']]
        lo = min(m//2 for m,n in ports if m%2)
        hi = max(m//2 for m,n in ports if m%2)
        assert (r['lo'],r['hi']) == (lo,hi)
        expected = set(product(tuple(product((0,-1), repeat=hi-lo)), repeat=3))
        actual = {tuple(tuple(w) for w in row['words']) for row in r['rows']}
        assert actual == expected and len(actual) == len(r['rows']) == 64
        assert r['word_count'] == 4 and r['triples'] == 64 and r['excluded'] == 0
        hist = {}
        for row in r['rows']:
            tables = []
            for w in row['words']:
                s = {lo:0}
                for j, step in enumerate(w, start=lo+1):
                    s[j] = (s[j-1]+step)%3
                tables.append({(m,n): n%3 if m%2==0 else 3+(n+s[m//2])%3 for m,n in ports})
            a,b,c = tables
            def valid(pb, pc):
                return (pb[0] == 0 and
                        set(pc[:3]) == {3,4,5} and set(pc[3:]) == {0,1,2} and
                        pb[b[ux,uy]] == pc[c[ux,uy]] and
                        all(a[v] != pb[b[v]] for v in roots) and
                        all(pb[b[v]] != pc[c[v]] for v in shifted))
            pb, pc = row['witness']
            assert sorted(pb) == sorted(pc) == list(range(6))
            assert valid(pb,pc)
            count = 0
            for tail in permutations(range(1,6)):
                pb = (0,)+tail
                for top in permutations(range(3,6)):
                    for bottom in permutations(range(3)):
                        count += valid(pb, top+bottom)
            assert count == row['count'] > 0
            hist[str(count)] = hist.get(str(count),0)+1
            checked += 1
        assert hist == r['count_histogram']

    # T018: exact physical unit edges and equalities, independent of search.
    def point(m,n):
        return field(F(2*m+n,2)), field(0,F(n,2))
    rho = field(F(5,6)), field(0,0,F(1,6))
    u = point(2,-1)
    ru = cmul(rho,u)
    delta = sub(ru[0],u[0]), sub(ru[1],u[1])
    def layer(k,m,n):
        p = point(m,n)
        kd = cmul((field(k),field(0)),delta)
        return add(p[0],kd[0]), add(p[1],kd[1])
    edges = 0
    for k in range(3):
        color_pairs = set()
        for j,n in product(range(3),repeat=2):
            assert distance_squared(layer(k,2*j+1,n),layer(k+1,2*j+1,n)) == ONE
            a = (n+(-j if k%2 else 0))%3
            b = (n+(-j if (k+1)%2 else 0))%3
            color_pairs.add((a,b))
            edges += 1
        assert color_pairs == set(product(range(3),repeat=2))
    for k in (0,3):
        assert layer(k,2*k,-k) == cmul(rho,point(2*k,-k))
        assert (-k)%3 == 0
    palette = set(range(6))
    chains = []
    for start in combinations(range(6),3):
        chain = [set(start)]
        for _ in range(3):
            chain.append(palette-chain[-1])
        chains.append(chain)
    assert len(chains) == 20
    assert not any(0 in c[0] and 0 in c[3] for c in chains)
    # T019: positive infinite colorings need only 18 matching-edge residues,
    # six central seam ports per layer, and four shared-point equalities.
    layer_rows = json.loads(path.with_name('layer_relations.json').read_text())
    assert len(layer_rows) == 32
    assert {(r['central_slope'],tuple(r['layer_slopes'])) for r in layer_rows} == set(
        product(range(2),product(range(2),repeat=4)))
    positive = negative = 0
    def periodic_color(m,n,slope):
        if m%2 == 0:
            return n%3
        return 3+(n-slope*((m-1)//2))%3
    for r in layer_rows:
        central = r['central_slope']
        slopes = r['layer_slopes']
        if slopes in ([0,1,0,1],[1,0,1,0]):
            assert r['status'] == 'PROVED_INCOMPATIBLE_T018' and r['witness'] is None
            negative += 1
            continue
        assert r['status'] == 'SAT'
        ps = r['witness']
        assert len(ps) == 4 and all(sorted(p)==list(range(6)) for p in ps)
        for k,p in enumerate(ps):
            assert p[periodic_color(2*k,-k,slopes[k])] == periodic_color(2*k,-k,central)
            for m,n in roots:
                x,y = m+2*k,n-k
                assert p[periodic_color(x,y,slopes[k])] != periodic_color(x,y,central)
        for k in range(3):
            for m,n in product(range(6),range(3)):
                assert ps[k][periodic_color(m,n,slopes[k])] != ps[k+1][periodic_color(m,n,slopes[k+1])]
        positive += 1
    assert (positive,negative) == (28,4)
    # T020: verify a complete covering set of maximal constraints, not searches.
    general_rows = json.loads(path.with_name('layer_extension.json').read_text())
    keys = set()
    expected_keys = {(b,a,k,r) for b in product((0,-1),repeat=4)
                     for a in product((0,-1),repeat=4) for k in range(3)
                     for r in range(3) if r != (-a[k])%3}
    for row in general_rows:
        central = tuple(row['central_steps'])
        local = tuple(row['layer_steps'])
        seam = row['relaxed_interface']
        omitted = row['omitted_residue']
        key = central,local,seam,omitted
        assert key in expected_keys and key not in keys
        keys.add(key)
        ps = row['frames']
        assert len(ps)==4 and all(sorted(p)==list(range(6)) for p in ps)
        central_values = [0]
        for d in central:
            central_values.append((central_values[-1]+d)%3)
        for k,p in enumerate(ps):
            assert p[(-k)%3] == (-k)%3  # Shared physical point.
            for dm,dn in roots:
                m,n = 2*k+dm,-k+dn
                if m%2==0:
                    a=b=n%3
                else:
                    j=(m-1)//2
                    assert j in (k-1,k)
                    a=3+(n+({k-1:0,k:local[k]}[j]))%3
                    b=3+(n+central_values[j+1])%3
                assert p[a] != b
        for k in range(3):
            assert all(ps[k][i]!=ps[k+1][i] for i in range(3))
            for a,b in product(range(3),repeat=2):
                if k != seam or (b-a)%3 != omitted:
                    assert ps[k][3+a] != ps[k+1][3+b]
    assert keys == expected_keys and len(general_rows)==1536
    return dict(translated_triple_inputs=checked, positive_witnesses=checked,
                obstruction_unit_edges=edges, complement_chains=20,
                compatible_endpoint_chains=0, five_lattice_positive_witnesses=positive,
                five_lattice_cases_excluded_by_T018=negative,
                arbitrary_word_maximal_extension_cases=len(keys))


if __name__ == '__main__':
    from pathlib import Path
    print(json.dumps(verify(Path(__file__).resolve().parents[1]/'certificates/translated_seam.json'),indent=2))
