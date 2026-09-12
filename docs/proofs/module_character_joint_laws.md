# T103–T104 / E069–E070：整个平移模的 joint 正律与三特征混合

2026-09-11。原始 HN 没有新上下界。本文正结论是固定有限 X 上
**无限多个运动的全部最大域联合分布**，不是无限宿主的 proper 染色。

## 1. 本轮入口与具体数据

沿用 E061 的 X=P∪R∪B：5084 点，12920986 点对，24844 条实际单位边。
令 η=e^(2πi/5)，z=−1/2−i√3/6，M=Z[η]+zZ[η]。
上一轮留下 x↦x+ηz 的完整最大域查询。

该域恰有 600 点。依次平移 1+ηz、−1 的共同词只覆盖其中 200 点；
反序覆盖 202 点。经 η 的共轭平移词覆盖 94 点。这些仅是三个
指定词的覆盖计数，不证明不在整个旧词闭包中。更重要的是，旧 E065
正词已经直接修复全部 600 点，无须再调用 SAT。

随后检查完整旋转轨道；旧 E065 词同样修复下列八个最大域：

| j | 平移 ηʲ 的域大小 | 平移 ηʲz 的域大小 |
| --- | ---: | ---: |
| 1 | 393 | 600 |
| 2 | 462 | 400 |
| 3 | 264 | 400 |
| 4 | 264 | 400 |

这些有限正例未被当成“全体平移已解决”。初步探索中，把旧词按
平移 1 的五循环重新标号后，在 55 个模陪集上仍不满足下面的仿射
模型（探索计数，不作为负结论）。我们在明确限定的仿射模型中重新
求解，没有冻结旧词；该模型不被当成完整 joint 的完备搜索空间。

## 2. 模、特征与精确陪集判定

M 的八个基向量为 ηʲ、zηʲ，j=0,…,3。独立检查器在 32 维精确
有理坐标中证明它们线性独立，行主元为
0,4,9,13,16,20,25,29。这里的秩八属于平移模，不是 X 坐标域的次数。

唯一写出 t=Σaⱼηʲ+Σbⱼzηʲ，定义

φ(t)=Σaⱼ+2Σbⱼ mod 5。

由 η⁴=−1−η−η²−η³、bar(z)=−1−z，可知 M 在
H={±ηʲ, ±ηʲ conjugation:j=0,…,4} 下不变；且
φ(ηt)=φ(t)，φ(bar(t))=φ(t)，φ(−t)=−φ(t)。
检查器对每个基向量直接验证这些恒等式及整数坐标，未假设有限
样本的平移相容性自动推广。

这里的 5 有明确结构来源：把各 ηʲ 的加性特征值都取 1，五项和
必须为零；共轭式又强制 2φ(z)=−1，故 φ(z)=2（mod 5）。但 φ 不是
整个坐标域的环同态：z 满足 3z²+3z+1=0，代入 2 在 F₅ 中得到
4 而非 0。不能把这个加性字符误叫作覆盖全域单位边的剩余域染色。

把任意坐标 p 唯一分解为 p=r+Σαᵢbᵢ，其中 r 的八个主元坐标为零。
取 K(p)=(r,(αᵢ−⌊αᵢ⌋)ᵢ)，h(p)=φ(Σ⌊αᵢ⌋bᵢ)。则

K(p)=K(q) 当且仅当 q−p∈M；此时 φ(q−p)=h(q)−h(p)。

这同时保留有理系数的小数部分，不能只比较 Q-span(M) 商空间。
5084 个点恰落在 941 个 M 陪集中。

## 3. T103：不再只修复有限平移列表

**T103。存在 X 上的 proper 五色词 c，使对所有
g(p)=r p+t、r∈H、t∈M，只要 p,g(p)∈X，就有**

c(g(p))=s(r)c(p)+φ(t) mod 5，

其中 r=±ηʲ 或 ±ηʲ conjugation 时，s(r) 为该显式正负号。
因此同一个 S₅ 平均律修复 Γ=M⋊H 中每个运动的整个最大域。

**有限核验如何覆盖无限量词。** 检查器验证 c(p)−h(p) 在每个 K(p)
上为常数 A(K)。对于 20 个 r 和每个 p∈X，若 K(rp) 在 X 中出现，
再验证 A(K(rp))=s(r)c(p)−h(rp)。对于任意 q=rp+t∈X，
代入上一节陪集恒等式立即得到所需等式。因此没有截断平移长度，
也没有要求一条实现 g 的运动词中间点留在 X 中。

