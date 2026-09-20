"""Build E098 finite support-cover refutation and sharpness witnesses.

This is a producer, not the proof checker.  No SAT/LP dependency is used.
"""
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path
import gzip
import hashlib
import json


def partitions(n, k):
    def visit(p, maximum):
        if len(p) == n:
            yield tuple(p)
            return
        for x in range(min(maximum + 2, k)):
            yield from visit(p + [x], max(maximum, x))
    yield from visit([], -1)


def canonical(p):
    labels = {}
    return tuple(labels.setdefault(x, len(labels)) for x in p)


def build():
    ps = list(partitions(6, 5))
    fibers = {}
    for a, p in enumerate(ps):
        for i in range(6):
            fibers.setdefault((i, canonical(p[:i] + p[i+1:])), []).append(a)
    blocks = [[fibers[i, canonical(p[:i]+p[i+1:])] for i in range(6)] for p in ps]
    records = []

    @lru_cache(None)
    def refute(positive, negative):
        assert set(positive).isdisjoint(negative)
        assert max(len(positive), len(negative)) <= 5
        selected = None
        for side, chosen, opposite in ((1, positive, negative), (-1, negative, positive)):
            for a in chosen:
                for deletion, fiber in enumerate(blocks[a]):
                    if set(fiber).intersection(opposite):
                        continue
                    options = tuple(b for b in fiber if b not in chosen)
                    if len(opposite) == 5:
                        options = ()
                    item = (len(options), side, a, deletion, options)
                    if selected is None or item < selected:
                        selected = item
        if selected is None:
            raise AssertionError(('closed support pair found', positive, negative))
        _, side, a, deletion, options = selected
        children = []
        for b in options:
            newp = tuple(sorted(positive + (b,))) if side == -1 else positive
            newn = tuple(sorted(negative + (b,))) if side == 1 else negative
            children.append(refute(newp, newn))
        index = len(records)
        records.append([list(positive), list(negative), side, a, deletion, children])
        return index

    shapes = {}
    for i, p in enumerate(ps):
        shapes.setdefault(tuple(sorted(Counter(p).values(), reverse=True)), i)
    roots = []
    for shape, a in sorted(shapes.items()):
        roots.append(dict(shape=shape, atom=a, node=refute((a,), ())))
    samples = {
        'four_points_necessary': {
            'left': ['0011', '0011', '0123', '0123', '0000'],
            'right': ['0012', '0012', '0122', '0122', '0000'],
            'weights_left': [1]*5, 'weights_right': [1]*5,
            'equal_through_points': 3, 'maximum_blocks': 5},
        'unequal_weights_need_five': {
            'left': ['00012', '00122', '01022', '01122', '01234'],
            'right': ['00011', '00123', '01023', '01123', '01233'],
            'weights_left': [1,1,1,1,2], 'weights_right': [1,1,1,1,2],
            'equal_through_points': 4, 'maximum_blocks': 5},
    }
    sides = [[], []]
    for bits in product((0,1), repeat=3):
        raw = [x for i,b in enumerate(bits) for x in (2*i, 2*i if b else 2*i+1)]
        sides[sum(bits)%2].append(''.join(map(str,canonical(raw))))
    # Padding both sides to five equal-weight entries does not erase the trade.
    for side in sides:
        side.append('000000')
    samples['six_colors_defeat_four_points'] = dict(
        left=sides[0], right=sides[1], weights_left=[1]*5, weights_right=[1]*5,
        equal_through_points=5, maximum_blocks=6)
    return dict(schema='partition-quartet-v1', experiment='E098',
                support_limit=5, block_limit=5, points=6,
                partitions=[list(p) for p in ps], roots=roots, nodes=records,
                sharpness=samples,
                scope='Finite support-cover certificate for T128; T127 has a separate complete analytical proof')


def encode(data):
    raw=(json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode()
    compressed=gzip.compress(raw,compresslevel=9,mtime=0)
    # Python 3.12 and 3.13 differ in the gzip OS header byte at mtime=0.
    return compressed[:9]+bytes([255])+compressed[10:]


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    data=build();out=encode(data)
    path=root/'certificates/partition_quartet_completeness.json.gz'
    path.write_bytes(out)
    print(json.dumps(dict(nodes=len(data['nodes']),roots=len(data['roots']),
                         bytes=len(out),sha256=hashlib.sha256(out).hexdigest())))
