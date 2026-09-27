# Hadwiger–Nelson research

目标是决定普通平面的单位距离色数；目前本项目没有改变 `5≤χ(R²)≤7`。
[当前状态](docs/CURRENT.md) · [结果账本](docs/RESULTS.md) · [路线](docs/ROUTES.md) ·
[统一框架](docs/proofs/hn_unified_framework.md) · [文献地图](references/LITERATURE_MAP.md)。

## 2026-09-27：准确基线及两项实际推进

接续远端归并分支82a396…，保留两条原始Git历史与主线全部证据。
基线完整回归、新增隔离检查、源码绑定和实际发布范围见[本轮收据](certificates/baseline_next_validation.json)。
本轮连接仅可读；本地Git提交、完整bundle和补丁不冒称已推送或已合并PR #5。

- **T138收尾：** 全部双旋转宿主已知恰五色，现补齐整个非零图及含原点图的连通性证书；不是染色唯一性。
- **T139：** 任意有限秩单位旋转群的两副本非零平移接触，除两类中心星及单位平移匹配外只有有限多解。
  [完整证明](docs/proofs/translated_rotation_contacts.md)使用ESS定理并分类全部退化；没有给出有效指数窗口或五色延拓。
- **E111：** 一份完整Y五色词同时满足u全部29点划分事件及12个具体二点失配事件，
  关闭这一共享势族的全词严格分离。[证明与可重放整数定价](docs/proofs/shared_event_pricing.md)。

全15域共同律仍未决定。旧UNKNOWN不变，更多同旋转宿主指数层已不是NON5路线。
主攻须引入其他运动的真正联合颜色信息，或有效确定非零平移例外并检查自由端口关系。

```sh
make check        # 旧全部检查与新增check-next
make check-next   # 无site packages的独立证据、语义编码与篡改检查
```

独立检查仅使用Python标准库；新增目标显式使用 `python3 -S`。
`run_event_pricing.py`的搜索另需python-sat，否定结果须完成独立RUP重放才获得认证。
旧E105主循环未被静默替换；一般RAT、不受资源约束的证明搜索和HN终局均不因此完成。
两份一次性导出/恢复工作流从本地候选树移除；常规只读 `verify.yml` 保留。
