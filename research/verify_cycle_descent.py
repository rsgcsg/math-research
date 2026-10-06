"""Independent original-Y cycle-descent and finite-kernel replay.

Uses the established independent Y reconstruction and exact field arithmetic.
Does not import this certificate's producer, SAT, MaxSAT, LP, or its search
scripts. Every positive witness is tested directly. The upper count bound is
verified from finite compatibility graphs, not a solver's optimum flag.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
from audit_full_law_preparation import reconstruct
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice
from verify_motion_packet import read, require, pattern

REMOTE_BASE = '09926d59b176c1f649aa30f7ec397fb8fa9ef9fa'
PARENT = 'b532e71453935088000fa54738163c28180b17b8'
POSITIONS = [1,13,15,16,19]
ROOT = [231,4641,5163,5412,7478]
PATTERNS = [[0,1,1,0,2],[0,1,0,0,1],[0,1,2,0,0]]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def exact(got, expected, message):
    require(canonical(got)==canonical(expected), message)


def labels(w, positions):
    blocks = pattern(w, positions)
    result = [0]*len(positions)
    for c, block in enumerate(blocks):
        for v in block:
            result[v] = c
    return result


def word_check(w, n, edges, k=5):
    require(isinstance(w,str) and len(w)==n and set(w)<=set(map(str,range(k))), 'word shape')
    require(all(w[a]!=w[b] for a,b in edges), 'invalid proper coloring')


def compatibility(left, right, patterns):
    overlap = sorted(set(left)&set(right))
    a = [left.index(v) for v in overlap]
    b = [right.index(v) for v in overlap]
    return [[int(pattern(p,a)==pattern(q,b)) for q in patterns] for p in patterns]


def count_closed_patterns(copies, patterns):
    matrices = [compatibility(copies[i], copies[(i+1)%len(copies)], patterns)
                for i in range(len(copies))]
    return sum(all(matrices[i][seq[i]][seq[(i+1)%len(copies)]]
                   for i in range(len(copies)))
               for seq in product(range(len(patterns)),repeat=len(copies)))


def hit(word, positions):
    return labels(word, positions) in PATTERNS


def exact_edges(data, vertices, multiplication):
    points = [data['points'][v] for v in vertices]
    target = [4*data['denominator']**2]+[0]*31
    edges = []
    for a,b in combinations(range(len(points)),2):
        delta = [x-y for x,y in zip(points[a],points[b])]
        if product_twice(delta,conjugate_twice(delta),multiplication)==target:
            edges.append([a,b])
    return edges


def check(cert, data, summary, local, local_raw, prior_events, prior_event_raw):
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    exact(set_to_list(cert), ['core','date','input_semantic_sha256','joined_zero','local_certificate_sha256',
          'parent_checkpoint','remote_base_commit','result_scope','schema','transport'], 'top-level fields')
    exact(cert['schema'],'hn-original-Y-cycle-descent-v1','schema')
    exact(cert['date'],'2026-09-28','date')
    exact(cert['remote_base_commit'],REMOTE_BASE,'remote provenance')
    exact(cert['parent_checkpoint'],PARENT,'inherited checkpoint')
    exact(cert['input_semantic_sha256'],summary['semantic_sha256'],'geometry binding')
    exact(cert['local_certificate_sha256'],hashlib.sha256(local_raw).hexdigest(),'inherited local certificate binding')
    exact(cert['result_scope'], 'Original-Y eta-law cylinder constraint, not an HN lower bound. '
          'The pointwise cycle inequality does not use the number of colors. '
          'No full fifteen-domain law or obstruction is asserted.', 'theorem scope')
    u=cert['core']; t=cert['transport']
    exact(u['local_positions'],POSITIONS,'core positions')
    exact(u['Y_indices'],ROOT,'root Y indices')
    exact([local['vertices_in_Y'][i] for i in POSITIONS],ROOT,'actual inherited subset')
    exact(u['patterns'],PATTERNS,'five-point patterns')
    exact([labels(w,POSITIONS) for w in local['three_word_extreme_law']['words']],PATTERNS,'restrictions of inherited triple')
    # Compare inherited local coordinates with reconstructed Y, not indices alone.
    for p,v in zip(local['points'],local['vertices_in_Y']):
        require(all(Q(x,local['coordinate_denominator'])==Q(y,data['denominator'])
                    for x,y in zip(p,data['points'][v])), 'local/Y coordinate mismatch')
    exact(u['rotation_motion'],2,'eta motion index')
    exact(u['rotation_order'],5,'geometric order')
    eta=dict(data['mappings'][2]); points={tuple(p):i for i,p in enumerate(data['points'])}
    algebra=multiplication_twice(); e=tuple(int(i==16) for i in range(32))
    def rotate(v):
        raw=product_twice(e,data['points'][v],algebra)
        require(all(x%2==0 for x in raw),'integral rotated coordinates')
        image=tuple(x//2 for x in raw)
        require(image in points,'fivefold core leaves actual Y')
        w=points[image]
        require(eta.get(v)==w,'eta map does not match exact multiplication')
        return w
    copies=[ROOT]
    for _ in range(4):
        copies.append([rotate(v) for v in copies[-1]])
    require([rotate(v) for v in copies[-1]]==ROOT,'eta^5 not identity')
    exact(u['copies_in_Y'],copies,'five copies in original Y')
    vertices=sorted({v for row in copies for v in row})
    exact(u['orbit_Y_indices'],vertices,'complete core')
    require(len(vertices)==11,'core size')
    ci={v:i for i,v in enumerate(vertices)}
    edges=exact_edges(data,vertices,algebra)
    exact(u['orbit_edges'],edges,'core induced unit edges')
    require(len(edges)==5,'core edge count')
    require(count_closed_patterns(copies,PATTERNS)==0,'five-step compatible pattern cycle exists')
    matrices=[compatibility(copies[i],copies[(i+1)%5],PATTERNS) for i in range(5)]
    exact(matrices,[[[0,1,0],[0,0,1],[1,0,0]]]*5,'exact inherited three-cycle')
    core_word=u['sharp_core_word'];word_check(core_word,11,edges,3)
    core_copies=[[ci[v] for v in row] for row in copies]
    require(sum(hit(core_word,row) for row in core_copies)==4,'core sharpness')
    rotations=[]; current=list(vertices)
    for _ in range(5):
        w=''.join(core_word[ci[v]] for v in current); word_check(w,11,edges,3);rotations.append(w)
        current=[rotate(v) for v in current]
    exact(current,vertices,'cyclic core average closes')
    require(sum(hit(w,core_copies[0]) for w in rotations)==4,'sharp average mass')
    exact(u['telescoping_coefficients'],[4,3,2,1],'telescoping potential')
    for f in product((0,1),repeat=5):
        require(5*f[0]==sum(f)+sum((4-i)*(f[i]-f[i+1]) for i in range(4)), 'telescoping identity')
        if sum(f)<=4:
            require(4-5*f[0]+sum((4-i)*(f[i]-f[i+1]) for i in range(4))>=0,'pointwise certificate')
    exact(u['probability_upper_bound'],'4/5','probability bound')
    exact(u['bound_applies_to_original_Y'],True,'original-Y scope')
    exact(u['sharpness_scope'],'The 11-point eta-invariant core only; not full Y.','sharpness scope')

    core_vertex_ids=list(vertices)
    poly=u['marginal_polytope']
    facets=[[-1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,1,2],[0,1,0,2],
            [0,1,1,3],[1,0,0,2],[1,0,1,3],[1,1,0,3],[1,1,1,4]]
    exact(poly['scale'],5,'marginal scale');exact(poly['minimum_colors'],3,'color threshold')
    exact(poly['facet_rows'],facets,'all marginal facets')
    exact(poly['description'],'([0,1]^3 + conv(0,e0,e1,e2))/5','polytope description')
    exact(poly['scope'],'Exact marginal polytope for all eta-invariant laws on the 11-point core, for every k>=3. Upper inequalities descend to Y; sharpness is not asserted for Y.','polytope scope')
    legal=[]
    for seq in product(range(4),repeat=5):
        if all(seq[i]==3 or seq[(i+1)%5]==3 or seq[(i+1)%5]==(seq[i]+1)%3 for i in range(5)):
            counts=[seq.count(i) for i in range(3)];legal.append(counts)
            require(all(sum(a*b for a,b in zip(row[:3],counts))<=row[3] for row in facets),'marginal facet excludes a compatible sequence')
    require(len(legal)==151 and len(set(map(tuple,legal)))==20,'complete symbolic cycle enumeration')
    # Independently enumerate rational intersections of 3 active facet planes.
    # These inequalities bound a full-dimensional 3-polytope; every vertex is
    # among these intersections. No numerical hull code is used.
    vertices=set()
    for active in combinations(facets,3):
        aug=[[Q(v) for v in row] for row in active];nonsingular=True
        for column in range(3):
            pivot=next((i for i in range(column,3) if aug[i][column]),None)
            if pivot is None:nonsingular=False;break
            aug[column],aug[pivot]=aug[pivot],aug[column]
            value=aug[column][column];aug[column]=[v/value for v in aug[column]]
            for i in range(3):
                if i!=column:
                    multiplier=aug[i][column];aug[i]=[a-multiplier*b for a,b in zip(aug[i],aug[column])]
        if nonsingular:
            point=tuple(aug[i][3] for i in range(3))
            if all(sum(a*b for a,b in zip(row[:3],point))<=row[3] for row in facets):vertices.add(point)
    witnesses=poly['vertex_witnesses']
    exact([x['counts'] for x in witnesses],[list(map(int,x)) for x in sorted(vertices)],'all thirteen polytope vertices')
    require(len(vertices)==13 and all(x.denominator==1 for p in vertices for x in p),'marginal vertex structure')
    for witness in witnesses:
        word_check(witness['word'],11,edges,3)
        counts=[sum(labels(witness['word'],row)==p for row in core_copies) for p in PATTERNS]
        exact(witness['counts'],counts,'marginal vertex coloring')
        # An exact geometric five-rotation average realizes counts/5.
        current=list(core_vertex_ids)
        for _ in range(5):
            rotated=''.join(witness['word'][ci[v]] for v in current)
            word_check(rotated,11,edges,3);current=[rotate(v) for v in current]

    # Independent fixed-point closure, rather than the producer's queue ordering.
    transforms={}
    for j,mapping in enumerate(data['mappings']):
        transforms[j+1]=dict(mapping);transforms[-j-1]={b:a for a,b in mapping}
    reached={tuple(ROOT)}
    while True:
        extra=set()
        for row in reached:
            for mm in transforms.values():
                if all(v in mm for v in row):
                    extra.add(tuple(mm[v] for v in row))
        before=len(reached);reached.update(extra)
        if len(reached)==before:break
    tuples=sorted(reached);ti={row:i for i,row in enumerate(tuples)}
    exact(t['tuples_in_Y'],[list(x) for x in tuples],'complete ordered tuple orbit')
    require(len(tuples)==122,'tuple count')
    exact(t['root_tuple_index'],ti[tuple(ROOT)],'root index')
    expected_transitions=sorted([i,step,ti[tuple(mm[v] for v in row)]]
       for i,row in enumerate(tuples) for step,mm in transforms.items() if all(v in mm for v in row))
    exact(t['transitions'],expected_transitions,'all allowed partial-motion steps')
    parents=t['rooted_paths'];require(len(parents)==122,'rooted path count')
    for i in range(122):
        current=i;seen=set()
        while parents[current] is not None:
            require(current not in seen,'cycle in purported rooted paths');seen.add(current)
            pair=parents[current]
            require(isinstance(pair,list) and len(pair)==2 and all(type(x) is int for x in pair),'path step type')
            prev,step=pair
            require(0<=prev<122 and step in transforms,'path range')
            mm=transforms[step]
            require(all(v in mm for v in tuples[prev]) and tuple(mm[v] for v in tuples[prev])==tuples[current], 'path leaves domain or wrong image')
            current=prev
        require(current==ti[tuple(ROOT)],'unrooted tuple')
    kernel=sorted({v for row in tuples for v in row});ki={v:i for i,v in enumerate(kernel)}
    exact(t['kernel_Y_indices'],kernel,'kernel vertices')
    require(len(kernel)==129,'kernel size')
    ke=exact_edges(data,kernel,algebra)
    exact(t['kernel_edges'],ke,'all kernel unit pairs')
    require(len(ke)==192,'kernel induced edge count')
    cycles=t['eta_cycles'];remaining=t['leftover_tuples'];flat=[]
    require(len(cycles)==24 and len(remaining)==2,'cycle decomposition dimensions')
    for cycle in cycles:
        require(isinstance(cycle,list) and len(cycle)==5 and all(type(i) is int and 0<=i<122 for i in cycle),'cycle type')
        require(len(set(cycle))==5,'cycle distinctness')
        physical=[list(tuples[i]) for i in cycle]
        for r in range(5):
            require(all(v in eta for v in physical[r]),'cycle leaves actual eta domain')
            require([eta[v] for v in physical[r]]==physical[(r+1)%5], 'wrong geometric cycle')
        require(count_closed_patterns(physical,PATTERNS)==0,'transport cycle allows all five hits')
        flat.extend(cycle)
    require(all(type(i) is int for i in remaining),'leftover type')
    exact(sorted(flat+remaining),list(range(122)),'cycles are not a disjoint partition')
    upper=4*len(cycles)+len(remaining)
    exact(t['maximum_hits'],upper,'combinatorial upper bound')
    kw=t['sharp_kernel_word'];word_check(kw,129,ke,3)
    rows=[[ki[v] for v in row] for row in tuples]
    require(sum(hit(kw,row) for row in rows)==upper==98,'sharp count coloring')
    exact(t['uniform_count_mass_bound'],str(Q(upper,122)),'averaged count bound')
    word_check(t['ordinary_three_word'],129,ke,3)
    triangle=t['triangle'];require(len(triangle)==3 and all(type(v) is int for v in triangle) and triangle==sorted(set(triangle)),'triangle')
    require(all([a,b] in ke for a,b in combinations(triangle,2)),'triangle edge missing')
    # These five inherited restrictions give a full LOCAL 15-domain law only.
    laws=t['known_local_law_words'];exact(t['known_local_law_weights'],['1/5']*5,'local law weights')
    exact(laws,[''.join(w[v] for v in kernel) for w in data['words']],'inherited local law restrictions')
    sizes=[]
    for word in laws:word_check(word,129,ke)
    for mapping in data['mappings']:
        localmap=[(ki[a],ki[b]) for a,b in mapping if a in ki and b in ki]
        sizes.append(len(localmap))
        source=Counter(pattern(w,[a for a,b in localmap]) for w in laws)
        target=Counter(pattern(w,[b for a,b in localmap]) for w in laws)
        require(source==target,'local complete-domain law failed')
    all_moments=[sum(hit(w,row) for w in laws) for row in rows]
    require(all(x==1 for x in all_moments),'expected inherited membership 1/5')
    exact(t['scope'],'Complete partial-motion tuple orbit in Y. Exact deterministic '
          'hit count on its 129-point kernel for every k>=3, not '
          'a full-Y law or a sharp common-moment bound.','transport scope')
    joined=cert['joined_zero']
    exact(joined['prior_event_certificate_sha256'],hashlib.sha256(prior_event_raw).hexdigest(),'E111 input binding')
    fullword=joined['word'];word_check(fullword,len(data['points']),data['edges'])
    events=prior_events['event_records']
    require(len(events)==418,'prior event count')
    for j,a,b,x,y in events:
        mm=dict(data['mappings'][j]);require(mm.get(a)==x and mm.get(b)==y,'prior event is not a real motion')
        require((fullword[a]==fullword[b])==(fullword[x]==fullword[y]),'joined word fails an inherited pair event')
    u_map=data['mappings'][14]
    require(pattern(fullword,[a for a,b in u_map])==pattern(fullword,[b for a,b in u_map]),'u complete partition differs')
    forbidden_hits=sum(labels(fullword,list(row))==p for row in tuples for p in PATTERNS)
    require(forbidden_hits==0,'transported forbidden pattern occurs')
    exact(joined['pair_event_count'],418,'joined event count')
    exact(joined['forbidden_tuple_patterns'],366,'joined cylinder count')
    common=labels(fullword,ROOT)
    exact(joined['common_complete_partition'],common,'common complete five-point partition')
    exact(joined['complete_tuple_partitions_equal'],True,'full tuple scope')
    require(all(labels(fullword,list(row))==common for row in tuples),'complete tuple partition differs')
    exact(joined['scope'],'A full-Y proper five-coloring; u complete partition unchanged, inherited 12 other pair-event differences zero, and the complete five-point partition identical at all 122 reachable tuples. Not a full fifteen-domain law.','joined scope')
    gap=joined['joint_observation_gap']
    exact(gap['motion'],0,'joint gap motion')
    exact(gap['tuple_indices'],[8,68],'joint gap tuples')
    exact(gap['image_tuple_indices'],[85,60],'joint gap images')
    source=list(dict.fromkeys(list(tuples[8])+list(tuples[68])))
    mm=dict(data['mappings'][0]);require(all(v in mm for v in source),'joint gap leaves domain')
    target=[mm[v] for v in source]
    exact(gap['source'],source,'joint gap source union')
    exact(gap['target'],target,'joint gap target union')
    require(len(source)==len(set(source))==7,'joint union shape')
    for a,b in zip([8,68],[85,60]):
        exact([mm[v] for v in tuples[a]],list(tuples[b]),'joint gap tuple movement')
        require(pattern(fullword,list(tuples[a]))==pattern(fullword,list(tuples[b])),'constituent tuple pattern gap')
    left,right=labels(fullword,source),labels(fullword,target)
    exact(gap['source_partition'],left,'joint source pattern')
    exact(gap['target_partition'],right,'joint target pattern')
    require(left!=right,'no claimed joint partition mismatch')
    exact(gap['cross_pair_source'],[4638,887],'cross-pair source')
    exact(gap['cross_pair_target'],[4672,5836],'cross-pair target')
    a,b=gap['cross_pair_source'];x,y=gap['cross_pair_target']
    require(a in tuples[8] and b in tuples[68] and not any(a in row and b in row for row in [tuples[8],tuples[68]]),'not a genuine cross-tuple pair')
    require(mm[a]==x and mm[b]==y and fullword[a]==fullword[b] and fullword[x]!=fullword[y],'cross-pair mismatch')
    exact(gap['scope'],'Mismatch of one saved word, not an all-word obstruction or a minimal-arity claim. A cross-tuple two-point equality already distinguishes the union patterns.','joint gap scope')
    complete_domains=[j for j,mm in enumerate(data['mappings']) if pattern(fullword,[a for a,b in mm])==pattern(fullword,[b for a,b in mm])]
    exact(complete_domains,[14],'unexpected full-domain status')
    return dict(status='PASS',core_vertices=11,core_induced_edges=5,
        original_Y_eta_probability_bound='4/5',full_Y_sharpness_proved=False,
        explicit_eta_event_differences=12,pointwise_identity_boolean_checks=32,
        marginal_polytope_facets=10,marginal_polytope_vertices=13,
        all_vertices_realized_with_three_colors=True,
        individual_pattern_probability_bound='2/5',two_pattern_probability_bound='3/5',
        tuple_orbit=122,checked_partial_steps=len(expected_transitions),
        kernel_vertices=129,kernel_actual_pairs=129*128//2,kernel_induced_edges=192,
        closed_eta_cycles=24,leftover_tuples=2,exact_maximum_membership_count=98,
        count_bound_sharp_for_every_k_at_least_three=True,
        uniform_count_bound='49/61',uniform_count_stronger_than_four_fifths=False,
        kernel_chromatic_number=3,local_full_domain_law_sizes=sizes,
        local_law_membership='1/5',joined_zero_word_edge_checks=len(data['edges']),
        joined_zero_preserved_pair_events=418,joined_zero_absent_patterns=366,
        joined_zero_equal_complete_tuple_partitions=122,
        joined_zero_common_complete_partition=common,
        joined_zero_passed_complete_domains=complete_domains,
        joint_gap_union_size=7,cross_tuple_pair_gap_verified=True,
        scope='Original-Y cylinder exclusion plus exact finite-kernel diagnostics. '
              'No full-Y15 law, new HN bound, or full-Y sharpness claim.')


def set_to_list(obj):
    require(isinstance(obj,dict),'expected object')
    return sorted(obj)


def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    data,summary=reconstruct(root)
    path=root/'certificates/localized_motion_packet.json'
    cert=read(root/'certificates/original_Y_cycle_descent.json')
    prior=root/'certificates/shared_event_research.json.gz'
    print(json.dumps(check(cert,data,summary,read(path),path.read_bytes(),read(prior),prior.read_bytes()),indent=2))


if __name__=='__main__':main()
