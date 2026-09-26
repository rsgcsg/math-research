# T128：满秩赋值把多旋转的完整接触编译成有限线性候选

2026-09-26。完整证明、已执行的小型校准及两种实现的Y全赋值重放。
本页不声称已经编译第二个完整大宿主，也没有新的 SAT 查询或 HN 界。
它是 [T127 的 η/u 宿主关闭](rotation_orbit_five_coloring.md)之后，
对加入真实新生成元 τ 的算术入口，而不是增加同一宿主的层数。

## 1. 一般引理：r 个独立有限处足够，无需指数窗口

设 K⊂C 是共轭稳定数域，ζ∈K 为阶 m 的单位根。取
u₁,…,u_r∈K，均满足 u_j bar(u_j)=1。给定 r 个可精确计算的
非阿基米德赋值 v₁,…,v_r，其值群允许按有理正数缩放。
假设矩阵

\[
V=(v_i(u_j))_{1\le i,j\le r}
\]

在 Q 上可逆。记 g(n)=∏_j u_j^{n_j}，n∈Z^r，
G=〈ζ,u₁,…,u_r〉。

**引理。** 对任意非零 p,q∈K：

1. 同点识别 p=ζ^h g(n)q 的整数向量 n 至多一个，可由一次
   r×r 有理线性方程求得；之后至多检查 m 个 h。
2. 全部单位接触 |p−ζ^h g(n)q|=1，可由至多 3^r 个有理向量
   候选 n、每个至多 m 个 h 完整恢复。丢弃非整数向量，余者精确
   代回。若下述 C=0，只有一个有理向量候选。
3. 精确代回后，所有 (h,n) 合计至多两个接触，不是每个 h 两个。

这里 3^r 是候选上界，不是运行时间上界：赋值、线性求解和大整数
幂的位复杂度另计。满秩是假设，不能从“有 r 个看似不同的旋转”
自动推断；若只有秩 d<r，本引理只约束 d 个线性组合，不能宣称
留下的无界核已经枚举。

### 1.1 独立性与识别证明

单位根在每个有限处赋值为0。若 ζ^h g(n)=1，则 Vn=0，因此 n=0，
继而 h=0 mod m。故 G≅C_m×Z^r，每个所列群元素表示唯一；
G 在非零复数上自由作用。

若 p=ζ^h g(n)q，逐赋值得

\[
Vn=(v_i(p)-v_i(q))_{i=1}^r. \tag{1}
\]

V 可逆，所以先唯一求 n，再检验 n∈Z^r，最后逐个 h 精确检查
原等式。这既没有忽略远处返回，也没有把赋值相同误当点相同。

### 1.2 单位接触证明

令

\[
A=\bar p q\ne0,\quad B=p\bar q\ne0,\quad
C=p\bar p+q\bar q-1.
\]

置 z=ζ^h g(n)。距离式严格等价于

\[
Az+Bz^{-1}=C. \tag{2}
\]

设 a_i=v_i(A)、b_i=v_i(B)。若 C≠0，设 c_i=v_i(C)，
s_i=(Vn)_i。等式(2)的三个项赋值为 a_i+s_i、b_i−s_i、c_i。
非阿基米德三角不等式说明最小值必须至少出现两次；特别地，至少
有一对相等，因此

\[
s_i\in\left\{(b_i-a_i)/2,\ c_i-a_i,\ b_i-c_i\right\}. \tag{3}
\]

每行至多三个数，故 s=(s_i) 至多有 3^r 种候选。每个候选通过
n=V^{-1}s 给唯一有理向量，之后整数性和原距离式决定保留与否。
仅相等但不是最小的两项可能产生伪候选；精确代回会剔除它们。

若 C=0，两项的赋值必须相等，每行只剩 s_i=(b_i−a_i)/2。
不对 v_i(0) 做有限数值运算。所有 h 都有零赋值，故最后逐个
ζ^h 检验；m3^r 是最粗的精确代回次数上界。

将(2)乘 z 得 Az²−Cz+B=0。A≠0，所以复数根至多两个；
上节的表示唯一性说明每个根至多对应一个 (h,n)。这证明第3项。
同样应检查反向关系 D_qp=D_pq^{-1}，自轨道的单位元素永远不是边。

## 2. 有限种子给完整 Z^r 接触图，但没有自动周期完备性

给有限 P⊂K，先用(1)完整归并 P\{0} 的 G 轨道，选有限代表集
r₁,…,r_s，再对代表对用(3)编译全部真实接触。每对至多两个
gain，全部表有限。每个非零点唯一表示为 ζ^h g(n)r_i；颜色字母
可记录固定 n 上所有 m×s 个位置的颜色。有限接触表给有限个
Z^r 位移约束，故这是一个有限型移位（SFT）染色问题。

