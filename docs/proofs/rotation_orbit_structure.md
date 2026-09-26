# 旋转轨道的接触度与等变调色板：结构证明与诊断

2026-09-26。结构补充，不另分配 T 编号；不改变 HN 上下界。
完整旋转宿主的 [T127](rotation_orbit_five_coloring.md) 已经通过
独立识别、完整接触枚举和色词检查，恰五色及最小正周期3均已成立。

本页把两个不同问题分开：真实单位图的边结构，以及额外要求一个
全局调色板置换表示实现每个旋转的受限染色。第二个问题的失败不是
第一个问题的下界。当前 Y 的半径检查在第4节给出完整重放命令；
它复用已有精确域运算，尚无另一个半径扫描实现，不能称为该扫描的
双实现认证。第9节统计及第10节整14运动审计仍为单实现；τ 两点
分离另已纳入 T127 独立色词检查。第11节提供其余数字的完整重放。

## 1. 对象、自由作用与唯一 gain

令 η=exp(2πi/5)，令 u∈C 满足 |u|=1 且 u 为无限阶，取

\[
H=\langle\eta,u\rangle
 =\{\eta^a u^n:a\in\mathbb Z/5\mathbb Z,\ n\in\mathbb Z\}.
\]

这里所有旋转都以原点为中心。若 η^a u^n=1，则 u^(5n)=1；
由 u 无限阶知 n=0，继而 a=0。因此 H≅C₅×Z，所列表示唯一，
其非平凡扭元恰为 η、η²、η³、η⁴，均为阶5。

H 在 C\{0} 上自由作用：hp=p 且 p≠0 就给 h=1。故取完整
非零 H 轨道代表 r₁,…,r_s 后，每个非零实际点唯一表示为 hr_i。
原点若属于种子则是一个固定顶点，不是每层一个顶点；下面的
非零代表计算不适用于原点。

当前候选使用[真实单旋转轨道定理](valued_rotation_orbits.md)中的
η、u及种子 Y。其 u 无限阶由 v₀(u)=−1 已有证明。本页的一般
代数论证只需无限阶，不需再假定有指定有限处赋值。

## 2. 每个有序代表对的完整 H-contact 至多两个

固定 r_i,r_j≠0，采用边方向

\[
D_{ij}=\{h\in H:|r_i-h r_j|^2=1\}.
\]

因为 h\bar h=1，直接展开并乘以 h 得严格等价式

\[
|r_i-h r_j|^2=1
\iff
(\bar r_i r_j)h^2
-(|r_i|^2+|r_j|^2-1)h+r_i\bar r_j=0. \tag{1}
\]

首项系数非零，因此这是 C 上真正的二次多项式，最多两个不同根。
所以 **|D_ij|≤2，计入全部 a、n 后合计也至多2**。这不是对每个
η 切片分别应用二次界后得到的10；五个切片的所有根属于同一个
多项式。第1节的唯一表示保证不同 gain 标签不会表示同一个 h。

这条基数界本身不枚举 D_ij，也不证明某张有限表已完整。表的
完整性仍须来自 T125 的精确返回界和逐项检查。它提供附加的
一致性断言：完整归并后若一个有序代表对有超过两个不同 gain，
必存在算术、重复或编码错误。重复存储同一 gain 不算新接触。

还有两条直接校验：

\[
D_{ji}=D_{ij}^{-1},\qquad 1\notin D_{ii}. \tag{2}
\]

第一式由将距离式乘以 h⁻¹ 得到；第二式因为同一点距离为0。
若用 |h r_i−r_j|=1 的相反约定，gain 必取逆，不能混用两种方向。

全部边由这些表恢复：hr_i 与 kr_j 相邻，当且仅当 h⁻¹k∈D_ij。
若原点在点集中，它与整条 i 轨道相邻，当且仅当 |r_i|²=1。
原点的这种无限星形关系必须另行记录，不受非零二次式的二根界。

## 3. 单条非零 H 轨道只有路径或五圈；两种危险半径足以区分

令 p≠0，考虑 **Hp 上全部实际单位边**，不是只运输种子中的边。
若 D_pp 为空，整个图无边。否则由(2)和二根界，

\[
D_{pp}=\{g,g^{-1}\}.
\]

两根不同：若 g=g⁻¹，则 g 阶至多2；而 H 没有非平凡2扭元，
g=1又不可能给单位边。因此每个顶点恰有两个邻点。

