# R2026-POTTS-GAP：平面χ=7等价于六色单位针能量具有严格正的热力学下界

日期：2026-11-07。**本报告不是χ=7的证明**，而是可用作真正证明目标的必要且充分数学转移。依赖：de Bruijn–Erdős有限图紧致性、OpenAI Family158任意有限k的ordinary↔weak measurable转移、概率Hadwiger–Nelson已有随机针思想与标准有限minimax。对已有概率思路不主张文献原创性。

## 1. 外部远领域的结构相似度

- **概率型Hadwiger–Nelson，直接同一数学对象**：Gwyn–Stavrianos，2020，https://arxiv.org/abs/2008.07987；Bourgeat–Heinrich–Melotti–Robert，2015，https://people.csail.mit.edu/bthom/hadwiger.pdf 。随机单位线段同色概率badness、有限图到积分下界已有成熟文献。本页的新整理是在2026已证的任意k weak-measurable转移下，写出6/7的双向等价与完整积分边界。
- **反铁磁Potts零温基态，准确的物理对象**：Shevchenko–Tanashkin，2022，https://doi.org/10.1016/j.jocs.2022.101607 。q种自旋标签，距离为1时同态自旋产生成本；q=7蜂窝完全零能基态，q=6是否存在严格正残余能隙与HN恰同一问题。模拟带长度容差及有限随机格不是数学证明。
- **层论/上下文性（sheaf/contextuality），相同全局量词但不同约束**：Abramsky–Brandenburger，https://arxiv.org/abs/1102.0264 。有限窗口各自可行不保证共享同一全局section；其非零上同调只是某些模型的充分不相容证书，不能把任意一份固定伪联合律无法延拓冒充对全部六标签的排除。
- **非周期Wang拼图/符号动力系统，严格的路线禁区**：Berger非周期SFT，https://link.springer.com/article/10.1007/s00224-021-10063-8 。一般二维局部规则可有解但没有周期解；所以从找不到周期六染不能直接推出普通六染不存在，也不能由简单七色周期解猜想一切候选都必须近周期。这不是说HN问题本身不可判定。
- **几何高围长、局部和整体分裂**：Tomon 2026 https://arxiv.org/abs/2610.03517 。若χ=7，存在任意大围长、χ7的有限单位图：所有固定小子图是2色的，却整体有严格正六色坏边能量。
- **集合论**：Shelah–Soifer关于其他差集图的选取公理依赖，https://doi.org/10.1016/j.jcta.2004.10.004 。不能误报原单位距离图的6/7已经被证明独立；χ=7一旦有有限代数证书便不依赖对全平面无穷点选择着色的额外假设。

## 2. 有限方形零温六态单位针能量

令Q_L=[−L/2,L/2]^2、u_θ=(cosθ,sinθ)。对任意Lebesgue可测标号c:Q_L→{1,...,6}定义
\[
E_L(c)=\frac1{2\pi L^2}\int_0^{2\pi}\int_{Q_L}
{\bf1}_{x+u_\theta\in Q_L}{\bf1}_{c(x)=c(x+u_\theta)}\,dx\,d\theta,
\quad e_6(L)=\inf_{c\ {\rm measurable}}E_L(c).
\]
跨越Q_L边界的单位段的被积函数按0处理。这是完全可测、非负的**精确单位距离**冲突比例。

**定理A（定量有限图转移及6/7二歧）**
\[
\boxed{\chi(\mathbb R^2)=7\quad\Longleftrightarrow\quad
\liminf_{L\to\infty}e_6(L)>0.}
\]
若χ=6，则e_6(L)=0对每一个L成立。若χ=7，取一张有限平面不可六染**精确单位边**图H=(V,E)，边数m>0；可把坐标平移至所有点p_i满足|p_i|≤R，则
\[
\boxed{E_L(c)\ge\frac1m\left(1-\frac{2R}L\right)^2\quad (L>2R)}
\]
对全部可测六标签c同时成立。L≥4R时甚至E_L(c)≥1/(4m)。

证明：若χ=6，由OpenAI Family158的Theorem1.3取得一份weak measurable六标签a:ℝ²→[6]，其单色单位事件在位置×圆周测度下为零。将a限制到Q_L，非负积分仍0，得e_6(L)=0；**a不一定是点态合法的可测染色**。

