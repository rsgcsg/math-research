"""Run the independent cover certificate checks and optimized-mode rejection."""
from pathlib import Path
import json
import subprocess
import sys

def main():
    if not __debug__:raise RuntimeError('Verification requires assertions')
    root=Path(__file__).resolve().parents[1]
    entries=[('verify_joint_nilpotent_cover.py',['--mutations']),
             ('verify_joint_s3_cover.py',['--mutations']),
             ('verify_joint_cover_normal_form.py',[])]
    reports=[];rejections=[]
    for name,args in entries:
        path=root/'research'/name
        result=subprocess.run([sys.executable,str(path),*args],capture_output=True,text=True,check=True)
        reports.append(json.loads(result.stdout))
        bad=subprocess.run([sys.executable,'-O',str(path)],capture_output=True,text=True)
        assert bad.returncode!=0 and 'Verification requires assertions' in bad.stderr
        rejections.append(name)
    report=dict(status='PASS',checks=reports,optimized_mode_rejections=rejections,
                scope='New cover certificate regression only; not the entire repository regression')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
