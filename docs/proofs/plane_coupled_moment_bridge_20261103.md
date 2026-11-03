# 2026-11-03：从全局染色到完备多点概率律；二点谱的精确天花板

状态：本项目完整书面证明和精确有理数校准；**不是**平面色数6/7的最终证明，未Lean形式化、未外部同行评审、无优先权声明。标识 R2026-MOMENT-A–E。独立脚本与证书另见同分支 research/verify_bessel_moment_ceiling.py 和 certificates/bessel_moment_calibration_20261103.json。

## A. 统一的主对象：同一份全局law，而不是各窗口不同law

对有限平面点集 F，令 Col_k(F) 为严格满足 F 中全部真实单位边的 k 标号集合。考虑一族 μ_F：每个 μ_F 是 Col_k(F) 上的概率；F⊂F' 时 μ_F 为 μ_F' 的限制边缘；任意欧氏等距变换 g 保持相应分布。

**定理A。** 对任意有限 k，下列三件事等价：

1. 整个 R² 有严格 k 染色。
2. 存在上述全部有限点集的等距不变、射影相容的概率族 μ_F。
3. 紧积空间 [k]^(R²) 上有等距群不变的Borel概率，支持在严格合法染色的闭子集上。

证明：3→2 取有限边缘。2→1：每个有限 Col_k(F) 非空，所有合法单位边柱约束有有限交性质，Tychonoff紧致性给全域染色。1→3：取合法染色 c，其全欧氏等距群 G=R²⋊O(2) 是阿贝尔群、有限群的连续扩张，作为抽象离散群仍amenable。以 G 的左不变均值平均 c 的轨道上连续函数值，得到紧空间上正、归一的线性泛函；Riesz表示为不变Borel概率。整个轨道位于严格合法染色闭集内，故概率支持在那里。证毕。

**不可数注意事项：** 每一条固定边的违规概率为0，不能直接将不可数零测事件相并；必须先对任一有限 F 作有限并，再由紧致性推出全域存在。这也说明同一Y的所有窗口分别可行不能代替同一个共同law。

## B. 完整二点谱与非负放松的颜色门槛是4

定义 Bessel J₀(t)=(2π)^{-1}∫₀^{2π}exp(it cosθ)dθ。令 β=min_{t≥0}J₀(t)，取极小点 s>0。第E节以严格有理数运算证明 -1/2<β<-1/3。

对所有 k≥4，设
\[
q(r)=\frac{J_0(sr)-\beta}{1-\beta},\quad
a_k=\frac{k}{(k-1)(1-\beta)},\quad
f_k(r)=1-a_k+a_k J_0(sr)=\frac{kq(r)-1}{k-1}.
\]
对颜色 i,j 和平面位移 z 定义
\[
\boxed{Q_{ij}(z)=\frac1{k^2}+\frac{\delta_{ij}-1/k}{k}f_k(|z|).}
\]

**定理B。** Q 对全部实平面位移是连续的、平移旋转和颜色置换不变的；对于任意两点它都是一张合法非负联合概率表（均匀单点边缘）；同点异色概率为0；任意单位距离同色概率为0；且对任意有限点集合和任意复系数，其全部颜色-位置二阶Gram矩阵半正定。

证明：J₀(s|z|) 是圆周角色的Haar平均，因此正定。β<-1/3使所有k≥4的 a_k∈(0,1)，f_k 是常数1与J₀的凸组合，故正定。置颜色空间投影 P∥=11ᵀ/k、P⊥=I−P∥；则 Q(z)=P∥/k+f_k(|z|)P⊥/k。两项Gram均PSD。又 β≤J₀≤1，故0≤q≤1，并且
\[
Q_{ii}(z)=q(|z|)/k,\qquad
Q_{ij}(z)=\frac{1-q(|z|)}{k(k-1)}\quad(i\ne j).
\]
故二点表非负、行和为1/k；q(0)=1，q(1)=0。证毕。

**定理C（模型内最优）。** 对k=2或3，满足定理B全部条件的连续径向、颜色置换不变PSD二点表不存在；所以本放松的最小颜色数**恰为4**。

证明：颜色置换不变、均匀边缘和同点互斥，使得任意可行Q必须分解为 P∥/k+f(|z|)P⊥/k；测试颜色标准表示可知f连续径向正定且f(0)=1。Bochner定理和旋转平均给f(r)=∫₀^∞ J₀(tr)dν(t)，ν为概率，因此f(1)≥β>−1/2。单位边对角Q_{ii}(1)=0要求f(1)=−1/(k−1)，k=2、3均矛盾。k=4由定理B可行。证毕。

重要：Q 的每张二点表是真概率、整块Gram也PSD，**但尚不是多点联合law**。标量Bessel松弛属于已有调和分析技术：Will Sawin 2026年6月 MathOverflow https://mathoverflow.net/questions/512024 。这里不声明发现新的经典theta界。

## D. 真正耦合从最简单的三个点开始：显式反例与普适尺度界

