# Hadwiger–Nelson 项目综合历史—前沿主文档 v3

**副标题：完整历史资产、证据时间轴、当前远端硬状态、历史未重放前沿、统一结构、5/6/7 三相、上下界与下一阶段技术障碍**

**版本日期：2026-09-08（Australia/Brisbane）**  
**当前只读核对远端：** `rsgcsg/math-research@d3048633a9029f9119cf844b593eaa59e0c2a4ce`  
**原始问题状态：** 未解决。公开基准仍为

\[
\boxed{5\le \chi(\mathbb R^2)\le 7}.
\]

> **文档定位**
>
> 这是一份面向“继续研究”的综合主文档，而不是论文、不是仓库规范、不是路线命令。它的目标是把此前分散在历史总账、5/6/7 统一图、当前 roadmap、R4/cross-lattice、Galois/reducibility、Parts509、post-ledger seven-orbit / pair compiler 等材料中的资产重新组织成一张**同时尊重历史脉络与当前证据等级**的地图。
>
> 与此前版本相比，本版最重要的结构修正有四个：
>
> 1. **把思想史、当前远端认证史、历史已完成但待重放史分成三条时间轴**，不再把“历史最高前沿”与“当前硬前沿”混成一层；
> 2. **补齐 T027–T031 / E015–E017**：Parts 四端口部分自由、整个 \(K=\mathbb Q(\sqrt3,\sqrt5,\sqrt{11})\) 安全域、逃域旋转、valuation depth 与单中心跨边森林是当前真正走向 Q005 的硬定理链；
> 3. **保护 post-ledger 更强资产**：six-orbit arbitrary nonuniform lists、seven-orbit 28 点/50 边 real anchored module、1280 bad boundaries、四色 activator no-go、\(J(5,2)\)/Petersen、Moser-incidence；它们不能被较弱但已远端认证的 T036 覆盖；
> 4. **重新保留 5/6/7 covering–ramification、\(J(6,2)\)、upper-side、idea bank**，避免“恢复定理资产”时把仍有研究价值的抽象一并删掉。

---

# 0. 先给最终总判断

目前整个项目最准确的状态不是“已经找到最终 proof architecture”，也不是“还在漫无目的搜索”，而是：

\[
\boxed{
\textbf{我们已经相当清楚地知道大量东西为什么不够，
也已经拥有数类真实的 extension / obstruction theorem；
真正缺口被压缩为 geometry-aware activation / joint extension。}
}
\]

换成大白话：

> 我们已经会造“有些钥匙打不开的房间”，会证明很大一类房间“任何钥匙都能打开”，会证明很多看似复杂的走廊其实永远五色，会精确知道小接口为什么传不了足够颜色信息；现在真正缺的是：**让真实二维单位距离几何把多个局部房间的钥匙绑在一起，使所有五色逃法不能同时存在。**

今天最稳定的两条前沿描述是：

### 下界侧

\[
\boxed{
\text{有限真实几何}
\to
\text{高信息 joint boundary relation}
\to
\text{activation / cyclic composition}
\to
R_5=\varnothing.
}
\]

### 上界侧

\[
\boxed{
\text{所有有限限制持续可延伸}
\to
\text{coherent inverse system / global section}
\to
\text{5 或 6 色全平面染色}.
}
\]

而当前最具体的硬前沿是：

\[
\boxed{
\textbf{Q005：逃离 }K=\mathbb Q(\sqrt3,\sqrt5,\sqrt{11})\textbf{ 安全域后，
多中心完整五色联合延伸是否仍总能修复？}
}
\]

它与历史 post-ledger 的 activation frontier 实际上是同一个问题的两个坐标系。

---

# Part I. 证据纪律：三条时间轴，而不是一条“最新状态”

## 1. 为什么必须拆成三条时间轴

本项目历史材料非常丰富，但不同成果处在不同证据层。以后任何 agent 若只读其中一份，很容易犯两种相反错误：

1. **只信当前远端**：会重复 six-orbit arbitrary lists、seven-orbit anchored bad boundary、Petersen/pair compiler 等历史已经做过的工作；
2. **只信历史最高前沿**：会忽略 T027–T031、T032–T036 已经证明的强安全域、强可约性和量词修正，从而在错误假设上继续。

所以本版统一使用三条时间轴。

---

## 2. 时间轴 A：思想史 / 路线史

它回答：

> 为什么项目一步步从“找大图”走到“boundary relation / activation / joint extension”？

这一层允许保留：

- 失败路线；
- 条件构造；
- 当时合理、后来被否定的猜想；
- 跨领域类比；
- 结构直觉。

它不是证据等级。

---

## 3. 时间轴 B：当前远端认证史

当前只读核对基线：

\[
\boxed{
d3048633a9029f9119cf844b593eaa59e0c2a4ce.
}
\]

当前 `RESULTS.md` 的硬账本到：

\[
\boxed{T001\text{--}T036,\quad C001\text{--}C004,\quad E001\text{--}E020,\quad Q001\text{--}Q005.}
\]

这里的内容应当优先用于：

- 当前 theorem dependency；
- 关闭旧路线；
- 新构造筛选；
- 当前仓库可复核事实。

---

## 4. 时间轴 C：历史已完成、但当前尚未全部恢复证书的前沿

这层尤其包括：

- flower/R4 原始 package；
- mod-5 / elliptic 旧证明包；
- finite Abelian / Galois 旧完整报告；
- six-orbit arbitrary nonuniform lists；
- seven-orbit 28 点 / 50 边 real anchored module；
- seven-orbit exact 1280 bad boundary relation；
- 四色 activator no-go；
- \(J(5,2)\)/Petersen detector；
- Moser-incidence hypergraph benchmark。

这类成果必须保留，但在远端重放前不能写成 `[REMOTE-HARD]`。

---

## 5. 统一标签

| 标签 | 含义 |
|---|---|
| **[REMOTE-HARD]** | 当前远端 theorem ledger 已正式认证 |
| **[REMOTE-COMP]** | 当前远端有 exact witness / independent verifier / replay |
| **[EXTERNAL]** | 外部公开成熟结果 |
| **[EXTERNAL-REPLAY]** | 外部结果被项目独立重建/重放 |
| **[HIST-THM]** | 历史材料给出完整数学证明，但当前远端未必重放 |
| **[HIST-COMP]** | 历史完成有限枚举/SAT/LP/geometry，原包未必恢复 |
| **[POSTLEDGER-THM]** | 旧总账之后的历史对话中进一步完成的定理 |
| **[POSTLEDGER-COMP]** | 同上，以 exact computation/certificate 为主要证据 |
| **[EXP]** | 实验观察 / UNKNOWN / 候选 |
| **[HEURISTIC]** | 结构猜想 / 类比 / 设计语言 |
| **[CLOSED]** | 已被 theorem/counterexample/saturation 明确关闭 |
| **[DEPRIORITIZED]** | 仍可能有数学价值，但当前 HN 杠杆低 |
| **[OPEN]** | 当前真实未解决 |

---

# Part II. 一页总路线：项目到底换过多少次“母问题”？

## 6. 从原问题到当前母问题

```text
原始目标：找一张不可五染有限 UDG
        │
        ▼
finite-direction / Cayley / Gram
“怎样精确表示有限欧氏几何？”
        │
        ▼
arithmetic / Moser / H25 / finite field
“哪些漂亮宿主其实天然低色？”
        │
        ▼
criticality / A6 / density
“离 abstract 六色逻辑还有多远？”
        │
        ▼
SAME / DIFF / terminal relation
“模块究竟强迫什么颜色关系？”
        │
        ▼
wheel / fresh fifth color
“第五色怎样修复并擦除信息？”
        │
        ▼
flower / R4 / joint marginals
“局部都可行，为何联合仍可矛盾？”
        │
        ▼
relative frame / S5 / pair alphabet
“到底应该保留什么颜色信息？”
        │
        ▼
R_k(P,B) + geometry/mobility
“逻辑关系怎样在真实二维几何里复合？”
        │
        ├─────────────────┐
        ▼                 ▼
reducibility          obstruction compiler
“任意边界可延伸”      “某些边界不可延伸”
        │                 │
        ▼                 ▼
finite Abelian /       R4 / lists / Galois bad fiber /
Galois orbit / Parts   pair compiler / Parts joint ports
        │                 │
        └────────┬────────┘
                 ▼
            activation
                 │
                 ▼
 multi-center / high-arity / cross-copy joint relation
                 │
                 ▼
     finite empty fiber 或 universal extension theorem
```

这条演化不是“不断换题”，而是不断发现上一层变量把真正的信息 quotient 掉了。

---

# Part III. 历史主干 I：表示、算术宿主、criticality

## 7. finite-direction / Cayley–Gram：正确的表示层，不是最终机制

任意有限 unit-distance witness 只使用有限多个单位方向。若方向为

\[
u_1,\dots,u_m,
\]

令 \(Q=U^TU\) 为 Gram matrix，整数方向关系由矩阵 \(M\) 编码，则二维真实单位向量几何满足

\[
Q\succeq0,\qquad
\operatorname{diag}Q=1,\qquad
\operatorname{rank}Q\le2,\qquad
QM=0.
\]

### 历史价值

- finite-direction exact host；
- integer relation lattice；
- exact coordinate infrastructure；
- 后续 number-field / finite-field / Galois / algebraic seam 的输入层。

### 为什么降级

它回答：

> 一张有限几何怎样编码？

但不回答：

> 为什么这张几何五染不了？

所以 Cayley–Gram 是 representation layer，而不是 mother obstruction.

---

## 8. 五方向、3-adic、Moser、H25：学会先检查 ambient ceiling

历史研究过：

- 五方向 quadratic shell；
- mod-3 / 3-adic structure；
- Moser lattice / Moser ring；
- cyclotomic coordinates；
- finite field \(H_{25}\)；
- Fourier / spectral probes。

长期得到的原则：

\[
\boxed{
\text{代数复杂、方向多、边密、对称漂亮}
\not\Rightarrow
\text{颜色信息强}.
}
\]

外部结果和内部结果都不断展示：很多均匀 Abelian/cyclotomic host 有低色 quotient。

### 长期规则

任何大规模 host 搜索前先问：

