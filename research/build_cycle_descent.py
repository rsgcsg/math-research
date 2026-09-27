"""Build the finite certificate for the original-Y cycle descent.

Standard library only. This is a certificate producer, not its checker.
The optional input cache is accepted only after its canonical semantic hash
matches the inherited independently audited geometry. The independent verifier
always reconstructs actual Y and its maximal motion maps.
"""
from collections import deque
from pathlib import Path
import argparse
import gzip
import hashlib
import json

REMOTE_BASE = '09926d59b176c1f649aa30f7ec397fb8fa9ef9fa'
PARENT_CHECKPOINT = 'b532e71453935088000fa54738163c28180b17b8'
LOCAL_POSITIONS = [1, 13, 15, 16, 19]
POLYTOPE_WITNESSES = [{'counts': [0, 0, 0], 'word': '10022002011'}, {'counts': [0, 0, 2], 'word': '21220222212'}, {'counts': [0, 1, 2], 'word': '12012010010'}, {'counts': [0, 2, 0], 'word': '20220220102'}, {'counts': [0, 2, 1], 'word': '22110010221'}, {'counts': [1, 0, 2], 'word': '12210122102'}, {'counts': [1, 1, 2], 'word': '11110012121'}, {'counts': [1, 2, 0], 'word': '00112202011'}, {'counts': [1, 2, 1], 'word': '00001101020'}, {'counts': [2, 0, 0], 'word': '01211220012'}, {'counts': [2, 0, 1], 'word': '00102202110'}, {'counts': [2, 1, 0], 'word': '20100112211'}, {'counts': [2, 1, 1], 'word': '20210122202'}]
FACETS = [[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 1, 2], [0, 1, 0, 2], [0, 1, 1, 3], [1, 0, 0, 2], [1, 0, 1, 3], [1, 1, 0, 3], [1, 1, 1, 4]]

SHARP_CORE_WORD = '11122210101'
KERNEL_THREE_WORD = '100122220111002222000010100221122000022220011111111012210102201120110201001001110111111100001111000000110011000011000110000110000'
SHARP_TRANSPORT_WORD = '011021111001100110101000110200102101000021010102022102201101102121012001010010010022211011121010100112100110221010011021201001110'


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def labels(word, ids):
    names = {}
    return [names.setdefault(word[v], len(names)) for v in ids]


