"""Second small-core RUP replay, deliberately ignoring all supplied hints.

Rebuilds the same local semantic CNF, but propagates by fresh occurrence counts
rather than trusting/exporting hint order. Supports only sequential additions
for this bounded certificate. This is not a new actual-unit-graph lower bound.
"""
from collections import defaultdict, deque
from pathlib import Path
import json
from verify_localized_motion_packet import actual_geometry, normalized_cnf
from verify_motion_packet import read, require


def replay(cert):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    built = normalized_cnf(actual_geometry(cert),cert['one_word_denial'])
    n = built['nv']
    require(n<=10000 and len(built['clauses'])<=200000, 'independent replay resource limit')
    db = [tuple(c) for c in built['clauses']]
    occurrence = defaultdict(list)
    units = []
    for i,clause in enumerate(db):
        for literal in clause:
            occurrence[literal].append(i)
        if len(clause)==1:
            units.append(clause[0])
    steps, propagated, last = 0, 0, len(db)
    for line in cert['one_word_denial']['proof']:
        fields = line.split()
        require(fields and 'd' not in fields, 'addition-only proof')
        numbers = list(map(int,fields))
        require(numbers[0]==last+1 and numbers[-1]==0, 'sequential proof identity')
        stop = numbers.index(0,1)
        clause = tuple(numbers[1:stop])
        require(all(1<=abs(v)<=n for v in clause) and len(set(clause))==len(clause), 'lemma shape')
        # Every token after the lemma's first zero is unnecessary for this
        # algorithm. No supplied hint, positive or negative, is executed.
        values = [0]*(n+1)
        remaining = [len(c) for c in db]
        satisfied = bytearray(len(db))
        pending = deque([-v for v in clause]+units)
        contradiction = any(not c for c in db)
        while pending and not contradiction:
            literal = pending.popleft()
            variable, sign = abs(literal), 1 if literal>0 else -1
            if values[variable]:
                contradiction = values[variable]!=sign
                continue
            values[variable] = sign
            propagated += 1
            for i in occurrence[literal]:
                satisfied[i] = 1
            for i in occurrence[-literal]:
                if satisfied[i]:
                    continue
                remaining[i] -= 1
                if remaining[i]==0:
                    contradiction = True
                    break
                if remaining[i]==1:
                    free = [v for v in db[i] if values[abs(v)]==0]
                    require(len(free)==1, 'occurrence propagation consistency')
                    pending.append(free[0])
        require(contradiction, 'non-RUP lemma '+str(numbers[0]))
        i = len(db)
        db.append(clause)
        for literal in clause:
            occurrence[literal].append(i)
        if len(clause)==1:
            units.append(clause[0])
        steps += 1
        last = numbers[0]
    require(steps>0 and not db[-1], 'missing final empty clause')
    return dict(status='PASS_HINT_FREE_RUP',initial_clauses=len(built['clauses']),
                steps=steps,propagated_assignments=propagated,cnf_sha256=built['cnf_sha256'],
                scope='Second propagation algorithm on the local semantic CNF; all supplied hints ignored. '
                      'Not a second independent geometry derivation or ordinary NON5 proof.')


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(replay(read(root/'certificates/localized_motion_packet.json')),indent=2))


if __name__=='__main__':
    main()
