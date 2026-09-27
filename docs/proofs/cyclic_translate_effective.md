# T140：单旋转平移接触的有效穷尽、54例外界与有限缺陷条带

2026-09-28。接续 T129、T139；自足的有限赋值证明，不调用 ESS 或未给出的指数上界。
本结果不宣称文献优先权，不解决双独立旋转群 H′，也不提供普通 HN 新界。

## 1. 精确结论与可执行输入

K⊂C 是对通常复共轭封闭、具有有效精确四则运算和零判定的特征零域。
给定可计算的离散非阿基米德赋值 ν:K*→Z，和 u∈K 满足

    u*bar(u)=1，d=ν(u)≠0。

不要求 ν 与复共轭交换；事实上这种 u 不可能在共轭稳定处具有非零赋值。
ν(0) 不作为有限整数使用。d≠0 已保证 u 不是单位根。
给定非零 a,b,t∈K，考虑全部整数 n,m：

    |a*u^n - (t+b*u^m)| = 1.                         (1)

**T140(a)。** (1) 的解可有效表示为至多三条明确类型的整条整数直线，以及至多54个
不在这些直线上的解。无限直线只能是：

- n=n₀，其中 a*u^n₀=t 且 |b|=1；
- m=m₀，其中 b*u^m₀=−t 且 |a|=1；
- n−m=h，其中 a*u^h=b 且 |t|=1。

每种类型至多一条。算法至多处理21条整数直线，每条上再做有限的必要赋值筛选和精确代回。
无需预先知道或猜测 |n|、|m| 的上界；54是**例外的数量界，不是指数界**。

有限扭转因子 μ_q 可逐项吸收入 a,b：H=μ_q×u^Z 时，至多处理 q² 个有序扭转分支，
得到每对种子至多54q²个例外的粗界。可能的重复解须按物理点/已知轨道识别消去。

**T140(b)。** 给定有限集合的中心 t_i 和种子 a_i∈K，同一个上述 u 所生成的实际点集

    S = union_i {t_i+a_i*u^n : n∈Z}

的全部重合与单位边可有效计算为有限程周期关系、有限个中心星及有限缺陷。
对每个固定 k≥1，S 的整个单位图是否可 k 染是可判定的；可染时存在两个尾部分别最终周期的表示。
消元得到s条非零轨道、有限实际中心集C、局部半径R≥1和缺陷窗口[−M,M]后，令N=k^(sR)，
只需检查指数位于[−M−R−N,M+R+N]的轨道点及C所成的有限诱导图。
这不是全局周期性，不是“所有此类宿主都五色”，也不覆盖两个独立无限阶生成元。

**T140(c)。** 进一步假设有s条非零轨道、中心两两不同，且每对轨道都没有T140(a)的无限接触族。
令B是全部跨轨道单位边的物理端点集合，则B可有效计算且|B|≤54s(s−1)。
对每个k≥3，整个S可k染当且仅当有限诱导图U(B)可k染；U(B)的任意k染色都能延伸到S。
若不可k染，则有至多 `floor(54s(s−1)/(k−2))` 个顶点的有限不可k染子图。
特别地，该子类的NON5若存在，可取至多18s(s−1)个顶点；s=3时为108。这里s计单点轨道，**不是s份Y或Parts副本**。
这是**指定子类的有条件规模界**，不是普通HN见证的108点界，也不表示该子类确实含有NON5。

## 2. 七项 Laurent 式和第一层覆盖

写 X=u^n,Y=u^m，乘共轭并减1，得到

    F(X,Y) = C - a*bar(t) X - bar(a)*t X^(-1)
              + b*bar(t) Y + bar(b)*t Y^(-1)
              - a*bar(b) X/Y - bar(a)*b Y/X,
    C = |a|²+|b|²+|t|²−1.                           (2)

其六个非常数系数非零，常数 C 可能为0。支持包含于

    A={(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)}.

设非零项为 c_α X^α₁Y^α₂。如果 F(u^n,u^m)=0，所有项的最小赋值至少出现两次。
否则唯一最小项不可能等于其余项之和。这给出某一对不同支持点 α,β 的精确等式

    d*((α₁−β₁)n+(α₂−β₂)m) = ν(c_β)−ν(c_α).         (3)

