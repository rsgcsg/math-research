"""Independent standard-library E115 certificate verifier.

No pricing producer, LP, SAT solver, or search code is imported. By default,
the original geometry is rebuilt independently; an optional supplied cache is
compared semantically. --authenticated-cache-only skips that rebuild but
still binds the cache to the checked-in E105 semantic/geometry receipt.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import sys

from audit_full_law_preparation import canonical, reconstruct, unique_keys
from verify_eta_joined_law import expand_compact
from verify_full_law_pricing import blocks, read_potential, score


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json_gzip(path):
    raw = path.read_bytes()
    payload = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
    return json.loads(payload, object_pairs_hook=unique_keys), raw


def column(word, maps):
    return [(blocks(word, [i for i, _ in mm]),
             blocks(word, [i for _, i in mm])) for mm in maps]


def rows_for(columns):
    return {(j, pattern) for col in columns
            for j, pair in enumerate(col) for pattern in pair}


def check_words(words, data):
    n = len(data['points'])
    require(isinstance(words, list) and words, 'empty word pool')
    columns = []
    reports = []
    for ix, word in enumerate(words):
        require(isinstance(word, str) and len(word) == n and set(word) <= set('01234'),
                'word shape '+str(ix))
        require(all(word[a] != word[b] for a, b in data['edges']),
                'improper whole-Y word '+str(ix))
        col = column(word, data['mappings'])
        require(len(col) == 15, 'missing complete motion pattern')
        columns.append(col)
        reports.append(dict(word_index=ix, actual_edge_checks=len(data['edges']),
                            complete_motion_patterns=len(col),
                            source_pattern_counts=[len(pair[0]) for pair in col],
                            image_pattern_counts=[len(pair[1]) for pair in col]))
    return columns, reports


def verify(root, cache_path, certificate_path, compact_path=None,
           rebuild_geometry=True):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    cert, cert_raw = read_json_gzip(certificate_path)
    audit = json.loads((root / 'certificates/full_law_preparation_audit.json').read_text())
    expected = audit['independent_inputs']
    cache_raw = None
    if cache_path is None:
        require(rebuild_geometry, 'cache-only mode requires --cache')
        data, summary = reconstruct(root)
        require(canonical(summary) == canonical(expected), 'independent input receipt changed')
    else:
        data, cache_raw = read_json_gzip(cache_path)
    semantic = hashlib.sha256(canonical(data)).hexdigest()
    require(semantic == expected['semantic_sha256'], 'cache semantic hash')
    require(data['geometry'] == expected['geometry'], 'cache geometry binding')
    require(len(data['points']) == 10077 and len(data['edges']) == 49858
            and len(data['mappings']) == 15 and len(data['words']) == 5,
            'original E105 geometry dimensions')
    if rebuild_geometry and cache_path is not None:
        rebuilt, summary = reconstruct(root)
        require(canonical(summary) == canonical(expected), 'independent input receipt changed')
        require(canonical(rebuilt) == canonical(data), 'cache differs from independently rebuilt geometry')

    require(cert['schema'] == 'joined-seed-pricing-v1' and cert['experiment'] == 'E115',
            'E115 schema')
    require(cert['input_semantic_sha256'] == semantic, 'E115 semantic binding')
    # The original compressed cache digest is provenance, not mathematical input.
    # A semantically identical regenerated gzip may have different header bytes.
    require(isinstance(cert['original_cache_sha256'], str)
            and len(cert['original_cache_sha256']) == 64, 'cache provenance digest')
    require(cert['geometry'] == data['geometry'], 'E115 geometry binding')

    compact_path = compact_path or root / 'certificates/eta_joined_three_compact.json.gz'
    compact, compact_raw = read_json_gzip(compact_path)
    require(cert['compact_s_certificate_sha256'] == sha(compact_raw), 'compact S certificate binding')
    require(cert['compact_s_input_semantic_sha256'] == compact['input_semantic_sha256']
            == semantic, 'compact S input binding')
    expanded = expand_compact(compact, data, expected)
    s_words = expanded['words']
    seed_words = list(data['words']) + list(s_words)
    require(cert['seed_words'] == seed_words and len(seed_words) == 8,
            'seed is not exactly five E083 plus expanded three-word S law')
    require(cert['seed_sources'] == ['E083'] * 5 + ['certified-S-law'] * 3,
            'seed source labels')
    require(cert['seed_word_sha256'] == [sha(w.encode()) for w in seed_words],
            'seed word hashes')

    run = cert['run']
    require(run['strategy'] == 'dense' and type(run['round_limit']) is int
            and 1 <= run['round_limit'] <= 3
            and type(run['conflict_budget_per_query']) is int
            and 1 <= run['conflict_budget_per_query'] <= 12000,
            'E115 exceeded declared search bounds or changed strategy')
    words = run['words']
    require(words[:8] == seed_words, 'run changed or reordered the exact seed')
    columns, word_reports = check_words(words, data)
    history = run['history']
    require(len(history) <= run['round_limit'], 'exceeded round limit')
    current_size = 8
    steps = []
    for step, record in enumerate(history):
        require(record['step'] == step and record['pool_size'] == current_size,
                'round/pool index')
        current_rows = rows_for(columns[:current_size])
        require(record['row_count'] == len(current_rows), 'round omitted full-domain rows')
        potential = read_potential(record['potential'], columns, current_size)
        pool_scores = [score(col, potential) for col in columns[:current_size]]
        require(record['pool_values'] == pool_scores and all(type(x) is int for x in pool_scores)
                and min(pool_scores) > 0, 'invalid integer pool cut')
        require(record['pool_strict_margin'] == min(pool_scores), 'pool margin')
        queries = record['queries']
        require(len(queries) == 1 and queries[0]['target'] == 0
                and not queries[0]['restricted_to_reused_patterns'],
                'pricing query was restricted or used wrong threshold')
        q = queries[0]
        require(q['answer'] in ('SAT', 'UNKNOWN', 'UNSAT_UNCERTIFIED'),
                'unsupported pricing verdict')
        step_result = dict(step=step, pool_size=current_size, pool_rows=len(current_rows),
                           pool_margin=min(pool_scores), query_answer=q['answer'],
                           conflicts=q['stats'].get('conflicts'), added_word=False)
        if 'new_word_index' in record:
            require(q['answer'] == 'SAT' and record['new_word_index'] == current_size,
                    'counterexample was not reported by SAT query')
            value = score(columns[current_size], potential)
            require(type(record['price']) is int and value == record['price'] <= 0,
                    'counterexample fails exact pricing inequality')
            require(columns[current_size] not in columns[:current_size],
                    'pricing witness repeats a complete column')
            added = rows_for([columns[current_size]]) - current_rows
            require(record['new_row_count'] == len(added), 'incomplete new all-domain rows')
            step_result.update(added_word=True, price=value, new_rows=len(added),
                               new_word_index=current_size)
            current_size += 1
        else:
            require(step == len(history)-1 and q['answer'] != 'SAT',
                    'missing SAT witness or nonterminal unresolved query')
        steps.append(step_result)
    require(current_size == len(words), 'unlogged pool word')
    final_rows = rows_for(columns)
    require(run['final_row_count'] == len(final_rows), 'final pool row count')

    final_status = run['final_pool_status']
    if final_status == 'EXACT_POOL_SEPARATOR':
        potential = read_potential(run['final_potential'], columns, len(words))
        final_scores = [score(col, potential) for col in columns]
        require(run['final_pool_values'] == final_scores and min(final_scores) > 0,
                'invalid final finite-pool cut')
        require(run['full_law'] is None, 'pool separator conflicts with positive-law claim')
    elif final_status == 'EXACT_POSITIVE_LAW':
        weights = [Fraction(x) for x in run['full_law']]
        require(len(weights) == len(words) and all(w >= 0 for w in weights)
                and sum(weights) == 1, 'positive law weights')
        balance = Counter()
        for col, weight in zip(columns, weights):
            for j, (a, b) in enumerate(col):
                balance[j, a] += weight
                balance[j, b] -= weight
        require(not any(balance.values()), 'claimed positive law fails a complete domain')
    else:
        require(final_status == 'NUMERICAL_MASTER_UNRESOLVED', 'unsupported final pool status')

    require(run['status'] in ('ROUND_LIMIT_UNKNOWN', 'PRICING_UNRESOLVED',
                              'EXACT_POSITIVE_LAW', 'NUMERICAL_MASTER_UNRESOLVED'),
            'producer made unsupported global verdict')
    # The producer only promotes an exact positive law when the final master
    # actually returns that law. Conversely, a numerical final master cannot
    # be reported as a positive law or as a certified separator. A bounded
    # round-limit status is also meaningful only when every declared round ran.
    if final_status == 'EXACT_POSITIVE_LAW':
        require(run['status'] == 'EXACT_POSITIVE_LAW',
                'final positive law missing matching global status')
    if run['status'] == 'EXACT_POSITIVE_LAW':
        require(final_status != 'EXACT_POOL_SEPARATOR',
                'global positive law conflicts with final pool separator')
        # The global status can retain a law certified by an earlier master
        # even if the final numerical master is unresolved. Validate that law
        # independently of final_pool_status in that case too.
        weights = [Fraction(x) for x in run['full_law']]
        require(len(weights) == len(words) and all(w >= 0 for w in weights)
                and sum(weights) == 1, 'global positive law weights')
        balance = Counter()
        for col, weight in zip(columns, weights):
            for j, (a, b) in enumerate(col):
                balance[j, a] += weight
                balance[j, b] -= weight
        require(not any(balance.values()), 'global positive law fails a complete domain')
    if run['status'] == 'ROUND_LIMIT_UNKNOWN':
        require(len(history) == run['round_limit'],
                'round-limit status before declared limit')
    require('finite pool' in run['scope'].lower()
            and 'no solver unsat is certified' in run['scope'].lower(),
            'producer scope must preserve nonclaim')
    report = dict(status='PASS', experiment='E115', seed_words=8,
                  pool_words=len(words), word_reports=word_reports, steps=steps,
                  final_pool_status=final_status, run_status=run['status'],
                  full_domain_rows=len(final_rows),
                  whole_edge_checks=sum(x['actual_edge_checks'] for x in word_reports),
                  all_word_obstruction_certified=False,
                  cache_sha256=sha(cache_raw) if cache_raw is not None else None,
                  certificate_sha256=sha(cert_raw),
                  geometry_rebuilt=rebuild_geometry,
                  scope='Exact finite-pool cuts and proper counterexample columns only; '
                        'solver UNSAT is uncertified and no all-word obstruction is claimed.')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--certificate', type=Path,
                        default=Path('certificates/joined_seed_pricing.json.gz'))
    parser.add_argument('--compact-s-law', type=Path,
                        default=Path('certificates/eta_joined_three_compact.json.gz'))
    parser.add_argument('--authenticated-cache-only', action='store_true',
                        help='skip expensive geometry rebuild; still bind cache to checked-in receipt')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = verify(root, args.cache, args.certificate, args.compact_s_law,
                    rebuild_geometry=not args.authenticated_cache_only)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
