"""Reproduce bounded discovery runs and preserve models, not only SAT labels."""
import json
from pathlib import Path
from search_phases import search
from search_triangle_defect_patch import run as patch_search


def main():
    runs = [search(6, 6, True, 100000)]
    for w, h in ((6, 6), (8, 8), (9, 6), (8, 12), (12, 8)):
        runs.append(search(w, h, False, 100000, True))
    patches = [patch_search(r) for r in (2, 3, 4, 6)]
    output = Path(__file__).resolve().parents[1] / 'certificates/search_models.json'
    output.write_text(json.dumps(dict(torus=runs, patches=patches), indent=2) + '\n')
    print(json.dumps(dict(torus=[{k: v for k, v in r.items() if k not in ('rows', 'partners')}
                                 for r in runs],
                          patches=[{k: v for k, v in r.items() if k != 'coloring'}
                                   for r in patches]), indent=2))


if __name__ == '__main__':
    main()
