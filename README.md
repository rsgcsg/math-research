# Hadwiger–Nelson research

目标是决定欧氏平面的单位距离色数。当前没有解决原问题；项目中的局部
六染色、条件不可满足和结构类比都不等于新的平面上下界。

开始阅读：[当前工作](docs/CURRENT.md) · [路线与关系图](docs/ROUTES.md) ·
[结果和实验账本](docs/RESULTS.md) · [外部资料](references/SOURCES.md)。

```text
references/       外部论文索引、原始历史资料
docs/            当前状态、研究路线、结果账本、完整证明
research/        精确检查与有限搜索程序
certificates/    可重放见证、输入和验证摘要
```

基本检查只需要 Python 3 标准库：

```sh
make check
```

需要重新做 SAT 搜索或符号代数时：

```sh
make setup
make explore
```

约定见 [AGENTS.md](AGENTS.md)。研究允许发散，但每约三轮实验做一次收敛：
问具体例子是否有更简单的机制、成熟理论是否已覆盖它、哪些分支应该合并。
本仓库不维护额外的任务系统；以上三个研究文档就是小型项目记忆。

