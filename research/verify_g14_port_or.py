#!/usr/bin/env python3
"""Exact, standard-library transcription/replay for the G14 virtual-edge OR.

Coordinates are transcribed from the pinned public proof, not imported from its code.
Local project inputs are the already saved exact Parts509 and full-Y coordinate/edge certificates.
No SAT solver, internet access, or repository module is used.
"""
from __future__ import annotations
import argparse, hashlib, json, gzip
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path

SOURCE_COMMIT = "4c84e4d67522e644faef704694cd5ba7fc273abc"
SOURCE_REPO = "https://github.com/HeliCorgi/fourteen-points-six-colors"
SOURCE_PROOF = f"{SOURCE_REPO}/blob/{SOURCE_COMMIT}/proofs/PROOF_G14.md"

# A scalar a+b*sqrt(3) is the pair of exact rationals (a,b).
def sadd(x,y): return (x[0]+y[0], x[1]+y[1])
def ssub(x,y): return (x[0]-y[0], x[1]-y[1])
def smul(x,y): return (x[0]*y[0]+3*x[1]*y[1], x[0]*y[1]+x[1]*y[0])
def ssq(x): return smul(x,x)
def point(xa,xb,ya,yb): return ((Q(xa),Q(xb)),(Q(ya),Q(yb)))

# Public PROOF_G14.md coordinate table, in its vertex order.
P = {
    "O":  point(0,0,0,0),
    "h0": point(1,0,0,0),
    "i0": point(Q(1,2),0,0,Q(1,6)),
    "h1": point(Q(1,2),0,0,Q(1,2)),
    "i1": point(0,0,0,Q(1,3)),
    "a1": point(1,0,0,Q(1,3)),
    "a2": point(1,0,0,Q(2,3)),
    "i2": point(Q(-1,2),0,0,Q(1,6)),
    "a3": point(Q(1,2),0,0,Q(5,6)),
    "i3": point(Q(-1,2),0,0,Q(-1,6)),
    "i4": point(0,0,0,Q(-1,3)),
    "a4": point(Q(3,2),0,0,Q(1,6)),
    "i5": point(Q(1,2),0,0,Q(-1,6)),
    "a5": point(Q(3,2),0,0,Q(-1,6)),
}
LABELS = list(P)
D2_LABEL = {(Q(1),Q(0)):"1", (Q(1,3),Q(0)):"1/sqrt3", (Q(4),Q(0)):"2"}
SIX_COLOR_CLASSES = [
    {"i0","i3"}, {"a1","O"}, {"i1","h0","a2"},
    {"i5","a3","i2"}, {"a5","h1","i4"}, {"a4"},
]

def norm2(p,q):
    dx=ssub(p[0],q[0]); dy=ssub(p[1],q[1])
    return sadd(ssq(dx),ssq(dy))

def exact_graph():
    types={}
    for u,v in combinations(LABELS,2):
        d2=norm2(P[u],P[v])
        if d2 in D2_LABEL: types[(u,v)] = D2_LABEL[d2]
    return types

def independent_sets(adj,k):
    return [S for S in combinations(LABELS,k)
            if all(v not in adj[u] for u,v in combinations(S,2))]

def find_coloring(base, extra, k=5):
    """Exhaustive DSATUR backtracking; returns a proper coloring or None."""
    adj={v:set(base[v]) for v in LABELS}
    for u,v in extra:
        adj[u].add(v); adj[v].add(u)
    color={}
    def visit():
        if len(color)==len(LABELS): return color.copy()
        uncolored=[v for v in LABELS if v not in color]
        v=max(uncolored,key=lambda w:(len({color[x] for x in adj[w] if x in color}),
                                      len(adj[w]),-LABELS.index(w)))
        used={color[x] for x in adj[v] if x in color}
        for c in range(k):
            if c not in used:
                color[v]=c
                witness=visit()
                if witness is not None: return witness
                del color[v]
        return None
    return visit()

def frac_pair(x): return [x.numerator,x.denominator]
def serialize_point(p):
    return [[frac_pair(z[0]),frac_pair(z[1])] for z in p]