将 Hp 识别为 H 后，这个图就是具有生成元 g、g⁻¹ 的 Cayley
图。其连通分量恰为 H 中的 ⟨g⟩ 陪集：

- 若 g=η^a u^n 且 n≠0，则 g 无限阶；每个分量由
  …,g⁻²h,g⁻¹h,h,gh,g²h,… 构成双向无限路径，按指数奇偶二染。
- 若 n=0，则 g=η^a、a≠0；每个分量是五圈 C₅，恰三色。

所以单条 H 轨道不可能独自产生 NON3，更不能产生 NON5。

扭元接触发生当且仅当

\[
1=|p-\eta^a p|^2
 =|p|^2(2-\eta^a-\eta^{-a}).
\]

对 a=1,4 与 a=2,3 分别计算，得到恰好两种平方半径

\[
|p|^2=\frac{5+\sqrt5}{10}
\quad\hbox{或}\quad
|p|^2=\frac{5-\sqrt5}{10}. \tag{3}
\]

如果种子没有这两种半径，其完整 H 饱和也没有，因为全部群元
都是旋转。因此每个单独轨道均二染；这里允许无边分量只用一种色。
这**不能**把不同轨道的二染自动拼成整个图的二染或五染；跨轨道边
是新的约束，须共同处理。

若另加入原点，单个轨道加原点仍二染，条件仍是排除(3)。证明如下：
当 |p|≠1 时原点与轨道无边；当 |p|=1 时，假如轨道内部存在单位
边，则 g+g⁻¹=1，即 g²−g+1=0，故 g 是本原六次单位根，与 H
的扭元分类矛盾。因此此时恰是一个以原点为中心的无限星形图。

## 4. 当前 Y：两个五圈半径均未出现，精确但尚未双实现认证

已执行的精确扫描重建 E077 的 Y=X∪τX，共10077个不同物理点，
逐点计算 p\bar p；式(3)的两个值均出现0次。这一有限事实连同
第3节证明意味着：当前 H 饱和的每个单独轨道均二染。

下面是可从仓库根目录直接重放的完整命令。它没有 SAT、浮点数、
半径容差或随机取样。先复用已有独立域检查器的几何构造和有理数
算术，再绑定 E077 的来源档案及整个整数点表 SHA；因此不会把
另一个10077点集合冒充 Y。基索引4代表 √5，代码也检查其平方。

**证据等级：** 本节是可重放的单实现精确有限检查；它复用了已有
域检查器，但不因那个文件名含 `verify` 就成为本次扫描的第二份
独立实现。本页没有为这次半径扫描新增独立检查器。现在 T127 的
独立完整接触枚举也已证明不存在 η 自轨道接触；结合第3节的
等价式，它另行支持当前没有 C₅ 半径的结构结论，不应混称为
重跑了本扫描。

```sh
.venv/bin/python - <<'PY'
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import math
import sys

if not __debug__:
    raise RuntimeError('Run with assertions enabled, not python -O')
sys.path.insert(0, 'research')
from verify_quintic_residue5_ring import verify
from verify_quintic_core_probe import conjugate_twice, digest

root = Path('.')
raw = (root / 'certificates/quintic_tau_union.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1')
source = json.loads(raw)
_, context = verify(root, geometry_context=True)
mul = context['mul']
X = context['points']
Y = sorted(set(X) | {mul(context['tau'], p) for p in X})
assert len(Y) == source['geometry']['vertices'] == 10077
den = math.lcm(*(x.denominator for p in Y for x in p))
assert den == source['denominator'] == 480
integer_points = [[int(den*x) for x in p] for p in Y]
assert digest(integer_points) == source['geometry']['point_sha256'] == (
    '6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1')

one = tuple(Q(i == 0) for i in range(32))
sqrt5 = tuple(Q(i == 4) for i in range(32))
assert mul(sqrt5, sqrt5) == tuple(5*x for x in one)
bar = lambda p: tuple(Q(x)/2 for x in conjugate_twice(p))
assert bar(sqrt5) == sqrt5
targets = [tuple(a/2 + sign*b/10 for a, b in zip(one, sqrt5))
           for sign in (-1, 1)]
hits = [[], []]
for i, p in enumerate(Y):
    squared_radius = mul(p, bar(p))
    for j, target in enumerate(targets):
        if squared_radius == target:
            hits[j].append(i)
assert hits == [[], []]
print(json.dumps({'vertices': len(Y), 'point_sha256': digest(integer_points),
                  'C5_radius_minus_indices': hits[0],
                  'C5_radius_plus_indices': hits[1]}, indent=2))
PY
```

