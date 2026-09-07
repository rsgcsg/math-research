"""Small standard-library entry point for independent finite verification."""
import json
from pathlib import Path
from phase_checks import run
from relations import calibrate
from exact_geometry import check_geometry
from balanced_weights import run as check_balanced_weights
import hashlib
from verify_search_models import verify as verify_search_models
from itertools import permutations
from verify_translated_seam import verify as verify_translated_seam


def main():
    import sys
    if not __debug__:
        sys.exit('Do not disable assertions when verifying mathematical certificates.')
    root = Path(__file__).resolve().parents[1]
    for p in ('README.md', 'AGENTS.md', 'docs/CURRENT.md', 'docs/ROUTES.md',
              'docs/RESULTS.md', 'references/SOURCES.md'):
        assert (root / p).is_file(), p
    result = run()
    result['relation_calibration'] = calibrate()
    result['exact_geometry'] = check_geometry()
    result['balanced_weights'] = check_balanced_weights()
    saved = root / 'certificates/phase_checks.json'
    assert saved.is_file(), 'Missing exact finite table'
    # JSON normalizes integer keys and tuples; compare serialized structures.
    assert json.loads(saved.read_text()) == json.loads(json.dumps(result))
    provenance = root / 'references/history/SHA256.json'
    if provenance.exists():
        for name, expected in json.loads(provenance.read_text()).items():
            assert hashlib.sha256((provenance.parent / name).read_bytes()).hexdigest() == expected
    models = root / 'certificates/search_models.json'
    assert models.is_file(), 'Missing saved search witnesses'
    print(json.dumps(verify_search_models(json.loads(models.read_text())), indent=2))
    for radius in (3, 4):
        seam = json.loads((root / f'certificates/seam_radius{radius}.json').read_text())
        points = [tuple(p) for p in seam['points']]
        expected = sorted((x,y) for x in range(-radius,radius+1) for y in range(-radius,radius+1)
                          if max(abs(x),abs(y),abs(x+y)) <= radius)
        assert points == expected
        # Independently use the all-contact theorem, rather than the search's field-distance routine.
        edges = []
        for i, (x,y) in enumerate(points):
            for j, (u,v) in enumerate(points):
                if ((x,y)==(u,v) and x*x+x*y+y*y==3) or (
                    (x,y)==(0,0) and u*u+u*v+v*v==1) or (
                    (u,v)==(0,0) and x*x+x*y+y*y==1):
                    edges.append([i,j])
        assert seam['cross_edges'] == edges
        lo = min(x//2 for x,y in points if x % 2)
        colorings = []
        for word in seam['words']:
            s = {lo:0}
            for i, step in enumerate(word):
                assert step in (0,-1)
                s[lo+i+1] = (s[lo+i]+step) % 3
            colorings.append([y%3 if x%2==0 else 3+(y+s[x//2])%3 for x,y in points])
        assert len(colorings)==len(set(tuple(c) for c in colorings))==8
        for i,a in enumerate(colorings):
            for j,b in enumerate(colorings):
                count = sum(all(a[u] != ((0,)+p)[b[v]] for u,v in edges)
                            for p in permutations(range(1,6)))
                assert count == seam['allowed_relative_permutation_counts'][i][j] == 53
    print('PASS: exact Moser-angle seam relations, 128 word pairs, 120 relative frames each')
    print(json.dumps(verify_translated_seam(root / 'certificates/translated_seam.json'), indent=2))
    print(json.dumps(dict(status='PASS', checks=list(result),
                          row_transitions=result['row_transitions'],
                          symmetry=result['symmetry']), indent=2))


if __name__ == '__main__':
    main()