1. 是否已有低色显式 coloring？
2. 是否有 finite quotient / residue coloring？
3. 是否有 ring homomorphism 拉回 coloring？
4. 是否已有 chromatic/fractional ceiling？

---

## 9. mod-5 / finite-field / elliptic 资产

### 9.1 [HIST-THM] mod-5 coordinate-ring ceiling

历史证明一大类实坐标环可约化到 \(\mathbb F_{25}\)，再拉回显式五染色。

曾直接关闭 9765 点 UNKNOWN 候选。

### 9.2 [HIST-THM] finite-field elliptic threshold

历史得到：

\[
\boxed{
\mathbb F_{q^2}^{\,2}
\text{ 的单位二次型图存在 }\mathbb F_q\text{-线性 }q\text{-染色}
\iff q=3,5.
}
\]

关键机制经过 genus-1 / elliptic curve 点数与 Hasse 型估计。

### 9.3 intrinsic valuation

后续把“坐标表达式是否有分母”升级成 squared-distance 的 intrinsic valuation/integrality 条件。

这条思路后来直接连接 T028–T031。

---

## 10. criticality / \(A_6(n)\)：为什么“离 UNSAT 很近”仍不是答案

项目曾定义 augmentation distance：

\[
A_6(n)
=
\text{一个 }n\text{ 点真实 UDG 至少需补多少条非单位 disequality 才不可五染}.
\]

它把：

- critical graph theory；
- unit-distance extremal geometry；
- gadget distance-to-unsat

连接起来。

但历史很快发现：

\[
\boxed{
A_6\text{ 小}
\not\Rightarrow
\text{端口 relation 新}.
}
\]

一个图可能“组合意义上离不可五染很近”，却对外没有可用信息。

因此 criticality 保留为 candidate filter / order parameter，不再承担母机制。

---

# Part IV. 历史主干 II：从 binary relation 到 joint relation

## 11. SAME / DIFF / terminal relation：第一次真正换母对象

给有限 UDG \(G\) 和端口 \(P\)，定义

\[
R_k(G,P)
=
\{c|_P:c\in\operatorname{Hom}(G,K_k)\}.
\]

以后很多语言都统一成 \(R_k\) 的 quotient 或 shadow：

- SAME / DIFF；
- wheel states；
- list coloring；
- missing color；
- pair alphabet；
- frame parity；
- R4；
- Galois boundary lists；
- Parts509 ports。

一个图即使自身仍可五染，也可能是很强的 relation gadget。

---

## 12. fresh fifth color：五色世界的核心 repair channel

第五色最重要的不是“多一个标签”，而是：

> 任意 independent set 都可整体改染为 fresh color。

它可以：

- split 旧颜色类；
- 临时降低/恢复 palette rank；
- 擦掉 relative frame；
- 让四色强 forcing 在五色变成 full projection。

因此长期原则：

\[
\boxed{
\text{任何五色 forcing theorem 必须显式处理 fresh-color repair.}
}
\]

---

## 13. 7-wheel：最持久的局部探针

中心 + 正六边形形成 7-wheel。

当前硬定理 T001：

\[
\boxed{D_{\min}=7-k,\qquad k=5,6,7.}
\]

若把 radial unit edge 的 pair state 写成

\[
T_i=\{c(o),c(v_i)\},
\]

则六个 \(T_i\) 都落在 \(J(k,2)\) 的同一个 star 中；star 只有 \(k-1\) 种状态，因此最少有 \(7-k\) 次 collision。

所以：

\[
\boxed{
\text{wheel defect}
=
\text{Johnson-star pair-state collision}.
}
\]

这把 defect route 与 pair route 完全接上。

---

## 14. 31-state wheel alphabet 与 61/62-state frame calculus

### 14.1 [HIST-THM/HIST-COMP] 31 oriented partitions / 9 orbits

五色 wheel mod 颜色名后保留 orientation，有 31 个 equality partitions；再除几何对称得到 9 个 orbit。

历史 exact extension 扫描得到：

\[
\boxed{
\text{high chromaticity}
\neq
\text{small-boundary rigidity}.
}
\]

### 14.2 [HIST-THM] frame observability

若接口显式看见 \(r\) 个颜色角色，隐藏 stabilizer 为 \(S_{5-r}\)。

五色 parity 可观察 iff

\[
r\ge4.
\]

### 14.3 [HIST-THM] overlap extension count

共享区域看见 \(m\) 个不同颜色角色时，partial frame 有

\[
(5-m)!
\]

个完整延伸。

- \(m=4\)：唯一 transport；
- \(m=3\)：两种 transport，parity 相反。

### 14.4 [HIST-THM] triangle flatness

三个局部模块围成物理单位三角形时，frame holonomy 为 identity。

### 14.5 [HIST-THM] simply-connected integration

在 occurrence connectivity、unit-edge coverage、局部 transport 合法的 simply-connected wheel complex 中，局部 frames 可积分成全局五染色。

**结论：**

> 神秘的大尺度平坦 holonomy 不是免费 obstruction；真正矛盾必须已经进入 local relation selection / activation。

---

## 15. flower 与 R4：local ≠ joint 的第一批真正资产

### 15.1 [HIST-COMP] 19 点 flower

历史记录：

- 19 点；
- 42 条 unit edges；
- 7 个 natural wheels；
- 指定任意至多 6 个目标 wheel states 可延伸；
- 7 个全部指定时 UNSAT。

它是最干净的：

\[
\boxed{
\text{所有低阶局部条件都可满足，但完整 join 为空}.
}
\]

后来可用 \(\mathbb Z_2\) parity / odd-cycle 解释。

### 15.2 [HIST-COMP] R4

历史记录：

- 61 centers / 91 physical points；
- 29-node proof tree；
- 56-point conditional core；
- 141 unit edges；
- 31 domain restrictions；
- denominator-9 weak marginal witness；
- pair-joint LP infeasible；
- exact Farkas dual；
- 3440-event unconditional escape ledger。

R4 没有证明一个真实 6-chromatic UDG；它证明的是：

\[
\boxed{
\text{低阶 projection / marginal 可以全部可行，
而完整 joint 已经矛盾}.
}
\]

### 成熟外部语言

- CSP local consistency；
- database joins；
- acyclic hypergraph；
- sheaf global section；
- contextuality；
- marginal polytope。

---

# Part V. boundary/list compiler 与 activation gap

## 16. [HIST-THM/HIST-COMP] 18 点 bad 3-list core

历史三角格核心：

- ordinary 3-colorable；
- 某套 3-lists 不可染；
- 删除任一顶点恢复；
- 恢复任一被禁颜色也恢复。

结论：

\[
\boxed{
\chi(G)\text{ 低}
\not\Rightarrow
\text{boundary/list relation 弱}.
}
\]

---

## 17. [HIST-COMP] 54 点 precolored geometry

通过 private unit neighbors 把坏 list 编译成真实几何预染色边界：

\[
b_{\rm bad}\notin R_5(G,B),
\qquad
R_5(G,B)\neq\varnothing.
\]

这第一次把缺口说清：

> 会造“某些钥匙打不开的房间”不够；还要让外部世界只能给出坏钥匙。

这就是：

\[
\boxed{\text{activation gap}.}
\]

---

## 18. 大型 direct attack：真正留下的是量词教训

### 18.1 3137

破坏一批漂亮 additive / finite-field coloring formulas，但仍有 ordinary 5-coloring。

### 18.2 6049

历史数据：

- 6049 vertices；
- 37838 unit edges；
- 452 个新点同时阻断保存的旧染色；
- 整体仍五染。

所以：

\[
\exists\text{ 大量被杀旧染色}
\not\Rightarrow
\forall\text{ 五染色被杀}.
\]

### 18.3 9431 / 12277 / 9765

继续说明：

- 点数；
- 边数；
- 5-core；
- 数域次数；
- 某个漂亮 coloring family 被击穿

都不是可靠的 proximity metric。

9765 最终被 arithmetic ceiling 显式五染，尤其具有代表性。

---

# Part VI. finite Abelian / Galois reducibility：项目最成熟的“上界型局部定理库”

## 19. [HIST-THM] unit four-cycle rhombus lemma

若 \(a,b,c,d\) 构成四条单位边的 4-cycle，则

\[
\boxed{a+c=b+d.}
\]

这是后续 finite-Abelian classification、rhombus elimination、signed-lift geometry 的基础恒等式。

---

## 20. [HIST-THM] finite Abelian Cayley planar UDG classification

若有限 Abelian Cayley graph 可单射单位距离实现，则每个连通分量形如

\[
\boxed{
C_{n_1}\square\cdots\square C_{n_r}\square K_2^{\square s}.
}
\]

因此：

\[
\chi\le3,
\]

且所有 cycle factors 偶时 \(\chi\le2\)。

### 结构解释

交换关系产生 unit rhombi；mixed finite differences 消失；有限 torsion 强迫 product decomposition。

---

## 21. [HIST-THM] 单个 real Abelian Galois orbit 低色

单个完整 orbit 的 unit graph 继承 finite Abelian Cayley structure，因此至多三色；多二次 sign orbit 更常是 hypercubes 的并，二色。

所以：

\[
\boxed{
\text{单 orbit 的代数复杂度不是六色来源}.
}
\]

真正复杂度必须来自多个低复杂模块共享 palette 的 joint interaction。

---

## 22. old-neighbor / anchoring 基础引理

### 22.1 三旧邻居锁域

一个新点若与三个非共线旧 \(K\)-点单位相邻，则距离差线性方程唯一确定新点，所以仍在 \(K^2\)。

### 22.2 Galois orbit common list

同一完整 orbit 的点看到相同旧 unit-neighbor set，因此获得同一 allowed list。

### 22.3 anchored orbit lemma

在旧域含 \(\sqrt3\) 等假设下，内部 unit-edge 与旧 anchor 联合可强迫很有限的 orbit geometry。

这些引理把“任意抽象 list assignment”大幅压缩成真实几何可实现的 list 类型。

---

# Part VII. five/six/seven pair-orbit：历史 phase transition 与当前认证边界

## 23. 五个 anchored two-point orbits

每对 orbit 间只有：

1. no edge；
2. straight matching；
3. crossed matching。