def verify(parts_path:Path, y_geometry_path:Path):
    types=exact_graph()
    counts=Counter(types.values())
    assert counts==Counter({"1":18,"1/sqrt3":27,"2":5}),counts
    assert len(set(P.values()))==14
    full_adj={v:set() for v in LABELS}
    for (u,v) in types: full_adj[u].add(v);full_adj[v].add(u)
    indep4=independent_sets(full_adj,4)
    indep3=independent_sets(full_adj,3)
    assert not indep4
    assert len(indep3)==22
    assert not any("i0" in S for S in indep3)
    assert not any("a1" in S for S in indep3)
    assert types.get(("a1","i0"), types.get(("i0","a1")))=="1/sqrt3"
    assert set().union(*SIX_COLOR_CLASSES)==set(LABELS)
    assert sum(map(len,SIX_COLOR_CLASSES))==14
    for C in SIX_COLOR_CLASSES:
        assert all((u,v) not in types for u,v in combinations(LABELS,2) if u in C and v in C)

    unit={e for e,t in types.items() if t=="1"}
    virtual={e for e,t in types.items() if t!="1"}
    unit_adj={v:set() for v in LABELS}
    for u,v in unit: unit_adj[u].add(v);unit_adj[v].add(u)
    unit_witness=find_coloring(unit_adj, set(),3)
    assert unit_witness is not None
    assert any(unit_witness[u]==unit_witness[v] for u,v in virtual)

    # Every event is individually essential relative to this 14-point unit-only core:
    # for each e, H plus inequalities on all other 31 virtual pairs has a 5-color witness.
    essentiality=[]
    for e in sorted(virtual):
        witness=find_coloring(unit_adj, virtual-{e},5)
        assert witness is not None, ("redundant virtual event",e)
        assert witness[e[0]]==witness[e[1]], ("omitted event not mono",e,witness)
        assert all(witness[u]!=witness[v] for u,v in virtual-{e})
        essentiality.append({"omitted_event":list(e),"distance":types[e],
                             "colors":[witness[v] for v in LABELS]})

    parts=json.loads(parts_path.read_text())
    assert parts["coordinate_denominator"]==96
    # Matches basis in the local verifier: (1, sqrt3, sqrt11, sqrt33, sqrt5, sqrt15, sqrt55, sqrt165).
    lookup={tuple(tuple(x) for x in p):i for i,p in enumerate(parts["points"])}
    mapping={}
    for label,p in P.items():
        target=(tuple([int(p[0][0]*96),int(p[0][1]*96),0,0,0,0,0,0]),
                tuple([int(p[1][0]*96),int(p[1][1]*96),0,0,0,0,0,0]))
        mapping[label]=lookup.get(target)
    assert all(i is not None for i in mapping.values())
    assert len(set(mapping.values()))==14
    parts_edges={tuple(sorted(e)) for e in parts["induced_edges"]}
    mapped_unit={tuple(sorted((mapping[u],mapping[v]))) for u,v in unit}
    mapped_all={tuple(sorted((mapping[u],mapping[v]))) for u,v in types}
    assert mapped_unit <= parts_edges
    assert mapped_all & parts_edges == mapped_unit

    # Verify the exact same point set against the full saved Y geometry as well.
    # The local construction embeds a Parts point as (x_8,y_8,0^16), then
    # clears denominator 96 to 480.
    y_raw=y_geometry_path.read_bytes()
    ydata=json.loads(gzip.decompress(y_raw))
    geometry_receipt=json.loads((y_geometry_path.parent/"full_law_preparation_audit.json").read_text())
    y_semantic=hashlib.sha256(json.dumps(ydata,sort_keys=True,separators=(",",":"),
        ensure_ascii=False,allow_nan=False).encode("utf-8")).hexdigest()
    assert y_semantic==geometry_receipt["independent_inputs"]["semantic_sha256"]
    assert ydata["denominator"]==480
    assert ydata["geometry"]["vertices"]==10077
    assert ydata["geometry"]["induced_edges"]==49858
    assert ydata["geometry"]["point_sha256"]=="6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1"
    y_lookup={tuple(p):i for i,p in enumerate(ydata["points"])}
    mapping_y={}
    for label,p in P.items():
        target=tuple([int(p[0][0]*480),int(p[0][1]*480),0,0,0,0,0,0]+
                     [int(p[1][0]*480),int(p[1][1]*480),0,0,0,0,0,0]+[0]*16)
        mapping_y[label]=y_lookup.get(target)
    assert all(i is not None for i in mapping_y.values())
    assert len(set(mapping_y.values()))==14
    y_edges={tuple(sorted(e)) for e in ydata["edges"]}
    mapped_y_unit={tuple(sorted((mapping_y[u],mapping_y[v]))) for u,v in unit}
    mapped_y_all={tuple(sorted((mapping_y[u],mapping_y[v]))) for u,v in types}
    assert mapped_y_unit <= y_edges
    assert y_edges & mapped_y_all == mapped_y_unit

    digest=hashlib.sha256(parts_path.read_bytes()).hexdigest()
    y_digest=hashlib.sha256(y_raw).hexdigest()
    certificate={
        "schema":"g14-port-or-exact-replay-v1",
        "external_attribution":{"repository":SOURCE_REPO,"commit":SOURCE_COMMIT,
            "proof_file":SOURCE_PROOF,"read_scope":["README.md","proofs/PROOF_G14.md",
            "proofs/PROOF_G15.md","proofs/LEMMA_CLIQUE_STARVATION.md","LITERATURE.md"],
            "warning":"The separate minimum-14/catalog/interval-certificate claim was not audited here."},
        "independent_check":{"method":"Python standard library only: Fraction arithmetic in Q(sqrt(3)); exhaustive 91-pair classification and 4-subset independence enumeration; custom exhaustive DSATUR backtracking for witness colorings; no SAT package, external solver, or external project code.",
            "source_coordinates":{v:serialize_point(P[v]) for v in LABELS},
            "distance_edges":[{"u":u,"v":v,"distance":t} for (u,v),t in sorted(types.items())],
            "distance_counts":dict(counts),"distinct_points":14,
            "independence_number":3,"independent_triples":[list(s) for s in indep3],
            "triple_free_vertices":["i0","a1"],"adjacent_poor_pair":{"vertices":["i0","a1"],"distance":"1/sqrt3"},
            "six_color_classes":[sorted(s) for s in SIX_COLOR_CLASSES],
            "unit_only_core":{"edges":[list(e) for e in sorted(unit)],"edge_count":len(unit),
                "five_color_witness_colors":[unit_witness[v] for v in LABELS],"witness_uses_at_most":3},
            "virtual_pairs":[{"u":u,"v":v,"distance":types[(u,v)]} for u,v in sorted(virtual)],
            "port_or_inequality":"For every proper 5-coloring c of the 14-point unit-only core H, sum_{e in the 32 virtual pairs} 1[c(u)=c(v)] >= 1. Proof: a zero sum would make c proper on all 50 D-edges, contradicting the independently verified alpha/poor-vertex class-size argument.",
            "virtual_event_essentiality":"For each of the 32 virtual events e, the certificate has a proper 5-coloring of H that makes every other virtual pair different and makes e equal. Thus no proper subset of these 32 events still forces the OR on this fixed 14-point H.",
            "event_deletion_witnesses":essentiality,
            "Parts509_embedding":{"input_sha256":digest,"coordinate_denominator":96,
                "basis":["1","sqrt3","sqrt11","sqrt33","sqrt5","sqrt15","sqrt55","sqrt165"],
                "vertex_indices":mapping,"unit_edge_subgraph_matches_induced_edges":True,
                "no_extra_unit_edges_among_14":True,
                "Y_inheritance":"Parts509 is contained in X and Y=X union tau X; the independent Y-coordinate check below additionally matches all 14 physical points and the exact unit edge subgraph."}},
        "actual_Y_embedding":{"input_sha256":y_digest,"semantic_sha256":y_semantic,
            "point_sha256":ydata["geometry"]["point_sha256"],
            "edge_count":ydata["geometry"]["induced_edges"],"vertex_indices":mapping_y,
            "unit_edge_subgraph_matches_Y_induced_edges":True,"no_extra_Y_unit_edges_among_14":True},
        "scope_limits":["This is not a unit-distance graph with chromatic number 6.",
            "It is not a strict 15-domain separating potential or proof of a non-5-colorable actual unit-distance graph.",
            "The 32-event minimality is only for the fixed 14-point unit-only core H, not for all proper colorings of the full 509-point graph or Y.",
            "No claim that the larger Y has free 3-terminal relations; only its pair-saturation result is used."]
    }
    return certificate

