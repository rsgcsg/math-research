#!/usr/bin/env python3
"""Positive replay, reproducibility and adversarial tests for E095/E096 only.

This is not a substitute for the repository-wide make check.
"""
from __future__ import annotations
import copy
import gzip
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from build_salem_sextic_four import build
from verify_salem_sextic_four import verify as verify_graph
from verify_salem_height_obstruction import verify as verify_height

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    require(__debug__, 'run without -O or -OO')
    graph_path = ROOT/'certificates/salem_sextic_four.json.gz'
    height_path = ROOT/'certificates/salem_sextic_height.json'
    graph_raw = gzip.decompress(graph_path.read_bytes())
    graph = json.loads(graph_raw)
    height = json.loads(height_path.read_text())
    results = {'graph': verify_graph(graph_path), 'height': verify_height(height_path)}
    rebuilt = (json.dumps(build(), separators=(',', ':'), sort_keys=True)+'\n').encode()
    require(rebuilt == graph_raw, 'producer did not reproduce the frozen certificate')
    rejected = []
    with tempfile.TemporaryDirectory(prefix='hn-salem-tests-') as directory:
        path = Path(directory)/'mutated.json'
        def reject(name, data, verifier):
            path.write_text(json.dumps(data))
            try:
                verifier(path)
            except (ValueError, TypeError, KeyError, IndexError):
                rejected.append(name)
                return
            raise ValueError(f'mutation was accepted: {name}')
        d = copy.deepcopy(graph); d['points'][0][0] += 1
        reject('coordinate', d, verify_graph)
        d = copy.deepcopy(graph); d['edges'].pop()
        reject('missing-unit-edge', d, verify_graph)
        d = copy.deepcopy(graph); d['polynomial'][0] = 2
        reject('field-polynomial', d, verify_graph)
        d = copy.deepcopy(graph); d['colors4'] = '0'*114
        reject('four-colouring', d, verify_graph)
        d = copy.deepcopy(graph); d['non3_tree'] = -1
        reject('false-conflict-leaf', d, verify_graph)
        d = copy.deepcopy(graph)
        children = d['non3_tree'][1]
        children[next(i for i, c in enumerate(children) if c is not None)] = None
        reject('omitted-colour-branch', d, verify_graph)
        d = copy.deepcopy(graph); d['anchor'] = [0, 0]
        reject('nonedge-palette-anchor', d, verify_graph)
        d = copy.deepcopy(graph); d['vertex_deletion_colors3'][0] = '-'+'0'*113
        reject('deletion-colouring', d, verify_graph)
        d = copy.deepcopy(height); d['l1_norms'][0] += 1
        reject('relation-norm', d, verify_height)
        d = copy.deepcopy(height); d['separators'] = [[0]*7 for _ in range(10)]
        d['l1_norms'] = [0]*10
        reject('no-sign-separation', d, verify_height)
        d = copy.deepcopy(height); d['separators'][0].pop()
        reject('relation-dimension', d, verify_height)
        d = copy.deepcopy(height); d['linear_coloring_basis'] = [0]*6
        reject('linear-three-colouring', d, verify_height)
        d = copy.deepcopy(height); d['direction_colors_mod3'][12] = 1
        reject('direction-thirteen', d, verify_height)
        d = copy.deepcopy(height); d['polynomial'][0] = 0
        reject('height-polynomial', d, verify_height)
    for script in ('verify_salem_sextic_four.py', 'verify_salem_height_obstruction.py'):
        run = subprocess.run([sys.executable, '-O', str(ROOT/'research'/script)],
                             capture_output=True, text=True, check=False)
        require(run.returncode != 0 and 'without -O' in run.stderr,
                f'optimized Python was not explicitly rejected: {script}')
    results.update(status='PASS', byte_identical_rebuild=True,
                   mutations_rejected=rejected, optimized_mode_rejections=2,
                   scope='new Salem checks only; not the full repository regression')
    print(json.dumps(results, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