对于任何真正的颜色联合分布，令 D(x,y)=Pr(c(x)≠c(y))。颜色相等的传递性保证 D(x,z)≤D(x,y)+D(y,z)。对等距不变law，D(x,y)=D(|x−y|)，是径向伪距离。

**定理D。** 定理B的全部k≥4伪核，**即使只取三个共线点也不能扩成共同颜色概率律**。取 h=1/(10s) 和位置0,h,2h。定理B的二点不同色概率
\[
D(r)=\frac{1-J_0(sr)}{1-\beta}.
\]
于是
\[
D(2h)-2D(h)=\frac{2J_0(1/10)-J_0(1/5)-1}{1-\beta}>0.
\]
后者由Bessel交错级数的两个有理截断严格认证：
\[
2S_3(1/10)-S_2(1/5)-1
=\boxed{\frac{5734799}{1152000000}}>0,
\quad S_N(x)=\sum_{j=0}^N\frac{(-1)^j(x^2/4)^j}{(j!)^2}.
\]
J₀(1/10)≥S₃，J₀(1/5)≤S₂。该严格不等式违反三点概率的三角不等式，证明完毕。

**定理E（任意合法全局law必须满足的耦合刚性）。** 对任意等距不变、支持于合法单位距离染色的概率律及0<r≤1，
\[
\boxed{D(r)\ge 1/\lceil1/r\rceil}.
\]
证明：n=ceil(1/r)；r=1即D(1)=1。n≥2时取n−2条长度r的水平向右位移，以及另外两条长度r的位移（角度为±θ），其中cosθ=(1/r−n+2)/2∈[1/2,1]；总位移长度恰为1。沿此n步链取不等色事件的并界，得到1=D(1)≤nD(r)。证毕。特别D(1/n)≥1/n和liminf_{r↓0}D(r)/r≥1；真law不可能有定理B那样的D(r)=O(r²)光滑伪距离。**这个结论不要求颜色函数空间可测或有有限周长。**

## E. 对β的完全有理界，不依赖浮点极值

设T_N(x)=Σ_{j=0}^N(-1)^j(x/2)^{2j+1}/(j!(j+1)!)。由交错级数，J₀(4)≤S₆(4)=−803/2025<−1/3。J₀(t)在∞处趋0（圆周投影可积密度的Riemann–Lebesgue引理），所以负全局极小点存在。

为证β>−1/2：J₀'=-J₁，Bessel微分方程给 E(t)=J₀(t)^2+J₁(t)^2 满足 E'(t)=−2J₁(t)^2/t≤0。在0<t≤5/2，J₁(t)≥t/2−t³/16>0，故J₀递减。在t=5/2处有
S₅<J₀<S₄<0 以及0<T₅<J₁<T₄，并且
\[
S_5(5/2)^2+T_4(5/2)^2
=\frac{91042963788852401}{364791569817010176}<1/4.
\]
因此t≥5/2时|J₀(t)|≤√E(5/2)<1/2；更小时J₀(t)≥J₀(5/2)>−1/2。故−1/2<β<−1/3。所有有限比较均可用Python标准库的Fraction独立重放。

## F. 回到原问题：尚缺哪一条精确义务？

\[
\boxed{\chi(\mathbb R^2)=6}
\iff\text{定理A中存在完整的6色射影law}
\]
而
\[
\boxed{\chi(\mathbb R^2)=7}
\iff\text{存在一张有限、精确单位距离、不能6染的图}.
\]
后一等价依赖已证χ≤7和de Bruijn–Erdős紧致性。

定理B–E**只解决一条扩展支线的可行性和非延拓性**，并没有选择6或7。其数学意义在于严格淘汰“二点统计+所有二次PSD+单位边零相关就足以推出高色数”的路线。下一步必须约束同一份有限颜色律的**至少三点、最终全部有限点的完整划分关系**，不能从不同窗口的局部正律推出一个全局law，也不能把pairwise PSD误当Kolmogorov一致性。对k=6，找到真正6染构造或者有限NON6的UNSAT证书才算终局。

## 2026-11-03核查的外部来源

- OpenAI Family158 范围：https://github.com/openai/math/blob/main/lean/docs/158.md
- 三内核独立审计：https://github.com/punk01-shaka/hadwiger-nelson-audit
- 10月26日Comparator配置修正记录：https://github.com/mathcommunity/oai-math-revised/blob/main/docs/LEAN_CHECKS.md
- Davies高维转移：https://arxiv.org/abs/2610.12301
- Koshelev–Kupavskii–Voronov三维转移：https://arxiv.org/abs/2610.18907
- Galán尺规可作域的外部Lean结果：https://github.com/decalion89/chromatic-number-of-the-plane/blob/main/notes/six_over_fields.md
- Sawin Bessel二点PSD已有松弛：https://mathoverflow.net/questions/512024/is-the-lov%C3%A1sz-theta-function-tight-for-the-unit-distance-graph-of-the-plane-chr