所以全部解被至多 binom(7,2)=21条有理直线覆盖。这里只使用“必要覆盖”，不把赋值相等当作实际单位边。
(3) 的整数点通过 gcd 整除检查和 Bézout 系数精确参数化：无整数点则丢弃；否则写成

    (n,m)=(n₀,m₀)+j(r,s)，j∈Z，gcd(r,s)=1.           (4)

所有整数点均被包含，不能只选择某个同余类或只枚举正指数。

## 3. 每条直线上的第二层筛选是有限的

将(4)代入(2)，按相同 j 指数合并**完整域元素系数**，得到

    Q(u^j)=sum_h q_h u^(hj).

必须先精确合并与零判定，然后才对非零 q_h 取赋值。
若所有 q_h=0，则整条直线是解；若只有一个非零项则无解。
否则相同的最小赋值原则给

    j = (ν(q_l)−ν(q_h))/(d*(h−l))，h≠l.             (5)

保留整数候选，并在 K 中精确代回。每条直线至多有21个此类候选，数量常数不依赖指数大小。
这个过程终止且不遗漏解，因而是有效算法，而非一个“解有限但找不到”的存在性证明。

数值近似不能代替系数合并；固定精度下的零剩余不能当作域中的0。
仓库实际域的适配器从8位起加倍2进精度，直到发现非零剩余；达到实现资源限额则报错，
不返回“无解”。域嵌入与有限赋值的正确性是数学输入，有限抽样不证明一个任意回调是真赋值。

### 3.1 抽象结构：共同底数Laurent模板的整格递归

同一证明不依赖“两个变量”来保证终止。对任意固定维数r和有限Laurent多项式F，
在相同的有效域/赋值假设下，集合

    {n∈Z^r : F(u^n₁,…,u^n_r)=0}

可有效写成有限个整数仿射子格的并。证明按r归纳：r=0是常数的零判定；
零多项式给整个格，非零单项无解。其余情形由最小赋值至少两次达到，覆盖于有限条
`d*(α−β)·n=ν(c_β)−ν(c_α)`的整数超平面。
对每条有整数解的超平面，反复Bézout把非零整数行化成(g,0,…,0)，
得到覆盖全部整数解的参数化n=n₀+Bz，z∈Z^(r−1)。代入后仍是共同底数u的Laurent式，
系数为c_α*u^(α·n₀)，指数为Bᵀα；合并同项后使用归纳假设，再将子格推回。
维数严格下降，非零项数不增加，因此终止。参数化中没有丢弃整数同余条件。

对有限个等式同时成立，分别算出的仿射子格并可用整数线性方程求交。
因此，坐标由有限个固定系数与u的整数幂构成的指定有限几何模板，
其单位边方程和点识别方程可以转为有限个整数仿射关系分支，不必浮点拟合。
这只决定**固定共同底数与固定系数模板**的几何约束，不决定所有模板上的五染色，
不把任意独立底数u、τ变成同一底数。代码本轮实现的是r=2接触特化，
没有宣称已经实现任意维整格求交器；一般递归的完整证明如上。

## 4. 为什么无限解只有三种类型

若 Q 恒等为0，考虑 r,s,r−s。若三者均非零，则 |r|、|s|、|r−s| 中有唯一最大者。
证明：r,s异号时 |r−s|=|r|+|s|；同号且不同则较大绝对值严格大于其余两者。
因此对应的正/负极端幂在Q中只出现一次，其系数来自(2)的某个非零非常数项，不可能相消。
矛盾。故 r=0、s=0 或 r=s。

r=0 时，把 A=a*u^n₀、B=b*u^m₀ 写入 |A−t−B*u^(sj)|²−1。
非常数项全部消失当且仅当 A=t，再由常数项得到 |B|=|b|=1。
因(r,s)原始，s=±1，得到 n=n₀ 的整条直线。s=0同理得到 b*u^m₀=−t、|a|=1。
r=s时得到 |(A−B)u^(rj)−t|²−1；t≠0迫使 A=B，随后 |t|=1。
这就是第三类 n−m=n₀−m₀。反向代回直接成立，三类条件均为必要且充分。

这给出了 T139 在本循环子类内的自足退化分类，不再依赖 ESS 定理。
不包含零半径或零平移；那些是中心/同中心轨道问题，另按T129处理。

