# OpenAI Family 158：来源、Lean 实际重放及项目转向

2026-10-07；固定上游 `openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`。
这不是对全部722份手稿的验证；只对目录作计数，对Family158作本页列明的读取与核验。

## 1. 已核实的发布事实

[官方说明](https://openai.com/index/sharing-ai-progress-in-mathematics/)发布于2026-10-06。
固定版本[CONTENTS](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/CONTENTS.md)
实际包含372个不同family标题与722条手稿PDF条目；不是722个独立定理。
平均约三小时Pro等价计算是官方对这批结果的统计，不是每篇证明完成时间的上界。

最相关的目录条目如下。除158外，本次只核对其目录陈述，没有独立重建其证明。

| Family | 目录所述主题 | 对本项目的准确关系 |
|---|---|---|
| 158 | 任意平面五染色必有同色单位对 | 直接给普通下界6；6与7仍未决定 |
| 167 | 平面单位距离边数的4/3次幂节省、距离问题 | 同一几何对象的边数问题，不直接给色数上界或下界 |
| 172 | 有限欧氏Ramsey配置分类 | 高维、任意有限染色的单色全等副本；不是固定二维五染问题 |
| 157 | Hadwiger、list coloring、minor | Hadwiger不等于Hadwiger–Nelson；抽象图还须真实单位实现 |
| 073 | Falconer距离猜想 | Hausdorff维数/距离集问题，不能直接替代普通单位染色 |

## 2. Family158的结论与证据级别

[论文](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Euclidean-plane-is-not-five-colorable-September-23-2026/paper.pdf)
题为 *The Euclidean plane is not five-colorable*，稿面日期2026-09-23，共62页。
正文明确不要求颜色类可测、连续、周期等，并明确剩余答案为6或7。
Introduction最后用紧致性推出有限不可五染图与正badness常数，且明确二者是存在性的。
本次没有从该稿获得一个带具体坐标/规模的有限六色见证。

实际形式化目标：`OAI.EuclideanFiveColor.no_proper_five_coloring`，实现位于
`lean/OAI/Geometry/PlaneColoring/Five.lean`，不是ComparatorChallenges中的占位题目。
挑战文件中的 `sorry` 是待比较的命题模板；相应JSON明确选择实际solution模块。

**本次已实际完成 Lean 重放，而不仅是读取“已形式化”声明。**
GitHub运行 `37573206401` / job `112636246661`：

- 用Lean 4.34.1、上游钉住的Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612`；
- 在最小Mathlib-only Lake包中，编译原始OAI依赖闭包的70个模块，保留原字节和 `autoImplicit=false`；
- 编译一个额外文件，将定理用于下面逐字写出的、不经别名隐藏假设的命题；
- 实际运行 `#print axioms`，输出仅 `propext, Classical.choice, Quot.sound`。

```lean
import OAI.Geometry.PlaneColoring.Five
set_option autoImplicit false
example : ¬ ∃ c : ℂ → Fin 5,
    ∀ x y : ℂ, ‖x-y‖ = 1 → c x ≠ c y := by
  simpa only [OAI.EuclideanFiveColor.ProperColoring] using
    OAI.EuclideanFiveColor.no_proper_five_coloring
#print axioms OAI.EuclideanFiveColor.no_proper_five_coloring
```

Mathlib使用标准缓存；没有重新从零构建其全部基础。
这不是官方Comparator/nanoda二次内核运行，不等于我们推广后的子域定理已经形式化。
[实际Lean收据](../certificates/openai_158_lean_replay.json)、
[原始日志包](../certificates/openai_158_lean_logs.zip)已保存，不只依赖临时Actions下载地址。

## 3. 来源保全和失败记录

首次按整个上游Git局部克隆的检索运行37571780272被取消，没有当作成功验收。
改用固定提交的有界逐文件检索，运行37572850907成功取得94个文件，
包括全部八份论文section源码、PDF、元数据与实际Five目标的OAI语法导入闭包。
全部SHA256及Git blob SHA1由本地再次重算一致。

[来源清单](../certificates/openai_158_source_audit.json)记录全部94个文件及大小和哈希。
原始源码在交付包中保留Apache-2.0许可证；工作区缓存位于ignored的references/cache/openai158，
未把上游整套库复制成我们的原创程序。复核下载包可运行：

```sh
python3 -S research/audit_openai_158_sources.py /path/to/family158-source.zip
```

这个脚本只校验字节、目录计数和文字token，不运行Lean。
其输出与上一节实际Lean编译的证据层次不同。

## 4. 与full15的关系：一项必要纠正

同一个全平面proper染色能平均为相容不变律；但给定的有限Y/15义务只保存有限信息。
全平面无五染并不逻辑蕴含这个固定系统不可行。即使它有正律，也与Family158不矛盾。
过去所有固定支持、词池、局部正律和UNKNOWN的量词都保留，不由外部大定理批量升级。
本项目T105仍可把一个合格的全词严格分离编译为有限实际NON5证据，但还缺这种分离。

Family158的谱转移适用于任意有限k；最后的几何反证则专门使用五个颜色。
例如palettes.tex的Palette cardinality证明由“三种颜色出现”推出补集只剩两色，
再用二色中心分离；六色时补集有三色，这一步不能照抄。
仅把证明或程序中的5替换成6，不会得到普通七色下界。

## 5. 本轮实际新增的书面推广

[子域Haar刚性/多距离转移](../docs/proofs/algebraic_subfield_haar_transfer.md)
把所需域性质压缩成“代数性、正平方根闭合、单位旋转群可除”。
[可解代数坐标主推论](../docs/proofs/radical_plane_colorability.md)
证明最大可解代数扩张的实部具有与整个平面相同的有限染色能力，并明确
它不具备所有有限单位图的同态普适性。这解决T122留下的一个精确的较弱共尾问题。

证据是逐条件移植的书面证明；八个单位数、70个非零子式、五次/三次模素数校准
只核验其中的有限代数，不给分析推广盖机器证明章。
尚无六染色构造、不可六染有限图、显式不可五染根式图或实用规模界。
本轮不把“所有代数数中的搜索”换成“固定有限根式层中的搜索”。

## 6. 本轮续写与实际验证范围

在上次已完成的Lean运行37573206401基础上，本轮重新读取和验收原始日志，未再编译一次该Lean目标。
恢复的草稿已逐页检查，再由运行37576935885按14个逐文件哈希发布；不是把未读blob自动认作证明。
新增[R158-C](../docs/proofs/radical_finite_template_transfer.md)补足不同颜色交叉相关的极化与反射步骤，
推广到全部有限径向二点模板；新增[R158-F](../docs/proofs/finitely_generated_rotation_rigidity_obstruction.md)
给出有限生成旋转下的显式非Haar谱，后者不依赖上游无五染定理。

最新专项检查的实际退出码与原始输出另存`certificates/radical_template_validation.json`及同目录日志。
有限测试不是新的分析形式化，也不能给没有输出的有限单位图或6/7终局盖认证章。
使用中的上游版本未被本项目修改；原论文、许可证和源哈希在单独交付中保留。