五 orbit raw relation 数：

\[
3^{10}=59049.
\]

历史结论后来被 T033 重新认证：

\[
\boxed{
\text{至多五个 anchored two-point orbits
总能延伸任意旧五染色}.
}
\]

当前远端证据包括：

- 59049 labelled graphs；
- 245925 positive coloring witnesses；
- 其中 196740 nonuniform-list witnesses。

---

## 24. 六个 orbits：必须区分“当前硬定理”和“历史更强版本”

### 24.1 [REMOTE-HARD] T036：共同三名单

当前远端正式认证：

\[
\boxed{
\text{六个 anchored two-point orbits 的 common 3-list 情形全部可延伸}.
}
\]

覆盖：

\[
14\,348\,907
\text{ raw relations}
\to
460\,728
\text{ normalized models}.
\]

证据分类：

- 240003 positive words；
- 4656 rhombus collisions；
- 90 个 T035 square-sum contradictions；
- 加上 \(K_{2,3}\)、\(K_4\) 等筛选。

**量词警告：**

T036 **不**认证 arbitrary nonuniform lists。

### 24.2 [POSTLEDGER-COMP] 历史更强 six-orbit arbitrary-list theorem

后续历史对话曾独立重做：

\[
32768\text{ labelled base graphs}
\to156\text{ graph isomorphism classes}
\to4562\text{ normalized signed instances}.
\]

最后 498 个 hard graphs 各检查 \(10^5\) normalized 3-list assignments。

两套独立算法各检查：

\[
\boxed{49\,800\,000}
\]

个 list instances，全部可染。

因此历史更强结论是：

> 在指定 real quadratic / anchored two-point 模型下，至多六个完整二点轨道，任意旧五染色均可保持延伸。

这目前应标：

\[
\boxed{\text{Historical stable statement / replay pending}}
\]

不能被 T036 的较弱量词覆盖，也不能在未恢复前升级成 `[REMOTE-HARD]`。

---

## 25. seven-orbit 第一代：abstract hard core 与 geometry gap

历史首先出现：

- 14 new vertices；
- 26 matching-type constraints；
- abstract graph 4-chromatic；
- 删除任意一整个 pair orbit 恢复 3-colorability；
- 有 faithful unit-distance realization。

但 old-anchor activation 要求 fiber pair geometry 满足更强条件；历史 12 个 branches 最优仍有最大 pair distance 约

\[
2.29089>2.
\]

于是第一次真正出现：

\[
\boxed{
\text{abstract relation logic 已硬，
但真实 anchor geometry 激活不了}.
}
\]

这是 logic–geometry gap 的典型原型。

---

## 26. [POSTLEDGER-THM/COMP] seven-orbit 28 点 / 50 边 real anchored module

后续历史不再死磕原 14-point lift，而用两份轻微共轭旋转 Moser spindle：

- 14 个新点；
- 每 pair 配两个 old anchors；
- 总计 28 points；
- 50 actual unit edges；
- 全部 \(\binom{28}{2}=378\) 点对 exact check；
- 无 old-old unit edge；
- 无 cross-copy accidental unit edge；
- 无错配 anchor edge。

在固定 old-boundary coloring 下，所有新点只剩三色，而两份 Moser spindle 都不可三染，因此该边界不可五色延伸；六色可延伸。

**整个 28 点图本身仍然四色。**

所以它是：

\[
\boxed{\text{真实 conditional bad boundary module}}
\]

而不是 6-chromatic UDG。

---

## 27. [POSTLEDGER-THM] seven-orbit exact boundary relation

令 14 个 anchors 分成 7 对，则历史得到：

\[
\boxed{
b\notin R_5(M,B)
\iff
\exists T\in\binom{[5]}2
\text{，七对 anchors 全都恰使用 pair }T.
}
\]

坏 labelled boundaries 数：

\[
\boxed{\binom52\,2^7=1280.}
\]

### spindle list lemma

若 Moser spindle 每个顶点 list size 至少 3，则不可列表染当且仅当七份 list 完全相同且均为同一个三元素集合。

这个 theorem 把七轨道 module 的逻辑本质完全抽离出来。

---

## 28. [POSTLEDGER-THM] 四色 activator no-go

若外部 activator \(H\) 只通过 boundary \(B\) 正确连接，且没有遗漏 cross-interior unit edges，则：

\[
\boxed{
\chi(H)\le4
\Longrightarrow
H\cup M\text{ 可五染}.
}
\]

原因：若 boundary 恰落在 bad 1280 states，使用 fresh fifth color 改一个 anchor 即可逃出 bad set，再延伸内部。

这把一个长期经验升级成精确 no-go：

\[
\boxed{
\text{要激活 seven-orbit bad module，
外部必须真正使用五色，
或多个 bad modules 联合耦合，使 repair 不能局部完成}.
}
\]

到这里，真正 frontier 已经不是“继续加第八轨道”，而是 activation。

---

# Part VIII. 从 Galois 到 \(J(5,2)\)：pair algebra 是更自然的五色中间语言

## 29. 单位边天然携带颜色对

任意五染色中，unit edge \(uv\) 携带：

\[
\lambda(uv)=\{c(u),c(v)\}\in\binom{[5]}2.
\]

所以五色有天然 10-state alphabet。

若点 \(x\) 与 base edge \(uv\) 构成等边三角形，则

\[
c(x)\notin\lambda(uv),
\]

所以 \(x\) 的 allowed list 正好是三元素补集。

这使 seven-orbit bad relation 脱离 Galois 外壳，变成纯 Euclidean pair language。

---

## 30. [POSTLEDGER-THM] Moser spindle = \(NAE_{10}\) pair gate

给 Moser spindle 七个顶点各配一条 unit base edge。若七条 base edges 的 pair labels 全相同，则七个 spindle vertices 都只能使用同一组三色，矛盾。

所以：

\[
\boxed{
\lambda(e_1),\dots,\lambda(e_7)
\text{ 不可能全部相同}.
}
\]

这是一个真实 Euclidean \(NAE_{10}\) relation。

---

## 31. [POSTLEDGER-THM/COMP] pair-intersection detector

历史 overlapping spindle module 得到：

对两个三名单 \(A,B\subset[5]\)，特定重叠结构不可列表染 iff

\[
|A\cap B|\ge2.
\]

换成 pair complements

\[
A=[5]\setminus T,\qquad
B=[5]\setminus U,
\]

则真实几何能区分：

- \(|T\cap U|=1\)；
- \(T\cap U=\varnothing\)。

所以我们已经不只会检测“七个 pair 是否全相同”，而开始拥有 pair-pair predicates。

---

## 32. \(J(5,2)\) / Petersen

五色二元素子集间只有三种 \(S_5\)-invariant orbit relation：

1. \(T=U\)；
2. \(|T\cap U|=1\)；
3. \(T\cap U=\varnothing\)。

disjointness graph：

\[
\boxed{KG(5,2)\cong\text{Petersen graph}.}
\]

\(S_5\) 在 10 pair states 上的 permutation representation：

\[
\boxed{10=1+4+5.}
\]

Petersen spectrum：

\[
3^1,\quad1^5,\quad(-2)^4.
\]

因此 \(J(5,2)\) 是 full \(S_5\) frame 与 1-bit parity 之间一个非常自然的中等信息层。

---

## 33. Moser-incidence hypergraph sufficient criterion

把逻辑 base edges 当超图顶点；若七条 base edges 可同时给一份 Moser spindle 提供禁色，则形成 hyperedge。

任何五染色给超图顶点 10 个 pair labels，而每个 hyperedge 不能 monochromatic。

因此：

\[
\boxed{
\chi(\mathcal H_{\rm Moser})>10
\Longrightarrow
\chi(\mathbb R^2)\ge6.
}
\]

### de Grey 1581 benchmark

历史重建中：

- 1581 points；
- 7877 actual unit edges；
- 904 Moser spindle structures；
- 对应 incidence hypergraph 找到 10-coloring。

所以已有五色 witness 并不会自动在新 invariant 上接近突破。

---

# Part IX. 当前远端硬主线 I：Parts509 从“最小五色图”变成 relation laboratory

## 34. Parts509 exact core qualification

当前项目独立重建：

- 509 distinct points；
- 2442 induced unit edges；
- public 2259-edge proof subgraph；
- 完整 five-coloring；
- 4-color CNF；
- public DRAT；
- 转成 LRAT；
- standard-library RUP replay：
  - 92649 clause additions；
  - 5,813,255 hint propagations；
  - 最终 empty clause。

因此 Parts509 已成为项目的第一个完全离线认证的真实

\[
\boxed{\chi=5}
\]

核心实验室。

---

## 35. [REMOTE-HARD] T026：任意三端口完全自由

对任意 \(|P|\le3\)：

\[
\boxed{
R_5(G_{509},P)
=
\operatorname{Hom}(G_{509}[P],K_5).
}
\]

即只要端口自身 proper，就能延伸到全图。

证据：

- 1744 full-color witnesses；
- 覆盖
  \[
  106\,793\,611
  \]
  个合法三端口 partition requests；
- 指定 13-point dual-hexagon boundary 的
  \[
  22327
  \]
  个 orbit-reduced legal partitions 全部延伸。

### gluing corollary

在无额外 cross-unit edges 且每次 overlap ≤3 的有序副本粘合中，有限或单向无限 union 仍五染。

所以：

\[
\boxed{
\text{Parts509 很高色，但低 arity boundary relation 极弱}.
}
\]

---

## 36. [REMOTE-HARD] T027：等中点四元组也全部自由

这是上一版最需要补上的结果之一。

当前远端认证：

\[
\boxed{
\text{Parts509 所有 equal-midpoint quadruples 的合法五色预染色全部延伸}.
}
\]

数据：

- 794256 quadruples（含共线退化）；
- 3807 complete witnesses；
- 覆盖 10,725,867 legal partitions。

**重要范围：**

T027 不是“任意四端口 universal extension”。

它关闭的是非常大、非常自然的一类：

- parallelogram；
- rhombus-like；
- equal-midpoint；
- 含共线退化

四元组。

所以以后说“优先搜 2+2 / rhombus four-port”必须先剔除 T027 已覆盖部分。

---

