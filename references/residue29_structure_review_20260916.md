# H29 来源审查：Paley 类型与谱界常数

2026-09-16。本文件仅保留来源核对，不承载新定理或独立研究状态。
T121的完整证明、E087查询记录与严格小例校准统一见
[H29旋转等变天花板](../docs/proofs/residue29_rotation_ceiling.md)。
H29自由六色查询仍未知；不得由任何引文、固定表示或搜索失败倒推L或HN下界。

## 已读来源与适用范围

1. **Schneider–Silva，arXiv:1306.6050v1（2013-06-25）**，
   [原PDF](https://arxiv.org/pdf/1306.6050v1)。已读§3定义和
   Theorem4.7(3)及其证明，印刷第9页、PDF第9页。
   平方阶广义Paley图的`ω=χ=p`判据要求指数m整除p+1。
   当前T121的指数是28，不整除30；不可误套普通Paley图结论。

2. **Vinh，math/0510092v1（2005-10-05）**，
   [原PDF](https://arxiv.org/pdf/math/0510092v1)。印刷第3页（PDF第3页）
   Lemma4与§3正文实际印的是`|λ|≤√q`，已渲染并视觉确认，不是抽取遗漏2。
   第4页Table1给出D7的四染色；E087独立重建全部196条边验证。
   本仓库T053早已警告正文常数不可靠，本轮补的是精确反例与原页核对。

3. **Vinh，math/0606482v1（2006-06-20）**，
   [原PDF](https://arxiv.org/pdf/math/0606482v1)。印刷第3页（PDF第3页）
   Lemma2同样写`|λ|≤√q`；第2页Theorem1据此给过强色数下界。
   第2–3页均视觉核验。E087的D5谱反例否定所印谱界，D7四词直接否定
   该Theorem1在q=7的陈述。不声称后续版本是否修改。

4. **Harcos，Weil's bound for Kloosterman sums**，
   [作者PDF](https://users.renyi.hu/~gharcos/weil.pdf)。2026-09-16下载版本，
   已读印刷／PDF第1页Theorem1与其证明框架：p>2为素数，a,b均非零
   模p时，Kloosterman和绝对值至多`2√p`。这已覆盖29及E082奇素数截止。
   未重新核查全部14页证明，不声称独立重证Weil的曲线输入。
   一般素数幂的原输入仍为T053已核对的
   [Conrad，Theorem3](https://kconrad.math.uconn.edu/articles/kloosterman.pdf)。

5. **Terras，Finite Models for Arithmetical Quantum Chaos**，
   [作者PDF](https://mathweb.ucsd.edu/~aterras/newchaos.pdf)。已读印刷／PDF
   第14页(4.1)的Ramanujan定义、第15–16页§4.1和Exercise4的
   特征和／Kloosterman公式。该段是标准平方和图，不能省略split/nonsplit区别。

1996年Medrano–Myers–Stark–Terras出版社原PDF本轮访问失败，未宣称已读。
Weil1948原文的PMC下载返回非PDF页面，也未宣称已读；本轮权威输入核验
限于上述Harcos明确陈述及T053既有Conrad依据。

## 已复核的本地原件

以下均为本轮下载的未修改原PDF，存于Git忽略的cache目录；持久引用采用上面URL和版本。
主代理已视觉复核两份Vinh列示页面及Harcos第1页；Terras列示段落由子代理阅读。

| 本地原件 | 需要复核的位置 |
| --- | --- |
| `references/cache/vinh-math-0510092v1.pdf` | PDF第3页Lemma4与§3；第4页Table1 |
| `references/cache/vinh-math-0606482v1.pdf` | PDF第2页Theorem1；第3页Lemma2 |
| `references/cache/harcos-weil.pdf` | PDF第1页Theorem1，准确常数2√p |
| `references/cache/terras-newchaos.pdf` | PDF第14页(4.1)；第15–16页§4.1、Exercise4 |

原件SHA256按上表顺序：

```text
4ce563d7cccdfe2ef0dd9bce00c6ff89488a870532503b9ff8723bfad6718431
1d98d8a7d52bed3519fa7c4bab87d099e74f05815706300d44aa2c5afc7781a3
ee17d5dff37e572d0a00727954cb5cbab0ea57693f90e010a4e6446edb2cc394
89cff7542f9cc14f520ca38eb6e481501b6aa2073bb3dabfa45a803838fab1cb
```
本轮没有找到H29的已知精确色数文献；这只是检索结果，不是文献不存在的证明。
