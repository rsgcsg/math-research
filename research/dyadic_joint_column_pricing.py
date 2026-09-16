"""One bounded, support-free column-pricing query, not a joint-law solver.

The finite master has all proper colorings as columns and full partition rows.
This isolated experiment invalidates a candidate cut from an old column pool.
It never calls a fixed-number-of-words joint solver.
"""

from itertools import permutations
from pathlib import Path
import argparse
import hashlib
import json

from quintic_multiword_joint import MultiwordEncoding
from verify_quintic_tau_union import verify as geometry
from verify_dyadic_mixed_return_joint import _new_definitions, _mapping
from verify_quintic_core_probe import digest


FILES = ('quintic_multiword_joint.json', 'quintic_multiword_return_joint.json',
         'quintic_tau_union.json')


def pattern(word, vertices):
    labels = {}
    return tuple(labels.setdefault(word[i], len(labels)) for i in vertices)


def read_pool(root):
    words, sources = [], []
    for name in FILES:
        raw = (root / 'certificates' / name).read_bytes()
        data = json.loads(raw)
        current = (data['result']['words'] if 'words' in data['result']
                   else [data['result']['five_coloring']])
        words.extend(current)
        sources.append(dict(file=name, sha256=hashlib.sha256(raw).hexdigest(),
                            count=len(current)))
    return words, sources


def run(root, budget):
    from pysat.solvers import Solver
    parent, context = geometry(root, geometry_context=True)
    pairs = _mapping(context, _new_definitions(context)[0])
    assert len(pairs) == 29
    left, right = [i for i, j in pairs], [j for i, j in pairs]
    words, sources = read_pool(root)
    assert len(words) == 11
    assert all(w[i] != w[j] for w in words for i, j in context['edges'])
    source_patterns = sorted({pattern(w, left) for w in words})
    image_patterns = {pattern(w, right) for w in words}
    assert set(source_patterns).isdisjoint(image_patterns)
    print(json.dumps(dict(progress='pool_checked', words=len(words),
                          source_patterns=len(source_patterns),
                          image_patterns=len(image_patterns))), flush=True)
    encoding = MultiwordEncoding(len(context['points']), context['edges'], 1)
    # Forbid each entire source partition, including every palette labeling.
    for pat in source_patterns:
        blocks = max(pat) + 1
        for palette in permutations(range(5), blocks):
            encoding.clauses.append([-encoding.color(0, vertex, palette[color])
                                     for vertex, color in zip(left, pat)])
    # The image must have one source-pool partition. Global relabeling lets
    # its selected partition use canonical labels without loss of solutions.
    selectors = [encoding.fresh() for _ in source_patterns]
    encoding.clauses.append(selectors)
    for select, pat in zip(selectors, source_patterns):
        encoding.clauses.extend([[-select, encoding.color(0, vertex, color)]
                                 for vertex, color in zip(right, pat)])
    print(json.dumps(dict(progress='pricing_formula', variables=encoding.top,
                          clauses=len(encoding.clauses), budget=budget)), flush=True)
    with Solver(name='cadical195', bootstrap_with=encoding.clauses) as solver:
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        status = ('SAT' if answer is True else 'UNKNOWN' if answer is None
                  else 'UNSAT_PRICING_QUERY_ONLY_UNCERTIFIED')
        result = None
        if answer is True:
            model = {x for x in solver.get_model() if x > 0}
            word = ''.join(str(next(c for c in range(5)
                              if encoding.color(0, i, c) in model))
                           for i in range(len(context['points'])))
            source_pattern, image_pattern = pattern(word, left), pattern(word, right)
            value = int(source_pattern in source_patterns) - int(image_pattern in source_patterns)
            assert value == -1
            assert all(word[i] != word[j] for i, j in context['edges'])
            result = dict(word=word, source_pattern=source_pattern,
                          image_pattern=image_pattern, cut_value=value)
        stats = solver.accum_stats()
    return dict(schema=1, experiment='dyadic_joint_column_pricing_20260916',
                geometry=parent['geometry'], source_files=sources,
                mapping=pairs, mapping_sha256=digest(pairs),
                pool_source_patterns=source_patterns,
                pool_image_patterns=sorted(image_patterns), pool_cut_values=[1] * len(words),
                query=dict(status=status, conflict_budget=budget, stats=stats), result=result,
                scope=('A proper column with negative old-pool cut value, if present; '
                       'not a complete joint law, not a non-5 obstruction, and not '
                       'an exhaustive pricing solution when UNKNOWN'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--budget', type=int, default=20000)
    args = parser.parse_args()
    assert 1 <= args.budget <= 20000
    print('PRICING_FINAL_JSON=' + json.dumps(run(Path(__file__).resolve().parents[1], args.budget),
                                           separators=(',', ':')), flush=True)