若χ=7，de Bruijn–Erdős紧致性提供有限不可六染单位图H。任取L>2R、任意t∈Q_{L−2R}、θ，所有t+Rotθp_i都落在Q_L，且总有至少一条H边同色：
\[
1\le\sum_{ij\in E}{\bf1}_{c(t+Rot_\theta p_i)=c(t+Rot_\theta p_j)}.
\]
在t∈Q_{L−2R}与θ∈[0,2π)积分。对每条边ij，换元x=t+Rotθp_i、角度φ=θ+arg(p_j−p_i)，单位边另端点为x+u_φ；积分区域是Q_L单位段集合的子集，Jacobian为1，因此每条边的积分最多2πL² E_L(c)。左侧为2π(L−2R)²，故(mL²)E_L(c)≥(L−2R)²。证毕。

## 3. 周期模型：更直接的等价判别

令P_6为所有双向周期、Lebesgue可测的六标签平面函数。取任何周期基本平行四边形F，定义
\[
E_{\rm per}(c)=\frac1{2\pi|F|}\int_F\int_0^{2\pi}
{\bf1}_{c(x)=c(x+u_\theta)}\,d\theta\,dx.
\]

**定理B**
\[
\boxed{\chi(\mathbb R^2)=7\quad\Longleftrightarrow\quad
\inf_{c\in P_6}E_{\rm per}(c)>0.}
\]
若χ=7，任何有限NON6单位图H、边数m都证明所有周期c有E_per(c)≥1/m。证明是将H作均匀旋转和在周期环面上均匀平移：每次有至少一条H坏边，而任意一条固定单位边的平均坏边概率恰为E_per(c)。对m边求和即1≤mE_per(c)。

若χ=6，用weak measurable六标签a在Q_L内的限制平铺成L-周期函数c_L。除基本方格距边界≤1的一条宽1区域外，c_L的单位事件等于a的事件，其位置×方向测度为零；剩余区域面积≤L²−(L−2)²。故
\[
\boxed{E_{\rm per}(c_L)\le 4/L-4/L^2\longrightarrow0\quad(L>2).}
\]
这不证明有**单份**合法周期六染；这是各尺度可测周期**近零能**构造，才足以说明inf=0。

## 3补. 无条件热力学极限存在：有限盒最优化精确等于周期最优化

**定理B2（对所有有限q成立；无需假设χ为6或7）。** 对一般q≥1定义q标签版本e_q(L)与周期能量下确界
\[
a_q=\inf_{c\in P_q}E_{\rm per}(c).
\]
则热力学极限**一定存在**，且
\[
\boxed{\lim_{L\to\infty}e_q(L)=a_q,\qquad
e_q(L)\ge a_q-\left(\frac4L-\frac4{L^2}\right)\quad(L>2).}
\]
故以上定理A中的liminf可以全部替换为真正的limit，并不需要预设求极限时存在最优周期态。

证明下界：任取有限Q_L上的可测标号c，把它周期L重复成\(\tilde c\)。对于从Q_L出发、向单位方向u的终点仍在本方格中的单位段，周期化事件与原始有限盒事件**完全相同**；额外的周期坏边只能出现在跨周期盒边界的单位段上。跨界起点一定在距某个方格边界≤1的宽1边条里，该条面积为\(L²-(L-2)²=4L-4\)。因此
\[
E_{\rm per}(\tilde c)\le E_L(c)+4/L-4/L².
\]
对所有c取inf，得\(a_q\le e_q(L)+4/L-4/L²\)，即要求的下界。

证明上界：任取一份固定双向周期、可测p。定义
\(g_p(x)=\frac1{2π}\int_0^{2π}{\bf1}_{p(x)=p(x+u_\theta)}\,d\theta\)。
它是有界的周期可测函数，故在越来越大的方形Q_L上的空间平均收敛到任一基本周期平行四边形F上的平均，即E_per(p)。有限盒E_L(p|Q_L)的每项均不大于完整g_p，故
\[
\limsup_{L\to\infty}e_q(L)\le\lim_{L\to\infty}
\frac1{L²}\int_{Q_L}g_p(x)\,dx=E_{\rm per}(p).
\]
对全部p取下确界得limsup e_q(L)≤a_q。与下界给出的liminf e_q(L)≥a_q结合，完成等式。证毕。

**全色数公式（这才是最远的数学图景）**。OpenAI的ordinary↔weak-measurable定理对每个有限q成立，结合有限精确图紧致性与以上积分下界，严格推出
\[
\boxed{\chi(\mathbb R²)=\min\{q\ge1:a_q=0\}.}
\]
由于χ∈{6,7}，即
\[
a_1,\ldots,a_5>0,\qquad a_7=0,\qquad
\boxed{a_6>0\iff\chi=7,\quad a_6=0\iff\chi=6.}
\]
这是**真正的零温六态order parameter**：不是“近似零能有多小”的口头比喻，而是有限盒→热力学极限→周期模拟→原始任意染色的同一判别式。

