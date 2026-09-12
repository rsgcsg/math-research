# Hadwiger–Nelson research

目标：解决原始 Hadwiger–Nelson，或证明足以决定它的结构定理。
**普通上下界仍为 5≤χ(R²)≤7；原问题尚未突破，研究目标未完成。**
本轮已收口，按用户要求停止自主研究。

[当前研究状态](docs/CURRENT.md) · [统一框架](docs/proofs/hn_unified_framework.md) ·
[路线与淘汰理由](docs/ROUTES.md) · [T/C/E/Q账本](docs/RESULTS.md) ·
[经典及最新文献地图](references/LITERATURE_MAP.md)

2026-09-12 本轮真正新增：

- [完整 joint](docs/proofs/quintic_multiword_joint.md)：10077 点实际图上，五个自由色词共同满足 14 个完整最大域及全部旧有限义务。Q009 已正解决；随后发现的旧律反例也被新律修复。
- [有限支持与小事件](docs/proofs/finite_joint_support.md)：固定有限 joint 可行当且仅当某个有限等权多词模型可行；两份各至多五原子的不同划分律可由源、像各至多六点区分。没有全 proper 空间的统一六点完备性。
- [算术宿主](docs/proofs/dyadic_integral_host.md)：整个最大 2 整环 R₂ 恰四色；Parts509 经精确旋转后最低分母深度是半层，而非原坐标的四分之一层。
- [全有限精度天花板](docs/proofs/dyadic_finite_precision_ceiling.md)：Aₙ=2⁻ⁿR₂ 的任何有限 2-进精度染色至少需 6n+4 色；逐个真实方向均可提升，因此不是伪边造成。它排除编码，不提高实际图下界。
- [证据复杂度与逻辑](docs/proofs/hn_effective_witnesses.md)：有限下界证据与无限上界的量词不同；固定点数有可计算代数证据界，但尚无最小 non-5 见证规模界或独立性结论。

最后已实际换线到 [E084新旋转回入](docs/proofs/dyadic_mixed_joint.md)：
29点与33点完整域的旧律失配获独立认证；加入第15域的五词查询为
UNKNOWN，第16域未执行。没有新正律或全词反证，不追加预算。

仅作续研记录：真正跨层的完整五色关系、二维整数闭环／Gram 构造、
全局 ≤6 共尾机制。它们仍未闭合，当前不继续启动。
**固定模型失败、SAT UNKNOWN、局部正例、数值迹象都不是 HN 突破。**

```text
references/      原始来源、文献地图、未经重放的历史输入
docs/            canonical 状态、依赖、结果账本、完整证明
research/        精确数学程序；搜索与独立检查分离
certificates/    可独立重放见证和来源绑定
```

基本检查只需 Python 3 标准库：`make check`。
重跑 SAT／符号代数搜索用本地环境：`make setup`、`make explore`。
证据规则见 [AGENTS.md](AGENTS.md)。本地研究不自动包含 GitHub 发布。