# Part X. 当前远端硬主线 II：T028 安全域与 T029–T031 逃域结构

这是当前真正把项目推到 Q005 的硬定理链。

## 37. [REMOTE-HARD] T028：整个 \(K^2\) 是五色安全域

令

\[
\boxed{
K=\mathbb Q(\sqrt3,\sqrt5,\sqrt{11}).
}
\]

当前远端证明：

\[
\boxed{
\chi(K^2)=5
}
\]

其中图是 \(K^2\) 上全部真实单位距离边的诱导图。

而且这不是“某个有限分母窗口”：

- 允许任意分母；
- 允许任意重叠；
- 允许任意同域 cross-unit edges；
- 使用成熟的 Madore-style valuation/residue reduction；
- finite target 为 121-point / 726-edge \(F_{11}\)-residue graph；
- Parts509 坐标有四种兼容映射；
- 保留 \(F_{11}\) residue field 的兼容扩域仍安全。

### 结构意义

\[
\boxed{
\text{不能再在 Parts 原坐标域里“继续堆更复杂构造”期待六色}.
}
\]

这比 T026/T027 更强：不是某类端口自由，而是整个 ambient field graph 已五色。

---

## 38. E016：四种真正逃域的双核心仍然五色

当前远端试了四类独立新根式旋转：

\[
\sqrt7,\quad\sqrt{13},\quad\sqrt{17},\quad\sqrt{41}.
\]

对应双核心各：

- 1017 points；
- cross edges 数分别 3 / 21 / 30 / 4；
- 所有 1,032,256 noncommon cross-pair displacements 做 exact algebra check；
- 全部整体仍恰五色。

这说明：

\[
\boxed{
\text{逃离已知安全域}
\not\Rightarrow
\text{立刻产生六色压力}.
}
\]

---

## 39. [REMOTE-HARD] T029：独立二次根式旋转跨边的充要条件

对独立根式旋转，两层间的非公共 unit edge 受到极强限制：

> 原向量必须共线，并满足一个径向二次方程。

证明通过比较 \(1\) 与 \(\sqrt d\) 系数。

同时两完整 \(K\)-片层只共享原点。

### 结构意义

单中心 escape-field geometry 并没有产生高维乱接触；跨边信息塌成径向/共线结构。

---

## 40. [REMOTE-HARD] T030：\(\sqrt{13}\) 打穿固定 valuation window

对

\[
\cos\theta=\frac58
\]

的 \(\sqrt{13}\)-rotation，存在真实单位跨边具有任意负的 11-adic valuation depth。

历史固定 valuation-window 方案因此失效。

核心 polynomial：

\[
F(t)=4t^2-5t+4
\]

有简单根可 Hensel-lift；前 24 层 exact calibration 与无限证明吻合。

### 关键量词

T030 只证明：

\[
\boxed{
\text{任何“固定有限 valuation 深度窗口”不够}.
}
\]

它**没有**证明：

- 所有 finite-state coloring encoding 都失败；
- \(K(\sqrt{13})^2\) 需要六色；
- multi-center 不能五染。

---

## 41. [REMOTE-HARD] T031：单中心跨边图度数 \(\le2\)，且常无有限环

非公共 cross-edge 图满足径向递推：

\[
a_{n+2}=2c\,a_{n+1}-a_n.
\]

当前证明：

- cross-edge graph degree \(\le2\)；
- \(c\in\mathbb Q\) 且 \(2c\notin\mathbb Z\) 时无有限 cycle；
- 四个测试角均落入无有限环情况。

### 结构意义

单中心根式旋转的真实跨边网络至多是路径/链式结构。

它解释了为什么“单中心 Galois sign / rotation cycle = color holonomy”是危险误读。

真正闭环若存在，很可能需要：

\[
\boxed{\text{多个中心 / 多个刚体片层 / 高度联合 relation}.}
\]

---

# Part XI. 当前远端硬主线 III：T032–T036 把历史 Galois 资产重新接回 Q005

## 42. [REMOTE-HARD] T032：anchored pair normal form

对实二次扩域：

\[
z^\pm=a\pm\sqrt d\,b,
\]

T032 给出：

- 真实 old anchor 的 exact square condition；
- 两点 orbit 的共同名单；
- orbit-orbit matching relations；
- 全部 cross-edge equations。

**范围：**

只覆盖 anchored points，不覆盖未锚定新点。

---

## 43. [REMOTE-HARD] T033：五轨道重新认证

重新生成并验证历史 five-pair theorem：

- 59049 labelled matching graphs；
- 245925 positive coloring witnesses；
- 196740 nonuniform-list witnesses；
- 原旧 ZIP 未恢复，所以是“新生成证书重证”，不是旧包 replay。

---

## 44. [REMOTE-HARD] T034：subcubic orbit networks 全部可约

任意规模 anchored pair network，只要剥除 degree \(\le2\) 后剩余 interaction core 仍 subcubic，并满足相应 list/K4 假设，则 universal five-color extension 成立。

因此真正坏 boundary core 必须具有：

\[
\boxed{\Delta\ge4\text{ 的分支}.}
\]

这把“需要多少 orbit”升级成“真正需要什么 interaction topology”。

---

## 45. [REMOTE-HARD] C004：Galois sign 不是 color-frame parity

一个 Galois 符号不平衡三环可以真实存在而且仍完全五染。

所以：

\[
\boxed{
\text{quadratic conjugation } \pm
\neq
\text{R4/S5 color-frame holonomy}.
}
\]

这是非常重要的概念纠偏。

---

## 46. [REMOTE-HARD] T035：real-conjugation square-sum obstruction

某类双菱形/三角结构通过共轭平均迫使：

\[
|h|^2=-1,
\]

与实平方和非负矛盾。

这是“数值 geometry failure → exact human-readable obstruction”的优秀范例。

---

## 47. [REMOTE-HARD] T036：六轨道共同三名单全部可约

当前远端正式结论：

\[
\boxed{
\text{six anchored two-point orbits + common 3-list}
\Longrightarrow
\text{always extend}.
}
\]

它与历史更强 arbitrary-list version 的关系必须一直明确：

\[
\boxed{
\text{T036 是当前硬量词；
post-ledger six-list theorem 是历史更强量词、待重放}.
}
\]

---

# Part XII. Q005：为什么当前硬前沿是 multi-center joint extension

## 48. 当前远端对 Q005 的精确描述

\[
\boxed{
\text{逃离 }F_{11}\text{ 安全域后，多中心完整五色延伸或全域五染色？}
}
\]

在 anchored pair 分支，T032–T036 已把候选压到：

- six-orbit **nonuniform lists**；
- 或至少 seven-orbit common 3-lists；
- interaction core 需有 degree \(\ge4\) branching；
- 必须满足真实 anchoring；
- 必须通过 T035 等 geometry filters；
- 还必须真正解决 activation；
- 未锚定新点仍开放。

这比“试试更多根号”精确得多。

---

## 49. 当前 arithmetic / local-field 的另一条分支

T030 已证明 fixed valuation-depth window 不够。

但这不等于 local-field 方向死亡。

仍开放：

> 能否构造一种允许任意 valuation depth 的有限/无限状态五色编码？

T031 反而给出一个正面信号：

> 无界深度的单中心 cross-edge path 本身仍是二染的。

所以 arithmetic upper-route 的正确问题从“固定 residue window”升级成：

\[
\boxed{
\text{是否存在兼容全 valuation tree / automaton 的 coloring code？}
}
\]

这与 symbolic dynamics / automata / tree automata 真正接上。

---

# Part XIII. 5/6/7 三相：仍应保留的 covering–ramification calibration

这一部分不是当前 theorem ledger 的主线，但它提供了最漂亮的 5/6/7 统一直觉之一，应当保留。

## 50. 三角格 affine calibration

令三角格坐标为 \((m,n)\in\mathbb Z^2\)，邻接方向：

\[
\pm(1,0),\quad
\pm(0,1),\quad
\pm(1,-1).
\]

### 50.1 七色

\[
c_7(m,n)=m+3n\pmod7.
\]

六个邻色差恰为所有非零 residues：

\[
1,2,3,4,5,6.
\]

因此每个点看到其余六种颜色各一次：

\[
\boxed{
T\to K_7
\text{ 是 locally bijective covering}.
}
\]

### 50.2 六色

\[
c_6(m,n)=m+3n\pmod6.
\]

邻色差：

\[
1,5,3,3,2,4.
\]

恰一个颜色重复，额外关系形成 perfect matching：

\[
P=\{\{0,3\},\{1,4\},\{2,5\}\}.
\]

### 50.3 五色

\[
c_5(m,n)=m+2n\pmod5.
\]

邻色差：

\[
1,4,2,3,4,1.
\]

两次重复按颜色上的 \(C_5\) 组织。

### 50.4 统一

\[
\boxed{
7=\text{unramified covering},\qquad
6=\text{one matching ramification},\qquad
5=\text{cycle-like double ramification}.
}
\]

这解释了为什么三角格既是极好 calibration host，又通常不是最终 obstruction：它太容易形成 tiny finite quotient，defect 可以无摩擦周期传播。

---

# Part XIV. \(S_6\)、duad/syntheme：什么被否定，什么仍值得保留

## 51. 六色 pair alphabet

\[
\binom{[6]}2
\]

有 15 个 duads。

把六个颜色分成三个 disjoint pairs 的 perfect matching 也有 15 个 synthemes。

经典 \(S_6\) exceptional outer automorphism 与 duad–syntheme–pentad geometry 紧密相关。

---

## 52. 被当前硬结果否定的版本

C001–C003 + T003 明确关闭：

\[
D=1
\Rightarrow
\text{global matching}
\Rightarrow
\text{canonical syntheme}
\]

以及：

> 同一普通 \(S_6\) action 下存在无参考 deterministic duad→syntheme map。

都不成立。

---

## 53. survives 的版本

### 53.1 T006

若额外有 equitable / role-consistency，再加 \(D=1\)，则 fixed perfect matching 恢复。

所以 syntheme 仍是：

\[
\boxed{
\text{equitable minimal-defect phase 的自然状态}.
}
\]

### 53.2 \(J(6,2)\) pair-CSP

六色 pair alphabet 仍然是自然对象。