这种扫描不用完整跨轨道接触表，也没有提前回答该表的五染性。

## 5. 原点使五色全局调色板等变模型把 η 完全忽略

这里增加一个**额外假设**：点集 S 对 H 不变且包含0，存在 proper
染色 c:S→{0,…,4} 及一个群同态 ρ:H→S₅，满足

\[
c(hx)=\rho(h)c(x)\quad(h\in H,\ x\in S). \tag{4}
\]

原问题、一般周期染色及 T125 都没有要求(4)。特别地，有限 joint
中对支持原子的置换，不是这里对五个颜色的全局置换。

由 h0=0，ρ(h) 必须固定颜色 c(0)，不论原点是否有邻边。又
ρ(η)^5=1，所以 S₅ 中 ρ(η) 的各个循环长度只能为1或5。
若非恒等，它必是一个覆盖全部五种颜色的五循环，没有不动点，
与固定 c(0) 矛盾。因此

\[
\rho(\eta)=1,\qquad c(\eta x)=c(x). \tag{5}
\]

这个论证同样适用于至多五种颜色，把不足五色嵌入五色集合即可。
若没有原点或别的 H 固定顶点，结论不成立：一个五循环可以作用
在全部颜色上。不能仅以旋转在平面上存在固定点，而忽略该点并未
属于被染色点集的区别。

ρ(u) 也固定 c(0)，故属于剩余四颜色的 S₄。模固定原点颜色的
全局颜色重命名，只需考虑五种循环型

\[
1^4,\quad 2\,1^2,\quad 2^2,\quad 3\,1,\quad4. \tag{6}
\]

其阶分别为1、2、2、3、4。对给定 σ=ρ(u)，只为各个 H 代表
选择颜色 b_i，所有非零点的颜色已经由

\[
c(\eta^a u^n r_i)=\sigma^n(b_i)
\]

确定。完整 gain 表上的精确约束为

\[
b_i\ne\sigma^n(b_j)
\quad\text{对每个 }\eta^a u^n\in D_{ij},
\]

并对 |r_i|²=1 的轨道加 b_i≠c(0)。因为 σ 固定 c(0)，后一
条件自动覆盖所有层。该有限模型有解，当且仅当指定 σ 的全局
等变染色有解。搜索五种循环型的完备性仅限于(4)，**不是**对
一般五色周期染色的完备性。正词必须用完整实际 gain 表核验；
五种模型全部失败也仍不是原始图 NON5。

## 6. 六点校准：普通三色，旋转等变却恰需六色

令

\[
r=(2-\eta-\eta^{-1})^{-1/2}>0,\qquad
S=\{0\}\cup\{r\eta^a:a=0,1,2,3,4\}.
\]

五个非零顶点构成边长1的正五边形。相邻顶点距离为1；非相邻
顶点距离为黄金比 (1+√5)/2>1。原点到五个顶点的距离为 r，
而 r²=(5+√5)/10≠1，所以原点没有单位邻边。因此 S 的全部
诱导单位图严格等于 C₅⊔K₁，普通色数恰为3。

现在只要求 C₅ 旋转群 ⟨η⟩ 的全局调色板置换等变。若最多五色，
第5节的固定点论证给 ρ(η)=1，于是五个非零顶点全同色，违反
五边形边的 proper 要求。故这种等变染色至少六色。

六色能够达到：原点独占第六色，五边形五个顶点各用一种颜色，
ρ(η) 循环置换这五色并固定原点色。因此它的这种受限等变色数
恰为6，而普通色数为3。

本例是有限 C₅ 作用的校准，不声称这个六点集对当前无限阶 u
也不变。它已足以严格否定“η 的调色板等变 NON5 就是普通
NON5”的推断。加入整个 H 饱和也不准许省略全部新跨轨道边。

## 7. 对当前研究的直接后果与非结论

1. H 代表的完整接触表应加入“每有序代表对最多两种不同 gain”
   及逆向一致性检查；这能发现编码错误，不能代替完整性证明。
