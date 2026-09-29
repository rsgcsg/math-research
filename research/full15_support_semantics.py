"""Independent streaming reconstruction of the full15 three-atom CNFs.

This module deliberately does not import the CNF producer or the search
driver.  It rebuilds the semantic clauses, computes the canonical DIMACS
digest in two passes, and retains only requested initial clauses for RUP
replay.
"""
from itertools import combinations
import hashlib


# Representatives for identity, transposition, and 3-cycle transports.
_EQUAL_ETA = (
    ((0, 0), (1, 1), (2, 2)),
    ((0, 0), (1, 2), (2, 1)),
    ((0, 1), (1, 2), (2, 0)),
)
_WEIGHTED_ETA = (
    ((0, 0), (1, 1), (2, 2)),
    ((0, 0), (1, 2), (2, 1)),
    ((0, 1), (0, 2), (1, 0), (2, 0)),
)


class _DisjointSet:
    """Union/find with path compression and union by size."""

    def __init__(self, size):
        self.parent = list(range(size))
        self.size = [1] * size

    def find(self, item):
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != item:
            nxt = self.parent[item]
            self.parent[item] = root
            item = nxt
        return root

    def union(self, left, right):
        left = self.find(left)
        right = self.find(right)
        if left == right:
            return
        if self.size[left] < self.size[right]:
            left, right = right, left
        self.parent[right] = left
        self.size[left] += self.size[right]


def _prepare(data, weighted, case):
    if type(weighted) is not bool or type(case) is not int or case not in range(3):
        raise ValueError('weight type / eta case')
    points = data['points']
    mappings = data['mappings']
    edges = data['edges']
    n = len(points)
    if n <= 4641 or len(mappings) <= 2:
        raise ValueError('incomplete full15 input')
    links = (_WEIGHTED_ETA if weighted else _EQUAL_ETA)[case]

    # Identity eta clauses are represented by equivalence classes.  Assign
    # class numbers by the least state/point index, matching canonical variable
    # order without relying on a graph traversal's discovery order.
    quotient = _DisjointSet(3 * n)
    for source_state, target_state in links:
        for source_point, target_point in mappings[2]:
            quotient.union(source_state * n + source_point,
                           target_state * n + target_point)
    minima = {}
    for vertex in range(3 * n):
        root = quotient.find(vertex)
        if root not in minima or vertex < minima[root]:
            minima[root] = vertex
    roots = sorted(minima, key=minima.__getitem__)
    component_id = {root: number for number, root in enumerate(roots)}
    component = [component_id[quotient.find(vertex)] for vertex in range(3 * n)]

    # Geometry rows are the exact-one clauses and projected proper-coloring
    # clauses, canonicalized and sorted as DIMACS rows.
    rows = set()
    for class_id in range(len(roots)):
        palette = tuple(range(5 * class_id + 1, 5 * class_id + 6))
        rows.add(palette)
        rows.update(tuple(sorted((-x, -y))) for x, y in combinations(palette, 2))
    quotient_edges = set()
    for state in range(3):
        offset = state * n
        for left, right in edges:
            a = component[offset + left]
            b = component[offset + right]
            quotient_edges.add((a, b) if a <= b else (b, a))
    for a, b in quotient_edges:
        for color in range(5):
            left = -(5 * a + color + 1)
            right = -(5 * b + color + 1)
            rows.add(tuple(sorted({left, right})))

    # The reference triangle is the lexicographically first origin-neighbor
    # pair completing a triangle, independently selected from actual edges.
    neighbors = [set() for _ in range(n)]
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    origin = 4641
    triangle = next((origin, b, c)
                    for b in sorted(neighbors[origin])
                    for c in sorted(neighbors[origin] & neighbors[b])
                    if b < c)

    atoms = (0, 0, 1, 2) if weighted else (0, 1, 2)
    return dict(n=n, mappings=mappings, links=links, atoms=atoms,
                component=component, component_count=len(roots),
                geometry_rows=tuple(sorted(rows)), triangle=triangle)


