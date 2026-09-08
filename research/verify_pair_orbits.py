"""Independent exhaustive coverage check. No search module or solver imports."""
import gzip
import json
from itertools import combinations
from pathlib import Path


def verify(root):
    data = json.loads(gzip.decompress((root/'certificates/pair_orbits_five.json.gz').read_bytes()))
    assert data['schema'] == 1 and data['pair_count'] == 5
    assert len(data['records']) == 59049
    pairs = list(combinations(range(5), 2))
    omissions = ((0, 0, 0, 1, 1), (0, 0, 0, 1, 2),
                 (0, 0, 1, 1, 2), (0, 0, 1, 2, 3))
    counts = dict(k23=0, k4=0, rhombus=0, positive=0)
    positive_words = 0
    # Formal integer identity: weighted rhombi = 5(F_0-F_2).
    coeff = [0]*10
    for i, weight in enumerate((4, 4, 3, 3, 2, 2, 1, 1)):
        for offset, sign in ((0, 1), (3, 1), (1, -1), (2, -1)):
            coeff[(i+offset) % 10] += weight*sign
    assert coeff == [5, 0, -5, 0, 0, 0, 0, 0, 0, 0]
    for code, (kind, witness) in enumerate(data['records']):
        edges = set()
        for pos, (i, j) in enumerate(pairs):
            digit = code // (3**pos) % 3
            if digit == 1:
                edges.update(((2*i, 2*j), (2*i+1, 2*j+1)))
            elif digit == 2:
                edges.update(((2*i, 2*j+1), (2*i+1, 2*j)))
        has = lambda a, b: tuple(sorted((a, b))) in edges
        assert kind in counts
        counts[kind] += 1
        if kind == 'positive':
            assert len(witness) == 5
            for number, raw in enumerate(witness):
                assert isinstance(raw, str) and len(raw) == 10
                word = list(map(int, raw))
                for v, c in enumerate(word):
                    if number == 0:
                        assert 0 <= c <= 2
                    else:
                        assert 0 <= c <= 3 and c != omissions[number-1][v//2]
                assert all(word[a] != word[b] for a, b in edges)
                positive_words += 1
        else:
            assert all(isinstance(v, int) and 0 <= v < 10 for v in witness)
            assert len(witness) == len(set(witness))
            if kind == 'k23':
                assert len(witness) == 5
                assert all(has(a, b) for a in witness[:2] for b in witness[2:])
            elif kind == 'k4':
                assert len(witness) == 4
                assert all(has(a, b) for a, b in combinations(witness, 2))
            else:
                assert len(witness) == 10
                # Every required rhombus edge checked, not merely an isomorphism label.
                for i in range(10):
                    a, b, c, d = [witness[(i+j) % 10] for j in (0, 1, 3, 2)]
                    assert all(has(u, v) for u, v in ((a, b), (b, c), (c, d), (d, a)))
                assert has(witness[0], witness[2])
    assert counts == data['counts'] == dict(k23=8832, k4=840, rhombus=192, positive=49185)
    assert positive_words == 245925
    return dict(status='VERIFIED_REBUILT_FIVE_ORBIT_CENSUS', graphs=59049,
                categories=counts, positive_words=positive_words,
                nonuniform_list_words=196740, original_package_recovered=False,
                scope='Not six/seven-orbit certification; not an HN lower bound.')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Do not disable verifier assertions.')
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
