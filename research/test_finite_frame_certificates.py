"""Exact replay, deterministic rebuild, and rejection tests for E103/E104."""
from pathlib import Path
import copy
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from verify_finite_frame_separation import (
    prepare, check_separator_structure, derive_separator_clauses,
    check_separator_consequence, check_arithmetic, calibrate_frames,
)

def check_gzip_portability():
    from unittest.mock import patch
    import build_finite_frame_certificates as builder
    sample = b"finite-frame certificate header calibration\n"
    compressed = gzip.compress(sample, mtime=0)
    for operating_system in (0, 3, 255):
        variant = compressed[:9] + bytes([operating_system]) + compressed[10:]
        with patch.object(builder.gzip, 'compress', return_value=variant):
            normalized = builder.canonical_gzip(sample)
        assert normalized[9] == 255
        assert normalized[:9] == variant[:9] and normalized[10:] == variant[10:]
        assert gzip.decompress(normalized) == sample
    return [0, 3, 255]


def check(root):
    if not __debug__:
        raise RuntimeError('Verification requires assertions')
    prepared=prepare(root)
    source=root/'certificates/finite_frame_separator.json.gz'
    frame_source=root/'certificates/arithmetic_frame_separation.json'
    sep=json.loads(gzip.decompress(source.read_bytes()))
    frame=json.loads(frame_source.read_text())
    structure=check_separator_structure(sep,prepared)
    derived=derive_separator_clauses(sep,prepared)
    check_separator_consequence(sep,derived)
    arithmetic=check_arithmetic(frame,prepared)
    rejected=[]
    def reject(name,original,mutation,verifier):
        data=copy.deepcopy(original); mutation(data)
        try:
            verifier(data)
        except (AssertionError,ValueError,KeyError,IndexError,TypeError):
            rejected.append(name)
        else:
            raise AssertionError('Accepted mutation: '+name)
    sf=lambda d:check_separator_structure(d,prepared)
    af=lambda d:check_arithmetic(d,prepared)
    cf=lambda d:check_separator_consequence(d,derived)
    reject('separator-source-hash',sep,lambda d:d.update(source_sha256='0'*64),sf)
    reject('separator-omitted-node',sep,lambda d:d['component_labels'].pop(),sf)
    reject('separator-wrong-root-label',sep,
           lambda d:next(x for x in d['component_labels'] if x[0]==d['root']).__setitem__(1,2),sf)
    reject('separator-duplicate-fiber-image',sep,lambda d:d['permutations'][0][0].__setitem__(0,0),sf)
    reject('separator-target-not-separated',sep,lambda d:d.update(target=d['root']),sf)
    reject('separator-false-edge-count',sep,lambda d:d['expected'].__setitem__('directed_component_edges',117148),sf)
    reject('separator-false-proper-class-count',sep,lambda d:d['expected'].__setitem__('literal_classes',2049),cf)
    reject('separator-false-unit-count',sep,lambda d:d['expected'].__setitem__('forced_literals',194),cf)
    reject('separator-false-event-count',sep,lambda d:d['expected'].__setitem__('unequal_counts',[0,0]),cf)
    reject('frame-composite-prime',frame,lambda d:d.update(prime=5700),af)
    reject('frame-bad-field-image',frame,lambda d:d['images'].__setitem__(1,(d['images'][1]+1)%5701),af)
    reject('frame-bad-conjugate-image',frame,lambda d:d['bars'].__setitem__(8,0),af)
    reject('frame-zero-linear-scale',frame,lambda d:d['actions'][0].__setitem__('scale',0),af)
    reject('frame-wrong-translation',frame,lambda d:d['actions'][6]['shift'].__setitem__(0,2),af)
    reject('frame-missing-u',frame,lambda d:d['actions'].pop(),af)
    reject('frame-noninjective-claim',frame,lambda d:d['expected'].__setitem__('injective_points',10076),af)
    reject('frame-wrong-coordinate-hash',frame,lambda d:d.update(coordinate_sha256='0'*64),af)
    reject('frame-bad-tree-gauge',frame,lambda d:d['gauge'].__setitem__(0,[1,0,2,3,4]),af)
    reject('frame-incomplete-palette-group',frame,lambda d:d['palette_group'].pop(),af)
    reject('frame-false-solvable-length',frame,lambda d:d['expected'].__setitem__('derived_orders',[24,4,1]),af)
    reject('frame-false-state-bound',frame,lambda d:d['expected'].__setitem__('cover_states',15),af)
    optimized=[]
    for name in ['verify_finite_frame_separation.py','test_finite_frame_certificates.py','build_finite_frame_certificates.py']:
        result=subprocess.run([sys.executable,'-O',str(root/'research'/name)],capture_output=True,text=True)
        assert result.returncode!=0 and 'Verification requires assertions' in result.stderr
        optimized.append(name)
    with tempfile.TemporaryDirectory() as directory:
        result=subprocess.run([sys.executable,str(root/'research/build_finite_frame_certificates.py'),
                               '--output-dir',directory],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        for name in ['finite_frame_separator.json.gz','arithmetic_frame_separation.json']:
            assert (Path(directory)/name).read_bytes()==(root/'certificates'/name).read_bytes(),name
    return dict(schema='finite-frame-validation-v1',status='PASS',date='2026-09-21',
                python=platform.python_version(),theorems=['T133','T134'],experiments=['E103','E104'],
                separator=dict(structure=structure,proper_consequence=derived),arithmetic_frame=arithmetic,
                calibrations=calibrate_frames(),mutations_rejected=rejected,
                optimized_rejections=optimized,byte_identical_rebuild=True,
                gzip_header_inputs_normalized=check_gzip_portability(),
                certificates={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,frame_source]},
                scope='New finite certificates only. General infinite-path claims use the written proof; no HN bound or 15-domain positive law.')

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; report=check(root)
    (root/'certificates/finite_frame_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