## 5. 54的来源不是搜索拟合

(3)的原始法向量只可能是下表六种（整体反号视为相同）。
每条非恒零 Q 乘最低幂后成为普通多项式，次数不超过支持沿(r,s)投影的宽度。
不同 j 给不同 u^j，故实际解数不超过该次数。

| 原始法向量 | 完整7点支持中的无序项对数 | 投影宽度 |
|---|---:|---:|
| (1,0) | 5 | 2 |
| (0,1) | 5 | 2 |
| (1,−1) | 5 | 2 |
| (1,1) | 2 | 4 |
| (2,−1) | 2 | 4 |
| (1,−2) | 2 | 4 |

所以，即使不消除不同项对给出的重复直线，非恒零分支上的解数总和至多

    3*5*2 + 3*2*4 = 54.

恒零分支上的所有解已包含于三类无限族。从剩余点中删去落在这些无限族上的点，
不会增加数目。C=0时可用更小的42界，但本轮统一保留54，不主张最优。
54是固定指数六边形与有限赋值相等原理给出的保证，不是当前样例观测到的最大值。

## 6. 从完整接触到可判定的有限缺陷条带

下面证明T140(b)，不把一个有限程序测试冒称一般定理的形式化。

先将 a_i=0 的轨道变成一个中心点。在同中心的非零轨道间，是否相同及指数差由
ν(a_i)−ν(a_j) 和d给出唯一候选，精确代回即可；相同轨道合并。
同中心的单位 offset 是T129的二次方程，至多两个，亦可直接按两次最小赋值筛选求全。

不同中心的两条轨道，其重合满足 a_i*u^n−a_j*u^m=t_j−t_i≠0。
对这个三项Laurent式使用第2–3节的同一算法。不存在恒零整数直线：r,s不同且非零有唯一极端项；
r=0、s=0或r=s也不能让非零常数和非零剩余项全部消失。
几何上两个不同圆最多交两点，故实际识别有限，且每个点的轨道指数唯一。

跨轨道单位边由T140(a)求全。无限中心星的固定端点是某个实际存在于S内的中心。
把所有**实际在S中的**中心作为有限特殊顶点C；中心成员资格也是一元幂等式，可有效判断。
不能擅自添加本来不属于S的中心。固定C的颜色之后，各中心星仅给相应轨道施加对所有n相同的颜色名单。
无限匹配给 n−m=h 的平移不变边。其他跨边与跨中心识别均有限，装入一个有限整数窗口。
轨道点与C的重合也作为有限颜色等式保存。中心之间的边直接检查。
一个中心与非同中心轨道的单位接触是一元二次Laurent方程，亦由最小赋值法求全；
同中心时按半径是否为1决定是全部相邻还是全部不相邻。这覆盖了零半径情形，不能只处理非零种子对。

于是，有限个轨道成为有限宽的一维整数条带：存在R≥1，使所有平移不变边/等式的offset绝对值≤R；
此外只有有限个窗口内约束，以及常数名单。枚举有限特殊顶点的k色赋值，再构造记住R层的有限状态图。
若有s条轨道，状态数至多 k^(sR)；不合法的局部块和名单被删除。
把全部有限例外端点纳入窗口，枚举窗口及R层边缘的有限着色，检查所有例外关系。
左边界能够延伸到−∞，当且仅当它可由某个有向环到达；右边界能延伸到+∞，当且仅当它能到达某个环。
这两项均可由有限有向图判断。

若存在完整染色，其左右无限状态路径必在有限图中遇到环，故通过上述判定。
反向，选择窗口、两侧连接路径和两个环，得到整个条带的合法染色，再按已核验的点识别下降到S。
沿环重复使两条尾部分别最终周期，周期各不超过状态数；中间过渡不要求周期，左右周期也可不同。
这是充要算法。没有证明每一可染实例都有从头到尾的同一个周期。

更具体地，取N=k^(sR)。若指数区间[−M−R−N,M+R+N]和C的有限诱导图可染，
左、右缺陷外各有N+R层，因此各包含N+1个连续R层状态。
至多N种状态迫使每侧重复某一状态；两次重复之间的非空闭游走可以向对应无穷方向重复。
保留它到中心窗口的原路径，便得到完整染色。中心星的名单在每层相同，泵引理不会破坏它们；
全部非周期识别和例外边都已在窗口内，所以也不受尾部替换影响。
反向从完整图限制当然成立。这给出一个**有效、依赖输入的有限等价实例**，顶点数不超过

    |C| + s*(2M+2R+2*k^(sR)+1).

