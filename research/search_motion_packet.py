"""Bounded positive packet search. Fixed-support failure is NEVER full-law failure.

Run with an independently bound cache, e.g.:
  python research/search_motion_packet.py --cache references/cache/geometry.json.gz \
    --support 2 --motions 5 6 9 11 13 14 --budget 50000 --output packet.json

A support-one Glucose3 denial can optionally be exported to the RUP checker.
All positive words need separate replay against reconstructed actual geometry.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import time
from collections import Counter
from full_law_pricing import column
from quintic_multiword_joint import MultiwordEncoding
from motion_packet_cnf import singleton_formula
from run_event_pricing import load


def run(data, motions, support, budget, certify_singleton=False):
    if (type(support) is not int or not 1<=support<=6 or type(budget) is not int
            or not 1<=budget<=100000 or not motions or len(set(motions))!=len(motions)
            or any(type(j) is not int or not 0<=j<len(data['mappings']) for j in motions)):
        raise ValueError('invalid or out-of-resource-limit search parameters')
    if certify_singleton and support!=1:
        raise ValueError('this exporter only certifies a one-word query')
    try:
        from pysat.solvers import Solver
        import pysat
    except ModuleNotFoundError as error:
        raise RuntimeError('Search needs optional python-sat; install requirements-packet-search.txt. '
                           'Independent check-packet does not need it.') from error
    n = len(data['points'])
    start = time.monotonic()
    name = 'glucose3' if certify_singleton else 'cadical195'
    output = dict(schema='motion-packet-search-v1', support=support, motions=motions,
                  conflict_budget=budget, environment=dict(python=platform.python_version(),
                  python_sat=pysat.__version__, solver=name), full_law_claim=False)
    if support==1:
        built = singleton_formula(n, data['edges'], 5, [data['mappings'][j] for j in motions])
        initial = built['clauses']
        decode = lambda model: [''.join(str(next(c for c in range(5) if 5*i+c+1 in model))
                                      for i in range(n))]
    else:
        enc = MultiwordEncoding(n, data['edges'], support)
        initial = enc.clauses
        del enc.clauses
        built = None
        decode = lambda model: enc.decode(list(model))['words']
    with Solver(name=name, bootstrap_with=initial, with_proof=certify_singleton) as solver:
        if support>1:
            for j in motions:
                solver.append_formula(enc.add_motion(data['mappings'][j]))
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        output['statistics'] = solver.accum_stats()
        model = {x for x in solver.get_model() if x>0} if answer is True else None
        trace = solver.get_proof() if answer is False and certify_singleton else None
    if answer is True:
        words = decode(model)
        if any(len(w)!=n or any(w[a]==w[b] for a,b in data['edges']) for w in words):
            raise ValueError('invalid solver coloring')
        cols = [column(w, data['mappings']) for w in words]
        passed = [j for j in range(len(data['mappings'])) if
                  Counter(c[j][0] for c in cols)==Counter(c[j][1] for c in cols)]
        if not set(motions)<=set(passed):
            raise ValueError('invalid packet matching')
        output.update(status='POSITIVE_PACKET', words=words,
                      full_domains_passed=passed, full_law_claim=len(passed)==15)
    elif answer is None:
        output['status'] = 'UNKNOWN_FIXED_SUPPORT'
    else:
        output['status'] = 'UNSAT_FIXED_SUPPORT_UNCERTIFIED'
        if trace is not None:
            from rup_hint_export import export
            from verify_rup_lrat import check
            output.update(cnf_sha256=built['cnf_sha256'], nv=built['nv'], clauses=len(initial))
            try:
                proof = export(initial, trace)
                checked = check(initial, proof)
            except (ValueError, AssertionError, KeyError, IndexError) as error:
                output['certification_error'] = str(error)
            else:
                output.update(status='VERIFIED_NO_SINGLETON', proof=proof, verification=checked)
    output['elapsed_seconds'] = time.monotonic()-start
    output['scope'] = ('Only the listed motions and fixed support. NO_SINGLETON does not '
                       'mean no distribution; a multiword positive law needs full-domain replay.')
    return output


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--support', type=int, default=2)
    parser.add_argument('--motions', type=int, nargs='+', default=[5,6,9,11,13,14])
    parser.add_argument('--budget', type=int, default=50000)
    parser.add_argument('--certify-singleton', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data = load(args.cache)
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',',':'),
                            ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    expected = load(root/'certificates/full_law_preparation_audit.json')['independent_inputs']['semantic_sha256']
    if digest!=expected:
        raise ValueError('cache does not match independently verified geometry')
    result = run(data, args.motions, args.support, args.budget, args.certify_singleton)
    result['input_semantic_sha256'] = digest
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('words','proof')}, indent=2))


if __name__=='__main__':
    main()