2. 当前每个单轨道均二染；实质高色障碍若存在，必须来自不同
   轨道间的约束。这不是给整个候选提供了自动低色上界。
3. 五种 S₄ 循环型是低成本的正证书候选，不是五个一般周期问题；
   即使它们全被严格排除，也必须转向允许 η 切片独立颜色的一般
   周期模型，而不能宣称 NON5。
4. [T127](rotation_orbit_five_coloring.md) 现在已给出整个 H 饱和
   的独立认证五染，并结合 Parts 下界得到恰五色；继续叠加该族
   旋转不能产生 NON5。仍没有原始平面六色上界或不可判定性证明。
   旧 shell 宿主的非覆盖已在 T125 讨论，本页不把“未被旧宿主
   覆盖”作为高色证据。

## 8. 一个真实 u² 接触排除所有颜色数下的时间周期1与2

当前 Y 的排序点597，亦即 H 代表表中的位置491，具有坐标

\[
p=-\frac23+\frac{\sqrt5}{2}-\frac{i\sqrt{11}}6
 +\eta\left(-\frac{19}{12}+\frac{7\sqrt5}{12}
             -\frac{i\sqrt{11}}{12}+\frac{i\sqrt{55}}{12}\right).
\]

使用 η²=((√5−1)/2)η−1 与 η̄=η⁻¹ 展开，直接得到

\[
|p|^2=2-\frac23\sqrt5.
\]

当前 u=(1−3√5−i√3−i√15)/8 是单位旋转，所以

\[
u+\bar u=\frac{1-3\sqrt5}{4},\qquad
|1-u^2|^2=4-(u+\bar u)^2=\frac{9+3\sqrt5}{8}.
\]

因此

\[
|p-u^2p|^2
=\left(2-\frac23\sqrt5\right)\frac{9+3\sqrt5}{8}=1. \tag{7}
\]

这只是明确两个不同实际点间的一条边；不是原图中的自环。
本轮已用32维有理数乘法核验 p 的成员身份、上述平方模长及(7)。
完整接触档案中同类记录为
`(i,i,h,n)=(491,491,0,2),(815,815,0,2),(816,816,0,2),`
`(2665,2665,0,2),(2666,2666,0,2),(2802,2802,0,2)`；
排除周期1/2只需第一个显式见证，不依赖其他五条或接触表完整性。

所谓时间周期 P 是对**每个**点 x 要求 c(u^P x)=c(x)，不是要求
η 对颜色也恒等。若 P=1 或2，这个条件使 c(p)=c(u²p)，与(7)
矛盾。因此整个当前 H 宿主不存在任何颜色数的时间周期1或2 proper
染色。它不排除非周期染色或更大周期。

完整实际接触表及周期3正词现已通过独立检查，因此由这个见证
得到：该宿主的最小正时间周期恰为3，见
[T127](rotation_orbit_five_coloring.md)。依据是完整接触表及逐边
正词检查，不是求解器的 SAT 标签。

还有一个仅适用于全局调色板等变模型的简化：第5节的五种 S₄
循环型中，阶1或2都给 σ_u²=1，与(7)冲突；所以这个模型只有
阶3与阶4两种循环型可能成功。本轮检查的两种循环不是任意选取
的常数。但这个分类不限制一般染色或一般周期染色。

## 9. 一次切口、临界剥离与换层诊断：没有小五色关键核

本节仅记录一次确定性结构检查，不再扩大该宿主的搜索。
输入 `certificates/rotation_orbit_contacts.json` 的 SHA256 为
`909fbb3f4bb687537259044425a45993710a0f81a251a77de3939ea913c5da20`，
含4176个 H 代表、22377条无向 gain 边轨道和60条原点邻轨。
输入表的几何完整性已由 T127 独立检查通过。本节切口、剥离与
换层的输出仍是单实现精确组合检查，不因输入已经认证就变成
输出也有第二实现；第11节给出完整无搜索重放命令。

### 9.1 切口的定义，特别是原点不能伪装成时间变量

将非零顶点写为 (i,a,t)，其中 a∈Z/5Z，t∈Z。记录
(i,j,h,n) 产生全部边
(i,a,t)∼(j,a+h,t+n)。当 n<0 时交换端点并取逆，使 n>0；
n=0 的边不跨时间切口。取左侧 t≤0、右侧 t≥1，则一条正 n
记录贡献恰5n条跨切口边。

