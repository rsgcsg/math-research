# Hadwiger–Nelson research

## 最终验收与停止（2026-09-30 16:10 UTC）

研究源冻结于 `73ebe849758f36544ccd6a378b31f7383b0b7ac0`，tree `3d2bb2058d46981b62fd5b40e83a27dbe8fe1d16`。本轮已完成并停止；下文历史待办仅记录当时状态，不再自动执行。

完整 `make check` 在最后阶段中断，没有总退出码。保留其成功前缀后，在同一精确源树重跑中断目标及剩余目标，退出码0；独立比对覆盖 Makefile 中全部55条不同Python命令。验收结论为**完整目标覆盖通过（中断后续跑）**，不是一次连续 `make check` 成功。完整日志、哈希、覆盖范围与两项运行元数据差异见[验收收据](certificates/research_checkpoint_73ebe84_validation.json)。本次归档只修改文档和证据，不修改研究程序或数学结果。

原始任意支持full15与普通Hadwiger–Nelson问题仍未解决，本轮没有新平面色数界。

目标：决定普通欧氏平面的单位距离色数。**尚未改变5≤χ(R²)≤7。**
[当前状态](docs/CURRENT.md) · [结果账本](docs/RESULTS.md) · [路线](docs/ROUTES.md) ·
[统一框架](docs/proofs/hn_unified_framework.md) · [文献地图](references/LITERATURE_MAP.md)。

## 本轮收尾（2026-09-30）

研究已收束到有限证据与范围边界：局部共同律、p=0面的支持无关排除、九点精确五边形、受限奇圈全长度上限，以及Q耦合和隐变量消去校准。**原full15与普通HN仍未解决。** 最后冻结组合树完成全仓验收并归档后停止，不自动展开新方向。

[最新状态与验证范围](docs/CURRENT.md) · [隐变量消去校准](docs/proofs/hidden_pair_elimination.md) · [Q/P/R审核](docs/proofs/q_pr_coupling_audit.md)。

## 2026-09-30：全长度奇圈族的有限结构证书

T159已把逐节点只使用实际P/R信息的BW边／奇圈体系处理到所有长度：它恰好只给三条既有上界，不能缩小九点可行五边形。证明用星形和二部结构，把无限长度问题压缩为完整的有限禁形检查；不是一次搜索超时或短圈抽样。[证明](docs/proofs/bw_pr_odd_cycle_ceiling.md) · [收据](certificates/bw_pr_odd_cycle_ceiling.json)。原full15与普通HN仍未解决。

精确c36源树完整回归已通过（3657秒，[收据](certificates/research_checkpoint_c36_validation.json)）；cccb源树随后也已完整通过（3883秒）。当前新增目标另有精确重放，不借旧树收据声称最新组合树全部通过。

## 2026-09-30：完整局部投影与整数覆盖缺口

T158将固定九点的P/R可行区域完整决定为五边形，五个顶点都有精确概率证书，1/27是该模型的尖锐下界。原Y中整个P/R匹配窗口族也不能缩小它。C028用循环区间矩给出一个成熟不等式的完整正反校准族：分数覆盖可行，真正划分还受整除约束。**这些都不是full15或HN的解。**

[九点精确投影](docs/proofs/nine_point_pr_polygon.md) · [完整匹配族上限](docs/proofs/pr_matching_window_ceiling.md) · [循环区间与颜色耦合](docs/proofs/cyclic_interval_kernel_gap.md)。重放：`make check-pr-local-projection check-cyclic-interval-kernel`。源树c36的完整验收随后已通过；cccb仍独立重放，本轮新增目标不由旧树收据覆盖。

## 2026-09-30：从局部正律提取真正的耦合限制

T155的2638条成对行有单原子律；T156进一步给出与50条四端口行同时相容的39原子精确律。随后T157证明：原15运动中的另一成对分量迫使同色概率p≥1/27，从而支持无关地排除整个p=0构造面。**full15完整律仍未解决；没有HN新界。**

[局部共同律](docs/proofs/g14_pair_port4_common_law.md) · [30行面排除证书](docs/proofs/g14_pr_transport_bound.md) · [理论脉络](docs/proofs/full15_joint_event_theory.md) · [C027匹配奇集反例](docs/proofs/matching_partition_family.md) · [算术方向／色数边界](docs/proofs/arithmetic_direction_and_coloring_boundaries.md)。

## 2026-09-30：恢复已有分支证据