表示分解：

\[
15=1+5+9.
\]

disjointness graph：

\[
KG(6,2).
\]

### 53.3 一个抽象小定理

若 \(D(T,U)\iff T\cap U=\varnothing\)，则在 six-pair universe 中：

\[
T=U
\iff
\exists X,Y:
D(T,X)\land D(U,X)\land
D(T,Y)\land D(U,Y)\land D(X,Y).
\]

所以在抽象 pair-CSP 中：

\[
\boxed{D\Rightarrow =.}
\]

真正难点仍然是 Euclidean routing / fan-out，而不是抽象逻辑定义能力。

---

# Part XV. transport obstruction：information–mobility tradeoff 已经部分定理化

## 54. [REMOTE-HARD] T007：低色 host 不能做 perfect higher-color pair copier

若 \(G\) 有 \((k-1)\)-coloring，则两条不同端口边不能在所有 \(k\)-colorings 中保持相同 palette。

所以真正五色 palette wire 必须生活在真正的 \(\chi=5\) 阈值附近。

这解释了 Parts509 为什么是自然 laboratory。

---

## 55. [REMOTE-HARD] T008：separator stabilizer

如果左右两部分只通过小 separator \(S\) 相接，那么 separator 上未出现的颜色仍可自由置换。

任何 deterministic transmitted information 必须对该 stabilizer 不变。

大白话：

> 小接口几何灵活，但它看不见太多颜色角色；大接口信息强，但几何越来越刚。

这就是：

\[
\boxed{\text{information–mobility tradeoff}.}
\]

---

## 56. [REMOTE-HARD] T009 / T003：先做 stabilizer test，再搜 gadget

- \(k\ge5\) 时，无参考 equivariant pair→pair deterministic self-map 只有 identity；
- six-color duad→syntheme same-action deterministic map 不存在。

这形成重要工程原则：

\[
\boxed{
\text{在大型 SAT/geometry 搜索前，
先求 port stabilizer orbit / equivariant-map obstruction}.
}
\]

---

## 57. [REMOTE-HARD] T010：抽象 join copier 二维不可实现

抽象上 \(Q\vee2K_2\) 是 perfect pair copier；二维 unit geometry 中两个单位圆交点最多两个，因此 \(\chi(Q)\ge3\) 时无法 faithful realize。

这是 logic–geometry gap 最小原型：

\[
\boxed{
\text{抽象颜色逻辑很容易；
二维单位距离实现才是真瓶颈}.
}
\]

---

## 58. [REMOTE-HARD] T014：nonzero-distance SAME 已接近终局

若存在非零距离端点在所有 \(k\)-colorings 中无条件 SAME 的 finite UDG gadget，则有限多个刚体副本可直接编译成不可 \(k\) 染 UDG。

所以“完美同色 wire”不是轻量中间目标，而已经接近 lower-bound breakthrough。

更现实的 primitive 应当是：

- multivalued relation；
- probabilistic relation；
- joint-only obstruction；
- feedback/cycle 后才矛盾的 relation。

---

# Part XVI. seam / long-chain：一条完整关闭但非常值得保留的方法学样板

## 59. T004/T005：六色 minimal-defect 具有 symbolic dynamics 自由度

T004 分类 affine ansatz 的两个 golden-mean components。

T005 构造任意 binary increment 的条纹 family。

这说明：

\[
\boxed{
\text{六色 minimal defect phase 不是几个 isolated crystals，
而可能有 SFT 级高熵自由度}.
}
\]

---

## 60. T015–T017：两个/三个格子仍太松

### T015

Moser-angle 两格除公共部分外只有 6 条 cross-unit edges；任意两条 binary words 都可 weld。

### T016

同原点第三方向仍只有链式接触。

### T017

translated three-grid loop 的 384 local word triples 全部可延伸。

这些结果共同说明：

\[
\boxed{
\text{“多一个方向”本身不是 joint obstruction}.
}
\]

---

## 61. T018–T021：五格第一次出现真正 joint constraint

### T018

连续三个 full phase-difference interfaces 不可能同时存在。

### T019

uniform two-phase 32 inputs 中 28 extend / 4 fail。

### T020

任意 bi-infinite words：

\[
\boxed{
\text{extend}
\iff
\text{至少一个 adjacent phase-difference set 漏 residue}.
}
\]

### T021

任意 finite / one-way / two-way infinite chain：

\[
\boxed{
\text{extend}
\iff
\text{不含连续三个 full interfaces}.
}
\]

证据压成：

- 36 invariant state sets；
- 416 closure obligations；
- reset identities。

---

## 62. T022：宿主本身 \(\chi=4\)，所以主下界路线关闭

\[
\boxed{
\chi(H_{\rm chain})=4.
}
\]

因此同类 layer-chain 不应再机械扩大。

但这条工作留下非常可迁移的方法：

- exact cross-contact classification；
- relation semigroup；
- antichain automaton；
- reset mechanism；
- infinite extension via finite-state closure。

---

# Part XVII. statistical compiler / moments / G27：什么已经被做到了能力边界

## 63. statistical compiler 的母思想

给 finite patch 的全部真实 colorings 赋概率，并要求全等子配置的 partition laws 一致。

若这个 exact linear system infeasible 且有 rational dual，则可尝试通过 amenability/Følner cancellation 编译成有限真实 obstruction。

必须一直区分：

\[
\mathcal A
\subseteq
\mathcal C_k(P)
\subseteq
\mathcal B.
\]

- inner approximation 空：不能推出真正 UNSAT；
- outer relaxation infeasible：才是真矛盾；
- outer relaxation feasible：可能是假解。

---

## 64. [REMOTE-HARD] T023：任意阶 monochromatic moments 不够

存在刚体不变 random independent-set law，使所有阶 monochromatic congruence moments 可行，总权：

\[
\boxed{\frac8{\sqrt3}<5.}
\]

所以：

\[
\boxed{
\text{只记录“哪些点同属一个颜色类”的任意阶 hierarchy
不能单独证明 }\chi(\mathbb R^2)\ge6.
}
\]

---

## 65. [REMOTE-HARD] T024：四点第一次出现真正 joint 信息

monochromatic-moment rank：

\[
2^n-n.
\]

四点正方形可构造两种 coloring laws：

- 所有 monochromatic moments 相同；
- \(2+2\) partition distribution 不同。

因此：

\[
\boxed{
\text{缺口不是“再升一阶”，
而是从 single-block moments 升到 complete partition law}.
}
\]

---

## 66. [EXTERNAL-REPLAY] G27/G29

远端重放：

- G27 182304 integer inequalities；
- 168 tight terms；
- G29 498168 inequalities；
- G29 blow-up 尚未完整 replay。

---

## 67. [REMOTE-HARD] T025：G27 complete joint law 也饱和

固定 G27 中：

- 348 candidate 4-block partitions 全可出现；
- denominator 566 full-support rational witness；
- 三个 atoms、各 \(1/3\) 的 non-deterministic extreme law；
- 8078 congruence maps 独立检查。

所以：

\[
\boxed{
\text{固定 G27 内继续“看得更全”也不会自动突破}.
}
\]

下一步必须换 geometry / multi-module joint system，而不是只换 observables。

---

# Part XVIII. cross-lattice：旧历史为什么已经提前剪掉很多“多格纸”直觉

## 68. [HIST-THM] 两任意 triangular lattices union

历史证明：

> 任意两个 unit triangular lattices 的有限诱导 unit graph 是 4-degenerate，因此 5-choosable；整个 union 五染。

更强：

> 固定第一张完整 lattice 的任意五染色，可以扩展到两格 union。

### 外部邻居引理

一个不在 triangular lattice 内的点，对该 lattice 至多有一个 unit neighbor。

这是两格 extension 的核心。

---

## 69. [HIST-THM] parallel translates

\(m\) 个同方向 triangular-lattice cosets 的 union 满足：

\[
\chi\le\max(3,m).
\]

所以至多五个 parallel cosets 不能给 6-chromatic graph。

---

## 70. [HIST-THM] six-corner pressure

若 triangular-lattice finite patch 每点 list size 至少 3 而不可列表染，则存在 minimal bad core，且：

- 至少 6 个 convex hull vertices；
- 每个 hull vertex degree = 3；
- list size = 3；
- hull angles \(\ge120^\circ\)。

这说明 extension failure 必须有空间上分布的压力，不会只靠一个局部尖点。

---

## 71. [HIST-THM] concentric incommensurate lattices finite contact

固定若干同心、pairwise incommensurate rotations 后，跨格 unit contacts 只有有限多个 endpoints。

所以盲目扩大半径最终可能不再增加任何新 coupling information。

---

# Part XIX. 上界路线：为什么仍应保留，而且必须比旧版本更精确

## 72. 上界与下界不是两条独立项目

Lower：

\[
\text{寻找 finite empty relation fiber}.
\]

Upper：

\[
\text{证明所有 finite restrictions 可 coherent extend}.
\]

它们共享同一个母对象：

\[
R_k(P,B).
\]

所以每一个 extension theorem 都是上界资产；每一个 failed extension module 都是下界资产。

---

## 73. hypothetical 6-coloring 必须是 zero-slack

历史/外部路线指出：若把 forbidden distance \(1\) 厚化成任意正宽区间，颜色需求跳到 7。

因此若 Euclidean 6-coloring 存在，它必须精确利用：

\[
\boxed{
\text{只避开“距离恰好 1”，
不能避开任何 }[1-\varepsilon,1+\varepsilon].
}
\]

这意味着普通 robust tiling / polygonal scheme 很可能不够。

---

## 74. polygonal / map-type 路线应降级

广泛的 polygonal/map-type six-coloring 受到强负结果限制。

所以上界不应继续默认：

> 找一个更聪明的有限多边形周期铺砌。

必须保留：

- infinitely refined boundaries；
- aperiodic structure；
- non-map-like color classes；
- pathological regularity；
- algebraic/local-field coding。

---

## 75. Minkowski \(P_{22}\to S^1\) continuation

附近的 polygonal Minkowski norms 确实存在 6-colorings。

所以可以把 unit ball 连续圆化：

\[
P_{22}\to S^1.
\]

定义可行极限参数 \(t^*\)。