“左时间端口”指左侧实际顶点中至少有一条边到右侧者；右侧同理。
若 i 作为左端的最大正 offset 为 N_i，则左端口数为5Σ_i N_i；
右端口数以右端对应最大 offset 同样计算。这里只按实际相同
(i,a,t) 去重，不将不同边计成不同端口。

原点是一个全局固定顶点。它若被硬放在左侧，会对右侧产生无限
多星形边。因此本节先固定原点颜色0，将60条邻轨化为各时刻
禁止颜色0的名单，再计算非零部分的有限切口；不隐去这一处理。

原代表选取给出的精确统计为：

| 指标 | 值 |
| --- | ---: |
| ∣n∣=0,1,2,3,4 的边轨道数 | 20816,258,1284,2,17 |
| n≠0 的边轨道数 | 1561 |
| 参与跨时间边的 H 代表 | 1027 |
| 左／右参与代表 | 356／745 |
| 左／右代表－时间端口（未乘η的5个相位） | 635／1380 |
| 左／右实际时间端口 | 3175／6900 |
| 跨切口实际边 | 14500 |
| 最大实际 ∣n∣ | 4 |

### 9.2 按整个轨道同步剥离的正确范围

每个代表的非零邻接度按实际 gain 多重邻接计数：同一对代表的
不同 gain 对应不同邻点，不能合并成简单商图的一条边；自轨道
非平凡 gain 的无向记录贡献两个邻点。另加原点相邻指标 ε_i∈{0,1}。
当前剩余轨道的有效度为 d_i+ε_i。

针对 k 色，在有效度<k 时删除整条轨道，按代表索引初始化队列，
每次删除后更新其余度，直到稳定。原点始终保留。反向恢复轨道时，
每个顶点至多有 k−1 个已经或待在本次轨道中处理的邻点：固定
已恢复部分颜色后，对本轨道的可数顶点按任一固定枚举逐个贪心
赋色即可。因此完整无限图可 k 染，当且仅当留下的核加原点可
k 染。该论证不保证保留一个事先指定的小时间周期；自轨道边
可能在某个周期商里变成自环，不能在恢复时删掉它。

| k | 移除 H 轨道 | 留下 H 轨道 | 核内边轨道 | 原点邻轨 | 核最小有效度 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5 | 16 | 4160 | 22313 | 60 | 5 |
| 6 | 988 | 3188 | 18087 | 60 | 6 |

五色剥离没有留下“小关键核”；六色剥离也仍有3188条轨道。
高最小度只是这一贪心算法不再适用，不是不可五染或不可六染证据。

### 9.3 一次确定性中位数换层，只压缩表示

令新代表 r'_i=u^(t_i)r_i，整数 t_i 只改变坐标标签，不改变任何
物理点或边。旧 gain (h,n) 变成 (h,n+t_i−t_j)。定义

\[
F(t)=\sum_{(i,j,h,n)}|n+t_i-t_j|.
\]

非零部分的跨切口边数就是5F(t)。固定其余 t_j 时，每条与 i
相邻的非自轨道边贡献 |t_i−b|，其中 b=t_j−n 使用从 i 出发的
有向 offset；自轨道项为常数。故所有整数最小值恰是这些 b 的
中位数区间。将 t_i 投影到该区间不会增大 F。

本轮只执行一次算法：从全零 t 开始，按 i=0,…,4175 顺序各更新
一次；偶数个数时取两中位数之间的闭区间，已有 t_i 若在区间内
就保持不动，否则取最近端点。没有重启、循环到收敛或另选启发式。

结果139个代表换层；t_i 的分布为
`−2:126, −1:3, 0:4037, 1:3, 2:7`。F 从2900降至1012：

| 指标 | 原代表 | 一次换层后 |
| --- | ---: | ---: |
| 非零 offset 边轨道 | 1561 | 601 |
| 跨时间活跃 H 代表 | 1027 | 570 |
| 左／右实际端口 | 3175／6900 | 1940／3385 |
| 跨切口实际边 | 14500 | 5060 |
| 最大绝对 offset | 4 | 4 |

新绝对 offset 0,1,2,4 的边数分别为21776,214,375,12。
它证明存在更紧凑的这一种时间切口，不证明得到最优切口、最小
路径宽度或更容易染色的图。有效度、色数及物理边在换层下不变。

