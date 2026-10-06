# W22 上最小 q-chorded cycle facets 的精确天花板

2026-10-06（Australia/Brisbane）。本页接续 PR #8 的 T164–T165 / C030，
只研究一个新的、文献中已经严格定义的 clique-partitioning facet 家族。
**没有 full15 终局，也没有普通 Hadwiger–Nelson 新界。**

## 1. 为什么检查这个家族

Irmai–Naumann–Andres 在 2026 年正式发表的工作中研究任意
q-chorded k-cycle inequality：

[
 sum_{iinmathbb Z_k}
 igl(x_{i,i+1}-x_{i,i+q}igr)
 le k-lceil k/qceil,qquad 2le qle k/2.
]

他们证明：该不等式诱导 clique partitioning polytope 的 facet，当且仅当
(kequiv1pmod q)，并且若 (k=3q+1)，则还需 (q=3) 或 q 为偶数。
这把 PR #7 中只校准的 2-chorded/G2COC 方向扩展到真正新的 q>2 facet。

C030 正好给出一个 W22 上的单独立集分数覆盖，其逐事件矩为

[
 p=1/27,qquad q_0=7/10,qquad r=14/27,
]

但它不能来自 proper 五块划分律。因此最自然的问题是：这个缺口是否其实已经被
一个很小的 chorded-cycle facet 看见？

## 2. 审计范围

只使用 q_joint_boundary_gap.json 已经逐点认证的真实点对，不补猜任何未知距离。

- P：47 对，C030 值 1/27；
- Q：11 对，C030 值 7/10；
- R：31 对，C030 值 14/27；
- E：从七个已认证 saturated K7 窗口中重建的 31 条单位边，值 0。

因此当前可安全使用 120 个 W22 点对。其余点对一律视为未知，任何候选周期只要
cycle edge 或 q-chord 碰到未知点对，就不进入本结论。

按文献 facet 判据，在支持大小 k<=10 内恰需检查六类：

[
(5,2),(7,2),(9,2),(7,3),(9,4),(10,3).
]

前三类是经典 2-chorded odd cycles；后三类是真正超出旧 q=2 家族的新 facet。

## 3. 精确结果

为避免小数，统一乘 270：
P=10，Q=189，R=140，E=0。逐个规范化简单周期穷举，商去旋转和反射。
每个周期的全部 cycle pairs 与 q-chord pairs 都必须属于上面的 120 个认证点对。

| (k,q) | 完整支持周期数 | C030 最大 LHS ×270 | 合法 RHS ×270 | 余量 ×270 |
|---|---:|---:|---:|---:|
| (5,2) | 2,388 | 280 | 540 | 260 |
| (7,2) | 26,181 | 430 | 810 | 380 |
| (9,2) | 295,740 | 609 | 1,080 | 471 |
| (7,3) | 26,181 | 658 | 1,080 | 422 |
| (9,4) | 295,740 | 987 | 1,620 | 633 |
| (10,3) | 243,888 | 997 | 1,620 | 623 |

所以六类全部有严格正余量。尤其最接近的新 q>2 facet 也远没有切到 C030。

这给出一个明确的方法结论：

> **C030 的“分数颜色类覆盖可行 / 完整五块划分不可行”缺口，不是由 W22 当前
> 已认证点对支持上的最小 q-chorded cycle facets 解释的。**

这比“没有搜到小切面”更强：在规定的真实支持和规定的六个 facet 家族中已经穷尽。

## 4. 一个结构信号

最好的 (10,3) 周期为

[
(31,227,5535,231,33,7479,4641,229,877,889).
]

其 cycle 类型为

[
(P,Q,R,P,Q,P,R,P,R,Q),
]

而 3-chord 类型为

[
(E,E,E,E,P,E,E,P,E,P).
]

这已经是非常有利于 C030 的形状：正项里塞入三个高值 Q，而负项大量落在零值单位边。
即使如此，它的值仍只有 997/270 < 6。也就是说，小 chorded-cycle 路线失败并非只是
因为周期没碰到 Q；而是现有 W22 支持中，想把足够多 Q 同时放在正 cycle 上且把
q-chords 压到 E/P，会很快受到实际点对兼容结构限制。

## 5. 重放与边界

精确检查器：

    python3 -S research/verify_q_chorded_w22_audit.py

冻结结果：

    certificates/q_chorded_w22_audit.json

检查器只读继承的 q_joint_boundary_gap.json，自行重建 P/Q/R 与 saturated-window
单位边，然后重新穷举六类周期并逐项比较冻结证书。它不调用 LP、SAT、浮点优化器。

本结论**不**覆盖：
- k>=11 的 q-chorded cycle facets；
- set-valued/generalized chorded-cycle 家族；
- W22 中尚未认证类型的点对；
- full Y 或 full15；
- Hadwiger–Nelson 色数本身。

## 6. 下一步

最合理的升级不是继续枚举同一批小周期，而是利用本轮暴露的兼容性瓶颈：

1. 先扩充能被实际运动分量认证的 W22/W更大点对，让较大 q-chorded 支持不再因为
   未知点对而被迫丢弃；
2. 优先搜索能同时承载更多 Q 正项、而 q-chords 落在 E/P 的 k>=11 facet；
3. 如果这仍失败，则把 C030 的七窗口零缺陷条件本身抽象成“多窗口耦合 facet”，
   因为现有 T165 分离式明显使用了多个窗口之间的共同划分一致性，而不是单一周期结构。
