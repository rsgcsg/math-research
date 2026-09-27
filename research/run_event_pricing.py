"""Bounded exact pricing with SAT witnesses or independently checked hinted RUP.

This search front end needs python-sat; the independent verifier does not.
A rejected/non-RUP solver trace is UNSAT_UNCERTIFIED, never an obstruction.
Input caches must first be produced by audit_full_law_preparation.py.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import time
from event_pricing_cnf import formula
from rup_hint_export import export
from verify_event_pricing import bind_events, check_word, score, verify_query


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def load(path):
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b': raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=unique_keys)


def search(instance, coefficients, target, conflicts=20000):
    if type(conflicts) is not int or conflicts <= 0: raise ValueError('conflict budget')
    from pysat.solvers import Solver
    started = time.monotonic()
    built = formula(**instance, coefficients=coefficients, target=target)
    with Solver(name='glucose3', bootstrap_with=built['clauses'], with_proof=True) as solver:
        solver.conf_budget(conflicts)
        answer = solver.solve_limited()
        statistics = solver.accum_stats()
        model = solver.get_model() if answer is True else None
        trace = solver.get_proof() if answer is False else None
    out = dict(status='UNKNOWN', coefficients=coefficients, target=target,
               cnf_sha256=built['cnf_sha256'], variables=built['nv'],
               clauses=len(built['clauses']), statistics=statistics,
               conflict_budget=conflicts, solver='glucose3',
               elapsed_seconds=round(time.monotonic()-started, 6))
    if answer is True:
        positives = set(x for x in model if x > 0)
        k, n = instance['k'], instance['n']
        if k > 10: raise ValueError('string witness alphabet limited to ten colors')
        choices = [[c for c in range(k) if i*k+c+1 in positives] for i in range(n)]
        if any(len(c) != 1 for c in choices): raise ValueError('solver model lacks unique color')
        word = ''.join(str(c[0]) for c in choices)
        check_word(word, n, k, instance['edges'])
        value = score(word, instance['events'], coefficients)
        if value > target: raise ValueError('invalid solver witness objective')
        out.update(status='SAT_WITNESS', word=word, value=value)
    elif answer is False:
        out['status'] = 'UNSAT_UNCERTIFIED'
        out['solver_trace'] = trace
        try:
            proof = export(built['clauses'], trace)
            query = dict(status='NO_WORD_AT_OR_BELOW_TARGET', coefficients=coefficients,
                         target=target, cnf_sha256=built['cnf_sha256'], proof=proof)
            checked = verify_query(instance, query)
        except (AssertionError, ValueError, IndexError, KeyError, TypeError) as error:
            out['certification_error'] = str(error)
        else:
            out.update(status='VERIFIED_NO_WORD_AT_OR_BELOW_TARGET', query=query, verification=checked)
            del out['solver_trace']
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--conflicts', type=int, default=20000)
    args = parser.parse_args()
    if not __debug__: raise RuntimeError('verification requires assertions')
    root = Path(__file__).resolve().parents[1]
    data = load(args.cache)
    raw = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()
    digest = hashlib.sha256(raw).hexdigest()
    receipt = load(root/'certificates/full_law_preparation_audit.json')
    if digest != receipt['independent_inputs']['semantic_sha256']:
        raise ValueError('input cache not the independently bound geometry')
    request = load(args.request)
    if set(request) != {'schema', 'events', 'coefficients', 'target'} or request['schema'] != 'event-pricing-request-v1':
        raise ValueError('request fields')
    events = bind_events(request['events'], data['mappings'])
    instance = dict(n=len(data['points']), k=5, edges=data['edges'], events=events)
    result = search(instance, request['coefficients'], request['target'], args.conflicts)
    result.update(schema='event-pricing-result-v1', input_semantic_sha256=digest, request=request,
                  scope='Specified event objective on all proper five-colorings; not automatically a positive strict gap.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'target', 'variables', 'clauses', 'statistics')}))


if __name__ == '__main__': main()