两种结果都好：

- \(t^*=1\)：可能产生 Euclidean 6-coloring；
- \(t^*<1\)：第一处 active-contact catastrophe 本身给出新的 finite \(R_6\) relation 候选。

这是天然 upper→lower feedback loop。

---

## 76. inverse-limit formulation

取 growing finite domains：

\[
P_1\subset P_2\subset\cdots
\]

以及 boundary state spaces：

\[
X_n=R_6(P_n,B_n).
\]

restriction maps：

\[
X_1\leftarrow X_2\leftarrow\cdots.
\]

那么 global 6-coloring 对应：

\[
\boxed{
\varprojlim X_n\neq\varnothing.
}
\]

若某级 relation 已空，则得到 finite 7-chromatic obstruction。

---

## 77. periodic 失败绝不等于 global 失败

二维 SFT / Wang tiles 已告诉我们：

> 有无限 configuration 不代表有 periodic point。

所以 upper search 必须分层：

1. periodic；
2. quasiperiodic；
3. SFT-like aperiodic；
4. measurable/Borel；
5. unrestricted。

如果 regularity ladder 一层层失败，而 ordinary 6-coloring 仍未排除，这本身就是结构信息。

---

# Part XX. 四层 Euclidean relation stack：现在最稳定的母框架

## 78. Layer 1 — Geometry / Mobility

记：

\[
\mathcal G(P,B).
\]

至少包括：

- boundary distance matrix；
- port type；
- Euclidean stabilizer；
- 固定输入后的剩余 realization dimension；
- rigid/flexible branches；
- accidental unit edges；
- allowed relative poses。

---

## 79. Layer 2 — Deterministic boundary relation

\[
R_k(P,B)
=
\{c|_B:c\in\operatorname{Hom}(U(P),K_k)\}.
\]

可以进一步 quotient 成：

- equality partitions；
- pair labels；
- frame data；
- list masks；
- orbit classes。

---

## 80. Layer 3 — Probabilistic / convex law

\[
\mathcal P_k(P,B)
\]

记录：

- invariant distributions；
- congruence marginals；
- partition-law polytopes；
- dual inequalities；
- Farkas certificates。

---

## 81. Layer 4 — Geometry-aware composition

两个逻辑 relation 能 relationally compose，不代表对应 gadgets 在 \(\mathbb R^2\) 能摆在一起。

真正 composition 是：

\[
\boxed{
\text{Euclidean fiber product}
+
\text{color relation join}
+
\text{all accidental unit edges}.
}
\]

这解释项目中大量失败：

- relation 强但不可 route；
- geometry 好拼但 relation 太弱；
- interface 太小 → 信息被 stabilizer 擦掉；
- interface 太大 → geometry 锁死。

---

# Part XXI. 一个更浓缩的统一：extension / obstruction / repair / frustration

## 82. Lower = obstruction

寻找 finite modules：

\[
R_1,\dots,R_m
\]

使真实几何 composition 后：

\[
\boxed{
R_1\Join\cdots\Join R_m=\varnothing.
}
\]

---

## 83. Upper = extension

证明某类 boundary state 总有 extension，或构造一个 globally coherent branch。

---

## 84. Repair vs frustration

历史中的 fresh color、Galois extension、Parts small-port freedom 都是 repair mechanism。

flower/R4/seven-orbit bad boundary/T018 则是 frustration mechanism。

所以一个很自然的统一研究量是：

\[
\boxed{
\text{repair capacity}
\quad\text{vs}\quad
\text{frustration accumulation}.
}
\]

最终 \(\chi=5,6,7\) 可以理解为两者在哪一级 palette 上发生相变。

---

# Part XXII. 5 / 6 / 7 三个答案今天分别意味着什么

## 85. 若 \(\chi=5\)

那意味着：

\[
\boxed{
\text{所有 finite five-color relation compilers 最终都有 repair}.
}
\]

大量现在看起来“只差一步”的 lower routes 必须由某个深层 extension principle 统一解释。

可能表现为：

- 某个 relation clone/polymorphism 保护 satisfiability；
- 某种 local-field / symbolic coloring code；
- 任意 finite geometry 的可约 configuration theorem；
- 非常 pathological 的 global coloring。

T028 已经提供一个小型原型：

> 整个巨大算术安全域 \(K^2\) 都五色。

---

## 86. 若 \(\chi=6\)

这是最临界的中间相：

\[
\boxed{
R_5\text{ 在有限尺度最终 UNSAT},
\qquad
R_6\text{ global SAT}.
}
\]

需要同时成功：

1. finite 6-chromatic UDG；
2. entire plane 6-coloring。

它很可能是 zero-slack / jammed-but-feasible phase。

---

## 87. 若 \(\chi=7\)

则：

\[
\boxed{
R_5,R_6
\text{ 都会在有限尺度产生 obstruction}.
}
\]

因此 six-color hypothetical phases 最终必须被压成一个 finite contradiction。

5/6/7 defect / covering calibration 在这里可能尤其有价值：七色三角格恰好是 zero-defect covering phase。

---

# Part XXIII. 当前应该怎样重画“真正 frontier”

## 88. Certified frontier

截至 `d304...`，当前硬前沿最准确是：

### A. Parts/arithmetic

- T026：任意 ≤3 ports free；
- T027：equal-midpoint 4-ports free；
- T028：整个 Parts field \(K^2\) 五色；
- E016：四种 escape-field double cores 仍五色；
- T029：single-center cross edges 共线/径向；
- T030：valuation depth unbounded；
- T031：single-center cross graph degree ≤2 / often acyclic。

### B. anchored Galois

- T032：exact anchoring normal form；
- T033：five pairs arbitrary old coloring extend；
- T034：subcubic networks reduce；
- C004：Galois sign 不是 color parity；
- T035：square-sum geometry obstruction；
- T036：six pairs common 3-list extend。

### C. current open

\[
\boxed{\text{Q005 multi-center joint extension / safe-field escape}.}
\]

---

## 89. Historical-unreplayed frontier

最值得恢复：

1. six pairs arbitrary nonuniform lists；
2. seven-orbit 28-point / 50-edge exact module；
3. seven-orbit exact 1280 bad boundary theorem；
4. four-color activator no-go；
5. Moser \(NAE_{10}\) pair gate；
6. pair-intersection detector；
7. Moser-incidence hypergraph criterion；
8. R4 proof tree / Farkas / escape ledger。

---

## 90. Synthesized frontier

把两条线融合后，最自然的问题不再是“继续哪个历史章节”，而是：

\[
\boxed{
\textbf{能否在逃离 T028 安全域的多中心真实几何中，
生成一个 post-ledger 意义上的非平凡 pair/list/joint boundary relation，
并让 repair 不能局部完成？}
}
\]

这句话同时包含：

- arithmetic escape；
- Galois activation；
- Parts high-arity relation；
- R4 cyclic join；
- \(J(5,2)\) pair compiler；
- information–mobility tradeoff。

这才是当前最统一的 frontier。

---

# Part XXIV. 现在真正最小的几个技术问题

## 91. 技术问题 A：Parts arbitrary 4-port relation

定义：

\[
a_5(G)
=
\min\{|P|:
R_5(G,P)
\subsetneq
\operatorname{Hom}(G[P],K_5)\}.
\]

T026 给：

\[
a_5(G_{509})\ge4
\]

若 \(a_5\) 有限。

T027 又关闭所有 equal-midpoint 4-tuples。

所以真正问题是：

> 除去 T027 类以后，是否存在任意 4-port nonextendable legal partition？

尤其应 quotient：

- \(S_5\) color symmetry；
- graph automorphisms；
- geometric orbit type；
- induced-edge type；
- midpoint/equal-distance invariants。

如果全体 arbitrary 4-ports 也 free，则得到：

\[
a_5(G_{509})\ge5.
\]

这是一个非常干净的新 theorem。

---

## 92. 技术问题 B：six-orbit arbitrary lists 重放

当前远端 T036 只覆盖 common 3-lists。

历史 post-ledger 已有更强结论。

所以优先级很高的工作不是“重新猜 six-orbit 会怎样”，而是：

1. 恢复历史算法/证书；
2. 重建 exact 4562-instance coverage；
3. 双 verifier 重跑；
4. 对齐 T032/T035 的新 geometry filters；
5. 若成立，正式升级当前 theorem ledger。

这样 Q005 的 anchored branch 会进一步直接推到 seven-orbit / higher branching。

---

## 93. 技术问题 C：seven-orbit bad module 与当前 T032–T036 对齐

需要重新核对：

- exact base field；
- anchoring square conditions；
- unit-edge closure；
- 1280 bad relation；
- activator no-go；
- 与 T035 是否有冲突；
- 是否能嵌入 \(K(\sqrt{13})\) multi-center geometry；
- 是否能由真实 five-chromatic external activator 触发。

一旦能在当前硬框架下重放，它就会成为真正的 activation benchmark。

---

## 94. 技术问题 D：multi-center first nontrivial joint relation

T031 说明 single-center cross graph 过于一维。

所以应系统搜：

- two-center / three-center rigid placements；
- cross-copy overlaps ≥4；
- cross unit-edge cycles；
- degree ≥4 anchored interaction core；
- no T028-safe-field collapse。

目标不是立刻 SAT-UNSAT，而是找到：

\[
\boxed{
R_5^{\rm joint}
\subsetneq
R_5^{(1)}\times R_5^{(2)}
}
\]

的第一个小型 exact witness。

---

## 95. 技术问题 E：valuation-depth compatible five-color automaton

T030 只杀固定窗口。

应尝试构造：

- state depending on valuation residue + direction；
- p-adic tree automaton；
- finite transducer with carry；
- infinite-state but finitely describable coloring rule。

成功会推进 upper-side；失败若能形成 finite obstruction，则反过来推进 lower-side。

---

## 96. 技术问题 F：R4 escape ledger × real geometry

R4 历史已经给出 weighted escape events。

如果恢复 certificate，可以问：

> 当前 multi-center / seven-orbit / Parts four-port geometry 是否会系统性删除 R4 的廉价 escape events？

这是 deterministic boundary compiler 与 statistical compiler 最自然的会合点。

---

# Part XXV. 哪些路线可以明确停止机械加规模