## 10. 两份新正词没有修复旧14共同律：一个共同两点见证

本节审计 `certificates/rotation_orbit_colorings.json` 中的两份词，
其档案 SHA256 为
`716c49299627bc279399820170dab11f3da4873f8aaf920d1bfedcf6016aa3d8`。
两份已认证词分别使用 σ₃=(1 2 3)、σ₄=(1 2 3 4)，都固定原点色0
且 η 对颜色恒等。

用 equality 档案的精确坐标 p=η^h u^n r_i 拉回 Y，定义
w_P(p)=σ_P^n(b_i)，原点为0。得到的10077项整数数组摘要为

- 周期3：`8e64f73aafea918958a5153ff20ef876810ff13bf9f1c274011aac4d06f5e917`；
- 周期4：`cecbe1e0a2e77eb5beff4f46ec4ce9dd47478af40368345c3001f2689b65d4d3`。

本次从精确 Y 坐标重新调用
`verify_quintic_multiword_joint._definitions/_mapping`，提取旧14个
运动的完整最大域，并逐一核对 E083 的映射 SHA；没有只检查
搜出的某个子域。对源／像带标签点序列，按颜色首次出现次序规范
其划分，再比较整个划分，结果如下。两份单词，以及二者的等权
混合，均只有 η 一项通过。这个整14项量化审计仍为单实现，
重放入口在第11节；不要把下述 τ 两点见证的独立 PASS 外推到
整张统计表也已由第二实现重算。

| 运动 | 完整域点数 | 周期3／周期4／等权混合的划分律 |
| --- | ---: | --- |
| τ | 5084 | 均不相容 |
| ν | 556 | 均不相容 |
| η | 5289 | 均相容 |
| ω | 4671 | 均不相容 |
| 共轭 | 1895 | 均不相容 |
| bridge | 513 | 均不相容 |
| 平移1 | 333 | 均不相容 |
| 平移z | 200 | 均不相容 |
| 平移1+η | 573 | 均不相容 |
| 平移1+η² | 513 | 均不相容 |
| 平移1+η³ | 513 | 均不相容 |
| 平移1+η⁴ | 512 | 均不相容 |
| bridge_shift | 511 | 均不相容 |
| 负共轭 | 1866 | 均不相容 |

τ 的失败不只是一个大表的统计差异。同一个两点事件已经分离
两份词及其任意混合：在 Y 排序编号中，完整映射包含

\[
\tau(p_{32})=p_{6268},\qquad \tau(p_{36})=p_{6256}.
\]

这个具体映射及下表颜色相等／不等事件现已由
`research/verify_rotation_orbit_colorings.py` 独立重建并检查通过；
对应入口及整链认证见 [T127](rotation_orbit_five_coloring.md)。

| 词 | w(p₃₂),w(p₃₆) | w(p₆₂₆₈),w(p₆₂₅₆) |
| --- | --- | --- |
| 周期3 | 0,0 | 4,1 |
| 周期4 | 3,3 | 4,2 |

因此任意非负权重混合这两份词，都有

\[
\Pr[c(p_{32})=c(p_{36})]=1,\qquad
\Pr[c(p_{6268})=c(p_{6256})]=0. \tag{8}
\]

全局颜色重命名不改变相等事件；对任一词施加任意 H 时间相移
也仅是全局 σ_P 的幂重命名，η 相移则不改色。所以加入这些
对称副本后，(8)仍成立，仍不可能得到 τ 不变 joint。

这条排除限于两份保存词及所述副本的凸包；没有枚举所有 proper
五色词，没有全词分离，也没有排除旧14加u的共同律。它说明
“整个 H 宿主五染”与“修复旧平移／其他旋转的共同律”仍是不同
层次，不应在正宿主结论之后悄悄把第二个量词视为已经闭合。

## 11. 第9节及整14运动审计的完整重放

以下命令从仓库根目录运行，直接读取固定 SHA 的证书，只使用
Python 标准库及已有独立检查器中的精确几何／映射函数。它先
重算第9节全部表格，再由 `verify_quintic_tau_union` 完整重建 Y
及其实际边，拉回两份词并重建全部14个最大运动域。后半段会
执行原几何检查，运行时间不能与前半段的小组合统计混同。

