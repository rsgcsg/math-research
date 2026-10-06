# T166 / E120：generalized partition facets 的结构上限与七点精确审核

2026-10-06。研究在 2026-09-30 的冻结验收后按用户要求重新开启。本页只处理
clique-partitioning polytope 的两个高阶不等式族及其在当前 P/R 局部模型中的作用。
**原始 full15 任意支持共同律仍未解决，普通 Hadwiger–Nelson 仍为
\(5\le \chi(\mathbb R^2)\le 7\)。**

外部输入是 Letchford–Sørensen, *New Facets of the Clique Partitioning Polytope*,
Operations Research Letters 59 (2025), 107242,
[DOI](https://doi.org/10.1016/j.orl.2025.107242)。本文只使用其中 GOW 与
G2COC 不等式的有效性；不把外部 facet 定理改记为本仓库原创结果。

## 1. 两个不等式族

对一个划分，令 \(x_{uv}=1\) 表示 \(u,v\) 在同一块，否则为 0。对互不相交、
非空的 \(H,S_1,\ldots,S_c\)，当 \(c\ge3\) 为奇数、\(f=\lfloor c/2\rfloor\)
时，generalised odd wheel (GOW) 为

\[
 \sum_i x(E(H:S_i))
 -f x(E(H))
 -\sum_i x(E(S_i))
 -\sum_i x(E(S_i:S_{i+1}))
 \le |H|f .
\]

对互不相交、非空的 \(S_1,\ldots,S_c\)，\(c\ge5\)，且
\(N=\sum_i|S_i|\) 为奇数，generalised 2-chorded odd cycle (G2COC) 为

\[
 \sum_i x(E(S_i:S_{i+1}))
 -\sum_i x(E(S_i))
 -\sum_i x(E(S_i:S_{i+2}))
 \le \lfloor N/2\rfloor .
\]

下标循环取模 \(c\)。注意 G2COC **不要求 \(c\) 为奇数**；因此七点审核必须包含
\(c=6,N=7\)，不能只扫 5、7 圈。

## 2. T166：GOW 不会越过单颜色独立集矩放松

### 定理

设随机集合 \(A\subseteq V\) 满足每点 \(\Pr(v\in A)=1/k\)，并令

\[
Q_{uv}=k\Pr(u,v\in A).
\]

则 \(Q\) 满足所有 GOW 不等式。特别地，当 \(A\) 是某图的随机独立集时，
**任意 equimarginal single-independent-set moment 都自动满足 GOW**。

这正是 C028 中已经校准过、但严格大于真实随机完整划分矩的放松。因此 GOW
不能单独修复 C028 暴露的“多个颜色类必须互斥且完整覆盖”的缺口。

### 证明

固定一份实现 \(A\)。写 \(h=|A\cap H|\)。

若 \(h=0\)，GOW 左端中所有 \(H:S_i\) 正项均为零，其余出现的
\(A\)-内边只带非正系数，所以该实现的二次贡献不超过 0。

设 \(h>0\)。取缩小后的 hub \(H'=A\cap H\)。对每个 \(i\)，若
\(A\cap S_i\ne\varnothing\)，令 \(S'_i=A\cap S_i\)；若为空，则加入一个全新的
dummy 单点作为 \(S'_i\)。现在 \(H',S'_1,\ldots,S'_c\) 都非空，可以使用外部
已证的 GOW 有效性。

构造一个划分：把所有真实的 \(A\)-点放入同一块；每个 dummy 各自为单点块。
dummy 不产生任何同块边，因此这个缩小实例的 GOW 左端恰好等于原实例中

\[
\sum_{u<v}a_{uv}1_A(u)1_A(v),
\]

而右端为 \(hf\)。故逐实现都有

\[
 \sum_{u<v}a_{uv}1_A(u)1_A(v)\le hf .
\]

取期望并乘 \(k\)，再用 \(k\mathbb E h=|H|\)，得到

\[
 \sum_{u<v}a_{uv}Q_{uv}\le |H|f.
\]

即所求。这里没有独立性、几何或有限支持假设；只用了等边际
\(\Pr(v\in A)=1/k\)。证毕。

### 对当前路线的含义

C028 已给出 single-independent-set moment 可行但真实划分矩不可行的完整族。
T166 说明：**继续全局搜索 GOW，希望仅靠它跨过这个缺口，是结构上不可能的。**
GOW 仍可作为别的放松中的有效切面，但不再作为当前 P/R 单集矩障碍的候选突破口。

G2COC 不同：普通 2-chorded odd cycle 已能切掉 C028 的某些单集矩，因此
T166 不排除 G2COC；它需要单独审核。

## 3. E120：T157 七点核上的完整 GOW / G2COC 枚举

T157 的局部七点为

\[
(4641,877,887,3483,5535,7479,7489).
\]

certificates/g14_pr_transport_bound.json 已精确认证这七点全部 21 个点对：
12 个 P、3 个 R、6 个真实单位边。对 proper 五色划分，单位边同色概率为 0；
P、R 同色概率分别记作 \(p,r\)。

T158 随后证明相应完整局部 P/R 投影恰为五边形，其五个顶点是

\[
(1/27,14/27),\ (1/6,0),\ (1/3,0),\
(1/3,1/3),\ (1/5,3/5).
\]

所以任何投影后的线性不等式，只需在这五个有理顶点上检查即可。

### 3.1 GOW：七点内全部可能实例

枚举允许顶点不参加不等式，要求 \(H,S_0,\ldots,S_{c-1}\) 全非空；
循环侧集合只按整体旋转去重，不按反射去重。

| c | 规范化实例数 | 不同 P/R 投影行 | 五边形最小余量 | 紧投影 |
|---|---:|---:|---:|---|
| 3 | 8400 | 70 | 0 | \(2p+r\le1,\ 3p\le1\)，以及它们的整数倍 |
| 5 | 4032 | 49 | 1/3 | 无 |

总计 12,432 个 GOW 实例，没有一条缩小 T158 五边形。这个局部结果与 T166
一致，但二者逻辑不同：T166 是一般放松定理；E120 是固定真实七点核的完整枚举。

### 3.2 G2COC：七点内全部可能实例

因为总点数至多 7 且 \(N\) 必须为奇数，全部可能参数只有
\((c,N)=(5,5),(5,7),(6,7),(7,7)\)。同样只商掉循环标签整体旋转。

| (c,N) | 规范化实例数 | 不同完整 P/R/unit 行 | 不同 P/R 投影行 | 最小余量 | 达到最小余量的一行 |
|---|---:|---:|---:|---:|---|
| (5,5) | 504 | 18 | 18 | 2/3 | \(4p-2r-2u\le2\)，在 \(u=0\) 时最大 4/3 |
| (5,7) | 3360 | 33 | 21 | 4/5 | \(2p+3r-6u\le3\)，最大 11/5 |
| (6,7) | 2520 | 34 | 34 | 4/5 | \(2p+3r-6u\le3\)，最大 11/5 |
| (7,7) | 720 | 24 | 24 | 1 | \(p+3r-4u\le3\)，最大 2 |

这里 \(u\) 是真实单位边的同色概率，proper 划分中 \(u=0\)。
总计 7,104 个 G2COC 实例，仍没有一条切入当前精确五边形。

## 4. 精确重放与范围

research/verify_generalized_partition_facets.py 不调用 LP、SAT 或浮点数。
它先核验 T157 证书自身 SHA256，再检查七点完整 K7 的 21 个标签，
随后用 fractions.Fraction 穷举上述所有 GOW/G2COC 分组并对 T158 五个顶点
逐一计算余量。收据是 certificates/generalized_partition_facet_audit.json。

复核：

~~~sh
python3 -S research/verify_generalized_partition_facets.py
# 或
make check-generalized-partition-facets
~~~

有限枚举只承担 E120；T166 的一般结论由第 2 节证明承担。

## 5. 下一步边界

本轮因此收掉两个看似自然但范围不同的候选：

1. **GOW 全局路线退休**：T166 证明它无法越过 single-independent-set moment
   放松，不值得继续在 Y 上机械扫更大的 GOW。
2. **G2COC 的 T157 七点核退休**：E120 已完整检查所有能塞入该核的分组。

G2COC 在更大的真实 Y 上仍完全开放，尤其是多个非空集合形成
\(\alpha\ge3\) 的 grouped window、且所有非零系数点对能够通过已认证运动分量
组合成合法 full15 行张成时。下一次搜索必须同时保留这两个条件；
只找到一个抽象划分 facet、却不能把系数运输回 15 个真实运动域，不构成 full15 进展。

这次没有 full15 正律、全词严格势、有限 NON5 或新的平面色数界。