它可能非常大，且M、R依赖已经精确算出的完整接触。没有固定见证规模或实用运行时间的承诺。

### 6.1 无无限跨轨道接触时，不必使用指数状态空间

证明T140(c)。单条轨道上的单位边满足

    |a|²*(2−u^h−u^(−h))=1，h=m−n。

对u^h这是二次方程；若有非零整数解h₀，全部整数解只能是±h₀，因为u不是单位根。
所以每条轨道内每个顶点的单位度数至多2，图是双向路径的若干分量，因而可二染。

每对不同轨道至多有54条单位接触，故全部跨轨道物理边数m≤54*binom(s,2)，
并且|B|≤2m≤54s(s−1)。在B外若一个物理点属于两条轨道，那么它的任一单位边
也能以不同轨道的端点表示，故本应进入B。于是这样的点只能孤立；其他B外点总单位度数≤2。
给定U(B)的任意k≥3染色，枚举S\B，在每步避开已经着色的至多两个邻点，永远存在可用颜色。
这构造完整延伸；反向限制显然成立。交点没有被当成两个独立变量，跨轨道记录按物理点去重。

若U(B)不可k染，取其顶点极小不可k染子图F，则每个顶点在F内的度数至少k。
给每个物理顶点选择一条包含它的轨道作为归属，将V(F)分成s类。
每个顶点同类邻点至多2，因此异类邻点至少k−2；全部异类边均包含于已计算的m条跨轨道边。
握手计数给(k−2)|V(F)|≤2m≤54s(s−1)，得到所述界。
归属选择不要求轨道不相交；跨轨道计数的重复只使上界更保守。

k≥3不可省掉：任意给定的两个路径端点颜色可能不满足二色奇偶条件，不能用上述贪心延伸。
有无限匹配、中心星或同中心不同轨道的无限接触时，也不能直接套本节有限核；需返回T140(b)。
54、18和108来自支持宽度与临界最小度，不是本次实验拟合。每条轨道可二染还给χ(S)≤2s；
因此两轨道实验本身不可能产生NON5，三条只是首个未被这一简单色数上界排除的规模。

## 7. 适用边界与最低反向校准

当前u在已核验的2进处满足ν(u)=−1，因此可用于Y或有限个η、τ层的**共同单u旋转饱和**。
若把τ指数也独立放开，则指数有四个自由变量；ν₂(τ)=0、ν₅(u)=0，某个最小项对相等可能不减少未知维数。
本证明不能由“有两个赋值”直接升级成H′的完整平移算法。
简单代数校准是2^n+1=3^m：n,m>0时，在2进处常数与3^m的赋值都为0，在3进处2^n与常数都为0。
这两条必要条件没有给任何指数限制。此例只否定该推理捷径，不表示H′算法不存在。

有限下界搜索仍不必等待完整无限接触算法；真实所列边的不可五染已经足够。
本结果主要使一个具体无限宿主子类的正/负判定有了有效入口，不能代替完整自由颜色关系。

对u=(3+4i)/5，t_N=u^N−2、a=b=1，(n,m)=(N,0)是一个非三类的实际例外：
距离差等于1；t_N非零且|t_N|≠1（否则Re(u^N)=1，会使u^N=1）。
算法在N=1、7、31、101时均直接找到该大指数，而不是将54误用为窗口。

## 8. 实际证据与复现

`cyclic_translate_contacts.py`实现二变量Laurent覆盖与单位接触特化，独立于求解器。
`test_cyclic_translate_contacts.py`用两种不同的高斯素点赋值算法（Gaussian整除、Hensel嵌入）交叉检查；
216组(a,b,t)、17496个窗口点对只作有限反向校准；完整性来自第2–5节，不来自窗口。
另检查无限族、零多项式、退化输入、大指数和`-O`模式拒绝。另对1–3个状态的全部530个有向图，
将环可达性与恰N步尾部的独立计算逐项对比；这校准有限状态步骤，不代替上述一般证明。

