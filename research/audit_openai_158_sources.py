"""Verify bytes and elementary metadata of the pinned upstream source archive.

This tool does not run Lean and does not prove any mathematical theorem.
The separate Lean replay receipt records the actual remote target rebuild.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def verify(archive, receipt):
    require(receipt['commit'] == 'adc7f1241b42e322a6451854ab7e4b4c146bf78a', 'upstream pin')
    with zipfile.ZipFile(archive) as z:
        require(len(z.namelist()) == len(set(z.namelist())), 'duplicate zip members')
        require(set(z.namelist()) == set(receipt['files']), 'source file set')
        for p, item in receipt['files'].items():
            raw = z.read(p)
            require(len(raw) == item['bytes'], 'size: '+p)
            require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'SHA256: '+p)
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == item['git_blob_sha1'], 'Git blob: '+p)
        text = z.read('CONTENTS.md').decode()
        families = re.findall(r'^\*\*(\d{3})\. ',text,re.M)
        papers = re.findall(r'^&emsp;\[(.*?)\]\((.+\.pdf)\)',text,re.M)
        require(len(families) == len(set(families)) == 372, 'families')
        require(len(papers) == 722, 'manuscript links')
        config = json.loads(z.read('lean/ComparatorChallenges/EuclideanFiveColor.json'))
        require(config['solution_module'] == 'OAI.Geometry.PlaneColoring.Five', 'solution target')
        require(set(config['permitted_axioms']) == {'propext','Quot.sound','Classical.choice'}, 'permitted axioms')
        actual = z.read('lean/OAI/Geometry/PlaneColoring/Five.lean').decode()
        require('theorem no_proper_five_coloring' in actual, 'missing actual theorem')
        own = [p for p in z.namelist() if p.startswith('lean/OAI/') and p.endswith('.lean')]
        require(len(own) == 70, 'import closure size')
        tokens = [(p, token) for p in own for token in re.findall(r'\b(?:sorry|admit|axiom|unsafe)\b',z.read(p).decode())]
        require(not tokens, 'literal placeholder tokens: '+str(tokens))
    return dict(status='PASS_SOURCE_BINDING_ONLY',source_files=len(receipt['files']),
                OAI_modules_scanned=70,families=372,manuscript_links=722,
                lean_executed=False,analytic_generalization_proved=False,
                scope='Pinned bytes, literal token scan and metadata only, not semantic proof verification.')


def main():
    if not __debug__:
        raise RuntimeError('Source audit requires non-optimized Python')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive',type=Path)
    args = ap.parse_args()
    receipt = json.loads((ROOT/'certificates/openai_158_source_audit.json').read_text())
    print(json.dumps(verify(args.archive,receipt),indent=2))


if __name__ == '__main__':
    main()
