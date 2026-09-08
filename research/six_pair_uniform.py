"""Build six-pair common-three-list certificates.

Enumerate all underlying labelled graphs and all signs modulo vertex switching.
An independent verifier checks coverage, positive words and geometric proofs.
"""
from fractions import Fraction as F
from itertools import combinations
import json
import gzip
from pathlib import Path

PAIRS = list(combinations(range(6), 2))
POPCOUNT = [bin(n).count('1') for n in range(4096)]


def instances():
    for mask in range(1 << 15):
        parent = list(range(6))
        def find(v):
            while parent[v] != v:
                v = parent[v]
            return v
        tree, chords = [], []
        for j, (a, b) in enumerate(PAIRS):
            if not (mask >> j & 1):
                continue
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                tree.append(j)
            else:
                chords.append(j)
        base = sum(3**j for j in tree+chords)
        for bits in range(1 << len(chords)):
            code = base + sum(3**j for k, j in enumerate(chords) if bits >> k & 1)
            adj = [0]*12
            for j in tree+chords:
                a, b = PAIRS[j]
                sign = (code // 3**j % 3)-1
                for k in (0, 1):
                    u, v = 2*a+k, 2*b+(k ^ sign)
                    adj[u] |= 1 << v
                    adj[v] |= 1 << u
            yield code, adj


def color(adj):
    def visit(domains, left, word):
        if not left:
            return word
        v = min(left, key=lambda v: (POPCOUNT[domains[v]], -POPCOUNT[adj[v]]))
        available = domains[v]
        while available:
            bit = available & -available
            available -= bit
            new = domains[:]
            ok = True
            for u in left:
                if adj[v] >> u & 1:
                    new[u] &= ~bit
                    if not new[u]:
                        ok = False
                        break
            if ok:
                w = word[:]
                w[v] = bit.bit_length()-1
                result = visit(new, left-{v}, w)
                if result is not None:
                    return result
        return None
    return visit([7]*12, set(range(12)), [-1]*12)


def collapse(adj):
    rows = set()
    for a, c in combinations(range(12), 2):
        common = [b for b in range(12) if (adj[a] & adj[c]) >> b & 1]
        for b, d in combinations(common, 2):
            row = [0]*12
            row[a] = row[c] = 1
            row[b] = row[d] = -1
            if next(x for x in row if x) < 0:
                row = [-x for x in row]
            rows.add(tuple(row))
    basis = {}
    for r in sorted(rows):
        r = list(map(F, r))
        for p, other in sorted(basis.items()):
            if r[p]:
                scale = r[p]
                r = [x-scale*y for x, y in zip(r, other)]
        p = next((j for j, x in enumerate(r) if x), None)
        if p is not None:
            scale = r[p]
            basis[p] = [x/scale for x in r]
    for a, b in combinations(range(12), 2):
        r = [F(int(j == a)-int(j == b)) for j in range(12)]
        for p, other in sorted(basis.items()):
            if r[p]:
                scale = r[p]
                r = [x-scale*y for x, y in zip(r, other)]
        if not any(r):
            return (a, b)
    return None


def trace_obstruction(adj):
    for a in range(12):
        for b in range(12):
            if not (adj[a] >> b & 1):
                continue
            opposite_common = adj[a] & adj[b ^ 1]
            diamond = next(((r, s) for r in range(12) for s in range(r+1, 12)
                            if opposite_common >> r & 1 and opposite_common >> s & 1
                            and adj[r] >> s & 1), None)
            if diamond is None:
                continue
            common = adj[a] & adj[b]
            for c, d in combinations([v for v in range(12) if common >> v & 1], 2):
                if adj[c] >> (d ^ 1) & 1:
                    return [a, b, c, d, *diamond]
    return None


def run():
    counts = dict(total=0, k23=0, k4=0, three_coloring=0, rhombus_collapse=0, trace_obstruction=0, unresolved=0)
    unknown = []
    records = []
    for code, adj in instances():
        counts['total'] += 1
        pair = next(((a, b) for a, b in combinations(range(12), 2)
                     if POPCOUNT[adj[a] & adj[b]] >= 3), None)
        if pair is not None:
            counts['k23'] += 1
            a, b = pair
            records.append([code, 'k23', [a, b]+[u for u in range(12) if (adj[a] & adj[b]) >> u & 1][:3]])
            continue
        clique = None
        for a, b in combinations(range(12), 2):
            if not adj[a] >> b & 1:
                continue
            common = adj[a] & adj[b]
            edge = next(((c, d) for c in range(12) for d in range(c+1, 12)
                         if common >> c & 1 and common >> d & 1 and adj[c] >> d & 1), None)
            if edge is not None:
                clique = [a, b, *edge]
                break
        if clique is not None:
            counts['k4'] += 1
            records.append([code, 'k4', clique])
            continue
        word = color(adj)
        if word is not None:
            counts['three_coloring'] += 1
            records.append([code, 'three_coloring', ''.join(map(str, word))])
            continue
        pair = collapse(adj)
        if pair is not None:
            counts['rhombus_collapse'] += 1
            records.append([code, 'rhombus_collapse', pair])
            continue
        witness = trace_obstruction(adj)
        if witness is not None:
            counts['trace_obstruction'] += 1
            records.append([code, 'trace_obstruction', witness])
            continue
        counts['unresolved'] += 1
        unknown.append(code)
        print(json.dumps(dict(unresolved_code=code, counts=counts)), flush=True)
    return dict(counts=counts, first_unresolved_codes=unknown,
                schema=1, records=records,
                status='GENERATED_PROOF_OBJECTS_REQUIRE_INDEPENDENT_VERIFICATION',
                scope='Common three-list only; not arbitrary old five-colorings.')


if __name__ == '__main__':
    data = run()
    target = Path(__file__).resolve().parents[1]/'certificates/pair_orbits_six_uniform.json.gz'
    target.write_bytes(gzip.compress(json.dumps(data, separators=(',', ':')).encode(), mtime=0))
    print(json.dumps({k: v for k, v in data.items() if k != 'records'}, indent=2), flush=True)