def _clause_stream(prepared):
    """Yield clauses in canonical order and fill compact pass metadata."""
    n = prepared['n']
    mappings = prepared['mappings']
    atoms = prepared['atoms']
    links = prepared['links']
    component = prepared['component']
    top = 5 * prepared['component_count']
    index = 0
    motion_ranges = {}

    def color(state, point, label):
        return 5 * component[state * n + point] + label + 1

    for row in prepared['geometry_rows']:
        index += 1
        yield row

    def allocate_permutation(size):
        nonlocal top
        matrix = []
        for _ in range(size):
            matrix.append(list(range(top + 1, top + size + 1)))
            top += size
        return matrix

    def permutation_clauses(matrix):
        for row in matrix + [list(column) for column in zip(*matrix)]:
            yield row
            for left, right in combinations(row, 2):
                yield [-left, -right]

    for motion, mapping in enumerate(mappings):
        if motion == 2:
            continue
        begin = index + 1
        support = allocate_permutation(len(atoms))
        for row in permutation_clauses(support):
            index += 1
            yield row
        palettes = []
        for _ in atoms:
            matrix = allocate_permutation(5)
            palettes.append(matrix)
            for row in permutation_clauses(matrix):
                index += 1
                yield row

        for slot, source_state in enumerate(atoms):
            for source_point, target_point in mapping:
                target = list(range(top + 1, top + 6))
                top += 5
                for other, target_state in enumerate(atoms):
                    selector = support[slot][other]
                    for label in range(5):
                        old = color(target_state, target_point, label)
                        new = target[label]
                        index += 1
                        yield [-selector, -old, new]
                        index += 1
                        yield [-selector, old, -new]
                for source_label in range(5):
                    source_lit = color(source_state, source_point, source_label)
                    for target_label in range(5):
                        index += 1
                        yield [-source_lit,
                               -palettes[slot][source_label][target_label],
                               target[target_label]]
        motion_ranges[str(motion)] = [begin, index]

    # A single representative state per undirected eta transport component
    # fixes the residual common color naming.  Directed arcs are treated as
    # undirected only for finding these switching components.
    pending = set(range(3))
    while pending:
        root_state = min(pending)
        seen = {root_state}
        frontier = [root_state]
        while frontier:
            current = frontier.pop()
            for source, target in links:
                neighbor = target if source == current else (
                    source if target == current else None)
                if neighbor is not None and neighbor not in seen:
                    seen.add(neighbor)
                    frontier.append(neighbor)
        pending.difference_update(seen)
        for label, point in enumerate(prepared['triangle']):
            index += 1
            yield [color(root_state, point, label)]

    return dict(nv=top, full_clause_count=index, motion_ranges=motion_ranges)


def reconstruct_case(data, weighted, case, selected_ids):
    """Rebuild one case and retain only selected 1-based initial clauses.

    Args:
        data: authenticated full-law input data.
        weighted: whether the atom weights are (2,1,1).
        case: one of the three eta transport representatives.
        selected_ids: strictly increasing positive DIMACS clause IDs.

    Returns the full CNF identity and only the requested clause rows.  The
    clause stream is traversed twice so its final variable/clause counts can
    be included in the canonical DIMACS header before hashing.
    """
    if not isinstance(selected_ids, list):
        raise ValueError('selected clause IDs must be a list')
    previous = 0
    for clause_id in selected_ids:
        if type(clause_id) is not int or clause_id <= previous:
            raise ValueError('selected clause IDs must be strictly increasing positive integers')
        previous = clause_id

    prepared = _prepare(data, weighted, case)
    # The first pass obtains the final header fields from the stream's return
    # value without retaining clauses.
    counter = _clause_stream(prepared)
    try:
        while True:
            next(counter)
    except StopIteration as stopped:
        metadata = stopped.value
    count = metadata['full_clause_count']

    for clause_id in selected_ids:
        if clause_id > count:
            raise ValueError('selected clause ID outside the reconstructed CNF')

    digest = hashlib.sha256(
        f"p cnf {metadata['nv']} {count}\n".encode('ascii'))
    selected = []
    wanted_index = 0
    stream = _clause_stream(prepared)
    for clause_id, row in enumerate(stream, start=1):
        digest.update((' '.join(map(str, row)) + ' 0\n').encode('ascii'))
        if wanted_index < len(selected_ids) and clause_id == selected_ids[wanted_index]:
            selected.append(list(row))
            wanted_index += 1
    # Exhaustion above raises StopIteration internally; the generator return
    # value is not needed a second time because the first pass fixed the header.
    if wanted_index != len(selected_ids):
        raise AssertionError('stream metadata / selected clause mismatch')

    footprints = {
        motion: sum(begin <= clause_id <= end for clause_id in selected_ids)
        for motion, (begin, end) in metadata['motion_ranges'].items()
    }
    return dict(nv=metadata['nv'], full_clause_count=count,
                cnf_sha256=digest.hexdigest(), initial_clauses=selected,
                selected_motion_clauses=footprints)
