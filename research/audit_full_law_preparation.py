"""Audit full-law preparation inputs, not a joint-law search or a new theorem.

Only pre-existing independent geometry/motion checkers are imported; the
preparation producer and SAT solvers are not. A supplied cache is compared
with all reconstructed data, not merely its self-reported hashes.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import math
import subprocess
import sys
from verify_joint_nilpotent_cover import prepare
from verify_quintic_core_probe import digest


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def reconstruct(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    prepared = prepare(root)
    context = prepared['context']
    den = math.lcm(*(x.denominator for p in context['points'] for x in p))
    points = [[int(x * den) for x in p] for p in context['points']]
    names = prepared['old']['motions'] + ['dyadic_u']
    data = dict(schema='full-law-search-cache-v1',
                geometry=prepared['report']['geometry'], denominator=den,
                points=points, edges=[list(e) for e in context['edges']],
                words=prepared['old']['words'], motions=names,
                mappings=[[list(e) for e in mm] for mm in prepared['maps'][:15]])
    assert len(names) == 15 and len(data['mappings']) == 15
    assert digest(points) == data['geometry']['point_sha256']
    words = data['words']
    assert len(words) == 5
    for word in words:
        assert isinstance(word, str) and len(word) == len(points)
        assert set(word) <= set('01234')
        assert all(word[i] != word[j] for i, j in data['edges'])

    def pattern(word, ids):
        # Blocks of positions, unlike the producer's first-occurrence labels.
        blocks = {}
        for pos, i in enumerate(ids):
            blocks.setdefault(word[i], []).append(pos)
        return tuple(sorted(tuple(b) for b in blocks.values()))

    laws = []
    for name, mm in zip(names, data['mappings']):
        left = Counter(pattern(w, [i for i, _ in mm]) for w in words)
        right = Counter(pattern(w, [j for _, j in mm]) for w in words)
        laws.append(dict(motion=name, size=len(mm), mapping_sha256=digest(mm),
                         seed_full_partition_law_equal=left == right))
    assert all(x['seed_full_partition_law_equal'] for x in laws[:14])
    assert not laws[14]['seed_full_partition_law_equal']
    mm = dict(data['mappings'][14])
    assert (mm[233], mm[239]) == (5557, 238)
    counts = [sum(w[i] == w[j] for w in words)
              for i, j in [(233, 239), (5557, 238)]]
    assert counts == [1, 5]
    summary = dict(semantic_sha256=sha(canonical(data)),
                   seed_certificate_sha256=prepared['source_sha256'],
                   geometry=data['geometry'], denominator=den,
                   proper_seed_edge_checks=len(words) * len(data['edges']),
                   motions=laws, seed_u_same_color_counts=counts, seed_support=5,
                   scope='Input geometry and E083 seed audit only; no pricing '
                         'query, no new law, and no all-word negative result.')
    return data, summary


def compare_cache(data, expected):
    # Also distinguishes True from 1 and 1.0 from 1, unlike Python equality.
    if canonical(data) != canonical(expected):
        raise ValueError('cache differs from independently reconstructed inputs')


def self_test(expected):
    tests = {
        'point-coordinate': lambda d: d['points'][0].__setitem__(0, d['points'][0][0] + 1),
        'missing-edge': lambda d: d['edges'].pop(),
        'missing-return': lambda d: d['mappings'][14].pop(),
        'wrong-return': lambda d: d['mappings'][14][0].__setitem__(1, -1),
        'seed-word': lambda d: d['words'].__setitem__(0, '0' * len(d['words'][0])),
        'motion-name': lambda d: d['motions'].__setitem__(14, 'not_u'),
        'denominator': lambda d: d.__setitem__('denominator', 1),
        'self-reported-hash': lambda d: d['geometry'].__setitem__('point_sha256', '0' * 64),
        'boolean-coordinate': lambda d: d['points'][0].__setitem__(0, True),
        'float-denominator': lambda d: d.__setitem__('denominator', float(d['denominator'])),
        'extra-key': lambda d: d.__setitem__('full_law_proved', True),
    }
    for name, mutate in tests.items():
        data = deepcopy(expected)
        mutate(data)
        try:
            compare_cache(data, expected)
        except ValueError:
            continue
        raise AssertionError('accepted mutation: ' + name)
    try:
        json.loads('{"x":1,"x":2}', object_pairs_hook=unique_keys)
    except ValueError:
        pass
    else:
        raise AssertionError('accepted duplicate JSON keys')
    process = subprocess.run([sys.executable, '-O', str(Path(__file__).resolve())],
                             capture_output=True, text=True, timeout=20)
    assert process.returncode != 0 and 'requires assertions' in process.stderr
    return sorted(tests) + ['duplicate-json-key', 'optimized-mode']


def main():
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, help='Optional original JSON or gzip cache')
    parser.add_argument('--write-cache', type=Path, help='Write rebuilt gzip input, never a proof')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data, summary = reconstruct(root)
    receipt = json.loads((root / 'certificates/full_law_preparation_audit.json').read_text())
    assert canonical(summary) == canonical(receipt['independent_inputs'])
    checked = None
    if args.cache:
        raw = args.cache.read_bytes()
        decoded = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
        compare_cache(json.loads(decoded, object_pairs_hook=unique_keys), data)
        checked = dict(path=str(args.cache), sha256=sha(raw))
    if args.write_cache:
        raw = bytearray(gzip.compress(canonical(data), mtime=0))
        raw[9] = 255  # cross-version portable gzip OS byte
        args.write_cache.parent.mkdir(parents=True, exist_ok=True)
        args.write_cache.write_bytes(raw)
    rejected = self_test(data) if args.self_test else []
    print(json.dumps(dict(status='PASS', kind='INPUT_PREPARATION_ONLY',
                          independent_inputs=summary, external_cache=checked,
                          rejection_tests=rejected, full_law_search_executed=False),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
