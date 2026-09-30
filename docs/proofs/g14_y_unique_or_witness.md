# G14 虚拟距离 OR 在实际全 Y 上的单触发见证

**C026。** 在仓库中的真实诱导单位图 $Y$ 上，存在一份 proper 五色染色，使 G14 的 32 个非单位距离事件里恰好一个同色：$a_2,i_4$，距离为 $2$。因此 G14 的全 32 事件 OR 下界在 $Y$ 上是尖锐的，并且任何省略 $(a_2,i_4)$ 的事件子集 OR 都有反例。仍不能据此判定包含该事件的其它子集。

## 来源与原命题边界

HeliCorgi 的 [`fourteen-points-six-colors`](https://github.com/HeliCorgi/fourteen-points-six-colors)，固定于提交 [`4c84e4d67522e644faef704694cd5ba7fc273abc`](https://github.com/HeliCorgi/fourteen-points-six-colors/commit/4c84e4d67522e644faef704694cd5ba7fc273abc)，`proofs/PROOF_G14.md` 给出 14 点图：两点在且仅在距离属于 $D=\{1,1/\sqrt3,2\}$ 时相邻，并证明该三距离图需要六色。它不是单位距离图；本文只取它的单位边子图与 32 条其余“虚拟事件”，不把外部非单位边当作实际边。

独立转录检查器 `research/verify_g14_port_or.py` 用有理数在 $\mathbb Q(\sqrt3)$ 中重建 14 点全部 91 对，并验证距离计数为：18 对距离 $1$、27 对距离 $1/\sqrt3$、5 对距离 $2$，其余 41 对不在 $D$。它重建 G14 的 50 条三距离边，检查最大独立集大小为 3、两个不属于独立三元组的点 $i_0,a_1$ 相邻，并核验公开六色分割。于是完整 $D$ 图不可能五染。检查器也验证 14 点嵌入现有 509 点核心及 10077 点 $Y$：其 18 条单位边确为子图，14 点间没有其它实际单位边。

令 $H$ 是该 14 点集上的真实单位边子图；另外 32 对组成集合 $S$。任一 $H$ 的 proper 五染若令 $S$ 中每对均异色，就会成为 G14 的 proper 五染，与上段矛盾。故每个 $H$ 五染、进而每个 $Y$ 五染均满足

\[
\sum_{uv\in S}\mathbf 1[c(u)=c(v)]\ge1.
\]

## 全 $Y$ 的精确见证

`certificates/g14_unique_event_y_result.json` 保存一份五色词；它以字面颜色串的 SHA-256 `c64b75adedcccbf4c561221b208c91e62392433bba1cb96abab83777f4e12468` 绑定。`research/verify_g14_unique_event_y.py` 不调用 SAT 求解器，只逐条检查压缩几何证书中的 $Y$ 全部 49858 条实际单位边，并检查所有 32 个虚拟事件的端点颜色。恰有一项同色，且证书指出该对就是 $(a_2,i_4)$，距离为 2。`make check-g14-port-or` 先从精确坐标独立重建 G14 关系和嵌入证书，再直接验色词；两阶段均通过。

该结果推翻“$Y$ 上每份 proper 五染至少有两个 G14 虚拟对同色”，也推翻任一不含 $(a_2,i_4)$ 的子集 OR。它不处理包含这一触发对、但遗漏其它事件的子集；不推出 $Y$ 的自由三端口关系，不构成全15域共同律或严格势，更不是实际单位图 NON5。$D$ 中的 $1/\sqrt3$ 与 $2$ 都不是单位距离；任何把这些虚拟边换成真实单位小工具的方案还须独立构造、核验所有实际交叉边。

本地只保留一个共享压缩 Y 几何语料 [`Y_full_geometry.json.gz`](../../certificates/Y_full_geometry.json.gz) 供两支独立检查器共用，不复制大批完整五色词。保存的 SAT 查询仅作为生成线索；数学见证是无提示检查器直接验证的颜色串。来源归属、范围和依赖另见 [`SOURCES.md`](../../references/SOURCES.md)。