E112使用当前Y中预先选择的12个真实种子对，每对先取t=1，再取
`t=a*u^N-b-1`，N依次按1、2、7、37循环。后者预先植入(n,m)=(N,0)的单位接触，
但仍要求算法找出**所有**接触，而不是仅验证植入的那一个。全部24个实例的结果为：

- 12个t=1实例在全部整数指数上均没有接触；只覆盖注明的12对种子，不代表全Y。
- 植入实例中10个恰好只含(N,0)；(230,232),N=7是一整条n=7中心星；
  (232,900),N=37恰好有(0,0)、(37,0)两个离散接触，没有其他解。
- Y的232号点恰为−1，所以中心星来自b=−1使t=a*u^N；额外接触来自a=−1使
  `a−t−b=u^N`。这些现象解释为具体几何恒等式，不归因于点编号的偶然性。

独立检查器不导入枚举生产器或通用求根模块：它重新构造全部Y几何，
使用另一种整数直线原点选择，并按三项差乘共轭重新构造单变量多项式。
它重做完整覆盖与精确代回；底层16维域/局部嵌入定义与生产器共享已有独立模块，
所以不声称本轮还实现了第三套完全不同的数域算术。8种证书篡改及`-O`被拒绝。
本轮实现了T140(a)的枚举器及上述实例，并未实现用于任意输入的整套T140(b)自动机编译器。
T140(b)由本节前的完整数学算法证明；24例没有求出新的无限宿主色数或五色反证。

    python3 -S research/test_cyclic_translate_contacts.py
    python3 -S research/verify_cyclic_translate_research.py

已有T129、T139的适用范围与全部历史UNKNOWN保持原样。


### 8.1 七个不同中心的完整无限实例：有限核恰为Moser图

使用实际域中的ω=2+3z、r=v，其中3z²+3z+1=0、3v²−5v+3=0，复共轭采用已验证定义。
令

    (p₀,…,p₆)=(0,1,ω,1+ω,r,rω,r(1+ω))，
    a_i=10(i+1)，t_i=p_i−a_i，S_i=t_i+a_i*u^Z。

中心两两不同；a_i均大于1且模长两两不同，所以不出现中心星或平移匹配。
本轮完整计算21对跨轨道接触和7条轨道内部的全部单位offset：
内部全部为空，跨轨道仅有11项(n,m)=(0,0)，正好给出Moser七点十一边图。
因此无限S除该七点核外全部为孤立点，恰四色。枚举全部3^7=2187种三色赋值无解，
全部4^7赋值中有384种合法着色；不是引用一个未经检查的SAT状态。

这演示有限化能够真正完成一个异中心无限对象，而不是仅找到有限窗口。
它同时提醒：把有限核心加上无限多轨道点，完全可能不增加任何颜色信息。
下面是**单独执行的标准库重放**，没有被静默计入Makefile总入口；它不导入接触生产器。
保存数据为 `certificates/cyclic_translate_moser_kernel.json`，其中每一项都由代码重算再逐字段比较。
本轮另检查6类篡改拒绝及优化模式拒绝；运行范围单独记录。
从仓库根目录执行：