它没有 SAT、缓存的映射代入、随机算法或新的搜索预算；中位数
算法恰执行一次同样的确定性扫描。命令复现的是本页单实现统计，
不是声称提供第二种独立统计算法。τ 两点事件的第二实现仍是
前述 T127 色词检查器。源码及证书不由本命令改写。

2026-09-26 已从本文原样提取并执行以下完整命令，进程 exit 0，
最后输出 `STRUCTURE_AND_OLD_FOURTEEN_REPLAY_PASS`；全部断言通过。
这份重放收据不改变上述单实现／独立认证的区分。

```sh
.venv/bin/python - <<'PY'
from collections import Counter, deque
from pathlib import Path
import hashlib
import json
import sys

if not __debug__:
    raise RuntimeError('Assertions must be enabled; do not use -O')
sys.path.insert(0, 'research')
from verify_quintic_core_probe import digest
from verify_quintic_tau_union import verify as geometry
from verify_quintic_multiword_joint import _definitions, _mapping, _pattern

root = Path('.')
expected = {
    'rotation_orbit_contacts':
        '909fbb3f4bb687537259044425a45993710a0f81a251a77de3939ea913c5da20',
    'rotation_orbit_equalities':
        'f0dd38c932cbf89fcb618db9b4c55411202da7a08d4bda5dc7ffe203ff0a31de',
    'rotation_orbit_colorings':
        '716c49299627bc279399820170dab11f3da4873f8aaf920d1bfedcf6016aa3d8',
    'quintic_multiword_return_joint':
        'e4ae7e9355783ee7606711ace881faba0353cbd01bef30c36b338dc3d3a844f9',
    'quintic_tau_union':
        '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1',
}
data = {}
for name, sha in expected.items():
    raw = (root / 'certificates' / (name + '.json')).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sha
    data[name] = json.loads(raw)
contacts = data['rotation_orbit_contacts']
E = [tuple(row) for row in contacts['contacts']]
N = contacts['representative_count']
O = set(contacts['origin_neighbors'])
assert N == 4176 and len(E) == len(set(E)) == 22377 and len(O) == 60
assert digest(E) == contacts['contact_sha256']
adj = [[] for _ in range(N)]
for i, j, h, n in E:
    adj[i].append((j, h, n))
    adj[j].append((i, (-h) % 5, -n))
assert all(len(row) == len(set(row)) for row in adj)

def cut(edges):
    left, right, active = {}, {}, set()
    hist = Counter()
    for i, j, h, n in edges:
        if n < 0:
            i, j, h, n = j, i, (-h) % 5, -n
        hist[n] += 1
        if n:
            active.update((i, j))
            left[i] = max(left.get(i, 0), n)
            right[j] = max(right.get(j, 0), n)
    return dict(offset_histogram=sorted(hist.items()),
                nonzero_contacts=sum(v for n, v in hist.items() if n),
                active_representatives=len(active),
                left_representatives=len(left), right_representatives=len(right),
                left_rep_time_ports=sum(left.values()),
                right_rep_time_ports=sum(right.values()),
                left_actual_ports=5*sum(left.values()),
                right_actual_ports=5*sum(right.values()),
                crossing_actual_edges=5*sum(n*v for n, v in hist.items()),
                max_offset=max(hist, default=0))

before = cut(E)
assert before == dict(offset_histogram=[(0,20816),(1,258),(2,1284),(3,2),(4,17)],
    nonzero_contacts=1561, active_representatives=1027,
    left_representatives=356, right_representatives=745,
    left_rep_time_ports=635, right_rep_time_ports=1380,
    left_actual_ports=3175, right_actual_ports=6900,
    crossing_actual_edges=14500, max_offset=4)
print('CUT_BEFORE', json.dumps(before, sort_keys=True), flush=True)

for k, target in [(5, (16,4160,22313,60,5)), (6, (988,3188,18087,60,6))]:
    active = [True]*N
    degree = [len(row) + int(i in O) for i, row in enumerate(adj)]
    queue = deque(i for i in range(N) if degree[i] < k)
    removed = []
    while queue:
        i = queue.popleft()
        if not active[i] or degree[i] >= k:
            continue
        active[i] = False
        removed.append(i)
        for j, h, n in adj[i]:
            if active[j]:
                degree[j] -= 1
                if degree[j] < k:
                    queue.append(j)
    core = [i for i in range(N) if active[i]]
    remaining = [e for e in E if active[e[0]] and active[e[1]]]
    summary = (len(removed), len(core), len(remaining),
               len(O.intersection(core)), min(degree[i] for i in core))
    assert summary == target
    print('CORE', json.dumps(dict(k=k, removed=summary[0], retained=summary[1],
          contacts=summary[2], origin_neighbors=summary[3], min_degree=summary[4])),
          flush=True)

# Exactly one coordinate-median sweep, in the original representative order.
t = [0]*N
for i in range(N):
    targets = sorted(t[j]-n for j, h, n in adj[i] if j != i)
    if targets:
        lo, hi = targets[(len(targets)-1)//2], targets[len(targets)//2]
        t[i] = max(lo, min(hi, t[i]))
shifted = [(i,j,h,n+t[i]-t[j]) for i,j,h,n in E]
after = cut(shifted)
assert sorted(Counter(t).items()) == [(-2,126),(-1,3),(0,4037),(1,3),(2,7)]
assert sum(x != 0 for x in t) == 139
assert sum(abs(e[3]) for e in E) == 2900
assert sum(abs(e[3]) for e in shifted) == 1012
assert after == dict(offset_histogram=[(0,21776),(1,214),(2,375),(4,12)],
    nonzero_contacts=601, active_representatives=570,
    left_representatives=228, right_representatives=396,
    left_rep_time_ports=388, right_rep_time_ports=677,
    left_actual_ports=1940, right_actual_ports=3385,
    crossing_actual_edges=5060, max_offset=4)
print('CUT_AFTER', json.dumps(after, sort_keys=True), flush=True)

# Independently reconstruct the source geometry; no saved motion map is loaded.
source_report, context = geometry(root, geometry_context=True)
Y = context['points']
assert source_report['geometry'] == data['quintic_tau_union']['geometry']
eq = data['rotation_orbit_equalities']
assert eq['representatives'] == contacts['representatives']
assert len(Y) == len(eq['coordinates']) == 10077
rep_index = {r:i for i,r in enumerate(eq['representatives'])}
words = []
results = data['rotation_orbit_colorings']['results']
assert [r['u_color_permutation'] for r in results] == [[0,2,3,1,4],[0,2,3,4,1]]
for result, period in zip(results, (3,4)):
    sigma, base = result['u_color_permutation'], result['word']
    assert len(base) == N and result['eta_color_permutation'] == list(range(5))
    word = []
    for coord in eq['coordinates']:
        if coord is None:
            word.append(0)
            continue
        r, h, n = coord
        color = int(base[rep_index[r]])
        for _ in range(n % period):
            color = sigma[color]
        word.append(color)
    assert all(word[i] != word[j] for i,j in context['edges'])
    words.append(word)
assert [digest(w) for w in words] == [
    '8e64f73aafea918958a5153ff20ef876810ff13bf9f1c274011aac4d06f5e917',
    'cecbe1e0a2e77eb5beff4f46ec4ce9dd47478af40368345c3001f2689b65d4d3']

old = data['quintic_multiword_return_joint']['result']
definitions = _definitions(context)
assert [row[0] for row in definitions] == old['motions']
expected_domains = [5084,556,5289,4671,1895,513,333,200,573,513,513,512,511,1866]
lookup = {p:i for i,p in enumerate(Y)}
for index, definition in enumerate(definitions):
    name = definition[0]
    mapping = _mapping(Y, lookup, context['ring']['mul'], definition)
    assert len(mapping) == expected_domains[index]
    assert digest(mapping) == old['mapping_sha256'][index]
    left = [_pattern(w, [i for i,j in mapping]) for w in words]
    right = [_pattern(w, [j for i,j in mapping]) for w in words]
    flags = [left[q] == right[q] for q in range(2)]
    flags.append(Counter(left) == Counter(right))
    assert flags == [name == 'eta']*3
    if name == 'tau':
        assert (32,6268) in mapping and (36,6256) in mapping
    print('MOTION', json.dumps(dict(name=name, domain=len(mapping),
          mapping_sha256=digest(mapping), period3_period4_equal_mixture=flags)),
          flush=True)
assert [[w[32],w[36],w[6268],w[6256]] for w in words] == [[0,0,4,1],[3,3,4,2]]
print('STRUCTURE_AND_OLD_FOURTEEN_REPLAY_PASS')
PY
```