def build(data, local, local_raw, joined_word, prior_event_raw):
    root = [local['vertices_in_Y'][i] for i in LOCAL_POSITIONS]
    patterns = [labels(w, LOCAL_POSITIONS) for w in local['three_word_extreme_law']['words']]
    maps = []
    for j, mapping in enumerate(data['mappings']):
        maps += [(j+1, dict(mapping)), (-j-1, {b:a for a,b in mapping})]
    eta = dict(data['mappings'][2])
    copies = [root]
    for _ in range(4):
        copies.append([eta[v] for v in copies[-1]])
    assert [eta[v] for v in copies[-1]] == root
    core_vertices = sorted({v for row in copies for v in row})
    ci = {v:i for i,v in enumerate(core_vertices)}
    core_edges = [[ci[a],ci[b]] for a,b in data['edges'] if a in ci and b in ci]
    start = tuple(root)
    parent = {start: None}
    queue = deque([start])
    while queue:
        point_tuple = queue.popleft()
        for step, mm in maps:
            if all(v in mm for v in point_tuple):
                image = tuple(mm[v] for v in point_tuple)
                if image not in parent:
                    parent[image] = (point_tuple, step)
                    queue.append(image)
    tuples = sorted(parent)
    ti = {row:i for i,row in enumerate(tuples)}
    tree = [None if parent[row] is None else [ti[parent[row][0]], parent[row][1]]
            for row in tuples]
    transitions = sorted([ti[row],step,ti[tuple(mm[v] for v in row)]]
                         for row in tuples for step,mm in maps
                         if all(v in mm for v in row))
    vertices = sorted({v for row in tuples for v in row})
    vi = {v:i for i,v in enumerate(vertices)}
    edges = [[vi[a],vi[b]] for a,b in data['edges'] if a in vi and b in vi]
    adj = {v:set() for v in range(len(vertices))}
    for a,b in edges:
        adj[a].add(b); adj[b].add(a)
    triangles = [[a,b,c] for a,b in edges for c in sorted(adj[a]&adj[b]) if b<c]
    cycles, unused = [], set(range(len(tuples)))
    for i in range(len(tuples)):
        if i not in unused:
            continue
        orbit, row = [], tuples[i]
        for _ in range(5):
            if not all(v in eta for v in row):
                break
            orbit.append(ti[row])
            row = tuple(eta[v] for v in row)
        if len(orbit)==5 and row==tuples[i] and len(set(orbit))==5:
            cycles.append(orbit)
            unused.difference_update(orbit)
    gap_source=list(dict.fromkeys(list(tuples[8])+list(tuples[68])))
    gap_target=[dict(data['mappings'][0])[v] for v in gap_source]
    gap=dict(motion=0, tuple_indices=[8,68], image_tuple_indices=[85,60],
             source=gap_source, target=gap_target,
             source_partition=labels(joined_word,gap_source),
             target_partition=labels(joined_word,gap_target),
             cross_pair_source=[4638,887], cross_pair_target=[4672,5836],
             scope='Mismatch of one saved word, not an all-word obstruction or a minimal-arity claim. A cross-tuple two-point equality already distinguishes the union patterns.')
    return dict(schema='hn-original-Y-cycle-descent-v1', date='2026-09-28',
        remote_base_commit=REMOTE_BASE, parent_checkpoint=PARENT_CHECKPOINT,
        input_semantic_sha256=hashlib.sha256(canonical(data)).hexdigest(),
        local_certificate_sha256=hashlib.sha256(local_raw).hexdigest(),
        core=dict(local_positions=LOCAL_POSITIONS, Y_indices=root, patterns=patterns,
                  rotation_motion=2, rotation_order=5, copies_in_Y=copies,
                  orbit_Y_indices=core_vertices, orbit_edges=core_edges,
                  sharp_core_word=SHARP_CORE_WORD,
                  marginal_polytope=dict(scale=5, facet_rows=FACETS,
                      vertex_witnesses=POLYTOPE_WITNESSES, minimum_colors=3,
                      description='([0,1]^3 + conv(0,e0,e1,e2))/5',
                      scope='Exact marginal polytope for all eta-invariant laws on the 11-point core, for every k>=3. Upper inequalities descend to Y; sharpness is not asserted for Y.'),
                  telescoping_coefficients=[4,3,2,1], probability_upper_bound='4/5',
                  bound_applies_to_original_Y=True,
                  sharpness_scope='The 11-point eta-invariant core only; not full Y.'),
        transport=dict(root_tuple_index=ti[start], tuples_in_Y=[list(t) for t in tuples],
                       rooted_paths=tree, transitions=transitions,
                       kernel_Y_indices=vertices, kernel_edges=edges,
                       eta_cycles=cycles, leftover_tuples=sorted(unused),
                       sharp_kernel_word=SHARP_TRANSPORT_WORD, maximum_hits=98,
                       ordinary_three_word=KERNEL_THREE_WORD, triangle=triangles[0],
                       known_local_law_words=[''.join(w[v] for v in vertices) for w in data['words']],
                       known_local_law_weights=['1/5']*5,
                       uniform_count_mass_bound='49/61',
                       scope='Complete partial-motion tuple orbit in Y. Exact deterministic '
                             'hit count on its 129-point kernel for every k>=3, not '
                             'a full-Y law or a sharp common-moment bound.'),
        joined_zero=dict(word=joined_word, prior_event_certificate_sha256=hashlib.sha256(prior_event_raw).hexdigest(),
            pair_event_count=418, forbidden_tuple_patterns=366,
            common_complete_partition=labels(joined_word,root),
            complete_tuple_partitions_equal=True, joint_observation_gap=gap,
            scope='A full-Y proper five-coloring; u complete partition unchanged, inherited 12 other pair-event differences zero, and the complete five-point partition identical at all 122 reachable tuples. Not a full fifteen-domain law.'),
        result_scope='Original-Y eta-law cylinder constraint, not an HN lower bound. '
                     'The pointwise cycle inequality does not use the number of colors. '
                     'No full fifteen-domain law or obstruction is asserted.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--witness-file', type=Path, help='Previously found joined-zero word (search result or existing certificate); reconstruction does not rerun SAT.')
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    if args.cache:
        raw = args.cache.read_bytes()
        data = json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
        expected = json.loads((repository/'certificates/full_law_preparation_audit.json').read_text())['independent_inputs']['semantic_sha256']
        if hashlib.sha256(canonical(data)).hexdigest()!=expected:
            raise ValueError('cache does not match inherited geometry hash')
    else:
        from audit_full_law_preparation import reconstruct
        data, _ = reconstruct(repository)
    path = repository/'certificates/localized_motion_packet.json'
    raw = path.read_bytes()
    witness_path=args.witness_file or repository/'certificates/original_Y_cycle_descent.json'
    witness_data=json.loads(witness_path.read_text())
    joined_word=witness_data['word'] if 'word' in witness_data else witness_data['joined_zero']['word']
    prior_event_raw=(repository/'certificates/shared_event_research.json.gz').read_bytes()
    cert = build(data, json.loads(raw), raw, joined_word, prior_event_raw)
    output = args.output or repository/'certificates/original_Y_cycle_descent.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(json.dumps(cert, ensure_ascii=False, indent=2).encode()+b'\n')
    print(json.dumps(dict(status='BUILT_NOT_INDEPENDENTLY_VERIFIED', output=str(output),
        core_vertices=len(cert['core']['orbit_Y_indices']), tuples=len(cert['transport']['tuples_in_Y']),
        kernel_vertices=len(cert['transport']['kernel_Y_indices']))))


if __name__=='__main__':
    main()