原点若在 P 中，只保留一个固定点；它邻接整条 i 轨道，当且仅当
|r_i|²=1。固定原点颜色后，这些位置有相应禁色名单。不能把原点
复制成 Z^r 的每层一点，也不能对其无限星形边套用二根界。

当 r=1，[T125](valued_rotation_orbits.md)的有限状态有圈论证
证明“可染 iff 存在周期染色”。当 r≥2，沿一个坐标切片时，横截面
仍无限；原来的有限状态证明已失效。一般 Z² SFT 确实存在非空但
没有周期点的例子：Robinson 的原文 §1、§2末及§3（尤其 pp.186,
189）给出只能非周期铺砌的有限局部规则；把有向瓦片种类作为字母，
边匹配就是 Z² 的最近邻约束。[原文](https://lipn.univ-paris13.fr/~fernique/qc/robinson.pdf)，
[出版页](https://link.springer.com/article/10.1007/BF01418780)。

这只排除把“一般 SFT”当成多维周期完备性的依据；**没有证明本页
特殊单位图染色 SFT 非周期、通用或不可判定**。本次原文核查读取
§1 和 §3 的有关陈述与层级构造结尾，未重新实现整套瓦片证明。
周期正词始终可直接证明一个上界；固定周期 UNSAT 不证明全宿主
NON5。真正有限实际图的不可五染证书则仍有效，紧致性也仍适用。

## 3. 当前最小新自由生成元：τ 与 u 的独立性

沿用

\[
u=\frac{1-3\sqrt5-\sqrt{-3}-\sqrt{-15}}8,\qquad
\tau=\frac{-1+3\sqrt{-11}}{10},\qquad\eta=e^{2\pi i/5}.
\]

两个根号虚部取与既有32维复坐标一致的正虚部。τ bar(τ)=1，且

\[
\tau^2+\tfrac15\tau+1=0. \tag{4}
\]

### 3.1 指定2处：v₂(u)=−1，v₂(τ)=0

[T125 §9](valued_rotation_orbits.md#9-已取得并归档的完整指数上界单位边9同点返回6)
指定的第0个2处满足 v₂(2)=1、v₂(u)=−1。式(4)及其倒数式均为
Z_(2) 上的首一方程，因此 τ 和 τ⁻¹ 都在每个2处整，故所有2处
v₂(τ)=0；这里不需要另做高精度 lift。

还可以直接在既有未分歧剩余域 F₁₆ 上校准。令
z=−1/2−√−3/6、ν=(5+√−11)/6、h=η+η⁻¹，则

\[
2u=1+3(h+1)z,\qquad\tau=(9\nu-8)/5. \tag{5}
\]

既有第0分量在 F₂[T]/(T⁴+T+1) 中为 (η,z,ν)↦(8,6,6)，
数字按多项式二进制编码。精确得到 2u↦6、τ↦6，二者均非零，
再次给出 v₂(u)=−1、v₂(τ)=0。η,z,ν 的指定根均简单，既有
T125 已核验其唯一提升；本次判断“单位”只需 mod2 的非零见证。

### 3.2 指定5处：v₅(u)=0，v₅(τ)=−1

令 s=√−11，w=(1+s)/2。w 是代数整数，

\[
w^2-w+3=0,\qquad\tau=(3w-2)/5. \tag{6}
\]

模5时 w 的根恰为2、4，导数2w−1分别为3、2，均非零。
由简单根提升，二者给 Q(s) 的两个5处。取 w≡2 的一处，则
3w−2≡4≠0 mod5，故以 v₅(5)=1 归一化有 v₅(τ)=−1。
该赋值延伸到包含 η,u,τ 的数域后仍按 v₅(5)=1 归一化。
延伸后的值群可能有分母，不假称它是 Z 值。

另一处分支 w≡4 的精确值可用范数直接确定：

\[
(3w-2)(3\bar w-2)=25.
\]

在 w≡2 分支，前一因子是单位；因此在 w≡4 分支其赋值为2，
τ 的赋值为1。本轮也实际执行到 mod125 的唯一根提升：
w≡2→17→92，w≡4→9→34；相应 3w−2 模125 为24、100，
明确给出赋值0、2，不把剩余0当成精确阶数。

u 与 bar(u) 的显式表达只以8为分母，分子全是代数整数，故在
每个5处都整。结合 u bar(u)=1，二者赋值必均为0。
单位根 η 在每个有限处的赋值亦为0。因此按列(u,τ)、行(v₂,v₅)，

\[
V=\begin{pmatrix}-1&0\\0&-1\end{pmatrix},\qquad\det V=1. \tag{7}
\]

于是 H′=〈η,u,τ〉≅C₅×Z²。τ 不是已有 H 的重命名或坐标选择。
每个非零代表对只需至多9个整数指数向量候选、每个5个 η 相位
精确代回；通过的真实接触仍总计至多2。

### 3.3 不能跳过的5处计算门槛

式(7)不等于已经实现任意 A、B、C 的 v₅。若使用第1节逐对至多
3^r 个候选的入口，还需取得 C=|p|²+|q|²−1 的精确赋值，不能用
零剩余猜它们。对固定种子也可改用有证明的统一指数范围；第6节
已在当前 Y 上实现后一入口，因此该具体全表不必等待通用 C 赋值库。
η 在5上是分歧的：若 π=η−1，则

\[
\pi^4+5\pi^3+10\pi^2+10\pi+5=0
\]

是5-Eisenstein多项式。模5的 Φ₅(X)=(X−1)^4 是重复根，
**不能照搬 T125 的简单根提升把 η 当成未分歧单位坐标**。
合适的局部接口可使用 π 的分歧扩张与 z 的未分歧二次扩张；
3z²+3z+1 模5不可约，其判别式−3≡2为非平方。
w 的选定分支则可用上述简单根逐步提升。也可采用等价的精确
素理想赋值算法；第6节验收的是当前 Y 所需的完整有限值表，仍不是
已经打包实现的任意输入／任意精度通用接口。

因此本轮消掉的是“第二方向可能从属于旧方向”和“必须拍一个
二维指数窗口”的量词，不是已经完成 H′Y 的全接触表或五染性。

## 4. 最小自证伪校准：自由秩变2仍可能恰二色

取

\[
p=(1-\tau)^{-1}=\frac12+\frac{3\sqrt{-11}}{22},
\qquad |p|^2=5/11.
\]

对 p=q，A=B=5/11，C=−1/11。2处的三个候选全部为0，故 u
指数必须 n=0；5处只给 τ 指数 k∈{−1,0,1}。连同 η 相位
只有15个待核验项。事实上距离二次式除以 A 后正好为
z²+(1/5)z+1=0，其两根是 τ、τ⁻¹；因此完整 H′ 轨道的
自接触恰为这两者。

H′p 的图于是分解成 〈τ〉 陪集上的双向无限路径，恰二色。
下面代码实际检查15个候选并只保留两条。这个例子说明 rank2
是真结构区别，却不是升色证据；跨轨道接触仍是唯一未被此例处理的
新颜色约束。

## 5. 本轮实际执行的完整小校准

在仓库根目录执行以下代码，`PYTHONPATH=research .venv/bin/python`
作为解释器。仅标准库及既有独立32维算术；没有 SAT、numpy、点对
大扫描或任意截断。普通入口输出 PASS；`-O` 必须主动拒绝。

```python
if not __debug__:
    raise RuntimeError('Assertions required; do not use -O')
from fractions import Fraction as Q
from verify_quintic_core_probe import multiplication_twice, product_twice, conjugate_twice
import json
T = multiplication_twice()
one = (Q(1),) + (Q(0),)*31
mul = lambda a,b: tuple(Q(x)/2 for x in product_twice(a,b,T))
bar = lambda a: tuple(Q(x)/2 for x in conjugate_twice(a))
eta = (Q(0),)*16 + one[:16]
u = tuple(Q({0:1,4:-3,9:-1,13:-1}.get(i,0),8) for i in range(32))
tau = tuple(Q({0:-1,10:3}.get(i,0),10) for i in range(32))
z = tuple(-Q(1,2) if i==0 else -Q(1,6) if i==9 else Q(0) for i in range(32))
nu = tuple(Q(5,6) if i==0 else Q(1,6) if i==10 else Q(0) for i in range(32))
h = tuple(a+b for a,b in zip(eta,bar(eta)))
assert tuple(2*x for x in u) == tuple(a+3*b for a,b in
    zip(one,mul(tuple(a+b for a,b in zip(h,one)),z)))
assert tau == tuple((9*x-8*y)/5 for x,y in zip(nu,one))
assert mul(u,bar(u)) == mul(tau,bar(tau)) == one
assert tuple(a+b/5+c for a,b,c in zip(mul(tau,tau),tau,one)) == (Q(0),)*32

def fmul(a,b):
    value = 0
    for i in range(4):
        if (b>>i)&1: value ^= a<<i
    for i in range(6,3,-1):
        if (value>>i)&1: value ^= 0b10011<<(i-4)
    return value

def fpow(a,n):
    value = 1
    for _ in range(n): value = fmul(value,a)
    return value

E,Z,N = 8,6,6
assert E^fpow(E,2)^fpow(E,3)^fpow(E,4)^1 == 0
assert fmul(Z,Z)^Z^1 == 0 and fmul(N,N)^N^1 == 0
two_u = 1^fmul(E^fpow(E,4)^1,Z)
assert two_u == 6 and N == 6
F = lambda w: w*w-w+3
lifts = {}
for r in (2,4):
    w = r
    for modulus in (5,25):
        candidates = [w+modulus*t for t in range(5)
                      if F(w+modulus*t) % (5*modulus) == 0]
        assert len(candidates) == 1
        w = candidates[0]
    lifts[r] = w
assert lifts == {2:92,4:34}
values = {}
for r,w in lifts.items():
    order,a = 0,(3*w-2)%125
    assert a != 0
    while a%5 == 0:
        a //= 5
        order += 1
    values[r] = order-1
assert values == {2:-1,4:1}
p = tuple(Q(1,2) if i==0 else Q(3,22) if i==10 else Q(0) for i in range(32))
assert mul(p,bar(p)) == tuple(Q(5,11)*x for x in one)
assert mul(p,tuple(a-b for a,b in zip(one,tau))) == one
torsion,actual = one,[]
for phase in range(5):
    for exponent,gain in ((-1,bar(tau)),(0,one),(1,tau)):
        delta = tuple(a-b for a,b in zip(p,mul(mul(torsion,gain),p)))
        if mul(delta,bar(delta)) == one: actual.append([phase,0,exponent])
    torsion = mul(torsion,eta)
assert actual == [[0,0,-1],[0,0,1]]
print(json.dumps(dict(status='PASS', F16_two_u=two_u, F16_tau=N,
    w_lifts_mod125=lifts, v5_tau=values,
    valuation_matrix=[[-1,0],[0,-1]], determinant=1,
    calibration_candidates=15, calibration_actual_contacts=actual)))
```

本代码是针对显式公式与剩余值的独立重算入口，不是任意输入的
5处赋值库。一般引理的有效性由第1节的完整证明给出。第6节继续
给出已执行的 Y 全值表及统一指数界；H′Y 的完整关系编译仍未完成，
也没有把二维 SFT 的正/负决定问题藏在“有限候选”四字里。

## 6. 已独立重放的 Y 全部5处赋值：完整二维指数矩形

本节是**有限精确验证加完整范围证明**，不是新一轮大图或 SAT。
生产侧在模5^6上直接二项式展开 η=1+π；独立重放改用模5^4=625，
逐次 Horner 代入 1+π。两种精度、两种展开算法得到同一10076行摘要：

`3bafba7ce838135f01a5ce3ff8076138df6b254dde67764a85c86b065df6d1c0`。

每行严格为 `[Y点索引, 4v_-(p), 4v_+(p)]`；v_-选择 w≡2，v_+
选择 w≡4，均按 v_±(5)=1 归一化。原点索引4641单独跳过，不赋
有限数值。输入证书及全部坐标摘要均在下方代码中绑定并重放。

### 6.1 为什么有限精度给的是精确值

在 L=Q(η,z,ν) 中使用既有精确基
`η^e z^b ν^c`，其中0≤e<4、0≤b,c<2，数组索引为 `8c+4b+e`。
先选 w 的简单5-adic根，并令 ν=(w+2)/3；这不是给 η 做简单根提升。
z 满足首一多项式 z²+z+1/3，其模5不可约，所以 Q₅(z)/Q₅ 为
未分歧二次扩张，{1,z} 的剩余类是 F₂₅/F₅ 的基。因此

\[
v_5(a+bz)=\min\{v_5(a),v_5(b)\},\qquad a,b\in\mathbb Q_5.
\]

理由是先提出共同的最低5次幂，再在 F₂₅ 中约化；只要两个系数
不同时为0，所得线性组合不可能消失。π 的多项式在此未分歧扩张
上仍 Eisenstein，故 π 是分歧次数4扩张的均匀元。记整数值赋值
\(\widetilde v=4v_5\)，于是 \(\widetilde v(\pi)=1\)、
\(\widetilde v(5)=4\)。

取 d≥0 清掉 p 的16个有理基系数中的5分母，展开

\[
5^d p=\sum_{j=0}^3(a_j+b_jz)\pi^j.
\]

四项非零时的赋值分别同余于 j mod4，所以不同 j 的最低阶不能
相等，因而不能发生跨 π 次数抵消。严格得到

\[
\widetilde v(p)=
\min_{0\le j<4}\bigl(4\min(v_5(a_j),v_5(b_j))+j\bigr)-4d. \tag{8}
\]

若系数只知模5^N，零剩余只给“阶≥N”；不得把它当成某个精确阶。
但只要式(8)减去4d前的最小值严格小于4N，它由一个非零剩余见证，
所以就是精确值。独立重放中 N=4、d≤1，全部20152个分支值的
清分母后最低阶至多12<16，没有一个未解决的零剩余。

**共轭交换两个分支。** 通常共轭满足
bar(w)=1−w、bar(z)=−1−z、bar(π)=−π/(1+π)。后两式分别给未分歧
扩张的自同构和另一个均匀元，均保持局部阶；第一式交换 w≡2、4。
因此正确等式是

\[
\widetilde v_-(\bar p)=\widetilde v_+(p),\qquad
\widetilde v_+(\bar p)=\widetilde v_-(p). \tag{9}
\]

不是同一分支的 \(v_-(\bar p)=v_-(p)\)；τ的−1与+1正好反驳后者。

### 6.2 从全值范围到完整 τ 指数界

对全部非零 p∈Y，记 x_p=\(\widetilde v_-(p)\)、
y_p=\(\widetilde v_+(p)\)。重放取得

\[
x_p\in[-4,4],\quad y_p\in[0,8],\quad
\max(y_p-x_p)-\min(y_p-x_p)=16.
\]

共17种实际 `(x_p,y_p)` 类型，完整直方图由下方程序输出。对单位接触
\(|p-\eta^h u^n\tau^k q|=1\)，在负分支有
\(\widetilde v_-(\eta^h u^n\tau^k)=-4k\)。令

\[
a=y_p+x_q,\quad b=x_p+y_q,\quad
\ell=\min(x_p+y_p,x_q+y_q,0).
\]

由(9)，a、b正是 A、B 的赋值，且 C 的赋值至少为ℓ；C=0时仍可
使用这个下界。若 k≥0 而 \(4k>a-\min(b,\ell)\)，则式(2)中的
\(A\eta^h u^n\tau^k\) 项成为唯一最低阶，矛盾。所以

\[
4k\le a-\min(b,\ell)
=\max\{(y_p-x_p)-(y_q-x_q),\ x_q-x_p,\ y_p-y_q,\ y_p+x_q\}
\le\max(16,8,8,12)=16.
\]

交换 p、q 并取 gain 的逆处理 k<0，故**所有**实际接触必有 |k|≤4，
不依赖 n 的大小。对于同点识别，赋值直接给
\(4k=x_q-x_p\)，故 |k|≤2，非整除4者直接排除。

τ在所有2处均为单位，所以 T125 原来的2处论证不变：单位接触
仍有 |n|≤9，同点识别仍有 |n|≤6，也不依赖 k 的大小。故对 Y，
以及其完整η饱和，全部非零点之间只需分别核验

- 单位接触：`h=0..4, n=-9..9, k=-4..4`，共855个 gain；
- 同点识别：`h=0..4, n=-6..6, k=-2..2`，共325个 gain。

这些是有证明的完整矩形，不是任意截断。各 gain 仍需精确代回，
原点的星形边与重复仍须单独处理。用此矩形编译当前 H′Y 不必先
计算每个 C 的精确5处值；一般第1节的至多9候选算法则仍需这些值。
**本节没有生成 H′Y 全部识别／单位边，也没有给它的五色词或 NON5。**

### 6.3 独立 Horner 重放命令与代码

在仓库根目录直接执行（不创建或修改研究源码）：

```sh
sed -n '/^# HN_Y_5ADIC_HORNER_BEGIN$/,/^# HN_Y_5ADIC_HORNER_END$/p' docs/proofs/valuation_rank_contact_compiler.md | PYTHONPATH=research .venv/bin/python
```

该完整命令已执行 PASS；首次独立运行52.397秒。此时间包含源诱导
几何重放，不是大宿主求解或 GPU 性能。代码不导入新的生产侧算法。

```python
# HN_Y_5ADIC_HORNER_BEGIN
if not __debug__:
    raise RuntimeError('Assertions required; do not use -O')
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import hashlib, json
from verify_quintic_core_probe import digest
from verify_quintic_tau_union import verify as geometry
root = Path.cwd()
assert hashlib.sha256((root/'certificates/quintic_tau_union.json').read_bytes()).hexdigest() == '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1'
report, ctx = geometry(root, geometry_context=True)
assert report['geometry']['point_sha256'] == '6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1'
coordinates = ctx['ring']['coordinates']
N, modulus = 4, 625
roots = []
for initial in (2,4):
    w, precision = initial, 5
    while precision < modulus:
        possibilities = [w + precision*j for j in range(5)
            if ((w+precision*j)**2-(w+precision*j)+3) % (5*precision) == 0]
        assert len(possibilities) == 1
        w, precision = possibilities[0], 5*precision
    roots.append(w)
assert roots == [217,409]
nu = [(w+2)*pow(3,-1,modulus) % modulus for w in roots]
assert nu == [73,137] and (sum(roots)-1) % modulus == 0

def order5_residue(x):
    if x == 0:
        return N  # Lower bound only, never an exact order for zero.
    result = 0
    while x % 5 == 0:
        result += 1
        x //= 5
    return result

def valuations(coefficients):
    d = 0
    for coefficient in coefficients:
        denominator, exponent = coefficient.denominator, 0
        while denominator % 5 == 0:
            denominator //= 5
            exponent += 1
        d = max(d,exponent)
    residues = []
    for coefficient in coefficients:
        integral = 5**d * coefficient
        assert integral.denominator % 5
        residues.append(integral.numerator * pow(integral.denominator,-1,modulus) % modulus)
    values, witnesses = [], []
    for nu_image in nu:
        polynomials = []
        for b in range(2):
            eta_coefficients = [(residues[4*b+e]+nu_image*residues[8+4*b+e]) % modulus
                                for e in range(4)]
            poly = [0,0,0,0]
            for coefficient in reversed(eta_coefficients):
                assert poly[3] == 0
                poly = [(poly[0]+coefficient) % modulus] + [
                    (poly[j-1]+poly[j]) % modulus for j in range(1,4)]
            polynomials.append(poly)
        weighted = [4*min(order5_residue(polynomials[0][j]),
                          order5_residue(polynomials[1][j]))+j for j in range(4)]
        minimum = min(weighted)
        assert minimum < 4*N, 'Unresolved residue; increase precision'
        values.append(minimum-4*d)
        witnesses.append(minimum)
    return values, d, witnesses

rows, maximum_cleared_order, max_denominator_power = [], 0, 0
for i,p in enumerate(ctx['points']):
    if not any(p):
        assert i == 4641
        continue
    values,d,witnesses = valuations(coordinates(p))
    rows.append([i,*values])
    maximum_cleared_order = max(maximum_cleared_order,*witnesses)
    max_denominator_power = max(max_denominator_power,d)
assert len(rows) == 10076
assert digest(rows) == '3bafba7ce838135f01a5ce3ff8076138df6b254dde67764a85c86b065df6d1c0'
assert maximum_cleared_order == 12 and max_denominator_power == 1
x,y = [r[1] for r in rows],[r[2] for r in rows]
assert (min(x),max(x),min(y),max(y)) == (-4,4,0,8)
joint = sorted(Counter(zip(x,y)).items())
assert len(joint) == 17
delta = [b-a for a,b in zip(x,y)]
terms = [max(delta)-min(delta),max(x)-min(x),max(y)-min(y),max(x)+max(y)]
assert terms == [16,8,8,12]
for xp,yp in dict(joint):
    for xq,yq in dict(joint):
        a,b = yp+xq,xp+yq
        lower = min(xp+yp,xq+yq,0)
        assert a-min(b,lower) <= 16 and b-min(a,lower) <= 16
        assert abs(xp-xq) <= 8
u_field = tuple(Q({0:1,4:-3,9:-1,13:-1}.get(i,0),8) for i in range(32))
eta_field = tuple(Q(int(i==16)) for i in range(32))
assert valuations(coordinates(u_field))[0] == [0,0]
assert valuations(coordinates(ctx['ring']['tau']))[0] == [-4,4]
assert valuations(coordinates(eta_field))[0] == [0,0]
print(json.dumps(dict(status='PASS',method='independent_Horner',modulus=modulus,
    w_roots=roots,nu_images=nu,nonzero_points=len(rows),valuation_rows_sha256=digest(rows),
    histogram_minus=sorted(Counter(x).items()),histogram_plus=sorted(Counter(y).items()),
    joint_histogram=[[a,b,count] for (a,b),count in joint],bound_terms=terms,
    maximum_cleared_order=maximum_cleared_order,max_denominator_power=max_denominator_power,
    tau_unit_offset_bound=4,tau_equality_offset_bound=2),indent=2))
# HN_Y_5ADIC_HORNER_END
```

## 7. E098：完整 rank2 自轨道扫描没有新增动作核障碍

在等待冻结源码的全回归期间，执行了一个有界的新检验：不编译全部
代表对，只检查 H′Y 的**全部自轨道单位接触**。第6节及 T125 已证
完整范围 h=0,…,4、n=−9,…,9、k=−4,…,4；不从搜不到远项推断界。
将 Y 的10076个非零点按精确平方半径归并为1259类，查询

\[
|r|^2\bigl(2-\eta^h u^n\tau^k-
  \overline{\eta^h u^n\tau^k}\bigr)=1. \tag{10}
\]

完整855个 gain 中，两个经逐基乘法验证的模同态（素数4261、20101）
筛选后仅余2项；两项均经精确整数域乘法及实际 Y 点距离复核。
**全部自接触仍恰为 (h,n,k)=(0,±2,0)**。对应唯一平方半径为

\[
R=2-\frac23\sqrt5.
\]

首次出现在 Y[597]，共12个 Y 点具有该半径，规范索引为
`597,1033,1034,3924,3925,4171,5233,6124,7822,9828,9829,9830`。
不依赖扫描还有可手算的阳性核对：由
`u+bar(u)=(1−3√5)/4`，得到
`|1−u²|²=4−(u+bar(u))²=(9+3√5)/8`，它与 R 的乘积恰为1。
这只重证已列出的正接触；“其余 gain 无接触”仍依赖完整模筛重放。
由于旋转保持半径，这覆盖整个 H′Y 的每个单独轨道；没有被忽略的
远层自接触。它**没有**检查不同轨道间的边或给出整个 H′Y 五染色。

### 7.1 对 commuting palette 的准确影响

仅考虑额外要求全局调色板群表示的五染，固定原点色0。η阶5且
必须固定0，故其颜色作用只能为恒等。设 σ、ρ∈S₄ 分别为 u、τ
在另外四种颜色上的作用；它们必须交换。自接触强制基色 b 满足
b≠σ²(b)，故 σ 只能有3循环或4循环：

- σ为3循环时，b必须属于被循环的三种颜色，不能取0或另一固定色；
  其在 S₄ 中的中心化子为 C₃，故 ρ=σ^a，a=0,1,2。
- σ为4循环时，b可取四个非零色，不能取0；中心化子为 C₄，
  故 ρ=σ^a，a=0,1,2,3。

**七个同时调色板共轭类全部通过本次自接触义务**，没有再排除任何
τ作用。直接枚举24×24个置换验证：交换的有序对恰120个，其中48个
通过，等于8×3+6×4。被排除的72对都因 σ 的阶为1或2，使 u²
落入整个颜色动作的核。这不是全词颜色关系的障碍，更不是 NON5。

这里的“通过”确实表示整个自接触子系统可满足，不仅是每条边
各自存在一个可用颜色。同一 H′ 轨道保持半径，完整自接触集合是
空集或 {u²,u⁻²}。在每条有边轨道任选一个上述允许的基色，再以
交换的 σ、ρ 延拓；因为 σ² 与两者交换，“不被 σ² 固定”的性质
在整条轨道上保持，故所有自边同时异色。不同轨道可独立选择基色。
固定原点色0在这里用于限制调色板表示，并不声称本扫描已经验收
所有原点星边或跨轨道义务；尤其不能由48对推出完整 H′Y 五染。

对一般自接触 (h,n,k)，上述七类的核筛选为 n+ak≢0 mod ℓ，
其中 ℓ=3或4；当前仅有 n=±2、k=0，故七类全保留。尚未编译的
跨轨道义务才可能给新信息，不继续在自接触上增加窗口或预算。

### 7.2 完整可重放命令与证据等级

以下是本次扫描本身的完整代码。它是**可重放的单实现精确有限检查**，
不是第二份独立扫描；复用既有独立算术并不会改变这个证据等级。
源几何重建绑定既有来源与点表摘要；本次不修改冻结的 `research/`
源码、JSON证书或求解器状态。将标记之间代码交给
`PYTHONPATH=research .venv/bin/python` 运行即可。

模筛没有漏掉零分母或退化项：每个分母显式检查与两素数互素；
若距离因子的模像为0，等式(10)的模像不可能为1，故可安全排除。
否则通过其逆像索引半径桶。任何真实边必在两个桶中，然后经过
不使用模容差的精确乘法。程序另核验855个 gain 都不同且范数一，
以及完整结果的取逆对称性。

```python
# HN_RANK2_SELF_CONTACTS_BEGIN
if not __debug__:
    raise RuntimeError('Assertions required; do not use -O')
from fractions import Fraction as Q
from pathlib import Path
from collections import defaultdict
from itertools import permutations
import hashlib, json, math, time
from verify_quintic_tau_union import verify as geometry
from verify_quintic_core_probe import product_twice, conjugate_twice, filter_map, digest
from verify_rotation_orbit_contacts import _split_map

started = time.monotonic()
root = Path('.')
assert hashlib.sha256((root/'certificates/quintic_tau_union.json').read_bytes()).hexdigest() == \
    '398d8490ee040ee29b93e4f9f3f6637f41ea45a3f2d8d6e5e47a70879e8a44f1'
_,ctx = geometry(root,geometry_context=True)
T = ctx['ring']['table']
den = math.lcm(*(x.denominator for p in ctx['points'] for x in p))
assert den == 480
points = [tuple(int(x*den) for x in p) for p in ctx['points']]
assert digest(points) == '6ca784d1ebe413a02dc35360fa9251d6497e221c39f9a0f9ef6aa6abc7d603a1'
radii = {}
for i,p in enumerate(points):
    if any(p):
        R = tuple(product_twice(p,conjugate_twice(p),T))
        radii.setdefault(R,[]).append(i)
assert len(radii) == 1259
Rden = 4*den*den
maps = [filter_map(T),_split_map(T,20001,True)]
assert [m[0] for m in maps] == [4261,20101]
ev = lambda v,im,pr: sum(x*y for x,y in zip(v,im)) % pr
buckets = defaultdict(list)
for R in radii:
    assert all(Rden % pr for pr,im,bars in maps)
    key = tuple(ev(R,im,pr)*pow(Rden,-1,pr) % pr for pr,im,bars in maps)
    buckets[key].append(R)
one = (Q(1),)+(Q(0),)*31
eta = (Q(0),)*16+one[:16]
u = tuple(Q({0:1,4:-3,9:-1,13:-1}.get(i,0),8) for i in range(32))
tau = tuple(Q({0:-1,10:3}.get(i,0),10) for i in range(32))
mul = lambda a,b: tuple(Q(x)/2 for x in product_twice(a,b,T))
bar = lambda a: tuple(Q(x)/2 for x in conjugate_twice(a))
assert mul(u,bar(u)) == mul(tau,bar(tau)) == mul(eta,bar(eta)) == one
Ep = [one]
for j in range(4): Ep.append(mul(Ep[-1],eta))
assert mul(Ep[-1],eta) == one and len(set(Ep)) == 5
def powers(g,N):
    result = {0:one}
    for n in range(1,N+1):
        result[n] = mul(result[n-1],g)
        result[-n] = mul(result[1-n],bar(g))
    return result
Up,Tp = powers(u,9),powers(tau,4)
hits,seen,checks = [],set(),0
for h in range(5):
    for n in range(-9,10):
        for k in range(-4,5):
            g = mul(mul(Ep[h],Up[n]),Tp[k])
            assert g not in seen and mul(g,bar(g)) == one
            seen.add(g)
            delta = tuple(2*a-b-c for a,b,c in zip(one,g,bar(g)))
            d = math.lcm(*(x.denominator for x in delta))
            D = tuple(int(x*d) for x in delta)
            assert all(d % pr for pr,im,bars in maps)
            residues = [ev(D,im,pr)*pow(d,-1,pr) % pr for pr,im,bars in maps]
            if any(x == 0 for x in residues): continue
            key = tuple(pow(x,-1,pr) for x,(pr,im,bars) in zip(residues,maps))
            for R in buckets.get(key,[]):
                checks += 1
                if product_twice(R,D,T) == [2*Rden*d]+[0]*31:
                    indices = radii[R]
                    p = ctx['points'][indices[0]]
                    physical = tuple(a-b for a,b in zip(p,mul(g,p)))
                    assert mul(physical,bar(physical)) == one
                    hits.append(dict(gain=[h,n,k],Y_indices=indices,
                        radius_sparse=[[i,str(Q(x,Rden))] for i,x in enumerate(R) if x]))
assert len(seen) == 855 and checks == 2
keys = {tuple(row['gain']) for row in hits}
assert keys == {(0,-2,0),(0,2,0)}
assert {((-h)%5,-n,-k) for h,n,k in keys} == keys
assert all(row['radius_sparse'] == [[0,'2'],[4,'-2/3']] and
           row['Y_indices'] == [597,1033,1034,3924,3925,4171,5233,6124,7822,9828,9829,9830]
           for row in hits)
classes = []
for order in (3,4):
    for a in range(order):
        killers = [list(g) for g in sorted(keys) if (g[1]+a*g[2]) % order == 0]
        classes.append(dict(u_cycle_order=order,tau_power=a,
                            self_contact_compatible=not killers,kernel_gains=killers))
compose = lambda a,b: tuple(a[b[i]] for i in range(5))
def ppow(p,n):
    result = tuple(range(5))
    for j in range(n % 12): result = compose(result,p)
    return result
perms = [(0,)+p for p in permutations(range(1,5))]
commuting,accepted = 0,0
for su in perms:
    for st in perms:
        if compose(su,st) != compose(st,su): continue
        commuting += 1
        allowed = set(range(5))
        for h,n,k in keys:
            motion = compose(ppow(su,n),ppow(st,k))
            allowed = {c for c in allowed if motion[c] != c}
        accepted += bool(allowed)
assert (commuting,accepted) == (120,48)
assert all(c['self_contact_compatible'] for c in classes)
print(json.dumps(dict(status='PASS',source_point_sha256=digest(points),
    nonzero_radii=len(radii),gain_count=len(seen),modular_primes=[m[0] for m in maps],
    exact_radius_checks=checks,hits=hits,commuting_S4_pairs=commuting,
    self_compatible_commuting_pairs=accepted,classes=classes,
    elapsed_seconds=time.monotonic()-started),indent=2))
# HN_RANK2_SELF_CONTACTS_END
```

执行收据：初次完整扫描32.26秒、完整归档命令复跑34.57秒，均退出0；
首版和归档版只差额外的855个 gain 唯一性／范数核对与详细索引输出，
数学结果一致。实际耗时仅描述本机该次运行，不是复杂度或硬件承诺。
归档版脚本临时副本 `/tmp/hn-rank2-self-contacts-replay.py`，日志
`/tmp/hn-20260926-rank2-self-contacts-replay.log`；可重放来源以本节
完整代码为准。此后补入12个索引的显式断言，核对的正是该次完整
输出，不改变搜索算法；主代理还将原样复跑并审计关键半径乘法。