同一 g 对整个域使用一个颜色置换 a↦s(r)a+φ(t)。在全部 120 个
全局颜色重命名下平均，得到一个共同的完整划分律。旧十最大域及
十八四点事件均属于 Γ，故全部保留，而非放弃旧义务。

E069 还保存了同一字符 φ 模型中仅加入 M、未加入 H 时的一份
proper 词，以及最终加入 H 后的一份词；两者均独立核验全部实际边。

## 4. 下一旋转确实改变单词关系，但固定 frame 不是终局

令 ω=e^(2πi/3)=−2−3z，故 ω²+ω+1=0，ωz=1+z，M 在 ω 下也不变。
ω 不在 H 中。它在 X 上的最大域有 2381 点。对于 T103 的最终词，
实际映射对 (0,4787)、(2,3700) 的源颜色同为 4，像颜色分别为 1、4，
故该词甚至不能保持这个两点划分。独立检查器核验坐标映射及划分差。

不过，不能据此排除完整 joint。单一五色仿射表示还有一个一般障碍：
若 M 的像是一个传递 C₅，ω 的共轭作用必须是 Aut(C₅) 中阶数整除 3
的元素，而 |Aut(C₅)|=4，故该作用只能平凡。于是 (ω−1)M 映为零。
由 (ω−1)(ω²−1)=3 得 3M 映为零，与非平凡 C₅ 像矛盾。
这是这种固定传递表示的天花板，不是所有五色分布的天花板。

## 5. T104：三份词修复整个扩大的运动群

定义 χⱼ(t)=φ(ωʲt)，j∈Z/3。若 a=Σaᵢ、b=Σbᵢ，则

χ₀=a+2b，χ₁=2a+3b，χ₂=2a（mod 5）。

三者由 ω 循环交换；共轭交换下标 j 与 −j。独立检查器逐基向量
验证这些公式。不是先假设三种相位应当等概率，而是先构造满足
下面协变恒等式的三份实际 proper 词。

**T104。存在 X 上的三份 proper 五色词 c₀,c₁,c₂。对于每个**

g(p)=sωᵏηᵉ bar^ε(p)+t，
s∈{±1}, k∈Z/3, e∈Z/5, ε∈{0,1}, t∈M，

**以及 p,g(p)∈X，均有**

cⱼ(g(p))=s c_{(-1)^ε(j+k)}(p)+χⱼ(t) mod 5。

证明与 T103 相同，但每个陪集保存三个常数 Aⱼ(K)，使用三个字符
χⱼ；检查 60 个正交部分与 X 中每点的完整陪集交会，而非仅原域
内的共同词。所有 3×24844 条边约束直接验证。有限恒等式通过
K(q)=K(rp) 当且仅当 q−rp∈M 推出任意平移 t 的结论。□

现在取 j 均匀，再独立取全局颜色置换 σ∈S₅ 均匀。每个 g 仅置换
j 的三个取值，并对各项作全局颜色重命名。因此这一个至多 360 词
的分布同时修复 Γ′=M⋊H₃₀ 的**所有完整最大域划分律**，其中
H₃₀={±ωᵏηᵉ, ±ωᵏηᵉ conjugation} 有 60 个元素。

整个 Γ 包含在 Γ′ 中；T104 没有牺牲 T103 或 E065 的任何 joint 义务。
T094 不允许固定原子数作为通用完备性假设，与这里一个具体实例的
三词构造不矛盾。三词也未声明最少。

## 6. 真正关闭了什么

任何从 Γ′ 选取运动、在当前 X 内选取任意大小源组的 full-joint
分离搜索，都不可能得到严格正余量：上述分布已是统一零向量见证。
这包含任意长出域重入词，而不只有限动作列表。

不证明 Γ′X 的诱导单位图可五染：新轨道点之间可能有未出现在
任何当前源图副本中的单位边。不证明全平面、整个 E 或全部部分
全等可行。新的攻击必须增加真正新几何，或使用 Γ′ 之外的运动。

由此不再逐个添加 M 内平移。下一候选采用
ν=(5+i√11)/6 的旋转最大域；其无限阶使它不在有限 H₃₀ 中。
它是无限阶旋转，不能直接套用 T096 的有限 H 公式。本轮已进一步
证明 [T105](arbitrary_motion_joint_compiler.md)，使任意有限运动族的
真正全词反证均可显式编译，不再为此额外悬置有限方向群假设。

