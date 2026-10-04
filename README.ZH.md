# MathCode

[English](./README.md) | [中文](./README.ZH.md)

MathCode 是支持终端和浏览器界面的编码助手，内置 Lean 4 能力，可以查看证明目标、
搜索声明、检查候选证明，并严格验证完成的证明。

[官网](https://math-ai-org.github.io/mathcode/) ·
[下载](https://github.com/math-ai-org/mathcode/releases) ·
[问题反馈](https://github.com/math-ai-org/mathcode/issues) ·
[Discord](https://discord.gg/f2AFP9W5)

![MathCode 终端演示](./Demo.png)

## 能做什么

- 在自己的工作区中编写代码与 Lean 证明。
- 使用终端或本地 WebUI，查看数学公式和图表。
- 保存已验证定理与显式假设，在 Obsidian 中查看依赖关系。
- 添加项目技能、Python 分析工具和 MCP 插件。

Lean 是证明的最终判定依据：只有严格验证成功才算完成。定理入库与 vault 更新
需要显式执行。

## 快速开始

支持 **macOS Apple Silicon（arm64）** 和 **采用 glibc、支持 AVX2 的 Linux x86_64**。
默认后端需要先安装 `codex` CLI 并登录 Codex。

```bash
git clone https://github.com/math-ai-org/mathcode.git
cd mathcode
bash setup.sh
codex auth login
./run
```

Setup 会询问是否安装 Lean/Mathlib。只安装 CLI 和 WebUI 可用
`bash setup.sh --without-lean`，完整安装用 `--with-lean`。Lean 支持需要额外约
10 GiB 磁盘空间，也可以之后通过 `bash setup.sh --install-lean` 补装。
非交互式 setup 默认完整安装。

Setup 会为新 shell 安装 `mathcode` 命令。当前 shell 可直接使用 `./run`，
或打开新 shell 后运行：

```bash
mathcode -p "证明偶数的平方仍然是偶数"
```

浏览器界面用 `./run webui` 启动，然后打开本地 URL。已有 checkout 执行
`git pull --ff-only` 后重新运行 setup 即可更新。

## 文档

在线阅读：[中文文档](https://math-ai-org.github.io/mathcode/docs/index.ZH.html)。

| 指南 | 内容 |
| --- | --- |
| [安装](docs/release/installation.ZH.md) | 环境要求、安装方式、升级、工具链与排障 |
| [使用](docs/release/usage.ZH.md) | CLI、WebUI、目标、会话、定时任务与诊断 |
| [Lean 工作流](docs/release/lean.ZH.md) | 证明工具、定理与公理库、Obsidian、可选反馈后端 |
| [配置](docs/release/configuration.ZH.md) | 后端、模型设置、技能、工具与插件 |

当前版本的变化见[发行说明](RELEASE_NOTES.md)。

## 引用

```bibtex
@misc{mathcode2026,
  title = {MathCode: A Frontier Mathematical Coding Agent},
  author = {Team Math-AI},
  journal = {math-ai-org.github.io},
  year = {2026},
  month = {April},
  url = "https://github.com/math-ai-org/mathcode"
}
```
