# Hadwiger–Nelson 文献地图：机制、量词与迁移边界

2026-09-12 定向补充：[环/模局部化](https://stacks.math.columbia.edu/tag/00CM)
统一解释 [T111–T113](../docs/proofs/tau_localization_joint.md) 的分母层：
单位方向的迹迫使素分母可逆，双向平移模闭包成为整个固定数域。
有限群作用则量化不变律支持增长；它在二色图上也出现，不能借此
推断 non-5 见证或证明复杂度。这不是新一轮全面文献审计。

审查日期：2026-09-10。本文是跨领域重审的 canonical 文献地图，不是成果账本；
本地定理与实验以 [RESULTS](../docs/RESULTS.md)、证明文件和独立检查器为准，
来源文件、固定提交、缓存哈希及较早阅读记录见 [SOURCES](SOURCES.md)。
普通欧氏 HN 的已知范围仍是 `5 ≤ χ(R²) ≤ 7`。

2026-09-11定向补充：本轮原文阅读版本与范围列于[SOURCES](SOURCES.md)。
近单位区间的零厚度量词、一般CSP宽度与平面单位输入的区别，见
[T097–098](../docs/proofs/near_unit_obstruction_compactness.md)；Mycielski
嵌入维数的单射假设与允许碰撞的本地反证，见
[T099/E066](../docs/proofs/mycielski_collision_refutation.md)。
这次补充没有重新宣称整张地图完成新的全面审计。

同日继续：[T101–T102](../docs/proofs/kneser_zigzag_ceiling.md)阅读
Matoušek 的 Kneser 原始组合证明与 Simonyi–Tardos 的 Zig-zag 原文。
迁移结果不是“拓扑六色图提供 HN 六色候选”，而是相反：任意有序
染色强迫的交替四色 K₂,₂ 与单位菱形等中点冲突，故 coind B₀≥3
的图没有平面单位同态，允许碰撞。该具体拓扑下界连已知单位图
的普通五色性也不能捕获；不把此天花板推广到所有拓扑工具。

## 怎么读这张地图

这里按可迁移的数学机制组织，而非按“看起来接近突破”的标题排序。
下文的“已读”指本轮研究团队实际检查了所列原文部分，不表示全文每个证明
均被重证。“既有核验”指仓库已有明确阅读记录；“本地重放”只覆盖注明的
数据与结论；“入口”明确表示没有检查原证明。网页抓取日期不作为论文日期。
尤其不能把作者的计算声明、外部定理和本仓库的独立证书合并成同一证据等级。

统一视角是 `Hom(U(R²), K_k)` 的存在性：有限几何配置给出有限约束，
端口关系记录其全部可延伸颜色状态，完整有限维联合律是同一可满足性问题的
凸表达；赋值、群同态和周期模板则提供特定宿主上的正解。三者共享的是
**兼容延伸**，不是某个固定根式、某个 SAT 编码或某个密度指标。

真正的迁移通常有两步：先辨认成熟的一般定理，再证明 HN 对象满足它的
全部假设。下面每个条目的“边界”就是目前不能省略的第二步。

## 一、普通 HN：有限见证与全域覆盖

1. **de Bruijn–Erdős，A colour problem for infinite graphs and a problem
   in the theory of relations（1951）。**
   [原始论文的大学归档入口](https://research.tue.nl/en/publications/a-colour-problem-for-infinite-graphs-and-a-problem-in-the-theory-/)。
   证据：本轮核验书目信息，未读取原扫描证明；其有限色紧致性在下列已读
   HN 原论文及本地论证中使用。结构意义是：固定有限 `k` 时，所有有限子图
   都可 `k` 染与整个图可 `k` 染等价。这里是“所有有限子图”，不是搜索过的
   所有样本，更不是所有固定周期商图；也没有构造性算法保证。

2. **de Grey，The chromatic number of the plane is at least 5，
   arXiv:1804.02385v3（2018-05-30）。**
   [原文](https://arxiv.org/abs/1804.02385v3)。
   证据：核验五色下界原论文及构造机制；1581 点实例的全套计算没有在本轮
   重跑。关键不是多二次坐标本身，而是两个有限颜色关系在几何拼接后不兼容。
   对六色下界，必须重新获得排除所有五染色的关系，不能把四染色时代的
   强制性直接换一个颜色数复用。

3. **Exoo–Ismailescu，The chromatic number of the plane is at least 5:
   a new proof（2018）。**
   [arXiv:1805.00157](https://arxiv.org/abs/1805.00157)。
   证据：原论文入口已核验，完整构造比较仍未完成。保留它是为了避免把一种
   spindle 拼接当作五色下界的唯一机制；目前不从未核验的 gadget 细节推导
   本地端口关系，也不将其当作第二份已经重放的下界证书。

4. **Parts，Graph minimization, focusing on the example of
   5-chromatic unit-distance graphs in the plane，
   arXiv:2010.12665v1（2020-10-23），§6。**
   [原文](https://arxiv.org/abs/2010.12665v1)。
   证据：509 点、2442 实际单位边的来源已核验；仓库另从固定
   [坐标及证书仓库](https://github.com/md-amer/hadwiger-nelson-e5/tree/6d5ac08491f7cadbebd7d5b79e3f825d08eedf7b)
   独立重建诱导边，并检查 2259 边子图的四色否定证书和正五染色。
   Parts509 是可靠的五色核心及端口状态宿主，不是“接近六色”的数值尺度；
   其全部坐标落在一个已经整体五染的数域，是后续单纯域内复制的上限。

5. **Heule，Computing a Smaller Unit-Distance Graph with Chromatic
   Number 5 via Proof Trimming，arXiv:1907.00929v1（2019-07-01）。**
   [原文](https://arxiv.org/abs/1907.00929v1)。
   已读 proof-trimming 方法；这里只指定实际检查的 v1，不冒充最新 v2。
   可迁移的是从否定证明中提取小不相容核心、把搜索器与证明检查器分开。
   只要删后子图仍有已检查的不可染证书，列出边子图便足以证明下界；
   任意删边不保持不可染性，正染色诱导图则必须补查所有实际单位边。

6. **Haugland，A Moser-spindle-free 5-chromatic unit distance graph
   on 2131 vertices in the plane，arXiv:2608.04542v4（2026-08-17）。**
   [原文](https://arxiv.org/html/2608.04542v4)。已读引言、§§2、4。
   740 点 DIFF4(√3) 关系可生成 2131 点无 Moser spindle 的五色图。
   v4 修正了纪录叙述：已有 Heule 的 1441 点无 spindle 图，2131 不是该类
   最小纪录；一般五色纪录在此文中仍为 509。七重对称有助于制造不同关系，
   但 §4 的有限四色样本并未证明可延伸到整个无限格。浮点方向穷尽不是
   本地的精确单位边认证。

7. **Parts，What percent of the plane can be properly 5- and
   6-colored?，arXiv:2010.12668v1（2020-10-23）。**
   [原文](https://arxiv.org/abs/2010.12668v1)。
   已核验部分覆盖构造与有限图推论：六色覆盖比例超过 99.985698%，由此得到
   所有至多 6992 点的单位距离图六色可染。剩余面积即使极小也不是零；
   有限阈值也不是任意阶。它迫使不可六染的七色下界见证至少6993点，
   不限制不可五染的六色下界见证规模，也没有给出
   `χ(R²)≤6`，更不允许把数值“几乎可染”当作极限证明。

## 二、联合律、分数染色与谱/凸优化

这一组统一了“局部关系能否粘合”和“颜色事件概率能否同时实现”。必须
分清三件事：单个独立集的密度、分数覆盖、完整 `k` 色划分的联合分布。
完整联合律包含整数染色的全部约束；只保留低阶边际或 PSD 条件通常是放松。

8. **Matolcsi 等，The fractional chromatic number of the plane is
   at least 4，arXiv:2311.10069v4（2025-03-27），§3。**
   [原文](https://arxiv.org/abs/2311.10069v4)。
   已读有限配置与 geometric fractional 的等价处理；文中的
   `χ_gf,0 = χ_f,0 =` 有限图 Hall ratio 上确界含有关键下标 `0`。
   不把它改写成对完整无限分数染色的无条件等式。G27 对偶在本地已重放
   182304 条整数不等式、168 个紧项；T025 的348个划分是内部全等不变
   完整四色划分分布的全部可能支持，不是所有普通四色划分。

9. **Dúcz–Varga，A unit-distance graph in the plane with independence
   ratio below 1/4，arXiv:2606.28157v1（2026-06-26），Theorem 1。**
   [原文](https://arxiv.org/html/2606.28157v1)。
   已读严格越过独立率 `1/4`、分数色数 `4` 的论证。G29 原始有理对偶
   `4000716307/1000000018 > 4.0007` 已由本地 E012 独立重放：406 对距离、
   16859 条全等约束、498168 条整数不等式。这个重放**已完成**，不应再次
   列为待做；从 geometric fractional 证书实现 amenable blow-up 的整条
   构造则**未在本地重放**。新增两点在普通图中只是叶子，不能因 LP 更强
   就推断普通染色更难。

10. **Dúcz，A note on geometric colorings of the Moser lattice，
    arXiv:2606.12325v1（2026-06-10），Theorem 3.1。**
    [原文](https://arxiv.org/html/2606.12325v1)。
    已读 Moser 格 `L` 的 geometric integral 四染色及 `L[1/3]` 扩展。
    “恰有两种”涉及指定geometric integral（整色）染色，不是所有普通染色的分类。
    结构意义：同一宿主可以对某种不变概率模型极刚性，而普通颜色空间仍然
    更大；不能从几何平均的唯一性回推每个非可测染色的唯一性。

11. **Ágoston，Probabilistic formulation of the Hadwiger–Nelson
    problem，2019 学位论文，arXiv:2112.07665（2021-12-14 上传）。**
    [原文](https://arxiv.org/pdf/2112.07665)。已读 §4.1，印刷页 31。
    对完整有限颜色事件使用 `S_4 × E(2)` 不变均值的思想已经存在。
    因而“从任意四色解得到等距不变联合律”不是本项目首创；本地重述的价值
    是把一致性、支持和有限见证提取写成可检查量词，而非更换术语宣称突破。

12. **Gwyn–Stavrianos，A Finite Graph Approach to the Probabilistic
    Hadwiger-Nelson Problem，arXiv:2008.07987v1（2020-08-18）。**
    [原文](https://arxiv.org/pdf/2008.07987v1)；Geombinatorics 32(1), 2022。
    已读 §2.2、Theorem 2.11/Corollary 2.12、Theorem 3.7。
    任意染色无需可测性也可放进不变概率框架；零单色单位边概率与 `k` 可染
    的等价、有限加权 max-`k`-cut 对偶均是成熟参照。原文把无限 `p=q`
    列作 Conjecture 3.8，不应省略有限/无限区别。

13. **Atserias–Kolaitis，Consistency, Acyclicity, and Positive
    Semirings，arXiv:2009.09488（2020），§§4.1–4.3。**
    [原文](https://arxiv.org/html/2009.09488)。本轮已进一步读取正文；
    [SOURCES](SOURCES.md) 中更早的“仅摘要”记录不代表目前最高核验程度。
    running-intersection / join-tree 精确说明什么时候局部关系或概率表可
    粘合。HN 的几何重叠网络通常有环；只给单点、成对或各核心分别可行的
    边际，不能引用无环定理得到全局解。完整 join 是成熟关系代数，不是新
    gadget；几何可实现性和状态爆炸仍需解决。

14. **Ambrus 等，The density of planar sets avoiding unit distances，
    arXiv:2207.14179v3（2023-07-28），Theorem 1。**
    [原文](https://arxiv.org/abs/2207.14179v3)；Mathematical Programming 207 (2024)。
    已读 `0.2470` 可测单位距离自由集密度上界。Fourier/自相关加有限配置
    不等式是可迁移工具；可测独立集密度问题并不等于任意非可测颜色划分。
    它比简单两点谱放松更强，但没有把普通 HN 下界提高到 6。

15. **DeCorte–de Oliveira Filho–Vallentin，Complete positivity and
    distance-avoiding sets，arXiv:1804.09099v4（2023-09-13）。**
    [原文](https://arxiv.org/pdf/1804.09099v4)；Math. Program. 191 (2022), 487–558。
    已读 Theorem 1.1：适当的完全正性锥给出密度问题的精确凸表达。
    “完全正”不等于“半正定”；有限 SDP 截断只是放松，不能把原定理的精确性
    转移给截断程序。[Matolcsi 等引言](https://arxiv.org/html/2311.10069v4)
    所述分数色数上界低于 4.36，意味着任何被该不变量支配
    的下界不可能到 6，但这不排除保留完整整色联合约束的所有 SDP 层级。

## 三、CSP、关系代数、符号动力学、gain graph 与刚性

补充（2026-09-11）：**Abramsky–Brandenburger，The Sheaf-Theoretic
Structure of Non-Locality and Contextuality，arXiv:1102.0264v7**。
[原文](https://arxiv.org/html/1102.0264v7)，已读§§2.2–2.5、4.3及§6定义。
关联矩阵把完整联合分布延伸写成非负归一化线性系统；支持中的全局
赋值与指定概率模型可延伸是不同层次。对HN的启发是区分普通五染色
与带全等义务的joint分布；该对应是方法参照，不是HN归约定理，
不能把量子测量约束直接当成单位距离图的必要条件。

HN 是一个无限几何关系结构到有限完全图的同态问题，但不是任意有限图 CSP
分类的直接推论。有限方向宿主有额外阿贝尔结构，适合用关系格与群环简化；
“指定方向边”与“该点集所有实际单位边”始终是两种图。

16. **Cervantes–Krebs，Chromatic numbers of Cayley graphs of abelian
    groups: A matrix method，arXiv:2303.06262v2（2023-11-12）。**
    [原文](https://arxiv.org/html/2303.06262v2)；Linear Algebra Appl. 676 (2023)。
    已读 §2.1、Lemma 2.11：`Z^m/L` 描述有限生成阿贝尔 Cayley 图；每条
    整数关系的系数和皆为偶数，恰是发送所有方向到 `1∈F₂` 的特征可定义条件。
    T080 对 C015 的 14 个方向的无限二分性就是这个一般机制的精确实例，
    不是局部星图碰巧二分。额外诱导单位边或核心拼接不自动被此特征覆盖。

17. **Cervantes–Krebs，Chromatic numbers of Cayley graphs of abelian
    groups: Cases of small dimension and rank，arXiv:2303.06272v2
    （2025-09-20）。**[原文](https://arxiv.org/html/2303.06272v2)。
    已读引言及小矩阵分类范围：一方向、关系秩一，以及若干维数至三/关系
    秩至二情形。最优染色是否一般来自 circulant pullback 仍是问题，不能
    把小秩分类升级成所有阿贝尔单位方向图均有最优周期染色。

18. **Restricted CSPs and F-Free Digraph Algorithmics（ICALP 2025）。**
    [原文 §§1、3](https://drops.dagstuhl.de/storage/00lipics/lipics-vol334-icalp2025/html/LIPIcs.ICALP.2025.158/LIPIcs.ICALP.2025.158.html)。
    已读有限模板 `A,B` 的 restricted CSP 框架。HN 可用它精确表述“几何
    允许的输入族”，但 `U(R²)` 是无限源模板，有限 dichotomy 不直接分类它。
    pp 定义告诉我们关系如何组合；它不保证抽象 copier、clique 或任意
    限制关系可以在二维以单位长度和所需端口互异条件实现。

19. **Abrishami 等，Periodic colorings and orientations in infinite
    graphs，arXiv:2411.01951v2（2024-11-27；2025 发表）。**
    [原文](https://arxiv.org/html/2411.01951v2)。已读 Theorem 5.2、§5.2。
    准传递且有界 pathwidth 等假设下存在相应最优周期染色；一般准传递图
    或非阿贝尔 Cayley 图的反例不能直接用作本项目阿贝尔宿主的反例。
    一般 SFT 的非周期性也没有自动回答“由 proper coloring 特殊规则定义
    的 SFT 是否周期”。固定周期 SAT 的 UNSAT 仍只排除该周期。

20. **Zaslavsky，Totally frustrated states in the chromatic theory
    of gain graphs，作者稿 2008-03-24；European J. Combin. 30 (2009)。**
    [原文](https://people.math.binghamton.edu/zaslav/Tpapers/tfs.pdf)，已读 §§1.1、2.6。
    gain 必须明确作用于 spin 集。几何位移 gain 和颜色置换 gain 不是同一
    数据；`k≥3` 时“不等色”是多值关系，不是可逆单值传输。一般 state
    count 不由 frame matroid 决定。因此合理统一对象是带几何标签的颜色
    关系网络，只有证明了真正的置换作用后才可压缩成 holonomy。

21. **Tyszka，Discrete versions of the Beckman–Quarles theorem，
    arXiv:math/9904047；Aequationes Math. 59 (2000)。**
    [原文](https://arxiv.org/pdf/math/9904047)。已读 Theorem 1、逼近引理及 Remark 1。
    代数距离有有限单位距离强制装置，提供 rigid realization 工具。
    整个平面的保单位距离自映射必须为等距映射，所以把全平面同态压到
    真正的平面真子集，作为上界方法，本来就受几何刚性阻挡；抽象颜色目标
    `K_k` 并不是要求嵌在平面的单位图，不受这个反证直接排除。

22. **Pach–Raz–Solymosi，Erdős’s Unit Distance Problem and Rigidity
    （SoCG 2026）。**
    [原文 Theorems 5–8](https://drops.dagstuhl.de/storage/00lipics/lipics-vol367-socg2026/html/LIPIcs.SoCG.2026.83/LIPIcs.SoCG.2026.83.html)。
    已读近 `n^(4/3)` 单位距离计数与刚性结构的结果及条件。
    rigidity matroid 衡量长度约束的独立性，不直接衡量五染色关系的排除力。
    六临界图的必要边数只有线性量级，不能假设潜在六色见证落在近极值密度
    定理的范围；稠密构造也可能二分或五色可染。

23. **Alon–Briceño–Chandgotia–Magazinov–Spinka，Mixing properties of
    colorings of the Z^d lattice，作者在线稿（访问 2026-09-09）。**
    [原文](https://web.math.princeton.edu/~nalon/PDFS/mixing4.pdf)。
    既有核验：§1 冻结定义，§2 Propositions 2.1、2.4 及证明。
    冻结、不能有限支撑修改、唯一染色和不存在染色是不同命题。
    标准整数格的 mixing/修复定理不能不经核验移植到 Parts 阵列。
    对本项目真正有用的是精确指定边界条件和允许修改集合，再证明延伸性质。

24. **Kiss–Laczkovich，Solutions to the discrete Pompeiu problem
    and to the finite Steinhaus tiling problem，
    arXiv:2403.01279v3（指定版本访问 2026-09-10）。**
    [原文](https://arxiv.org/html/2403.01279v3)。已读主要定理与推论。
    非零总权的有限加权配置若在所有刚体副本上满足零和方程，可迫使函数
    恒零，且无需可测性。这是有力的“所有副本”工具；总权为零的 copier
    差分不在假设内。消掉这一总权条件等于改动定理，不是一个记号简化。

## 四、赋值、分圆支撑、S-unit 与 CM 塔

这一组最容易发生目标偷换。单位距离是选定实嵌入下的 `z bar(z)=1`；
数论的“unit”也可能只是可逆元或 `S`-unit。宿主整体色数受剩余域与
各向异性控制，而边数可受根判别式、完全分裂素数和范数一元的数量控制。
它们是可相互独立的结构量，不是同一“代数复杂度”。

25. **Madore，The Hadwiger–Nelson problem over certain fields，
    arXiv:1509.07023v1（2015-09-23）。**
    [原文](https://arxiv.org/html/1509.07023v1)。已读 Proposition 3.2 的
    赋值/积分陪集证明、F11 五色表所在 §4 及 §5.4 的实闭域转移。
    这统一了 T028 后大量正染色：先证明单位位移坐标在赋值环中，再约化到
    有限目标，最后分别处理积分加法陪集。`χ(R²)=χ(A²)`，其中 `A` 为实
    代数数，给出正确的代数共尾目标；一个固定数域、所有多二次域、甚至
    任意高次数的一族可染数域，都不因此覆盖所有有限实代数配置。
    2026-09-11重读¶2.2的环同态保单位与¶1.3紧致性；本地T090据此
    给出纯超越专门化证明和有理模板例外边筛选。未将该推论冒称
    原文已单列的定理，也未据此关闭代数扩域。

26. **Milne，Fields and Galois Theory，v5.10（2022-09）。**
    [原文](https://www.jmilne.org/math/CourseNotes/FT.pdf)，已读 pp.71–73，
    Theorem 5.23、Corollary 5.25 的 Hilbert 90 及证明。
    二次共轭扩张中范数一元可写成 `a/bar(a)`；它统一生成旋转的坐标公式。
    参数化范数一群不等于理解其加法关系，更不等于颜色分类。
    HN 的循环约束同时使用乘法范数和加法闭合，这是下一步必须面对的接口。

27. **Milne，Algebraic Number Theory，作者在线课程讲义。**
    [原文](https://www.jmilne.org/math/CourseNotes/ANT.pdf)，本轮已读
    Theorems 3.7/3.29，Proposition 6.2(b,c) 及证明（PDF pp.50、58、97–100），
    并核验 §8 的二次互反应用。使用的是 Dedekind 理想分解、素数幂分圆域
    的分歧与剩余域等成熟事实。T077 的 127 主素理想及 T078 的局部染色
    在本地具体展开，不假定类数一，也不宣称分圆理论的新颖性。

28. **Turyn，Character sums and difference sets（1965）。**
    [原文](https://msp.org/pjm/1965/15-1/pjm-v15-n1-p32-p.pdf)，已读 pp.321–323，
    Lemma 1、群代数等式 (4)、(5)。difference set 的非平凡特征值范数由
    `k−λ` 控制，解释分圆支撑中出现的常模 Fourier 图样。
    T079 应抽象为群环自相关/范数恒等式，而不是某个系数列表的巧合。
    常模谱既不强制加法关系奇性，也不强制色数高；必须回到实际方向关系格。

29. **Lam–Leung，On Vanishing Sums of Roots of Unity，
    arXiv:math/9511209（1995 预印本；2000 发表）。**
    [原文](https://arxiv.org/pdf/math/9511209)，已读 §2 Theorem 2.2 及群环核证明。
    分圆消失和把“为何有方向闭合”变成支撑与素因数的代数问题。
    正整数权消失和的限制不能照搬给任意数域系数；扩张后的相对次数与
    交域必须先算清楚。对当前 `F=Q(i,√3,√5,√11)`，`ζ5∉F`，
    `F∩Q(ζ5)=Q(√5)`，相对次数为 2；7 只是首个保持完整相对次数 `p−1`
    的奇素数，不是跳出 `F` 的最小选择。

30. **Evertse–Schlickewei–Schmidt，Linear equations in variables
    which lie in a multiplicative group，Annals 155 (2002), 807–836。**
    [原文](https://arxiv.org/pdf/math/0409604)，已读 pp.807–809，Theorem 1.1。
    特征零、固定有限秩乘法群中的非退化线性方程解数有统一有限界。
    可迁移任务是固定方向乘法秩与循环长度后，分类不可分解的加法闭合关系。
    总体 HN 没有固定该秩或长度；退化子和也须递归处理。定理没有提供一个
    已实现的、可直接终止所有坐标搜索的有效高度界。

31. **Győry–Hajdu–Tijdeman，Representation of finite graphs as
    difference graphs of S-units I，arXiv:1408.5873（2014）。**
    [原文](https://arxiv.org/pdf/1408.5873)。已读 §§1–6 的主要陈述与 §8
    中 Theorems 2.1、3.1、5.1、6.1 的相关证明。
    S-unit difference graph 为数论与图表示提供成熟框架，但差属于可逆元
    并不等于在选定复嵌入下模长为一。任意有限图的某种 S-unit 表示定理
    不能转换为任意有限图的二维单位距离表示定理。

32. **Lorenz–Zimmermann，Cliques in representation graphs of
    quadratic forms（2026-01-06）。**
    [原文](https://link.springer.com/article/10.1007/s10801-025-01493-5)。
    已读 Definition 1.1、Theorems A–C、§1.3。
    把单位图放入二次型 representation graph 的大类很自然，也便于辨认
    局部域不变量。但这里的 local-global 结论针对 clique；平面六色图
    不需要六团，不能用团数分类代替色数分类。

33. **Alon–Bloom–Gowers–Litt–Sawin–Shankar–Tsimerman–Wang–Wood，
    Remarks on the disproof of the unit distance conjecture，
    arXiv:2605.20695v1（2026-05-20）。**
    [原文](https://arxiv.org/html/2605.20695v1)。已读 Theorem 1.1、§2.1
    及范数一元到有限窗口的关键引理。
    CM 数域、低根判别式和完全分裂素数构造 `n^(1+ε)` 单位距离对。
    这是 Erdős 单位距离**计数**问题的突破，不是 HN 的突破。本地 T081
    检查其原始奇素数分歧塔保留了二进制染色机制；大量边可以出现在整个
    二色可染宿主中。

34. **Sawin，An explicit lower bound for the unit distance problem，
    arXiv:2605.20579v1（2026-05-20）。**
    [原文](https://arxiv.org/html/2605.20579v1)。已读 Theorem 1、相关
    Lemmas 2–12、Proposition 10 和 Lemma 11 的证明。
    明确得到 `n^1.014` 计数；关键量是根判别式与小分裂素数的贡献。
    从窗口归一化回指定 CM 宿主时必须除以实际范数为 `α` 的元 `β0`，
    不能未经检查地只除以 `√α` 而离开该域。本地 T083 另保留安全的 11
    处，说明任意高次数、超线性单位边密度和整个宿主恰五色可以共存。

35. **Hajir–Maire，Asymptotically Good Towers of Global Fields，
    ECM 2000 会议论文，2001 发表，pp.207–218。**
    [原文](https://www.math.uni-bielefeld.de/~rehmann/ECM/cdrom/3ecm/pdfs/pant3/maire.pdf)，
    本轮已直接读 §2，Theorems 2.2、2.4 及其前置假设。
    数域的分裂集合 `S` 包含所有无穷处；允许分歧集合须满足所列 tame 条件。
    对不分歧 pro-2 塔，T083 使用 `|S|=5, θ=1, d≥7`，
    `r−d≤5`，并以 `7≥2+2√6` 确保无限性。把实处漏出 `S` 会错误地
    改变关系秩预算。原 PDF 已缓存为 `cache/hajir-maire-2001-towers.pdf`；
    数值参数的独立检查不替代此深定理。

36. **Medrano–Myers–Stark–Terras，Finite Euclidean graphs over
    rings，Proc. AMS 126(3) (1998), 701–710。**
    [作者上传原文](https://www.researchgate.net/publication/246193320_Finite_Euclidean_graphs_over_rings)，
    DOI `10.1090/S0002-9939-98-04294-4`。既有核验 Theorems 2.1、2.3
    的度数和旧谱递推；出版社 PDF 请求 403，未完成该 PDF 的视觉核验。
    高阶剩余环上的 Euclidean 图谱是成熟对象。本地一般 DVR 的末层相消
    是具体证明，不把非 Ramanujan 性、谱界停滞或大剩余域等同于低/高色数。

37. **Conrad，On Weil's proof of the bound for Kloosterman sums，
    作者讲义（访问 2026-09-09）。**
    [原文](https://kconrad.math.uconn.edu/articles/kloosterman.pdf)。
    既有直接渲染核验 pp.1、4、5，Theorem 3 的安全界是 `2√q`。
    仓库没有重证其中的 Riemann hypothesis 输入。它纠正了使用某些有限
    unit-quadrance 文献所印 `√q` 常数的风险；有限正表和精确谱校准都
    应独立于这类排印问题。相应 T053/T056 结论不能被外推到所有非线性目标。

## 五、拓扑、可测性、范数与“几乎染色”

这些邻近问题有真实而有力的结果，但假设变化不是无关紧要的技术细节。
原始 HN 不允许默认可测、局部有限边界、正厚度距离禁区或周期性。

38. **Falconer，The realization of distances in measurable subsets
    covering R^n，JCTA 31(2) (1981), 184–189。**
    [原作者机构入口](https://research-portal.st-andrews.ac.uk/en/publications/the-realization-of-distances-in-measurable-subsets-covering-rn/)，
    [出版社](https://www.sciencedirect.com/science/article/pii/0097316581900145)。
    证据：书目及摘要已核验，原始证明未取得并检查，明确保留此缺口。
    这是可测五色下界的经典来源，不是普通染色六色下界来源；当前普通五色
    结果已不需可测性。不能把后来的可测密度论证当作其原证明已重放。

39. **Voronov，The chromatic number of the plane with an interval
    of forbidden distances is at least 7，arXiv:2304.10163v3（2025-04-13）。**
    [原文](https://arxiv.org/abs/2304.10163v3)。
    已核验正宽度禁止距离区间所需七色的范围。
    固定 `ε>0` 的稳健染色与只禁止精确距离 1 的问题不相同；
    即便对每个正 `ε` 都证明七色，也不能在 `ε→0` 时无条件保留下界。
    这是对连续/稳健模板的屏障，不是原始 HN 七色的证明。

40. **Sokolov–Voronov，On the chromatic number of the plane for
    map-type colorings，arXiv:2502.01958v1（2025-02-04）。**
    [原文](https://arxiv.org/abs/2502.01958v1)。
    本轮进一步核验 Theorem 2 的局部有限 polygonal 范围，以及 Theorem 1
    的 Jordan 区域、顶点和单位圆有限交等附加条件。
    七色结论排除的是这类 map-type 上界方案；它不排除任意可测六染色，
    更不排除所有非可测六染色。旧来源记录的“仅摘要”不能被用来伪称已经
    独立重证全文，这里也只声明所列定理范围被检查。

41. **Gehér，Note on the chromatic number of Minkowski planes:
    the regular polygon case，arXiv:2301.13695（2023）。**
    [原文](https://arxiv.org/abs/2301.13695)。
    已核验正偶多边形范数、边数至 22 的六色构造范围。
    改变单位球会改变所有禁止位移；与圆接近不代表精确单位圆约束得到保存。
    可迁移的是边界设计思路，不是欧氏六色结论。

42. **Mundinger–Pokutta–Spiegel–Zimmer，Extending the Continuum
    of Six-Colorings，arXiv:2404.05509v1（2024-04-08）。**
    [原文](https://arxiv.org/abs/2404.05509v1)。
    已核验 off-diagonal 六色构造：五种颜色禁距离 1，第六种禁另一个距离
    `d∈[0.354,0.657]`。`d=1` 不在该区间；标题中的 six-colorings 不是
    原始 HN 的六色上界。值得借鉴的是从数值图形提取可证明的边界公式。

43. **Mundinger 等，Neural Discovery in Mathematics: Do Machines
    Dream of Colored Planes?，arXiv:2501.18527v3（2025-06-05）。**
    [原文](https://arxiv.org/abs/2501.18527v3)，ICML 2025。
    已读 §4.1：形式化的 almost-five-coloring 留白约 3.7356%，不能和
    数值观察约 3.60% 混为一项已证明结果。神经网络可提出候选，最终必须
    独立检查连续区域之间全部距离约束；训练损失、小面积缺口和采样通过
    都不能填上全域量词。

## 六、概率修复与列表染色：需要真实余量

44. **Moser–Tardos，A constructive proof of the general Lovász
    Local Lemma，arXiv:0903.0544v3（指定版本访问 2026-09-10）。**
    [原文](https://arxiv.org/html/0903.0544v3)。既有核验 §1
    Theorems 1.1、1.2。坏事件必须有明确独立变量、概率与依赖图；本地
    `D≤22, x=1/23` 的算术检查只服务于实际满足这些假设的模型。
    假定 palette activation 或假定随机选择独立后才成立的 obstruction
    不是原始 HN 下界。若模型没有足够余量，应更换局部构造而不是省略依赖。

45. **Rabern，A different short proof of Brooks' theorem，
    arXiv:1205.3253v5（指定版本访问 2026-09-10）。**
    [原文](https://arxiv.org/html/1205.3253v5)。既有核验 Theorem 2
    列表版本及证明：`χ_l≤max{3,ω,Δ}` 的适用对象和名单大小必须保持。
    普通三染不能代替非均匀可用颜色名单的延伸定理。项目的端口删除、背景
    修复与调色板分割应首先被写成准确的 list-coloring 实例，再选择成熟
    定理；更多有界调色板与 independent transversal 原文及范围见 SOURCES。

## 七、从边数到任意固定图形的副本计数

46. **Bhattacharya–Goenka，Congruent copies of finite patterns in
    planar point sets，arXiv:2606.27352v1（2026-06-25）。**
    [原文](https://arxiv.org/html/2606.27352v1)。已读Theorem1.1、
    Proposition2.1与构造入口；未声称全文证明本地重放。对任意固定至少
    两点的有限平面图形，有超线性多份全等副本的点集：固定正指数在无穷
    多规模成立，缩小指数后覆盖所有充分大规模。它将CM计数推广到固定
    motif，而非把该motif的五色关系放大到非五染。指数的算术依赖也未
    被证明是图形的内在必要不变量；大量Parts副本不自动产生activation。

## 参数为何出现：哪些是坐标，哪些是不变量

E061–E062的新增收敛见[完整划分与色框天花板](../docs/proofs/joint_word_closure_and_frontier.md)。
这里“五次旋转”还有一层必须与坐标域分开的含义：素数轨道长度与有限
调色板/概率支持的相容性。T094对任意奇素数p≥k都成立，并非ζ5特有。
其机制是群作用的固定点、轨道和凸平均，不是单位边变多；固定色框或
固定支持数的失败因此没有HN负证据资格。Dúcz–Varga的可迁移步骤仍是
完整可行面的精确分离，不能以极点或有限样本筛选替代。

`K=Q(√3,√5,√11)` 的意义是当前精确核心的一个小坐标宿主；其次数和根号
表示依赖选择，整体五色的关键却是某个安全赋值处上的各向异性约化及
有限目标。11 不是宇宙常数：它同时兼容这些二次剩余条件并给出实用的
五色有限图。换坐标不会自动破坏这个图同态，必须检查实际域和所有单位边。

13/23 来自同一个有理圆锥曲线 `4x²−3y²=1` 的不同参数值。
在二壳中心构造中 `x²=1−3β, y²=1−4β`，故系数 3、4 是三角格所选
二壳的平方半径，分母 13、23 不是两种基本现象。C016 的标准库检查器
独立校准了多个有理参数，防止把一个漂亮分母过拟合成必要条件。

127 在七次分圆局部分类中承担的是完全分裂、剩余阶和特定主理想证书的
角色；其不可替代性若被声称，必须另外证明。分圆方向应首先看交域、相对
次数、共轭范数、支撑差集及整数关系，而不是“更多旋转角度”这一单调直觉。
尤其 `ζ5` 已是当前复域的二次扩张：C016 只用三个单位方向就阻断整个
`F`-线性保范数投影，同时这三个指定方向的无限图仍是 `Z³` 型二分图。
最小投影反例恰好展示了“方法失败”和“染色困难”的分离。

同样，CM 塔的高次数与超线性边数不替代颜色关系。本轮 T081/T083 将
稠密性参数和安全局部染色处放在同一构造中，直接淘汰“稠密/大次数本身
使宿主离六色更近”的推断。保留这条数论路线的合理理由，是它能提供新的
加法关系和可控制的几何端口，而不是因为计数纪录更新了。

## 收敛后的成熟问题与下一次证据门槛

2026-09-12 接续：[T108–T109](../docs/proofs/quintic_residue5_ring.md)的
625 点范数图经 `B≅F₂₅×F₂₅` 与共轭交换两分量，恰化为 HG(F₂₅)。
已对照 [Iosevich–Murphy–Pakianathan](https://arxiv.org/html/1405.7657v1)
的 hyperbola / Kloosterman 语言与
[Bardestani–Mallahi-Karai §2.4](https://arxiv.org/html/1507.05300v2#S2.SS4)
的二次型图。这里的 12 个字符是精确有限结构，不是待相信的新机制名。
后者 Theorem1.9 的局部域结论含 Borel 限制；不能拿局部 split 范数
的 Borel 障碍充当普通欧氏非五染。具体版本和阅读层级见 SOURCES。
新的真实缺口在 5 分母跨层：环 R 内已全体五染，τ∉R 的第一有限
并集也正修复；接下来须获得跨层全词证据或无条件延伸定理。

当前唯一优先级以[CURRENT](../docs/CURRENT.md)和[统一框架](../docs/proofs/hn_unified_framework.md)
为准。下列是文献提供的工具门槛，不另设四条活动分支：

- **低复杂度扩域后的真实颜色关系。** 给定已经认证五色的核心，加入
  `ζ5` 等低相对次数旋转，计算全部实际单位边和完整五色端口关系。
  正结果须提供覆盖诱导边的染色/图同态；负结果须给出检查过的 UNSAT
  证书。C016 投影失败和 C015/T080 方向二分性是筛选条件，不是负证据。
- **关系谱的共尾延伸定理。** 上界需要某一类宿主覆盖所有有限实代数
  单位配置，或提供直接对所有有限配置成立的延伸法。任意高次数的可染
  塔不等于共尾；无界的样本序列也不等于全部数域。必须明确哪条统一引理
  将小范围正结果提升到这个量词。
- **整数兼容性的有限对偶。** 对六色下界寻找保留完整五色联合支持的
  有限不相容关系，避免只增强已被分数色数上界封顶的指标。
  join-tree、pp 定义和不变平均提供语言，不负责生成几何可实现的矛盾。
- **范数一加法循环的分类。** 固定扩域和受控方向乘法群，用 S-unit /
  群环 / valuation 排除或认证真正的循环关系；先检测奇偶特征等廉价
  全局正解。若所有指定方向闭包仍二分，就停止仅复制这些方向，转而寻找
  实际新增单位边与核心状态之间的耦合。

停止规则同样明确：固定编码失败、周期商失败、投影失败、条件 activation
obstruction、稠密性或 `UNKNOWN` 均不能计入 HN 下界进度。文献重审的成果
是把这些障碍归入成熟机制并用反例淘汰错误推断；是否已有原问题突破，仍
由一个完整的新全域上界证明或一个真正需要六/七色的有限单位图决定。


## 2026-09-12：有效见证、稀疏关系与编码延拓的收敛补充

以下为原文范围核查及本轮实际验证。Q009 已由 E080 正修复；当前
优先级以 CURRENT 为准，不把本节来源清单视为额外活动路线。

### 新鲜度与见证尺度

Haugland 的 [arXiv:2608.04542v4](https://arxiv.org/html/2608.04542v4)
仍将一般五色最小已知阶记为 509；其 2131 点无 Moser spindle 构造不是该类
最小纪录，v4 已承认 Heule 的 1441 点先例。它否定 spindle 是所有五色构造的
必要核心，但并不提供新的五色状态强迫机制可直接升为六色。

此前地图遗漏了 de Grey–Parts 的
[On lower bounds of the order of k-chromatic unit distance graphs,
arXiv:2303.14714v1](https://arxiv.org/html/2303.14714v1)。本次读完三页原文。
其报告值为 `v5 ≥ 28, e5 ≥ 99, v6 ≥ 42, e6 ≥ 182`；论文也重复
`v7 > 6992`。这里 `vr` 表示 r 色见证的点数，故 non-5 对应 `v6`，
不能把 `v7` 的阈值错配给 non-5。

该短文的技术价值是把单位边的平均单色概率 `p_(r-1)` 转为边数限制，
再经精细单位距离计数不等式转为点数限制。但其积分部分描述了
Mathematica/NIntegrate，并未附本项目可重放的区间积分证书；本稿把上述
新数值列为“原论文报告、原文范围已读”，不升级为本地独立认证的界。

已知局部复杂度不应被排列为单一进度条：点数、列边数、诱导边数、
最小实代数编码长度、最小点间距、特定证明系统中的反证长度，是六个
不同参数。T113 的不变律支持数又是第七种参数，不能替代其中任一个。

### 真正的坐标精度障碍，以及它没有证明什么

Marcus Schaefer 的作者稿
[Realizability of Graphs and Linkages](https://ovid.cs.depaul.edu/documents/realizability.pdf)
对应 2013 年 Springer 论文。本次直接读 §2.2–2.3、§3.1 的定理与相关
证明：Corollary 2.7 给出严格与非严格单位图识别的 `∃R` 完全性；
Corollary 2.9 给出 n 点单位图族，任何单射单位实现中都有两点距离
至多 `2^(-2^(c n))`，其中 c 为正常数。Theorem 3.1 进一步表明，允许
非邻顶点碰撞的单位 linkage 可实现性仍是 `∃R` 完全问题。

这里两条不能合并：Corollary 2.9 的强迫精度量词针对单射实现；
Theorem 3.1 则允许碰撞。后者恰好匹配本项目的单位同态搜索，说明
“允许碰撞”虽排除了伪几何反证，却没有一般性地消掉可实现性难度。

这些是一般输入族的最坏情况结果，不是最小 non-5/non-6 见证的精度下界。
`∃R` 完全性也不是不可判定性，不排除特定结构输入有简单算法，不能
从某次拟合困难推断当前图不可实现。原文的 matchstick 讨论属于当时版本；
本稿不把 2013 年列出的其他开放题宣称为 2026 年仍开放。


### 有效性与逻辑：已抽出自足证明

[T115 完整证明](../docs/proofs/hn_effective_witnesses.md)给出固定 n 的
可计算实代数编码上界与近单位间隙，以及原始 HN 的 Σ1 下界／Π1
上界翻译。保持 ω 的 forcing 不能改变答案；若真为7便有 ZFC
证明。没有据此证明实际独立性或控制最小 non-5 见证的 n。

[Jeronimo–Perrucci–Tsigaridas, arXiv:1112.0544](https://arxiv.org/pdf/1112.0544)
的 Theorem 1 给整数多项式在紧连通基本闭半代数分支上非零最小值的
显式界；本轮读完定理假设，未实施长常数公式。K4误差下界2/3另有
T115内完整平方恒等式，不依赖数值最优化。

### 稀疏高围长 lifting：成熟的颜色关系放大与二维阻挡

Bucić–Davies 的最新已核验版本为
[Geometric graphs with exponential chromatic number and arbitrary girth,
arXiv:2312.06898v3](https://arxiv.org/html/2312.06898v3)，2024-10-17。
本次读完 §3 的 Proposition 6、Theorem 8 及证明和 §4 的维数限制。
对固定 `(G,g,k)`，Theorem 8 构造高围长 `G′→G`，使 G′ 的每个 k 染色
都能在各纤维出现的颜色名单内选出 G 的 k 染色。若取 `k=χ(G)-1`，
它与同态一起确保 `χ(G′)=χ(G)`。v2 未清楚写出固定 k 的外层量词，
v3 已明确修正；本稿不使用“一个 G′ 同时对任意 k 完备”的更强读法。

机制不是低阶一致性压缩成小障碍，而是相反：经高色高围长超图，将
不可染性分散到许多局部近似森林的纤维匹配中。它说明一般 CSP 的
少量短圈、固定 gadget 或局部视野不承担全部强迫关系。

但其几何 lifting 用球面正交表示的维数翻倍，从 `R^d` 到 `R^(2d)`。
**不能把该步骤省掉而声称得到二维六色图。** 最小反例无需计算：
完整平面单位 `K_(2,3)` 不可单射实现，因为两个不同圆心的单位圆
最多有两个公共点，而右部要求三个不同公共点。允许重合则可二色折叠，
故它也不能用来排除一般单位同态。维数翻倍和顶点互异两项均必须保留。

论文对高围长性质还只承诺列边子图；它明确不承诺其点集**全部实际单位边**
仍高围长。作为下界证据列边足够，作为“诱导图局部像森林”的结论则不足。

收口时补齐了 O'Donnell 的
[1999博士论文原扫描](https://jakemallen.com/papers/odonnell1999.pdf)，
并亲读印刷p.5、pp.13–15、25–26、31–32；p.26还直接看图核对≥符号。
Theorem28对每个k≥3给围长恰k、χ恰4的单射平面单位距离图。
但p.5仅规定边⇒距离1，proper仅指顶点互异；Theorem11只去点重合，
不排除额外单位对。因此安全结论是**列边子图**，不是诱导单位图任意围长。

[T119短推论](../docs/proofs/finite_joint_support.md#8-列边单位图类的真正小障碍天花板t119)
据此排除该列边／单位同态许诺类的统一有界大小non-3子图或前向同态障碍：
取围长>N，至多N点的子图都为森林；非3染F的短奇圈也不能同态进去。
补齐全部实际单位边可能引入小圈，故诱导图版本未由此证明；non-5/non-6
更不能越级套用。这里取得的是一条准确的结构天花板，不是HN下界推进。


### 本轮新增成熟连接：MacWilliams 延拓准确隔开二点与完整 joint

针对 m 个等权 k 色词，把每个几何点的颜色向量看作 `[k]^m` 中的码列。
保持全部二点同色计数，恰好是相应有限码映射保持 Hamming 距离。
在全局 S_k 平均后，完整 joint 则等价于 m 个坐标分划多重集相同，
也等价于映射可延拓为统一坐标置换与逐坐标字母置换。
三个等价的直接证明及全 Hamming 等距分类的短证明见
[完整证明](../docs/proofs/hamming_joint_extension.md#1-三个不同命题)。
等权、几何点标号不动、颜色平均、重复码列先商去，均是明确条件。

原文入口为 Jay A. Wood 的 2011 年会议作者稿
[Applications of finite Frobenius rings to the foundations of algebraic coding theory](https://ring-theory-japan.com/ring/oldmeeting/2011/report2011/27WOOD.pdf)，
本次已读 §5.1 Definition 29 / Theorem 30 与 §5.2 完整字符证明
（印刷 pp.236–238）；不是声称读完 MacWilliams 的 1962 年博士论文。
另核对 [Greferath 等，arXiv:1309.3292v1 §1–2](https://arxiv.org/html/1309.3292v1)
的线性假设；其 HTML 动态 Date 不作发表日期。

准确的有限域定理是：**整个线性码上的线性保重量映射**延拓成单项变换。
因此可用于“二点压成 joint”的是已证明为线性或仿射的码映射；
不能把任意有限码点集合放入 span 后就略去缺失的 span 权重等式。
证明文档还给出有限域字符的自足证明。当前五词模型可在 F5 上检查
样本线性关系，再穷举最多 `5^5=3125` 个 span 向量的重量，以得到
一个严格的充分判据；失败只关闭该补全模型，不是全词 joint 障碍。
不能把五颜色或四个码点偷换为 F4 线性码。

两个最小尺度校准均已直接重放，且各有不变量证明：

- **码点数最小是 3：** `000,110,101 → 000,110,220`，每对距离均为 2，
  但坐标分划由 `{011,010,001}` 变为 `{012,012,000}`；两个及以下码点
  总可延拓。此例码长 3，可补零成为 F5 的五词校准。
- **码长最小是 2：** `00,01,22,23 → 00,01,22,32`，六对距离全相同，
  分划却为 `{0011,0123}` 与 `{0012,0122}`；码长 1 总可延拓。

因此二点、三点和整个联合不是可凭直觉混同的层次。第一例若由 proper
词实现，它的三个几何点必为独立集，故尤其不构成高色单位图。

对 T109 必须避免倒推：既有证明直接给出 12 字符的统一置换，所以
已经有完整 joint；并不是只验证二点后调用 MacWilliams。环上线性
字符不保证某个物理有限域的码点闭合，也不保证新部分运动在线性 span
上保重量。此连接只给一个可立即证伪的候选工具，不追认新低阶完备性。


### 局部不变律与共尾算术的实际落点

[Chazottes–Gambaudo–Hochman–Ugalde, 1011.2442v2](https://arxiv.org/html/1011.2442v2)
的局部不变多面体／一维 Markov 延拓解释了有限循环流，但其整数整窗
与全部平移条件不能套到稀疏 Y。[Atserias–Dalmau, Corollary 1](https://arxiv.org/pdf/2107.05886)
排除一般近似图染色的有界和次线性一致性宽度，不排除二维单位图的
专门结构定理。T114的等权表示与固定支持小事件界分别标明范围。

[E082](../docs/proofs/cofinal_residue29.md)将当前 L 的稳定素点方法
收敛到唯一小目标29，排除全部一维线性投影捷径；5/6色自由 SAT
均 UNKNOWN。√2 扩域破坏唯一小稳定处，说明这条完整剩余目标法
不能无条件共尾。反过来，T116的2处配对分裂产生HG(F16)与整个
2整环的4色公式；它未覆盖 Parts 的分母层。29、16、25的作用来自
分解群、共轭和范数商，不是新的神秘几何常数。

继续执行后，[T117](../docs/proofs/dyadic_finite_precision_ceiling.md)
将有限域范数图推到全部 Galois-ring 精度：真实可提升方向经赋正权，
各赋值层具有相同度数；Kloosterman 和的高导子消去及 Hoffman 界
给 Aₙ 所有有限精度编码的6n+4天花板。CRT／共轭比值证明方向确能
逐个在全局数域实现，却不给同时实现所有目标闭环的平面图。
这里“局部到全局逐方程可解”与“整份关系网络可解”的差别，是和
几何承诺 CSP 真正共享的结构，而非把有限目标高色倒灌到源图。

[T118](../docs/proofs/dyadic_marginal_rigidity.md)再利用 Hoffman **取等**
而非更大数值优化，证明最优有限精度四色下降到单个HG(F16)因子；
轴向 Fourier 频率缺失使每条轴每色恰四点。完整陪集邻域因此给
固定边际至少八色的相对延拓障碍。34点实际二色校准说明，这种漂亮的
谱刚性仍不是普通下界。至此停止纯有限2精度与固定四调色板路线，
转回跨素点的自由完整关系；不继续把更多局部谱定理当作原问题进度。