## 97. [CLOSED] Moser translated-layer chain

T021 完整分类，T022 宿主 \(\chi=4\)。

---

## 98. [CLOSED] fixed G27 内继续堆同类 moments/events

T025 已对完整 partition law saturation。

---

## 99. [CLOSED] 任意阶 monochromatic moment hierarchy 单独冲 6

T023 给统一 \(<5\) feasible law。

---

## 100. [CLOSED] minimal six-color defect 自动 syntheme

C001–C003 反例。

---

## 101. [CLOSED] canonical same-action duad→syntheme

T003 stabilizer proof。

---

## 102. [CLOSED] 在 \((k-1)\)-colorable host 里找 perfect \(k\)-pair copier

T007。

---

## 103. [CLOSED] 天真 \(Q\vee2K_2\) Euclidean join

T010。

---

## 104. [CLOSED] 在 Parts 原数域继续堆六色候选

T028：

\[
\chi(K^2)=5.
\]

---

## 105. [DEPRIORITIZED] 单中心独立根式旋转直接造闭环

T029/T031 已说明其 cross relation 基本一维/森林化。

只有当它参与 multi-center composition 时才重新有价值。

---

# Part XXVI. 仍应保留但改变角色的旧路线

## 106. R4 / frame / holonomy

不应恢复成“单独的最终 proof theory”。

应作为：

- cyclic joint relation benchmark；
- escape ledger；
- frame observability language；
- multi-center joint relation 的解释工具。

---

## 107. finite Abelian / Galois

不应被理解成“从根式越来越复杂最终长出六色”。

应作为：

- reducibility theorem library；
- geometry pruning；
- anchoring exact test；
- safe deletion rules；
- activation benchmark。

---

## 108. \(S_6\) outer automorphism

不再支持无条件 syntheme reduction。

但仍值得作为：

- equitable minimal-defect phase；
- \(J(6,2)\) representation organization；
- six-color pair/defect dual language。

---

## 109. harmonic / PSD / representation

单色 scalar moments 已到 ceiling。

应升级为：

- full color partitions；
- pair alphabet association scheme；
- \(S_5\)/\(S_6\) irreducible blocks；
- orientation-aware \(E(2)\times S_k\) channels；
- joint geometry across multiple modules。

---

## 110. rigidity / real algebraic geometry

它不负责直接制造颜色矛盾。

正确职责：

\[
\boxed{
\text{精确焊接高信息 relation modules，
控制 accidental unit edges，
证明 candidate pose 可/不可实现}.
}
\]

---

# Part XXVII. 跨领域关联图：哪些已经“落地”，哪些仍是 idea bank

## 111. 已经真正落地的外领域

### 111.1 CSP / database joins

对应：

- \(R_k(P,B)\)；
- projection / natural join；
- tree-like gluing；
- cyclic incompatibility。

### 111.2 symbolic dynamics / automata

T004/T005/T021 已经是实际 SFT / finite automaton 味道。

### 111.3 equitable partitions / mass transport

T006 的天然语言。

### 111.4 group actions / stabilizers

T003/T008/T009 已经直接用作 theorem tools。

### 111.5 LP/Farkas/marginal polytopes

R4 / G27 / G29 / statistical compiler。

### 111.6 real algebraic geometry

T029/T035、cross-distance exact classification。

---

## 112. 高价值但尚未转成主定理的 idea bank

### 112.1 partition algebra / representation information spectrum

高 arity terminal states 本质是 set partitions；可以按 \(S_k\) irreps block-diagonalize relation / SDP。

### 112.2 group synchronization

relative color frames 可视为 \(S_k\)-valued synchronization；cycle products 对应 holonomy。

### 112.3 coding theory / Tanner / Tseitin

局部 relation 像 parity checks；最终 obstruction 像 syndrome inconsistency。

### 112.4 finite semigroups / syntactic monoids

repeated relation composition 可研究 transition semigroup；T021 已给一个小型样板。

### 112.5 sheaf / contextuality

适合解释“局部 sections 存在但 global section 不存在”；应作为解释/压缩层，而非替代 exact relation。

### 112.6 Hasse/Brauer–Manin 思维模板

不是说 HN 真有 Brauer–Manin obstruction，而是借鉴“所有局部检查都过，但全局对象不存在”的层级设计。

### 112.7 tensor networks / Holant

module relation 可以当 tensor；gluing 是 contraction；低 treewidth 可能解释为什么某些 overlap 总能扩展。

### 112.8 descriptive set theory

如果 \(\chi=5\) 或 6 的 global coloring 必须极端不规则，则 ordinary / Borel / measurable chromatic numbers 的分离会变得核心。

---

# Part XXVIII. 推荐统一 order parameters

以后不应只记录 SAT/UNSAT。

## 113. Relation volume

\[
|R_k(P,B)|
\]

以及 symmetry-reduced version。

---

## 114. Extension ratio

\[
\frac{|R_k(P,B)|}
{|\operatorname{Hom}(G[B],K_k)|}.
\]

---

## 115. Minimal nontrivial relation arity

\[
a_k(G).
\]

Parts 当前已知：

\[
a_5(G_{509})\ge4
\]

若有限，且 T027 又删除了一个巨大 structured 4-port family。

---

## 116. Joint shrinkage

对两个模块：

\[
\Delta_{\rm joint}
=
\log|R_1|+\log|R_2|-\log|R_{12}|.
\]

它直接测量“两个模块联合后新增了多少信息”。

---

## 117. Information–mobility score

同时记录：

- relation information；
- fixed-input realization dimension；
- fan-out；
- port stabilizer；
- accidental-edge cost。

---

## 118. Repair cost

一次 fresh-color / recoloring / list extension 需要改变多少 boundary roles。

这与 activator no-go 直接相关。

---

## 119. Interaction-core degree

anchored/Galois network 在剥除 reducible vertices 后的：

- minimum degree；
- maximum degree；
- branch number；
- cycle rank。

T034 已说明 subcubic core 太弱。

---

## 120. Valuation depth / state complexity

arithmetic coloring 需要记忆多深的 p-adic 信息？

T030 说明 depth unbounded，下一问题是 state description complexity。

---

## 121. Escape-face dimension

对 convex/statistical relation，记录：

- feasible polytope dimension；
- tight faces；
- dual support；
- extreme laws。

---

# Part XXIX. 推荐的研究优先级

## 122. 第一优先：恢复强历史资产，使证据时间轴合并

建议先恢复：

1. six-orbit arbitrary-list package；
2. seven-orbit 28-point exact module；
3. 1280 bad-boundary checker；
4. four-color activator no-go；
5. pair-intersection detector；
6. Moser-incidence benchmark；
7. R4 proof/Farkas/escape package。

原因：

> 这些不是“旧材料整理工作”，而是会直接改变 Q005 的搜索空间。

---

## 123. 第二优先：Parts arbitrary 4-port

不再重复：

- arbitrary ≤3 ports；
- equal-midpoint 4-tuples；
- 同域 gluing。

应专门搜索 T027 之外的 4-port geometry orbits。

优先：

- non-parallelogram 2+2 candidates；
- shared-neighborhood structures；
- wheel-crossing quadruples；
- ports participating in multiple distance types；
- symmetry-small orbits。

---

## 124. 第三优先：multi-center exact geometry

设计最小构造，使：

- 不落 T028 safe field；
- 不退化成 T031 single-center paths；
- anchored core 有 degree \(\ge4\)；
- overlap ≥4 或有真实 cross-unit cycles；
- 能计算 exact \(R_5\)。

目标首先是：

\[
R_{12}\subsetneq R_1\times R_2,
\]

不是一上来要求 6-chromatic。

---

## 125. 第四优先：activation benchmark

拿历史 seven-orbit bad relation 当 target：

\[
\mathcal B_{\rm bad}.
\]

寻找真实 five-chromatic activator \(A\)，使：

\[
R_5(A,B)\subseteq\mathcal B_{\rm bad}
\]

或多个 modules 联合后 repair impossible。

若发现 no-go，也应形成 theorem：

> 某类 activator 永远能 fresh-color escape。

---

## 126. 第五优先：local-field infinite-depth coloring

把 T030 的负结果转成更自然的上界研究：

- Hensel tree；
- valuation automaton；
- residue/state carry；
- possibly infinite-state but recursive coloring。

成功可能直接解释为什么新 field 仍五色；失败可能产生 finite joint obstruction。

---

## 127. 第六优先：R4/statistical 与 deterministic activation 会合

若 R4 escape ledger 恢复，则把 multi-center / seven-orbit / Parts ports 对 escape events 的影响做 exact scoring。

这可能第一次真正把：

\[
\text{deterministic boundary relation}
\]

与

\[
\text{statistical dual compiler}
\]

合成同一条 lower route。

---

# Part XXX. 当前不应误读的几个句子

## 128. “arity 4 是关键”

正确说法：

> 对 Parts509，arity 4 是第一个**尚未被 T026 普遍排除**的端口 arity；T027 又排除其中所有 equal-midpoint quadruples。

不能说：

> 五色的本质就是四元关系。

T024 的 2+2 coincidence 很有启发，但尚非因果 theorem。

---

## 129. “six orbit safe”

当前远端只敢说：

> six anchored pairs + common 3-lists safe。

历史更强 arbitrary-list theorem 尚待重放。

不能把两者混写。

---

## 130. “seven orbit 已经做出六色图”

错误。

28-point module 只是在固定 boundary 下需要第六色 extension；整图 itself 仍四色。

---

## 131. “T028 接近证明平面五色”

错误。

T028 只覆盖：

\[
K^2,\quad K=\mathbb Q(\sqrt3,\sqrt5,\sqrt{11}).
\]

这是巨大、重要的 countable algebraic host，但不是整个 \(\mathbb R^2\)。

---

## 132. “T030 证明 finite-state arithmetic coloring 不可能”

错误。

T030 只否定固定 valuation-depth window。

---

## 133. “T031 cross graph 是森林，所以整个组合五色”

错误。

T031 只描述非公共 cross-edge subgraph，不是整个 union 的 coloring theorem。

---

## 134. “Galois sign cycle 就是 color holonomy”

C004 已明确反例。

---