def main():
    here=Path(__file__).resolve().parent
    root=here.parent
    parser=argparse.ArgumentParser()
    parser.add_argument("--parts-core",type=Path,default=root/"certificates/parts509_core.json")
    parser.add_argument("--y-geometry",type=Path,default=root/"certificates/Y_full_geometry.json.gz")
    parser.add_argument("--output",type=Path,help="write a freshly rebuilt certificate to this path")
    parser.add_argument("--check-certificate",type=Path,
                        help="require exact structural equality with this saved certificate")
    args=parser.parse_args()
    if args.output and args.check_certificate:
        parser.error("choose --output or --check-certificate, not both")
    cert=verify(args.parts_core,args.y_geometry)
    if args.check_certificate:
        saved=json.loads(args.check_certificate.read_text(encoding="utf-8"))
        if saved != cert:
            raise ValueError("saved G14 certificate differs from fresh independent replay")
        print("PASS: saved certificate exactly matches independent replay",args.check_certificate)
    else:
        output=args.output or root/"certificates/g14_port_or_certificate.json"
        output.write_text(json.dumps(cert,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print("PASS",output)
    print("source commit",SOURCE_COMMIT)
    print("pair counts",cert["independent_check"]["distance_counts"])
    print("OR events",len(cert["independent_check"]["virtual_pairs"]),"; essential deletion witnesses",len(cert["independent_check"]["event_deletion_witnesses"]))
    print("Parts509 ports",cert["independent_check"]["Parts509_embedding"]["vertex_indices"])
    print("Parts core SHA256",cert["independent_check"]["Parts509_embedding"]["input_sha256"])
    print("Y point SHA256",cert["actual_Y_embedding"]["point_sha256"])
    print("G14-to-Y indices",cert["actual_Y_embedding"]["vertex_indices"])
if __name__=="__main__": main()
