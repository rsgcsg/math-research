# 下一构造入口：有限下界、双接触平移和便宜排除

2026-09-27。初等推导与有限接口校准；不新增T/E编号，不宣称HN新界。
本页修正研究顺序，不修改[T139](translated_rotation_contacts.md)或[E111](shared_event_pricing.md)的证明。

## 1. 不给有限下界加上无限穷举的额外义务

取有限实际点集V及一组已逐条精确认证长1的边E₀，允许它漏掉实际单位边。
任何实际单位图U(V)的五染色都是(V,E₀)的五染色。因此若(V,E₀)不可五染，U(V)也不可五染。
邻点不能重合；非邻点允许重合时，亦可通过图同态将反证传至有限物理像。
若要给一个正染色证明U(V)可染，才须确认所有实际单位边；无限宿主正结论更需完整覆盖。

故T139的例外有限性可启发候选，但有效列出全部无限接触不是有限NON5搜索的前置条件。
“没有找全”不能充当无限正染色证明，却不妨碍一份真实所列子图给负证据。

## 2. 用两个接触方程直接生成平移，而不是盲选小数

选a₁,a₂∈A及b₁,b₂∈B，要求

`|a₁−(t+b₁)|=|a₂−(t+b₂)|=1`。

令d₁=a₁−b₁、d₂=a₂−b₂、δ=d₂−d₁、s=|δ|²。
当0<s≤4时，全部解为

```
t = (d₁+d₂)/2 ± (i δ/2) sqrt(4/s−1).
```

证明：两条半径1的圆方程相减，给t位于线段d₁d₂的中垂线。
写t=(d₁+d₂)/2+iδq，其中q为实数，则
`|t−d₁|²=s(1/4+q²)=1`，解得q=±sqrt(4/s−1)/2。
代回同时满足两个距离条件，故既必要又充分。
s=4时两个根重合；s>4无解；s=0只有一条独立圆条件，不能套公式除以零。
有限代数输入产生精确代数候选，可排除t=0后再收集实际跨边；不能把浮点近似边放进负证据。

最小反向校准：A=B={0,1}，取(a₁,b₁)=(0,0)、(a₂,b₂)=(1,0)，
得到t=(1+i√3)/2。四个实际点0,1,t,t+1诱导K₄去一边，有五条单位边，恰三色。
所以两个独立接触、三角形甚至新的根式都不等于五色强迫。

## 3. 少量跨边的无条件调色板修复

若A、B是两个**顶点不交**的可k染图，且合并后新增跨边的总数m<k，那么合图可k染。
任选两块各自合法染色，均匀随机重命名B的k个颜色。
每条跨边同色的概率为1/k，故冲突边数期望m/k<1；它是非负整数，至少一种重命名给0冲突。
这不冻结某份染色作负推理，而是对任选两块染色都证明存在合法匹配。

等价的有限检验是在k×k颜色配对表中找避开所有禁止格的置换；失败仅排除这两份已选染色的置换拼接，
不能据此排除自由重染。如果只知道部分跨边，则上面的正结论只属于该所列子图。
有物理交点时还存在颜色等同条件，必须另记；不能套“不交”的结论。
对k=5，m≤4是廉价退休条件，m≥5绝不是NON5充分条件。

## 4. 实际执行的标准库自检

下段本轮用python -S执行：121个有理中心差，92个精确根、4个相切中心、72个分离中心和1个重心；
菱形全部六对距离精确比较；k=2,3,4,5的禁配矩阵分别5、46、697、15276种，总16024种全部可修复。
这是有限校准，一般结论来自上面的完整初等证明。没有执行新的10077点平移扫描或取得NON5证书。

```python
from fractions import Fraction as F
from itertools import product, combinations, permutations
from math import comb
import json

# Each pair denotes a+b*sqrt(q); squaring is exact even when q is a rational square.
def square(x,q):
    a,b=x
    return (a*a+b*b*q,2*a*b)

def norm2(x,y,q):
    xx,yy=square(x,q),square(y,q)
    return (xx[0]+yy[0],xx[1]+yy[1])

roots=0; tangent=0; separated=0; coincident=0
for i,j in product(range(-5,6),repeat=2):
    d=(F(i,2),F(j,2));s=d[0]*d[0]+d[1]*d[1]
    if s==0:
        coincident+=1;continue
    if s>4:
        separated+=1;continue
    q=4/s-1
    for sign in ([1] if q==0 else [-1,1]):
        x=(d[0]/2,-sign*d[1]/2)
        y=(d[1]/2, sign*d[0]/2)
        assert norm2(x,y,q)==(1,0)
        assert norm2((x[0]-d[0],x[1]),(y[0]-d[1],y[1]),q)==(1,0)
        roots+=1
    if q==0:tangent+=1
# A=B={0,1}, t=(1+i*sqrt(3))/2: exactly the diamond, not a non-five graph.
z=F(0);o=F(1);h=F(1,2)
pts=[((z,z),(z,z)),((o,z),(z,z)),((h,z),(z,h)),((h+1,z),(z,h))]
edges=[]
for i,j in combinations(range(4),2):
    x=tuple(pts[i][0][k]-pts[j][0][k] for k in range(2))
    y=tuple(pts[i][1][k]-pts[j][1][k] for k in range(2))
    if norm2(x,y,F(3))==(1,0):edges.append((i,j))
assert edges==[(0,1),(0,2),(1,2),(1,3),(2,3)]
colors=[0,1,2,0]
assert all(colors[i]!=colors[j] for i,j in edges)
# All forbidden color-pair sets of size <= k-1, k<=5, leave a permutation.
permutation_cases={}
for k in range(2,6):
    masks=[sum(1<<(a*k+b) for a,b in enumerate(p)) for p in permutations(range(k))]
    count=0
    for m in range(k):
        for cells in combinations(range(k*k),m):
            f=sum(1<<x for x in cells)
            assert any(not(f&p) for p in masks)
            count+=1
    assert count==sum(comb(k*k,m) for m in range(k))
    permutation_cases[k]=count
print(json.dumps({'status':'PASS','double_contact_centers':121,'exact_roots':roots,'tangent_centers':tangent,'separated_centers':separated,'coincident_centers':coincident,'diamond_edges':edges,'diamond_proper_colors':colors,'forbidden_color_matrices':permutation_cases,'scope':'Elementary construction and disjoint-copy rejection calibration, not a Y experiment or an HN obstruction.'},indent=2))
```

## 5. 与完整共同律的接口

E111保存词在“u所有域事件＋12项指定二点差”上为零；该族继续调权不能得到全词严格正势。
下一负候选要加入其他运动的真正联合事件并用完整proper空间定价；正候选仍须验收15个完整域。
有限几何下界入口和共同律入口可以互相提供候选，但都必须最终输出无条件完整颜色证据。
不要用这份生成公式或廉价筛选替代尚未找到的颜色限制。
