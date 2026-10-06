# W22 当前已知支持上的 2-partition facets 精确天花板

2026-10-06（Australia/Brisbane）。本页接续 E121 的 q-chorded W22 审计，继续寻找能解释 C030“分数颜色类覆盖可行 / proper 五块划分不可行”缺口的 clique-partitioning facet。**没有 full15 终局，也没有普通 Hadwiger–Nelson 新界。**

## 1. 目标与范围

经典 2-partition inequality 对不交非空点集 A,B 为

    x(A:B) - x(E(A)) - x(E(B)) <= min(|A|,|B|).

在完整图情形，|A| != |B| 时是标准 facet 家族。仍只使用 q_joint_boundary_gap.json 已认证的120个 W22 点对：47个P、11个Q、31个R、31个E。C030 乘270后的矩权重为 P=10,Q=189,R=140,E=0。

要无猜测评价一条 2-partition inequality，A union B 内每一对点都必须是已认证点对，所以 A union B 必须是已知支持图的 clique。检查器递归枚举全部 clique，而不是只检查七个 K7。

## 2. 完整精确审计

| clique大小 | 个数 |
|---:|---:|
|2|120|
|3|277|
|4|323|
|5|199|
|6|61|
|7|7|

对每个 clique 枚举所有非平凡二分并商去 A/B 交换，共得到 8529 条当前支持上可完整评价的 2-partition inequalities；其中 6830 条满足 |A| != |B| 的 facet 大小条件。

C030 **不违反任何一条**。分层最小余量（乘270）如下：

| support / split | 条数 | 最小余量×270 |
|---|---:|---:|
|2 / 1+1|120|81|
|3 / 1+2|831|0|
|4 / 1+3|1292|91|
|4 / 2+2|969|211|
|5 / 1+4|995|130|
|5 / 2+3|1990|211|
|6 / 1+5|366|180|
|6 / 2+4|915|230|
|6 / 3+3|610|330|
|7 / 1+6|49|470|
|7 / 2+5|147|400|
|7 / 3+4|245|330|

8529 条中恰一条取等：C={229,305,4641}，A={229,305}，B={4641}。它正是 T165 已用的实际 PRR 三角；等式就是 2*(14/27)-1/27=1。

因此整个当前可评价的 2-partition 家族没有给出独立于 PRR transitivity 的新紧约束。

## 3. 方法结论

> 在当前120条已认证 W22 点对能完整承载的全部 clique 上，整个 2-partition inequality 家族都无法分离 C030；唯一紧式已经就是 T165 的 PRR 三角约束。

结合 E121 已证明的小 q-chorded facets 全部有正余量以及已知支持没有 K8，这进一步把 C030 的来源压缩到真正的多窗口共同划分同步，而不是单一局部 clique facet。

下一步应直接抽象七个 saturated K7 的零缺陷结构：每个窗口都必须恰为两个 doubleton 加三个 singleton，并要求重叠窗口的 doubleton 选择来自同一个全局等价关系。目标是从这个 matching-synchronization CSP 导出小系数解析不等式，替代 T165 当前89项大整数 separator。

## 4. 重放

    python3 -S research/verify_two_partition_w22_audit.py

冻结证书：certificates/two_partition_w22_audit.json。检查器只用标准库，重新构建标签、全部 clique 与全部二分，不调用 LP、SAT 或浮点优化器。
