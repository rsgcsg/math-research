"""Search producer for a complete two-terminal coloring portfolio of Y.

Requires python-sat 1.9.dev15 (CaDiCaL 1.9.5). All budgets are finite. A raw
negative or timeout is recorded, never promoted to a forced-color theorem.
The resulting portfolio must be checked by verify_Y_pair_portfolio.py.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import random
import time

from pysat.solvers import Solver
from audit_full_law_preparation import reconstruct, canonical


def graph_cnf(n, edges):
    clauses = []
    for i in range(n):
        vs = [5*i+c+1 for c in range(5)]
        clauses.append(vs)
        for c in range(5):
            for b in range(c):
                clauses.append([-vs[c], -vs[b]])
    for i, j in edges:
        for c in range(5):
            clauses.append([-5*i-c-1, -5*j-c-1])
    return clauses


def decode(solver, n, edges):
    model = set(solver.get_model())
    word = ''.join(str(next(c for c in range(5) if 5*i+c+1 in model))
                   for i in range(n))
    if not all(word[i] != word[j] for i, j in edges):
        raise ValueError('solver returned an invalid coloring')
    return word


def classes(words):
    groups = defaultdict(list)
    for i, sig in enumerate(zip(*words)):
        groups[sig].append(i)
    return sorted((v for v in groups.values() if len(v)>1),
                  key=lambda v: (-len(v), v))


def uncovered(n, edges, words):
    mask = (1<<n)-1
    remaining = [mask ^ ((1<<(i+1))-1) for i in range(n)]
    for i, j in edges:
        remaining[min(i, j)] &= ~(1<<max(i, j))
    for word in words:
        cover(remaining, word)
    return remaining


def cover(remaining, word):
    masks = [0]*5
    for i, c in enumerate(word):
        masks[int(c)] |= 1<<i
    for i, c in enumerate(word):
        remaining[i] &= ~masks[int(c)]


def normalized(word):
    names = {}
    return ''.join(str(names.setdefault(c, len(names))) for c in word)


def build(root, limit=1000):
    started = time.monotonic()
    data, summary = reconstruct(root)
    n, edges = len(data['points']), data['edges']
    seed = list(data['words'])
    prior = json.loads(gzip.decompress((root/'certificates/full_law_pricing.json.gz').read_bytes()))
    for run in prior['runs']:
        seed.extend(run['words'])
    if not all(len(w)==n and set(w)<=set('01234') and
               all(w[i]!=w[j] for i,j in edges) for w in seed):
        raise ValueError('invalid inherited search seed')
    clauses = graph_cnf(n, edges)
    records = []
    # Generate witnesses separating the signatures of all vertices.
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        for step in range(250):
            groups = classes(seed)
            if not groups:
                break
            i, j = groups[0][0], groups[0][-1]
            active = 5*n+step+1
            for c in range(5):
                solver.add_clause([-active, -5*i-c-1, -5*j-c-1])
            solver.conf_budget(10000)
            answer = solver.solve_limited(assumptions=[active])
            record = dict(stage='different', pair=[i,j], result=str(answer),
                          stats=solver.accum_stats())
            records.append(record)
            if answer is not True:
                return None, dict(status='INCOMPLETE_UNCERTIFIED_SEARCH', queries=records)
            word = decode(solver, n, edges)
            if word[i] == word[j]:
                raise ValueError('inequality assumption violated')
            seed.append(word)
    if classes(seed):
        return None, dict(status='DIFFERENCE_ROUND_LIMIT', queries=records)
    # Cover every nonedge by equality in some full proper word.
    remaining = uncovered(n, edges, seed)
    fresh = []
    rng = random.Random(20260929)
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        for step in range(limit):
            pending = sum(x.bit_count() for x in remaining)
            if not pending:
                break
            rows = [i for i, x in enumerate(remaining) if x]
            i = rows[rng.randrange(len(rows))]
            bits = remaining[i]
            offset = rng.randrange(bits.bit_count())
            while offset:
                bits -= bits & -bits
                offset -= 1
            j = (bits & -bits).bit_length()-1
            active = 5*n+step+1
            for c in range(5):
                solver.add_clause([-active, -5*i-c-1, 5*j+c+1])
            phase = [rng.randrange(5) for _ in range(n)]
            solver.set_phases([(5*v+c+1)*(1 if c==phase[v] else -1)
                               for v in range(n) for c in range(5)])
            solver.conf_budget(10000)
            answer = solver.solve_limited(assumptions=[active])
            record = dict(stage='equal', pair=[i,j], pending=pending,
                          result=str(answer), stats=solver.accum_stats())
            records.append(record)
            if answer is not True:
                return None, dict(status='INCOMPLETE_UNCERTIFIED_SEARCH', queries=records)
            word = decode(solver, n, edges)
            if word[i] != word[j]:
                raise ValueError('equality assumption violated')
            fresh.append(word)
            cover(remaining, word)
    if any(remaining):
        return None, dict(status='EQUALITY_ROUND_LIMIT', queries=records)
    # Remove all inherited seeds; cover the few residual pairs in one query.
    residual = uncovered(n, edges, fresh)
    pairs = []
    for i, bits in enumerate(residual):
        while bits:
            bit = bits & -bits
            pairs.append((i, bit.bit_length()-1))
            bits -= bit
    extra = [row[:] for row in clauses]
    for i,j in pairs:
        for c in range(5):
            extra.append([-5*i-c-1, 5*j+c+1])
    with Solver(name='cadical195', bootstrap_with=extra) as solver:
        solver.conf_budget(30000)
        answer = solver.solve_limited()
        records.append(dict(stage='seed_removal', pairs=len(pairs),
                            result=str(answer), stats=solver.accum_stats()))
        if answer is True:
            fresh.append(decode(solver, n, edges))
        else:
            # A failed simplification cannot invalidate the existing witnesses.
            fresh = seed+fresh
    words = list(dict.fromkeys(normalized(w) for w in fresh))
    if classes(words) or any(uncovered(n, edges, words)):
        raise ValueError('producer did not cover all two-terminal obligations')
    certificate = dict(schema='Y-two-terminal-portfolio-v1', colors=5,
                       vertices=n, edges=len(edges),
                       input_semantic_sha256=summary['semantic_sha256'], words=words)
    report = dict(status='POSITIVE_CANDIDATE_REQUIRES_INDEPENDENT_CHECK',
                  word_count=len(words), seed=20260929, python_sat='1.9.dev15',
                  solver='cadical195', queries=records,
                  seconds=time.monotonic()-started)
    return certificate, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=1000)
    args = parser.parse_args()
    if args.limit <= 0:
        parser.error('limit must be positive')
    root = Path(__file__).resolve().parents[1]
    cert, report = build(root, args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix('.search.json').write_text(json.dumps(report, indent=2)+'\n')
    if cert is None:
        raise SystemExit('No complete positive portfolio; see the search record')
    raw = bytearray(gzip.compress(canonical(cert), mtime=0))
    raw[9] = 255
    args.output.write_bytes(raw)
    print(json.dumps(dict(status='CANDIDATE_SAVED', words=len(cert['words']),
                          sha256=hashlib.sha256(raw).hexdigest()), indent=2))


if __name__ == '__main__':
    main()
