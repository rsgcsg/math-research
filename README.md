# Hadwiger–Nelson research

目标：解决原始 Hadwiger–Nelson，或证明足以决定它的结构定理。
**普通上下界仍为 5≤χ(R²)≤7；原问题尚未突破，研究目标未完成。**
已按用户新指令恢复自主研究；以下是研究checkpoint，不是目标完成。

[当前研究状态](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[路线与淘汰理由](docs/ROUTES.md) · [T/C/E/Q账本](docs/RESULTS.md) ·
[经典及最新文献地图](references/LITERATURE_MAP.md)

2026-09-16 恢复后的实际推进：

- [九点非CM反例](docs/proofs/cm_escape_nine.md)：9点15边、恰四色，却不能单位同态进任何CM宿主（T123/E091）。新点不改变Moser七端口颜色关系，几何逃逸不等于升色；真正non-5逃域核须有3-core及4度分支。
- [无限方向仍低色数](docs/proofs/salem_field_three_coloring.md)：Radchenko非CM四次宿主的整个数域恰χ3，包括任意分母（T124）；接着检验的六次全有限处不分歧宿主仍≤4。无限valency或消除有限分歧都不自动升色。
- [共尾量词修正](docs/proofs/unit_homomorphism_cofinality.md)：实域平方族的有限单位同态普适性恰等价于包含全部实数域的共尾性（T122）。CM族不普适，但仅保色数极值的较弱归约仍未排除。
- [固定旧表示天花板](docs/proofs/dyadic_fixed_representation.md)：旧14算子下任意重新选词均被4/5→0事件排除（E089），独立8步RUP另证；不是自由完整joint反证。
- [回入与新正词](docs/proofs/dyadic_identity_extension.md)：u²有805个返回，800个被一步链遗漏（E090）；已认证10077点Y上同时满足u29和u²805身份作用的完整五色词（E092），尚未修复旧14共同律。
- [几何扩包退休](docs/proofs/joint_package_symmetry_probe.md)：Y全欧氏对称群只有恒等（E088）；旧22模式的任意内部重染也不能闭环，E092已实际越出旧模式库。
- [单算子与颜色合并天花板](docs/proofs/dyadic_eta_release.md)：E093筛选后，E094已独立反证最后的η释放；旧表示只改一组算子的路线全部关闭。旧／新颜色对的点无关五色合并及任意非负混合也不能组合两律。

同日上一checkpoint保留：

- [有限对称补全](docs/proofs/finite_joint_completion.md)：full-joint 可行恰等价于有限可染组合对称补全（T120）；四点 P₄ 给最小二色全词 joint 反例，增加一点成为实际 C₅（C023）。补全不保证二维实现，普通 EPPA 不能代替保色数条件。
- [完整词定价与闭环](docs/proofs/dyadic_joint_column_pricing.md)：新 proper 五色词使旧分离式从 +1 降至 −1，但12词池仍被完整模式行分离（E085）。已实际尝试的指定三循环又被同一物理点对的同／异色矛盾排除（E086）；不排除其他循环或完整 joint。
- [旋转等变天花板](docs/proofs/residue29_rotation_ceiling.md)：H29 的完整旋转等变染色至少需11色（T121），只是固定表示限制；非线性 H29≤6 仍未知，有限搜索没有正构造（E087）。

没有 non-5 实际图、全局 ≤6 证明或不可判定性结果。最新范围和回归状态见
[CURRENT](docs/CURRENT.md)。以下是已提交的上一轮基础，不是本轮重复成果：

- [完整 joint](docs/proofs/quintic_multiword_joint.md)：10077 点实际图上，五个自由色词共同满足 14 个完整最大域及全部旧有限义务。Q009 已正解决；随后发现的旧律反例也被新律修复。
- [有限支持与小事件](docs/proofs/finite_joint_support.md)：固定有限 joint 可行当且仅当某个有限等权多词模型可行；两份各至多五原子的不同划分律可由源、像各至多六点区分。没有全 proper 空间的统一六点完备性。
- [算术宿主](docs/proofs/dyadic_integral_host.md)：整个最大 2 整环 R₂ 恰四色；Parts509 经精确旋转后最低分母深度是半层，而非原坐标的四分之一层。
- [全有限精度天花板](docs/proofs/dyadic_finite_precision_ceiling.md)：Aₙ=2⁻ⁿR₂ 的任何有限 2-进精度染色至少需 6n+4 色；逐个真实方向均可提升，因此不是伪边造成。它排除编码，不提高实际图下界。
- [证据复杂度与逻辑](docs/proofs/hn_effective_witnesses.md)：有限下界证据与无限上界的量词不同；固定点数有可计算代数证据界，但尚无最小 non-5 见证规模界或独立性结论。

上一轮已换线到 [E084新旋转回入](docs/proofs/dyadic_mixed_joint.md)：
29点与33点完整域的旧律失配获独立认证；加入第15域的五词查询为
UNKNOWN，第16域未执行。本轮 E085/E086 改查全词定价和指定循环，
并未修复全部15域。新E089只关闭固定旧表示，E092只解决u/u²子问题；
自由15域查询仍是历史UNKNOWN，不以重复预算代替新结构。

第一优先仍是新算子／新模式下保留旧14域的完整共同律或全词分离；
几何备线须通过真正域外临界核筛选，上界须越过T122的共尾量词。
**固定模型失败、SAT UNKNOWN、局部正例、数值迹象都不是 HN 突破。**

```text
references/      原始来源、文献地图、未经重放的历史输入
docs/            canonical 状态、依赖、结果账本、完整证明
research/        精确数学程序；搜索与独立检查分离
certificates/    可独立重放见证和来源绑定
```

基本检查只需 Python 3.10+ 标准库：`make check`。
若系统 `python3` 较旧，使用项目环境：`PATH="$PWD/.venv/bin:$PATH" make check`。
重跑 SAT／符号代数搜索用本地环境：`make setup`、`make explore`。
证据规则见 [AGENTS.md](AGENTS.md)。本地研究不自动包含 GitHub 发布。
