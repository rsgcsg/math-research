#!/usr/bin/env python3
"""Solver-free verification of one whole-Y G14 event witness."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
Y=ROOT/'certificates/Y_full_geometry.json.gz'
AUDIT=ROOT/'certificates/full_law_preparation_audit.json'
OR=ROOT/'certificates/g14_port_or_certificate.json'
RESULT=ROOT/'certificates/g14_unique_event_y_result.json'

def require(condition,message):
    if not condition:
        raise ValueError(message)

def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False,
                      allow_nan=False).encode('utf-8')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def list_sha(data):
    return sha(json.dumps(data,separators=(',',':')).encode('utf-8'))

def check_geometry_binding(ydata,audit):
    """Bind every cached point/edge byte to the independent input audit."""
    expected=audit['independent_inputs']
    geometry=expected['geometry']
    points=ydata['points'];edges=ydata['edges']
    semantic=sha(canonical(ydata))
    require(semantic==expected['semantic_sha256'],
            'Y geometry cache differs from independently audited semantic input')
    point_digest=list_sha(points);edge_digest=list_sha(edges)
    require(point_digest==geometry['point_sha256'],'reconstructed point digest differs from audit')
    require(edge_digest==geometry['edge_sha256'],'reconstructed edge digest differs from audit')
    require(ydata['geometry']['point_sha256']==point_digest,'cache point metadata mismatch')
    require(ydata['geometry']['edge_sha256']==edge_digest,'cache edge metadata mismatch')
    require(len(points)==geometry['vertices']==10077,'audited vertex count')
    require(len(edges)==geometry['induced_edges']==49858,'audited induced-edge count')
    require(len(points)*(len(points)-1)//2==geometry['actual_pairs'],'audited pair count')
    require(ydata['denominator']==480,'audited coordinate denominator')
    return semantic,point_digest,edge_digest

def reject_paired_missing_edge_mutation(ydata,audit,out,rel):
    """Reject a cache edit even if its own edge/hash metadata is refreshed."""
    altered=deepcopy(ydata)
    altered['edges'].pop()
    altered['geometry']['induced_edges']=len(altered['edges'])
    altered['geometry']['edge_sha256']=list_sha(altered['edges'])
    altered_raw=gzip.compress(canonical(altered),mtime=0)
    altered_sha=sha(altered_raw)
    altered_semantic=sha(canonical(altered))
    # Update every relevant self-report in dependent certificates. The trusted
    # independent_inputs receipt must still reject the changed point/edge data.
    altered_out=deepcopy(out)
    altered_out['y_geometry_sha256']=altered_sha
    altered_out['y_edge_sha256']=altered['geometry']['edge_sha256']
    altered_out['geometry_semantic_sha256']=altered_semantic
    altered_out['verified_actual_Y_edges']=len(altered['edges'])
    altered_rel=deepcopy(rel)
    altered_rel['actual_Y_embedding']['input_sha256']=altered_sha
    altered_rel['actual_Y_embedding']['semantic_sha256']=altered_semantic
    altered_rel['actual_Y_embedding']['edge_count']=len(altered['edges'])
    require(altered_out['y_geometry_sha256']==sha(altered_raw)
            and altered_out['y_edge_sha256']==list_sha(altered['edges'])
            and altered_rel['actual_Y_embedding']['input_sha256']==sha(altered_raw),
            'mutation test did not refresh self-reported hashes')
    try:
        check_geometry_binding(altered,audit)
    except ValueError:
        return
    raise AssertionError('accepted cache with missing edge and refreshed self-reported hashes')

def main():
    if not __debug__:
        raise RuntimeError('verification requires assertions')
    raw=Y.read_bytes(); ydata=json.loads(gzip.decompress(raw))
    audit=json.loads(AUDIT.read_text(encoding='utf-8'))
    rel=json.loads(OR.read_text(encoding='utf-8'))
    out=json.loads(RESULT.read_text(encoding='utf-8'))
    semantic,point_digest,edge_digest=check_geometry_binding(ydata,audit)
    require(out['schema']=='g14-unique-event-wholeY-query-v1','result schema')
    require(out['status']=='SAT_WITNESS','result is not a verified-coloring witness')
    require(out['geometry_semantic_sha256']==semantic,'result semantic geometry binding')
    require(out['y_geometry_sha256']==sha(raw),'result compressed geometry binding')
    require(out['y_point_sha256']==point_digest,'result point digest binding')
    require(out['y_edge_sha256']==edge_digest,'result edge digest binding')
    require(out['verified_actual_Y_edges']==len(ydata['edges']),'result edge count')
    require(rel['actual_Y_embedding']['semantic_sha256']==semantic,'G14 map semantic binding')
    require(rel['actual_Y_embedding']['input_sha256']==sha(raw),'G14 map source-byte binding')
    require(rel['actual_Y_embedding']['edge_count']==len(ydata['edges']),'G14 map edge count')
    require(rel['actual_Y_embedding']['point_sha256']==point_digest,'G14 map point digest')

    word=out['coloring']
    require(len(word)==len(ydata['points']) and set(word)<=set('01234'),'invalid coloring word')
    require(sha(word.encode('utf-8'))==out['coloring_sha256'],'coloring word digest')
    for u,v in ydata['edges']:
        require(word[u]!=word[v],f'improper stored Y edge {(u,v)}')
    mapping=rel['actual_Y_embedding']['vertex_indices']
    events=rel['independent_check']['virtual_pairs']
    mono=[(e['u'],e['v']) for e in events if word[mapping[e['u']]]==word[mapping[e['v']]]]
    require(mono==[('a2','i4')],f'unexpected monochromatic virtual events: {mono}')
    target=next(e for e in events if (e['u'],e['v'])==('a2','i4'))
    require(target['distance']=='2' and out['target']==['a2','i4']
            and out['target_distance']=='2','unique event target metadata')

    reject_paired_missing_edge_mutation(ydata,audit,out,rel)
    print('PASS: audited Y geometry binds 10077 points and 49858 actual edges')
    print('PASS: exact Y coloring has only mono virtual event a2-i4 at distance 2')
    print('PASS: rejected missing-edge cache mutation after refreshing self-reported hashes')
    print('coloring SHA256',sha(word.encode('utf-8')))
    print('colors used',sorted(set(word)))

if __name__=='__main__':
    main()
