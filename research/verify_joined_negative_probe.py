"""E115 supplemental negative-price witness; no CNF or solver is trusted."""
from pathlib import Path
import hashlib
import json

from audit_full_law_preparation import reconstruct, unique_keys
from verify_joined_seed_pricing import check_words, column, read_json_gzip, require
from verify_full_law_pricing import read_potential, score


def verify(root):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    data, summary = reconstruct(root)
    original, raw = read_json_gzip(root / 'certificates/joined_seed_pricing.json.gz')
    cert = json.loads((root / 'certificates/joined_seed_negative_probe.json').read_text(),
                      object_pairs_hook=unique_keys)
    require(cert['schema'] == 'e115-negative-face-probe-witness-v1', 'probe schema')
    require(cert['cache_semantic_sha256'] == original['input_semantic_sha256']
            == summary['semantic_sha256'], 'geometry binding')
    require(cert['e115_certificate_sha256'] == hashlib.sha256(raw).hexdigest(), 'E115 binding')
    require(type(cert['potential_index']) is int and cert['potential_index'] == 0, 'probe index')
    record = original['run']['history'][0]
    require(cert['potential_records'] == record['potential'] and cert['pool_size'] == 8,
            'not the first E115 potential')
    columns = [column(w, data['mappings']) for w in original['seed_words']]
    potential = read_potential(record['potential'], columns, 8)
    probe_columns, reports = check_words([cert['word']], data)
    value = score(probe_columns[0], potential)
    require(type(cert['exact_score']) is int and value == cert['exact_score'] <= -1,
            'not a negative-price witness')
    return dict(status='PASS', value=value, actual_edge_checks=reports[0]['actual_edge_checks'],
                motion_patterns=reports[0]['complete_motion_patterns'],
                nonnegative_candidate_refuted=True, hn_bound_changed=False,
                scope='Only the first E115 potential is refuted as an all-word nonnegative cut.')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), sort_keys=True))