## 135. “R4 conditional UNSAT 就是 HN 下界”

错误。R4 有人工 domain restrictions。

---

# Part XXXI. 整个项目最稳定的直觉，用大白话说一遍

## 136. 第一层：颜色不是主要难点，颜色之间“怎么对齐”才是

单看一个局部模块，颜色名字都可以随便改。

真正的全局信息在于：

> 两个模块的颜色角色怎样对应。

这就是 frame / pair / joint relation。

---

## 137. 第二层：第五色最像“修补胶”

每当一个局部关系快要锁死时，第五色往往能：

- 拆一个颜色类；
- 改一个 independent subset；
- 让 boundary 跳出 bad set。

所以成功 lower proof 不能只造一个“很坏的房间”，而必须让修补一个房间时别处付代价。

---

## 138. 第三层：真正难的是把信息通过二维几何传过去

抽象颜色逻辑里：

- equality；
- disjointness；
- list obstruction；
- pair copier

往往很好定义。

但真实 unit geometry 会卡：

- 两圆交点；
- port rigidity；
- accidental edges；
- low-dimensional cross contacts；
- small-separator stabilizer。

所以真正稀缺资源是：

\[
\boxed{
\text{颜色信息}
\times
\text{几何可动性}.
}
\]

---

## 139. 第四层：很多“看起来复杂”的 host 实际只是安全区

Moser lattice、两 triangular lattices、layer chain、Parts field \(K^2\) 都在不同层次展示：

> 结构巨大不等于危险；可能存在一个低色 quotient / extension principle 把整个 host 吃掉。

---

## 140. 第五层：真正 obstruction 更可能是“多个中心组成闭环”

T031 已经把 single-center cross geometry 压到 degree ≤2 / often acyclic。

历史 seven-orbit / R4 又反复表明：

> 真正坏东西常常来自 joint compatibility，而不是单模块本身。

所以现在最自然的画面是：

\[
\boxed{
\text{多个各自可修复的模块}
\to
\text{共享 palette / shared ports}
\to
\text{repair dependencies 闭环}
\to
\text{无全局 repair}.
}
\]

---

# Part XXXII. 如果要让一个新 agent 在 30 分钟内上手，应读什么？

## 141. 第一层：当前硬状态

优先：

1. `docs/CURRENT.md`
2. `docs/RESULTS.md`
3. `docs/ROUTES.md`
4. `proofs/parts_core_ports.md`
5. `proofs/residue_field_ceiling.md`
6. `proofs/valuation_escape.md`
7. `proofs/anchored_pair_reduction.md`
8. `proofs/six_pair_trace.md`

---

## 142. 第二层：历史最高前沿

优先：

1. 本文；
2. `Hadwiger_Nelson_historical_assets_frontier_master_2026-09-08.md`
3. `Hadwiger_Nelson_complete_historical_asset_ledger_2026-09-08.md`
4. 5/6/7 unified map；
5. R4 / cross-lattice / Galois reports。

---

## 143. 第三层：开始新研究前的 checklist

每个新 candidate 必须先问：

1. 是否落入 T028 safe field？
2. 是否只是单中心 T029/T031 structure？
3. 是否有真实 accidental unit edges 全部恢复？
4. port separator 多大？T008 stabilizer 是否已判死？
5. host 是否 \((k-1)\)-colorable，触发 T007？
6. 是否只是 T027 equal-midpoint four-port？
7. anchored branch 是否被 T032/T034/T035/T036 可约？
8. 是否只是历史 seven-orbit bad boundary 的重新发明？
9. 是否把 UNKNOWN 当 UNSAT？
10. 是否有独立 verifier / proof certificate？

---

# Part XXXIII. 当前 theorem / counterexample / experiment 总账速查

## 144. T001–T036 分组速查

### Wheel / phase
- T001：wheel excess \(7-k\)；
- T002：历史 D/I pair equality；
- T003：无 canonical duad→syntheme；
- T004：affine minimal-defect classification；
- T005：binary seam family；
- T006：equitable + D=1 ⇒ matching。

### Transport
- T007：低色 host 不能 perfect higher-color pair copy；
- T008：separator stabilizer；
- T009：pair equivariant self-map only identity；
- T010：\(Q\vee2K_2\) Euclidean no-go；
- T014：nonzero-distance SAME ⇒ finite lower compiler。

### Pompeiu
- T011：equal-mass sufficient criterion；
- T012：vertex-critical no nonzero equal mass；
- T013：exact rational linear test。

### Seam / automaton
- T015：Moser-angle seam fully free；
- T016：third same-origin direction chain-like；
- T017：translated three-grid all extend；
- T018：FFF joint obstruction；
- T019：32 uniform inputs 28/4；
- T020：five-grid arbitrary words iff criterion；
- T021：arbitrary chain iff no FFF；
- T022：host \(\chi=4\)。

### Statistical
- T023：all mono moments \(<5\) feasible；
- T024：first missing joint at 4 points / 2+2；
- T025：G27 full partition-law saturation。

### Parts / arithmetic
- T026：all ≤3 ports free；
- T027：all equal-midpoint four-ports free；
- T028：entire \(K^2\) five-color safe domain；
- T029：independent-root cross-edge criterion；
- T030：unbounded negative 11-adic depth；
- T031：single-center cross graph degree ≤2 / no cycles under rational condition。

### Galois / reducibility
- T032：anchored pair normal form；
- T033：five pairs arbitrary old coloring extend；
- T034：subcubic networks reducible；
- T035：real conjugate square-sum obstruction；
- T036：six pairs common 3-list extend。

---

## 145. 当前 counterexamples

- C001：minimal D=1 不给 global matching；
- C002：antipodal repetition 仍不够；
- C003：partner support 可为 \(K_3\sqcup K_3\)；
- C004：Galois sign-unbalanced cycle 仍五染。

---

## 146. 当前实验 E001–E020 的真正作用

### 已完成基础/校准
E001–E006。

### seam 方向完整收敛
E007–E010。

### statistical/moment
E011–E013。

### Parts
E014–E015。

### escape field
E016–E017。

### historical reducibility recovery
E018–E020。

其中 E019 的 periodic \(F_{11}^2\) layer probes 只是 UNKNOWN observations，不构成负结论。

---

# Part XXXIV. 资源索引：本版主要吸收了哪些历史文档？

## 147. 核心输入

- `Hadwiger_Nelson_complete_historical_asset_ledger_2026-09-08.md`
- `Hadwiger_Nelson_historical_assets_frontier_master_2026-09-08.md`
- `Hadwiger_Nelson_5_6_7_upper_lower_unified_research_map_2026-09-08.md`
- `Hadwiger_Nelson_current_project_full_roadmap_2026-09-08.md`
- `Hadwiger_Nelson_full_history_remote_structural_synthesis_2026-09-08.md`

以及这些文档所索引的：

- R4 / parity / statistical compiler；
- cross-lattice；
- mod-5 / elliptic；
- finite Abelian / Galois；
- reducibility finite cases；
- direct attack；
- boundary/list；
- Parts509 / current remote proofs。

---

## 148. 当前远端只读基线

\[
\boxed{
rsgcsg/math-research@
d3048633a9029f9119cf844b593eaa59e0c2a4ce
}
\]

当前主线文件已经明确写出：

- T028 safe field；
- T029–T031 escape-field geometry；
- T032–T036 anchored pair reduction；
- Q005 multi-center frontier；
- R4 package 仍未完全恢复；
- six-orbit arbitrary nonuniform lists 尚未当前认证。

---

# Part XXXV. 最终收敛：现在我们到底“搞明白”到什么程度？

## 149. 已经真正搞明白的

### 历史脉络

基本已经清楚：

> 为什么从 finite direction → arithmetic → criticality → terminal relations → fresh color → joint obstruction → reducibility → activation → multi-center。

### 失败原因

大量旧路线已经不是“暂时没搜到”，而是有 theorem/counterexample/saturation：

- Moser layer chain；
- G27 fixed-geometry events；
- monochromatic moment hierarchy；
- minimal-defect syntheme；
- simple pair copier；
- Parts same-field search；
- single-center rotation closure。

### 当前数学缺口

已经明显缩小：

\[
\boxed{
\text{高信息五色 relation}
+
\text{真实 multi-center geometry}
+
\text{无法局部 repair 的 activation}.
}
\]

---

## 150. 还没有搞明白的

### 150.1 原问题答案

5、6、7 三种都仍与现有证据相容。

### 150.2 arbitrary Parts four-port

T027 只处理 equal-midpoint family。

### 150.3 six-orbit historical full list theorem

需要远端级 replay。

### 150.4 seven-orbit bad module 在当前 Q005 geometry 中能否真正激活

这是历史与当前最关键的连接之一。

### 150.5 multi-center \(K(\sqrt{13})\) 是否总五色

未知。

### 150.6 unbounded valuation-depth coloring code

未知。

### 150.7 deterministic relation 与 statistical compiler 是否能自然合流

未知。

### 150.8 upper-side regularity

若 5/6-coloring 存在，到底需要多 pathological，未知。

---

# 151. 最后一句项目级直觉

如果要把这几天所有数学压成一句话，我现在会写：

\[
\boxed{
\textbf{Hadwiger–Nelson 当前真正难的不是“颜色不够”，
而是二维单位距离几何能否让多个本来各自可修复的颜色关系
共享同一份有限 palette 后形成一个无法同时修复的闭环。}
}
\]

下界是在寻找这个闭环。

上界是在证明无论怎样形成局部压力，总还有一种 repair / extension 能把闭环拆开。

T028 告诉我们一个巨大算术世界里 repair 永远存在；T026/T027 告诉我们一个真实 \(\chi=5\) 核心的小端口几乎完全自由；T032–T036 告诉我们大量 anchored Galois interaction 仍可约；而历史 seven-orbit / R4 / pair compiler 告诉我们 **joint obstruction 不是幻想，它已经在条件系统里真实出现过**。

因此现在最值得做的不是“再找一个更大的图”，而是：

\[
\boxed{
\textbf{找到第一个小而真实的 multi-center / high-arity joint relation，
证明它到底能否被第五色修复。}
}
\]

这既是当前 lower frontier，也是通向真正 upper extension principle 的反面入口。
