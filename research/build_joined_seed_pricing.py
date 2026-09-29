"""Bounded E115 pricing seeded by the certified three-word S law.

This is a diagnostic around the existing E105 producer, not a new pricing
algorithm. It preserves the five E083 words, appends the three independently
expanded S-law words, and runs at most three unrestricted dense rounds.
Solver UNSAT is recorded only as uncertified.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import tempfile

from audit_full_law_preparation import canonical, unique_keys
from full_law_pricing import run
from verify_eta_joined_law import expand_compact


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json_gzip(path):
    raw = path.read_bytes()
    payload = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
    return json.loads(payload, object_pairs_hook=unique_keys), raw


def proper(word, data):
    return (isinstance(word, str) and len(word) == len(data['points'])
            and set(word) <= set('01234')
            and all(word[i] != word[j] for i, j in data['edges']))


def build(root, cache_path, compact_path, output_path, rounds=3, budget=12000):
    if not 1 <= rounds <= 3:
        raise ValueError('E115 is bounded to at most three rounds')
    if not 1 <= budget <= 12000:
        raise ValueError('E115 query budget is bounded to 12000 conflicts')

    cache, cache_raw = read_json_gzip(cache_path)
    audit = json.loads((root / 'certificates/full_law_preparation_audit.json').read_text())
    expected = audit['independent_inputs']
    semantic = hashlib.sha256(canonical(cache)).hexdigest()
    if semantic != expected['semantic_sha256']:
        raise ValueError('original cache semantic hash differs from authenticated E105 input')
    if cache['geometry'] != expected['geometry'] or len(cache['words']) != 5:
        raise ValueError('original geometry or five-word E083 seed changed')

    compact, compact_raw = read_json_gzip(compact_path)
    expanded = expand_compact(compact, cache, expected)
    s_words = expanded['words']
    if len(s_words) != 3 or not all(proper(w, cache) for w in s_words):
        raise ValueError('expanded S witness is not three proper full-Y words')
    seed_words = list(cache['words']) + list(s_words)
    if len(seed_words) != 8 or any(not proper(w, cache) for w in seed_words):
        raise ValueError('expected exactly eight proper seed words')

    data = dict(cache)
    data['words'] = seed_words
    with tempfile.TemporaryDirectory(prefix='e115-joined-seed-') as temp:
        raw_run = Path(temp) / 'run.json'
        result = run(data, 'dense', rounds, budget, raw_run)

    artifact = dict(
        schema='joined-seed-pricing-v1', experiment='E115',
        input_semantic_sha256=semantic,
        original_cache_sha256=sha(cache_raw),
        geometry=cache['geometry'],
        compact_s_certificate_sha256=sha(compact_raw),
        compact_s_input_semantic_sha256=compact['input_semantic_sha256'],
        seed_words=seed_words,
        seed_word_sha256=[sha(w.encode()) for w in seed_words],
        seed_sources=['E083'] * 5 + ['certified-S-law'] * 3,
        run=result,
        scope=('Three-round dense full-word pricing diagnostic seeded by the '
               'five E083 words and three S-law words. Finite-pool cuts are '
               'not all-word obstructions; solver UNSAT is uncertified.'))
    encoded = bytearray(gzip.compress(canonical(artifact), mtime=0))
    encoded[9] = 255
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(encoded)
    return artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--compact-s-law', type=Path,
                        default=Path('certificates/eta_joined_three_compact.json.gz'))
    parser.add_argument('--output', type=Path,
                        default=Path('certificates/joined_seed_pricing.json.gz'))
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--budget', type=int, default=12000)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    artifact = build(root, args.cache, args.compact_s_law, args.output,
                     args.rounds, args.budget)
    r = artifact['run']
    print(json.dumps(dict(status=r['status'], rounds=len(r['history']),
                          seed_words=len(artifact['seed_words']),
                          final_pool_status=r['final_pool_status'],
                          final_row_count=r['final_row_count'],
                          artifact=str(args.output)), sort_keys=True))


if __name__ == '__main__':
    main()
