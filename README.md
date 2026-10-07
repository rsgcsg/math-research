# Hadwiger–Nelson research

目标：决定普通欧氏平面的单位距离色数。**2026-10-06公开的OpenAI Family158给出6≤χ(R²)≤7；本项目已重放其Lean无五染目标。答案6或7、显式有限NON5证书及任意支持full15仍未由本项目解决。**

[当前成果与真实瓶颈](docs/CURRENT.md) · [结果账本](docs/RESULTS.md) · [编号映射](docs/ID_ALIASES.md) ·
[统一证明框架](docs/proofs/hn_unified_framework.md) · [路线与淘汰理由](docs/ROUTES.md) ·
[分支、来源与恢复](docs/BRANCHES.md) · [文献地图](references/LITERATURE_MAP.md)。

## 2026-10-07：外部无五染定理核验与可解坐标推广

[Family158来源和实际Lean重放](references/OPENAI_158_AUDIT.md) · [可解代数坐标主结果](docs/proofs/radical_plane_colorability.md) · [完整子域转移论证](docs/proofs/algebraic_subfield_haar_transfer.md)。

本轮书面证明：正平方根闭合且单位旋转可除的代数子域，对其中任意距离集具有与全平面相同的有限染色能力。最大可解代数扩张的实部满足这些条件，却不是所有有限单位图的同态普适宿主。新推广尚未形式化；其有限算术校准与上游Lean重放分开记录。

[有限二点模板转移](docs/proofs/radical_finite_template_transfer.md)进一步保留多重染色与有理循环模板；
[有限生成旋转反例](docs/proofs/finitely_generated_rotation_rigidity_obstruction.md)说明稠密旋转不足以推出全域谱刚性。

`make check-radical-transfer`重放有限代数、标签支持与谱样本校准，不认证无限分析证明。旧数据、定理编号和UNKNOWN不因外部结果改写。

## 2026-10-07续篇：完成的扩展与准确方法边界

[紧目标与固定维数量子模板](docs/proofs/compact_target_radical_transfer.md) ·
[二维投影的精确普通化与奇圈误差](docs/proofs/qubit_coloring_rounding.md) ·
[任意阶混合但整域不可分辨的谱反例](docs/proofs/mixing_spectral_camouflage.md)。

新紧目标转移依赖前轮R158-C；二维投影取整和谱反例另有独立证明。
奇圈二标签的最小乘积Frobenius误差恰为sin(π/(2m))，不是数值估计。
原始6/7、显式有限NON5及任意支持full15仍未解决；不把扩展问题的完成混同为原问题完成。
`make check-compact-mixing`执行新增精确有限校准；无限结论未Lean形式化。

## 历史统一基线（2026-10-06快照）

PR #11已把可读取的本地成果和远端研究分支归入main。远端只保留main；
11个研究分支和1个维护分支已按原SHA归档，连同更早归档及4个本地检查点，共保留28个标签。
原提交是真实Git祖先或明确归档，不只复制文件；旧失败与UNKNOWN不因整合改写。

统一账本为T001–T169、E001–E124、C001–C032、Q001–Q011。编号是证据索引，不是169次原问题突破。
T141–143已恢复；广义奇轮旧T160现T166，18边模型最优13现T167，完整34边最优12仍T162。
九Q计数包络为T168；独立整数平移证据为T169。完整对应关系见编号映射。

同一冻结源码的70条不同Python检查已在8个隔离工作树全部通过，原始日志永久入库；
这是完整命令覆盖，不是一次串行make check。本次收尾重新验收日志、源指纹、历史和文档，
没有重跑这70条数学检查，也没有改动研究程序或原证书。
[原始完整验收](certificates/unified_integration_validation.json) · [本次收尾复核](certificates/unified_closeout_validation.json)。

```sh
make check                     # 全部已接入的独立检查，不执行新研究搜索
make check-integration         # 编号、JSON、Python语法及本地文件引用
make check-packet check-cycle-descent
make check-q-joint-boundary-gap check-two-partition-w22-audit
```

仅保留手动、只读的verify.yml；一次性导入、封存、归档工作流均已移除。
未完成的边界端点实验和已纠正旧稿在references/unverified内单独保存，不冒充有效证书。
请先读[AGENTS.md](AGENTS.md)。搜索器和独立检查器分开；一般证明不因程序PASS就被称为形式化或同行评审完成。

本轮[奇次纯根式显式二染校准](docs/proofs/odd_radical_plane_two_coloring.md)把新逃逸旋转放回已知低色数宿主，
不重复计算Moorhouse的既有二色结论。全仓尝试在300秒预算处中断，专项验证范围见本轮收据。