```python
from pathlib import Path
from itertools import combinations, product
from copy import deepcopy
import sys, json
if not __debug__:
    raise RuntimeError('verification requires assertions')
root = Path.cwd()
sys.path.insert(0, str(root/'research'))
from cyclic_translate_field16 import Element, U, valuation
from verify_cyclic_translate_research import independent_contacts
zero, one = Element.scalar(0), Element.scalar(1)
z = Element(tuple(int(i == 4) for i in range(16)))
r = Element(tuple(int(i == 8) for i in range(16)))
w = 2*one + 3*z
assert w*w-w+one == zero and r*r.bar() == one
points = [zero, one, w, one+w, r, r*w, r*(one+w)]
radii = [10*(i+1) for i in range(7)]
a = [Element.scalar(x) for x in radii]
t = [p-b for p, b in zip(points, a)]
assert len(set(t)) == 7 and valuation(U) == -1
roster, boundary, all_edges = [], set(), set()
for i, j in combinations(range(7), 2):
    found, _ = independent_contacts(a[i], a[j], t[j]-t[i])
    assert not found['lines']
    for n, m in found['points']:
        x, y = t[i]+a[i]*U**n, t[j]+a[j]*U**m
        assert (x-y)*(x-y).bar() == one
        boundary.update((x,y)); all_edges.add(frozenset((x,y)))
    roster.append(dict(tracks=[i,j], points=found['points']))
internal = []
for ai in a:
    A = ai*ai.bar()
    coeff = {0: 2*A-one, 1: -A, -1: -A}
    candidates = set()
    for h, l in combinations(coeff, 2):
        num = valuation(coeff[l])-valuation(coeff[h])
        den = valuation(U)*(h-l)
        if num % den == 0:
            candidates.add(num//den)
    offsets = sorted(h for h in candidates
                     if (ai*U**h-ai)*(ai*U**h-ai).bar() == one)
    assert not offsets
    internal.append(offsets)
vertices = sorted(boundary, key=lambda x: x.serial())
index = {x: i for i, x in enumerate(vertices)}
edges = sorted(tuple(sorted(index[x] for x in e)) for e in all_edges)
actual = [(i,j) for i,j in combinations(range(len(vertices)),2)
          if (vertices[i]-vertices[j])*(vertices[i]-vertices[j]).bar() == one]
assert edges == actual and set(vertices) == set(points)
colors = {}
for k in (3,4):
    count, first = 0, None
    for word in product(range(k), repeat=len(vertices)):
        if all(word[i] != word[j] for i,j in edges):
            count += 1
            if first is None:
                first = word
    colors[k] = dict(count=count, first=first)
assert len(vertices) == 7 and len(edges) == 11
assert colors[3]['count'] == 0 and colors[4]['count'] == 384
model = dict(schema='cyclic-translate-moser-kernel-v1', status='PASS',
             u=U.serial(), points=[x.serial() for x in points], radii=radii,
             pair_results=roster, internal_offsets=internal,
             kernel_vertices=[x.serial() for x in vertices], kernel_edges=edges,
             colorings=colors,
             scope='Complete seven translated single-u orbits: exactly this Moser kernel and isolated remaining points; chromatic number 4, not a new HN bound.')
def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',',':'))
def check(observed):
    if canonical(observed) != canonical(model):
        raise ValueError('certificate does not equal independent reconstruction')
cert = json.loads((root/'certificates/cyclic_translate_moser_kernel.json').read_text())
check(cert)
mutations = {
    'missing-edge': lambda c: c['kernel_edges'].pop(),
    'false-loop': lambda c: c['kernel_edges'].append([0,0]),
    'false-three-coloring-count': lambda c: c['colorings']['3'].__setitem__('count',1),
    'invented-unbounded-contact': lambda c: c['pair_results'][0]['points'].append([123,456]),
    'false-internal-offset': lambda c: c['internal_offsets'][0].append(1),
    'boolean-radius': lambda c: c['radii'].__setitem__(0,True),
}
for name, mutate in mutations.items():
    bad = deepcopy(cert); mutate(bad)
    try:
        check(bad)
    except ValueError:
        continue
    raise AssertionError('accepted mutation '+name)
print(json.dumps(dict(status='PASS', complete_track_pairs=21, internal_tracks=7,
                      kernel_vertices=7, kernel_edges=11, kernel_colors=4,
                      assignments_enumerated=3**7+4**7, four_colorings=384,
                      rejected=sorted(mutations)), indent=2))
```

## 9. 文献连接和依赖范围

赋值取最小值且至少两项并列，是热带超曲面的初等必要条件。
D. Maclagan, *Polyhedral structures on tropical varieties*, arXiv:1302.5372v1，
[原文](https://arxiv.org/pdf/1302.5372)第1–2页Definition1.1和Remark1.7明确给出这个语言；
本轮读取这两页并核对定义。T140只需要本页第2节的一行非阿基米德三角不等式证明，
不使用其代数闭包上的热带基本定理、不把必要热带条件当作实际几何充分条件。
这里真正使第二次筛选结束的是**所有未知幂共用一个ν(u)≠0的底数**。

T139仍在更一般的有限秩H中使用ESS；本结果只在上述循环子类内移除了该深层输入，
并将“有限例外”加强为可执行的完整枚举。有限状态尾部论证属于一维有限禁形系统的标准思想，
本页给出所需证明，不宣称这些一般方法由本库首创。
