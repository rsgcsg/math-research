"""E098 replay, independent proof-DAG validation and deliberate tampering tests."""
from copy import deepcopy
from pathlib import Path
import gzip
import hashlib
import json
import random
import subprocess
import sys
from build_partition_quartet_certificate import build, encode
from verify_partition_quartet_completeness import check
from joint_moment_cegar import separating_events, shape


def run(root):
    if not __debug__:raise RuntimeError('Do not disable verification assertions')
    path=root/'certificates/partition_quartet_completeness.json.gz'
    raw=path.read_bytes();data=json.loads(gzip.decompress(raw))
    report=check(data);assert encode(build())==raw
    mutations=[]
    branch=next(i for i,r in enumerate(data['nodes']) if len(r[5])>1)
    leaf=next(i for i,r in enumerate(data['nodes']) if not r[5])
    def rejected(label,change):
        altered=deepcopy(data);change(altered)
        try:check(altered,exhaustive=False)
        except (AssertionError,IndexError,KeyError,TypeError,ValueError):mutations.append(label)
        else:raise AssertionError('Accepted tampering: '+label)
    rejected('support_limit',lambda d:d.update(support_limit=6))
    rejected('block_limit',lambda d:d.update(block_limit=6))
    rejected('duplicate_partition',lambda d:d['partitions'].__setitem__(0,d['partitions'][1]))
    rejected('omitted_root',lambda d:d['roots'].pop())
    rejected('wrong_root',lambda d:d['roots'][0].update(node=leaf))
    rejected('omitted_branch',lambda d:d['nodes'][branch][5].pop())
    rejected('false_leaf',lambda d:d['nodes'][branch].__setitem__(5,[]))
    rejected('cyclic_child',lambda d:d['nodes'][branch][5].__setitem__(0,branch))
    rejected('wrong_child_state',lambda d:d['nodes'][branch][5].__setitem__(0,d['nodes'][branch][5][1]))
    rejected('invalid_selected_atom',lambda d:d['nodes'][leaf].__setitem__(3,202))
    rejected('false_deletion',lambda d:d['nodes'][leaf].__setitem__(4,6))
    rejected('unequal_total_mass',lambda d:d['sharpness']['unequal_weights_need_five']['weights_left'].__setitem__(4,1))
    rejected('false_sharpness_word',lambda d:d['sharpness']['four_points_necessary']['left'].__setitem__(0,'0000'))
    rejected('false_six_color_cap',lambda d:d['sharpness']['six_colors_defeat_four_points'].update(maximum_blocks=5))
    rng=random.Random(20260920);tested=0;quadratic=0
    sample=data['sharpness']['four_points_necessary']
    candidates=[([shape(w) for w in sample['left']],[shape(w) for w in sample['right']])]
    for n in (2,3,4,6,12,40):
        for _ in range(25):
            left=[shape(rng.randrange(5) for _ in range(n)) for a in range(5)]
            right=[shape(rng.randrange(5) for _ in range(n)) for a in range(5)]
            candidates.append((left,right))
    for left,right in candidates:
        found=separating_events(left,right)
        if sorted(left)==sorted(right):assert not found
        else:assert found
        for event,counts in found:
            assert len(event) in (1,2)
            assert len({i for pair in event for i in pair})<=4
            direct=[sum(all(w[i]==w[j] for i,j in event) for w in side) for side in (left,right)]
            assert direct==counts and counts[0]!=counts[1]
            quadratic+=len(event)==2
        shuffled=left[:];rng.shuffle(shuffled)
        assert not separating_events(left,shuffled)
        tested+=1
    optimized=[]
    for name in ('verify_partition_quartet_completeness.py','test_partition_quartet_completeness.py'):
        proc=subprocess.run([sys.executable,'-O',str(root/'research'/name)],capture_output=True,text=True)
        assert proc.returncode!=0 and 'assertions' in proc.stderr
        optimized.append(name)
    report.update(byte_identical_rebuild=True,mutations_rejected=mutations,
                  optimized_modes_rejected=optimized,event_extractor_pairs_tested=tested,
                  genuine_quadratic_events_tested=quadratic,
                  certificate_sha256=hashlib.sha256(raw).hexdigest())
    return report


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Do not disable verification assertions')
    root=Path(__file__).resolve().parents[1];report=run(root)
    (root/'certificates/partition_quartet_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