选择性恢复并独立重放 `research/mixed-motion-20260929` 已有结果，没有新编号，也没有改变普通HN的 `5≤χ(R²)≤7` 界或full15任意支持未决状态：原Y全部二端口关系已饱和；`Y+Z+Zω` 有完整的五色证书；64点有理 `Q₆` 说明抽象图部分同构不能替代真实几何；更大的混合宿主仍为 UNKNOWN。
[二端口证明](docs/proofs/Y_two_terminal_completion.md) · [平移宿主证明](docs/proofs/triangular_lattice_saturation.md) · [对称性边界](docs/proofs/geometric_versus_graph_symmetry.md) · [恢复记录](docs/BRANCHES.md)。
`make check-lattice-ports` 将这些独立检查接入全仓检查；未把一次性自更新工作流并入主线。

## 2026-09-30：有界新定理与验证范围

T152给出任意有限维奇分母有理诱导 $Q_d$ 平面实现；T153用T028/F11陪集表排除 $K^2$ 内距离2或 $1/\sqrt3$ 端口强制；C026在实际Y上使G14的32事件OR恰由 $(a_2,i_4)$ 单触发。T154另给出指定四端口事件行的精确47原子律，但不平衡任何原15完整域。它们都不改变普通 $5\le\chi(\mathbb R^2)\le7$ 界或全15域任意支持未决状态。

完整 `make check` 已在精确发布基线 `1bf57231b05730364372136c065e4f25bf3fdbef` / tree `0ecb82cd627823b3b25ef7be0206a0f775a79786` 通过（Python 3.12.14，3309秒，见[收据与日志](certificates/mixed_motion_integrated_validation_20260930.json)）。随后精确发布树 `9cca7e48b8ae270797dc1838457279cbc0396960` 也完整通过（3361秒，[收据](certificates/research_checkpoint_9cca_validation.json)）。新加入T155–T157/C027的目标已分别核验；它们不由9cca的旧树收据覆盖，新增组合树的完整检查另行进行。


## 2026-09-29 第二轮：从七重几何得到无限宿主定理

- **T150：** Haugland的整个84方向加法宿主**恰四色**，原表六种标号均已全局延拓。
  赋值＋CM/Kronecker证明其全部实际单位方向恰是这84个，不是假定没有隐藏跨边。
  下界由21点核的完整三色排除树独立验证。
- 继续扩到`L_m=Σr^j O`，完整方向恰有`42(m+1)`个。第二层的模2商
  **T151严格至少六色**，关闭该商的所有五色公式；这不是实际单位图或平面的六色下界。
- 随后实际检查729点的另一剩余域目标，五/六色查询仍UNKNOWN，没有新全域上界。
  第二层7939点的实际单位图也已独立重建，五色查询UNKNOWN，不构成下界。
  full15任意支持问题仍未决；错误的跨运动同步乘积推论已剔除。

[完整证明与执行结果](docs/proofs/heptagon_cm_module.md) ·
[六份全局公式](certificates/heptagon_table_extensions.json)。
**这是严格的局部研究进展，不是原始HN突破。**

## 2026-09-29：远端归并、完整三原子排除与方法边界

- 原Y的**全部15个完整域不存在至多三原子共同律**，允许任意实权重。
  六种完备情形已有独立重建、RUP反证；不是把求解器UNSAT直接当定理。
- 一般尖锐质量界：无三原子律时，任意三个完整划分至多占9/10。
  另给真实平面构造，说明五色η正规形不能直接推广到六色。
- 继续证明：连通实际χ5单位图仍不能用统一固定阶边际识别任意支持划分律；
  [核心接树的奇偶构造](docs/proofs/connected_partition_marginal_ceiling.md)明确保留其非结论。
- **这些都不是原问题突破。** 任意支持的共同律仍未知；主攻转向跨支持的全词严格势，
  不把m=4、5、6的枚举自动当作下一研究路线。

[完整反证](docs/proofs/full15_three_atom_exclusion.md) · [9/10定理](docs/proofs/three_atom_mass_gap.md) ·
[五/六色正规形区别](docs/proofs/anchored_palette_threshold.md) ·
[本轮结构重审](docs/proofs/research_reassessment_20260929.md)。

已有S子系统仍最少三原子；其正律只通过原15域中的7个。
T138的整个同中心双自由旋转宿主仍恰五色。
9月29日初次分支审计时，三角格/混合运动文稿缺少所引用证据；9月30日恢复并独立重放，范围与非结论见[分支审计](docs/BRANCHES.md)。

```sh
source .venv/bin/activate  # make setup可准备环境；全仓检查要求Python≥3.10，CI固定3.13.5
make check-full15-support
make check-eta-support
make check-heptagon-module
make check
```

独立检查仅需Python标准库；搜索另用固定研究依赖。先读[AGENTS.md](AGENTS.md)。
真实有限NON5需要精确单位边与完整不可五染证据；全平面六色上界需要全配置量词。
UNKNOWN、固定词库/周期失败、缺证书的文稿和漂亮新几何都不代替这些义务。
