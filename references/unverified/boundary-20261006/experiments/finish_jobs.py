from pathlib import Path
import subprocess,os,json,time,traceback,shutil
w=Path(__file__).resolve().parents[1];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
report={}
try:
    # Only supervise this turn's explicit child jobs; never kill unrelated work.
    pidfile=w/'experiments/local.pid'
    if pidfile.exists():
        pid=int(pidfile.read_text());deadline=time.monotonic()+600
        while Path(f'/proc/{pid}/stat').exists() and time.monotonic()<deadline:
            state=Path(f'/proc/{pid}/stat').read_text().split()[2]
            if state=='Z':break
            time.sleep(2)
    if not (w/'experiments/endpoint_min.json').exists() or not (w/'experiments/endpoint_max.json').exists():
        with (w/'experiments/local-retry.log').open('w') as log:
            p=subprocess.run(['python',str(w/'experiments/close_boundary.py')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900)
        report['discovery_returncode']=p.returncode
    with (w/'verification/independent-replay-final.log').open('w') as log:
        p=subprocess.run(['python','-S',str(w/'experiments/finalize_boundary.py')],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
    report['independent_returncode']=p.returncode
    if p.returncode==0:
        target=w/'repo/research/check_exact_local_pr_boundary.py';shutil.copyfile(w/'experiments/check_exact_local_pr_boundary.py',target)
        with (w/'verification/portable-replay.log').open('w') as log:
            p=subprocess.run(['python','-S',str(target),'--self-test'],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
        report['portable_returncode']=p.returncode
        if p.returncode==0:
            report['status']='PASS'
            q=json.load(open(w/'verification/completion.json'));report['q_interval']=[q['minimum_q'],q['maximum_q']]
            cur=w/'repo/docs/CURRENT.md';cur.write_text('# 2026-10-06：固定22点P/R尖点的Q区间已精确闭合\n\n'+f"本轮独立整数重放给出 q∈[{q['minimum_q']}, {q['maximum_q']}]。两端都有逐事件精确有理正律。\n"+'这是固定22点局部模型的边界，不是原Y/full15的共同律，不改变普通HN界。\n[完整证明](proofs/exact_local_pr_boundary_interval.md) · [证书](../certificates/exact_local_pr_boundary_interval.json)。\n同一局部截面的端点优化已结束，后续应检验V外运输/联合模式的相容性。\n\n'+cur.read_text())
            mf=w/'repo/Makefile';s=mf.read_text();s+='\n.PHONY: check-exact-pr-boundary\ncheck-exact-pr-boundary:\n\tpython3 -S research/check_exact_local_pr_boundary.py --self-test\n';mf.write_text(s)
    report.setdefault('status','NOT_COMPLETED')
except Exception:report.update(status='NOT_COMPLETED',error=traceback.format_exc())
(w/'verification/final_jobs.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False),flush=True)
