# T172：三类总量匹配后仍有显式身份偏差下界

2026-10-06（Australia/Brisbane）。接续 T165、T170–T171。普通 Hadwiger–Nelson 没有新界；任意支持 full15 仍未解决。

## 1. 结论

在 T165 的七个 saturated K7 等式与 PRR 等式共同定义的 W22 边界面上，设一份 proper 至多五块划分概率律的逐事件同色边际为 (x_e)。假设它只在三类总量上与 C030 一致：

[
sum_{ein P}x_e=47/27,qquad
sum_{ein Q}x_e=77/10,qquad
sum_{ein R}x_e=434/27.
]

则 89 条指定 P/Q/R 事件中至少一条满足

[
left|x_e-t_eight|ge rac{115}{120663}approx 9.530676	imes10^{-4},
]

其中 (t_e=1/27)（P）、(7/10)（Q）、(14/27)（R）。

因此 T171 的“三类总量可行”不能被误读成逐事件近似也可以任意精确：T165 的 separator 给出一个显式、严格正的 identity-sensitive 距离下界。

## 2. 从 T165 separator 出发

T165 给出整数系数 (alpha_e)，对边界面上每份 proper 划分逐点成立

[
L(c)=sum_ealpha_e,1[e	ext{ 同色}]le2.
]

三类系数和为

[
sum_Palpha=-2267,qquad sum_Qalpha=500,qquad sum_Ralpha=-501.
]

在 C030 的逐事件均匀目标 (t) 上，

[
alphacdot t
=-rac{2267}{27}+500rac7{10}-501rac{14}{27}
=rac{169}{27}.
]

故任意边界律 (x) 都满足

[
alphacdot(t-x)ge rac{169}{27}-2=rac{115}{27}. 	ag{1}
]

## 3. 利用 T171 的 class-total 超平面做最优 gauge

在本节假设下，每一类都有

[
sum_{ein C}(t_e-x_e)=0,qquad Cin{P,Q,R}.
]

因此对任意类常数 (m_P,m_Q,m_R)，令

[
eta_e=alpha_e-m_Cquad(ein C),
]

都有

[
etacdot(t-x)=alphacdot(t-x). 	ag{2}
]

为了由 Hölder 得到最强的 (L^infty) 下界，应最小化 (|eta|_1)。对一组实数 (a_i)，函数 (sum_i|a_i-m|) 在中位数处最小；三类事件数 47、11、31 都是奇数，所以最优 gauge 唯一取各类中位数：

[
m_P=-21,qquad m_Q=46,qquad m_R=0.
]

直接整数求和得到

[
sum_{P}|alpha_e+21|=3066,qquad
sum_{Q}|alpha_e-46|=178,qquad
sum_{R}|alpha_e|=1225,
]

从而

[
|eta|_1=4469. 	ag{3}
]

由 (1)–(3)，

[
rac{115}{27}
le etacdot(t-x)
le |eta|_1,|t-x|_infty
=4469,|t-x|_infty.
]

于是

[
oxed{|t-x|_inftyge rac{115}{120663}}.
]

## 4. 这个常数对“单 separator + 三个总量等式”已经尖锐

中心化后 P 类系数符号数为 (23+,23-,1零)，Q 类为 (5+,5-,1零)，R 类为 (13+,14-,4零)。

取
[
arepsilon=rac{115}{120663}.
]
在每个非零 (eta_e) 上令 (d_e=t_e-x_e=arepsilon,mathrm{sgn}(eta_e))。P、Q 的正负数相等，类内和自动为0。R 类先得到总和 (-arepsilon)，再在任意一个 (eta_e=0) 的 R 坐标上取 (d_e=+arepsilon)，于是三类总量全部保持不变，而且

[
etacdot d=arepsilon|eta|_1=rac{115}{27}.
]

所有 (t_e-d_e) 仍严格落在 ([0,1]) 内。因此在仅保留

1. 三个 class-total 等式；
2. T165 的单个 separator；
3. 概率盒 (0le x_ele1)

的外放松里，上述 (L^infty) 常数恰可达到。要得到更大的强制偏差，必须引入新的独立边界不等式或更高阶共同结构，不能只继续给 T165 separator 做类内 gauge 调参。

## 5. 范围

本定理只对 T165 七窗口边界面、且三类总量已经匹配 C030 的概率律成立。它不证明哪一条具体边必须偏离，也不把 T171 的四原子总量正律升级为逐事件律。更不等价于 full-Y/full15 不可行或新的平面色数下界。

精确证书：`certificates/identity_sensitive_robustness.json`  
独立重放：`python3 -S research/verify_identity_sensitive_robustness.py`