### E071：该下一候选也已实际抽域，不只留下路线图

ν 的完整最大域恰有 271 点，整个域与像都不包含于任一单 Parts
副本。精确映射中包含 (32,66)、(215,3048)。对于 T104 保存的三词混合，
源点 32、215 的同色概率为 0，像点 66、3048 的同色概率为 2/3。
全局 S₅ 平均不改变同色概率，故这是该特定正律的新缺口。

ν 虽属于原域 F，当前 X 并不包含于 F；此处检验的是实际跨副本
部分全等的联合律，不是在 F 内另找普通 NON5，故不与 T028 混同。

这不否定其他五色词或其他混合：T095 已证明单个合法两点状态可延伸。
下一任务是将这个运动的整个最大域义务与此前 Γ′ 义务一起保留，
进行完整词定价／寻找新自由混合；不得把 0≠2/3 升格成全词分离。
三字符构造也不作为下一次负搜索的完备词空间。

以下用独立几何检查器重放该有限探针（不是调用生产器）：

```sh
PYTHONPATH=research .venv/bin/python - <<'PY'
from pathlib import Path
from fractions import Fraction as Q
import hashlib, json
from verify_quintic_joint_ports import verify
from verify_quintic_core_probe import multiplication_twice, product_twice
r=Path.cwd()
_,pts,edges,_,copies=verify(r,r/'certificates/quintic_joint_translations.json',geometry_context=True)
den=json.loads((r/'certificates/quintic_joint_translations.json').read_text())['denominator']
points=[tuple(Q(x,den) for x in p) for p in pts]
lookup={p:i for i,p in enumerate(points)};table=multiplication_twice()
nu=[Q(0)]*32;nu[0]=Q(5,6);nu[10]=Q(1,6)
mapping=[]
for i,p in enumerate(points):
    q=tuple(Q(x)/2 for x in product_twice(nu,p,table))
    if q in lookup:mapping.append((i,lookup[q]))
assert len(mapping)==271 and (32,66) in mapping and (215,3048) in mapping
assert not any({i for i,j in mapping}<=b or {j for i,j in mapping}<=b for b in copies)
raw=(r/'certificates/quintic_three_character_law.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='b83104c8249a23c074af7cb7791b62c2d42c2e6bdcc1f41077c23a08cb8423ac'
words=json.loads(raw)['result']['words']
assert len(words)==3
assert all(len(w)==len(points) and set(w)==set('01234') and all(w[i]!=w[j] for i,j in edges) for w in words)
assert sum(w[32]==w[215] for w in words)==0
assert sum(w[66]==w[3048] for w in words)==2
print('PASS E071: 271-point maximal domain, old-law mismatch only')
PY
```

## 7. 证据与重放

- [E069 证书](../../certificates/quintic_module_law.json)：绑定 E065 来源，
  两份词、八个新最大域及 20 个正交部分的陪集交会计数。
- [E070 证书](../../certificates/quintic_three_character_law.json)：绑定 E069，
  三份词及 60 个正交部分交会计数。
- 两生产器使用 SymPy/SAT；独立检查器只用标准库，以另一套精确
  代数和携带基恒等式的有理消元核验；不导入生产器或求解器。

```sh
.venv/bin/python research/quintic_module_law.py
.venv/bin/python research/quintic_three_character_law.py
python3 research/verify_quintic_module_law.py
python3 research/verify_quintic_three_character_law.py
make check
```

本轮源树继承了上一轮未提交改动，未覆盖或回滚它们。新证书 SHA256：

- E069：`7b77306b1027462799f6e3ebeb5f194a78e9c82af292537e5010f9c36092c25d`
- E070：`b83104c8249a23c074af7cb7791b62c2d42c2e6bdcc1f41077c23a08cb8423ac`

2026-09-12 收尾：两项独立检查已 PASS；E071 另用独立几何重放域与
概率差。新增 E069、E070、T105 校准入口集成后的完整 `make check`
已退出 0，其后只补充文档回执。

六项定向篡改全部拒绝：错误陪集数、用旧 proper 词替换模词、
阶段标签、前置 SHA、交换两份仍 proper 的字符词、单色坏词。
篡改测试复用了先独立验证过的几何上下文，没有以生产器充当检查器。
三个新验证入口均拒绝 `-O`；七个相关 Python 文件 AST、文档本地链接
及 `git diff --check` 通过。未提交、推送或修改索引。
