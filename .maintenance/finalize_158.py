"""Reviewed one-use publication closeout; removed from the final source tree."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = 'rsgcsg/math-research'
BRANCH = 'research/openai-158-audit-20261007'
BASE = '65874a0e56ebbcaff8a33fc0cac1137c152c9131'
BEFORE = {
'Makefile':'cd4df09189ad9200e3f8bf7828349b1cb2845117e11f14f684431a18f9b1bf61',
'README.md':'64dfb01ee8db74ac9a7ff09c837359d80dcb6d60cdef5f67ca10d14a16758c21',
'docs/CURRENT.md':'ecb4bb8d2ae439dfe2d3291af7f25dd8bccedf4c160654d8889a6f65878e6854',
'docs/RESULTS.md':'cfcd4bfb31a7f64c8b87ba2af6008281c040083715177f1e0d0cd0ae98cb928f',
'docs/ROUTES.md':'aa8932fb6a61b12158130104d79d00cb02e6f0396863e4f1ff66ba54a4596425',
'docs/proofs/hn_unified_framework.md':'c0503ad12ce37f50ec6b471afaa1326bb064444f30cacc8f474c31999af6c4d3',
'references/OPENAI_158_AUDIT.md':'7aa382db0a0ff57e350fe6c553c0c52b1eeab59dd04516991315cacf3b20afda'}

ADDITIONS = {
'docs/CURRENT.md': '''## 追加闭合：有限二点模板与旋转群不足性

[R158-C](proofs/radical_finite_template_transfer.md)把同色禁配推广到任意有限标签集、
按正距离给定的对称允许关系。F_sol²与R²对每一个这样的模板具有相同存在性答案。
关键新步骤是利用旋转−1与极化，证明连续因子投影保留所有不同颜色的非零位移交叉相关，
再以正坐标选标签保留零禁配。特别地，每个有限(a,b)多重染色与有理循环模板答案相同。
未给任何新分数/循环色数的数值，未把任意高阶CSP归入该结论。

[R158-F](proofs/finitely_generated_rotation_rigidity_obstruction.md)独立证明：
任何有限生成代数旋转群H都允许wild而非Haar的字符概率。
取包含其生成元的真数域N，N的湮灭子Haar概率具有Fourier系数1_N。
即使H在圆周稠密也成立；因此不能直接用固定旋转群的更深指数层替代上游全K刚性。
这个谱反例不是proper染色，不决定full15，也不否定有限图证据的存在。

所有R158推广与反例在本项目中属于完整书面证明；上游无五染的Lean重放是另一证据层次。
新增有限检查穷尽25234份标签/支持组合，核对3645项反射极化恒等式和891项有理旋转样本。
更新后的专项检查和来源/静态检查独立执行；未重新跑旧70条全仓数学检查。
本轮未合并其他并行研究分支，也没有将另行交付的boundary-saturation提交默认为主线已收录。

''',
'docs/RESULTS.md': '''| R158-C | 对满足R158-H的子域，任意有限、按距离指定的二点允许关系，在子域平面与R²上可满足性相同；涵盖有限图目标、多重染色和有理循环模板 | [交叉相关与密度点的完整证明](proofs/radical_finite_template_transfer.md)；不是任意高阶CSP或新色数数值，未Lean形式化。 |
| R158-F | 任意真子域N⊊E包含Q(i)时，N湮灭子Haar概率的Fourier系数为1_N；对所有N×子群不变、避开连续字符且非全Haar。覆盖任意有限生成代数旋转群 | [完整反例](proofs/finitely_generated_rotation_rigidity_obstruction.md)；不依赖Family158、不等于染色反例或full15正律。 |
''',
'docs/ROUTES.md': '''[有限模板转移R158-C](proofs/radical_finite_template_transfer.md)保留不同颜色交叉相关，
使多距离与多重染色不必另开互不相干的分析路线。高阶共同律仍须另证，不能由二点模板自动推出。
[有限生成旋转障碍R158-F](proofs/finitely_generated_rotation_rigidity_obstruction.md)关闭
“旧有限H下wild谱自动Haar”的无额外条件路线：必须加入颜色指标共同结构，
或在有限化中引入新的域/旋转，而不是仅增加旧H的指数。
它不禁止最终有限NON5/NON6证据，也不判定任何固定Y的full15。

''',
'docs/proofs/hn_unified_framework.md': '''更精确的[R158-C](radical_finite_template_transfer.md)表明两平面对所有**有限二点目标模板**不可区分，
但R158-N仍排除到无限宿主U(F_sol²)的普适同态。有限目标与无限目标的量词不可互换。
[R158-F](finitely_generated_rotation_rigidity_obstruction.md)又说明，有限生成代数旋转群
在大域上留下子域湮灭子谱；“通常拓扑稠密”不是谱连续性的替代条件。
该反例没有颜色指标的全部非负/乘法约束，不能转述为full15可行性。

''',
'references/OPENAI_158_AUDIT.md': '''
## 6. 本轮续写与实际验证范围

在上次已完成的Lean运行37573206401基础上，本轮重新读取和验收原始日志，未再编译一次该Lean目标。
恢复的草稿已逐页检查，再由运行37576935885按14个逐文件哈希发布；不是把未读blob自动认作证明。
新增[R158-C](../docs/proofs/radical_finite_template_transfer.md)补足不同颜色交叉相关的极化与反射步骤，
推广到全部有限径向二点模板；新增[R158-F](../docs/proofs/finitely_generated_rotation_rigidity_obstruction.md)
给出有限生成旋转下的显式非Haar谱，后者不依赖上游无五染定理。

最新专项检查的实际退出码与原始输出另存`certificates/radical_template_validation.json`及同目录日志。
有限测试不是新的分析形式化，也不能给没有输出的有限单位图或6/7终局盖认证章。
使用中的上游版本未被本项目修改；原论文、许可证和源哈希在单独交付中保留。
'''
}
REMOVE = [
'.github/workflows/openai-158-source-audit.yml',
'.github/workflows/openai-158-lean-check.yml',
'.github/workflows/recover-158-draft.yml',
'.github/workflows/publish-158-reviewed.yml',
'.github/workflows/finalize-158.yml',
'.maintenance/finalize_158.py']


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args]).decode().strip()


def one_replace(path, old, new):
    p = Path(path)
    text = p.read_text()
    require(text.count(old) == 1, 'ambiguous edit: ' + path)
    p.write_text(text.replace(old, new, 1))


def apply():
    require(all(sha(Path(p).read_bytes()) == s for p,s in BEFORE.items()), 'changed input')
    one_replace('Makefile',
                '\tpython3 -S research/verify_radical_transfer_calibration.py --self-test\n',
                '\tpython3 -S research/verify_radical_transfer_calibration.py --self-test\n\tpython3 -S research/verify_radical_template_mechanism.py\n')
    one_replace('README.md', '`make check-radical-transfer`只重放本轮有限代数校准。',
                '[有限二点模板转移](docs/proofs/radical_finite_template_transfer.md)进一步保留多重染色与有理循环模板；\n[有限生成旋转反例](docs/proofs/finitely_generated_rotation_rigidity_obstruction.md)说明稠密旋转不足以推出全域谱刚性。\n\n`make check-radical-transfer`重放有限代数、标签支持与谱样本校准，不认证无限分析证明。')
    one_replace('docs/CURRENT.md', '## 原问题的准确剩余义务\n', ADDITIONS['docs/CURRENT.md'] + '## 原问题的准确剩余义务\n')
    one_replace('docs/RESULTS.md', '\n以下为保留的统一账本', '\n' + ADDITIONS['docs/RESULTS.md'] + '\n以下为保留的统一账本')
    one_replace('docs/ROUTES.md', '下面是保留的历史路线', ADDITIONS['docs/ROUTES.md'] + '下面是保留的历史路线')
    one_replace('docs/proofs/hn_unified_framework.md', '下面保留旧框架', ADDITIONS['docs/proofs/hn_unified_framework.md'] + '下面保留旧框架')
    p=Path('references/OPENAI_158_AUDIT.md');p.write_text(p.read_text()+ADDITIONS[str(p)])


def main():
    if not __debug__:
        raise RuntimeError('Optimization not permitted')
    if sys.argv[1:] == ['--apply-only']:
        apply()
        print('REVIEWED_EDITS_APPLIED_LOCALLY')
        return
    require(os.environ.get('GITHUB_REPOSITORY')==REPO, 'wrong repository')
    require(os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH, 'wrong branch')
    source=os.environ['GITHUB_SHA']
    apply()
    for p in REMOVE:
        require(Path(p).is_file(), 'missing cleanup path: '+p)
        Path(p).unlink()
    inherited=git('ls-tree','-r','--name-only',BASE,'research','certificates').splitlines()
    for p in inherited:
        old=subprocess.check_output(['git','show',BASE+':'+p])
        require(Path(p).read_bytes()==old,'inherited scientific content changed: '+p)
    plan=subprocess.check_output(['make','-n','check'],text=True).splitlines()
    require(len(plan)==72 and len(set(plan))==72,'unexpected full check plan')
    out=Path('certificates/radical_template_replay');out.mkdir()
    commands=[(['make','check-radical-transfer'],0),
              (['python3','-S','research/audit_openai_158_sources.py',str(Path(os.environ['RUNNER_TEMP'])/'upstream/family158-source.zip')],0),
              (['python3','-O','-S','research/verify_radical_template_mechanism.py'],1),
              (['python3','-S','research/check_integration.py'],0)]
    records=[]
    for i,(command,expected) in enumerate(commands):
        r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
        (out/f'{i}.log').write_bytes(r.stdout)
        require(r.returncode==expected,'check returned unexpected exit: '+str(command))
        if expected:
            require(b'Finite mechanism checks require non-optimized Python' in r.stdout,'wrong optimized failure')
        records.append(dict(command=command,returncode=r.returncode,expected_returncode=expected,log_sha256=sha(r.stdout)))
    relevant=list(BEFORE)+[
        'docs/proofs/algebraic_subfield_haar_transfer.md','docs/proofs/radical_plane_colorability.md',
        'docs/proofs/radical_finite_template_transfer.md','docs/proofs/finitely_generated_rotation_rigidity_obstruction.md',
        'research/verify_radical_transfer_calibration.py','research/audit_openai_158_sources.py',
        'research/verify_radical_template_mechanism.py']
    report=dict(schema='hn-radical-template-closeout-v1',status='PASS_SCOPED_CHECKS',date='2026-10-07',
                tested_parent=source,run_id=os.environ['GITHUB_RUN_ID'],base_commit=BASE,
                files={p:sha(Path(p).read_bytes()) for p in relevant},commands=records,
                inherited_scientific_files_unchanged=len(inherited),full_make_plan_commands=len(plan),full_make_check_rerun=False,
                original_lean_run='37573206401',new_results_lean_formalized=False,
                exact_plane_chromatic_number_determined=False,explicit_non5_graph_produced=False,
                full15_determined=False,removed_completed_workflows=REMOVE,
                scope='Written proofs R158-H/T/S/N/C/F with specified external analytic inputs. Fresh finite mechanism/source/static checks only. Standard Lean replay of external no-five result retained from earlier completed run. No claim of a complete new formalization or all 72-command replay.')
    receipt=Path('certificates/radical_template_validation.json')
    receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    r=subprocess.run(['python3','-S','research/check_integration.py'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    (out/'4-final-static.log').write_bytes(r.stdout);require(r.returncode==0,'final static audit')
    report['final_static_audit']=json.loads(r.stdout)
    report['final_static_log_sha256']=sha(r.stdout)
    receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    subprocess.run(['git','diff','--check'],check=True)
    allowed=set(BEFORE)|set(REMOVE)|{str(receipt)}|{str(p) for p in out.glob('*.log')}
    changed=set(git('diff','--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    require(changed==allowed, 'unexpected paths: '+str(changed^allowed))
    subprocess.run(['git','add','-A','--',*sorted(allowed)],check=True)
    subprocess.run(['git','commit','-m','research: complete finite-template transfer and finite-generation obstruction with scoped replay'],check=True)
    require(git('ls-remote','origin','refs/heads/'+BRANCH).split()[0]==source, 'branch moved before publication')
    auth=base64.b64encode(('x-access-token:'+os.environ['GH_TOKEN']).encode()).decode()
    env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+auth)
    subprocess.run(['git','push','--porcelain','origin','HEAD:refs/heads/'+BRANCH],check=True,env=env)
    final=Path(os.environ['RUNNER_TEMP'])/'final';final.mkdir()
    subprocess.run(['git','branch','audit-export','HEAD'],check=True)
    subprocess.run(['git','bundle','create',str(final/'source.bundle'),'audit-export','--tags'],check=True)
    subprocess.run(['git','archive','--format=zip','HEAD','-o',str(final/'source.zip')],check=True)
    (final/'publication.json').write_text(json.dumps(dict(status='PUBLISHED_TO_RESEARCH_BRANCH',commit=git('rev-parse','HEAD'),tree=git('rev-parse','HEAD^{tree}')),indent=2)+'\n')
    print('PUBLISHED',git('rev-parse','HEAD'))


if __name__=='__main__':
    main()