**精确但可能非常慢的数值逼近上界：**每份固定可测周期p满足\(e_q(L)\le E_L(p|Q_L)\to E_{\rm per}(p)\)；反向周期化每份盒内candidate，能量只增加≤4/L。故大盒搜索若能给出**对所有自由可测q标签场的严格统一下界**，会成为七色证明；单个优化程序的返回值/局部极小值仍不能推出对全体场的下界。

## 4. 完整共同颜色律的有限最小最大对偶

固定一张真实精确单位图H，边集E非空。设Δ_E为边权概率单纯形、Σ=[6]^V为所有**完整**六色顶点词，定义
\[
\beta_6(H)=\max_{w\in\Delta_E}\min_{\sigma\in\Sigma}
\sum_{ij\in E}w_{ij}{\bf1}_{\sigma_i=\sigma_j}.
\]
有限零和博弈minimax得
\[
\boxed{\beta_6(H)=
\min_{\mu\in\Delta(\Sigma)}\max_{ij\in E}
\Pr_{\sigma\sim\mu}[\sigma_i=\sigma_j].}
\]

**定理C**：
\(\beta_6(H)>0\iff\chi(H)>6\)；若χ(H)>6，则均匀w给β≥1/m；若χ(H)≤6，选一份全图合法σ给β=0。
更强地，任意周期可测六染c满足E_per(c)≥β6(H)；任意L>2R的方形模型满足E_L(c)≥β6(H)(1−2R/L)²。证明把定理A/B每次随机刚体运动下“≥1条坏边”改成“按w加权的坏边总和≥min_σ权重坏边”，再对w最优化。

**注意这个对偶的真实含义**：最小化者μ是H的整张图上**一份共同的完整六标签概率律**，而不是给每条边分开挑选颜色、也不是预先固定二点边缘；所以它精准对应本仓库full15/4D-Coupling的最后量词障碍。找到某个固定伪律不能延拓绝不等于β>0。普通统计力学的“挫折能量”正是这样的全词冲突负担。

因此有严格的三重等价：
\[
\boxed{\chi(\mathbb R^2)=7
\iff\inf_{\rm periodic\ measurable} E_{\rm per}>0
\iff\liminf_{L\to\infty} e_6(L)>0
\iff\exists H\ {\rm finite\ unit},\ \beta_6(H)>0.}
\]
**没有任何一个正值目前已经被证出。**

## 5. 物理直觉、与旧仓库最有用的耦合、退出条件

- 七态晶体：经典六角完美码给q=7一份严格零能的、带正距离安全余量的周期基态；结构简单不意味着q=6没有某种无序零能基态。
- 若χ=7，六态零温仍被统一“挫折”：每一份可测六色场的单位同色针比例≥δ>0，而且这个δ由某张有限精确图控制。它更像真实的**长程不可兼容与全局共同section阻碍**，不只是局部七格团。
- 若χ=6，存在weak measurable六态零能场，即使没有一份真正点态合法的可测/周期六染；各周期方格的六态能量inf为0。这是“热力学极限零能可逼近”，不能据此猜测任何特定实际周期模拟会完美做到。
- 外部Tomon的高围长单位图若χ=7存在，说明可以令每个固定尺寸的小窗口都只需2色，整个图却六色不够；典型零温挫折可能完全来自**远程颜色身份耦合**。
- R2026-SEVEN-CRYSTAL的六态正面积强制混色不是同色单位针能量；单片混色与全局零能否同时存在仍未被证明冲突。
- 真正优先方向：寻找对全部六标签可测场的**严格统一**E_per≥δ>0，或直接构造有限精确单位图并证明β6(H)>0。OpenAI的palette/两和点提供分析工具，R2026-SEVEN-PORT提供有限图目标。只检验一个指定周期纹样、一个近单位误差SAT或一个固定概率核无法结束原题。

## 6. 结果归属与有限验证范围

概率needle下界与有限图关系早见Gwyn–Stavrianos 2020、Bourgeat等2015；OpenAI Family158的Corollary1.5还为q=5提供强定量概率下界。本文只在目前q=6/7情形写明零温有限盒、周期inf、标准minmax对偶和严格量词界。脚本research/verify_potts_six_gap_bridge.py 用整数/Fraction核验一个合法的**低维小图toy**：C5用2色时每种完整颜色词必有至少1坏边，且随机旋转最优模式让每条边坏概率均为1/5，故β2(C5)=1/5；同时校准方形边界比。**不验证无限积分、弱可测分析或χ7**；没有Lean形式化或全仓make check。
