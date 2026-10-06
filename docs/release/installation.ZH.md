# 安装与排障

[English](installation.md) · [使用](usage.ZH.md) · [配置](configuration.ZH.md)

## 环境要求

- macOS arm64，或采用 glibc、支持 AVX2 的 Linux x86_64。Linux 发行包基于 Ubuntu 22.04 构建。
- `curl`，以及 `shasum` 或 `sha256sum`。
- 默认后端需要 `codex` CLI；也可以配置[其他后端](configuration.ZH.md)。
- Lean/Mathlib 需要额外约 10 GiB 磁盘空间。Linux 的 Lean 支持还需要 `bwrap`（`bubblewrap` 包）与 `socat`。
- 仅使用内置 Python 分析工具时才需要 Python 3.12+。

## 选择安装方式

在发行版 checkout 或解压后的安装目录执行：

```bash
bash setup.sh               # 默认仅安装 CLI 与 WebUI
bash setup.sh --with-lean     # CLI、WebUI、Lean 和 Mathlib
bash setup.sh --without-lean  # 仅 CLI 与 WebUI
bash setup.sh --install-lean  # 之后补装或修复 Lean
```

`bash setup.sh` 默认只安装 CLI 和 WebUI，不显示安装方式选择提示；交互终端与脚本调用行为一致。
安装 Lean/Mathlib 需要显式传入 `--with-lean` 或 `--install-lean`，已有 Lean 安装会保留。

轻量安装后，第一次获准执行本地 Lean goal、check、verify 或库操作时，可以自动
补装工具链，并显示安装进度和失败原因。自动补装只作用于发行包自带的
`lean-workspace`；远程 `LeanSearch` 和用户自己的 Lean 项目不会触发安装。

Setup 按需创建 `.env`，并在 `~/.local/bin/` 安装受管理的 `mathcode` 启动脚本。
已有配置会保留。安装包自带 CLI、WebUI 与 ripgrep，不需要源码 checkout 或
`node_modules`。

## 升级与修复

```bash
git pull --ff-only           # 适用于 clone 的发行仓库
bash setup.sh --without-lean # 也可按需选择 --with-lean
bash setup.sh --status
```

Setup 检查运行时版本和哈希，从对应 GitHub Release 修复缺失、过旧或无效的文件，
并在替换已有安装前验证下载内容的校验和。`--status` 显示 CLI、WebUI、ripgrep
和 Lean 的状态。升级后请重启正在运行的 WebUI daemon。

`bash setup.sh --clean` 清理已安装的运行时和工具链，保留 `LeanFormalizations/`
中的证明、vault 数据和锁定的 Lake manifest；之后重新执行 setup。
全部选项见 `bash setup.sh --help`。

## 直接下载 archive

从 [Releases](https://github.com/math-ai-org/mathcode/releases) 下载对应平台的
`.tar.gz` 和 `SHA256SUMS.txt`。用匹配条目验证 archive 后解压，在该目录运行
setup。Archive 是自包含的，只有需要修复时 setup 才会下载运行时文件。
手动更新时也要选择正确平台。

## Lean 工具链选择

选择安装 Lean 时，默认使用 `.local/elan` 中的本地工具链，版本由 `lean-workspace/lean-toolchain`
锁定。Setup 保留随包提供的 `lake-manifest.json`，并要求 `MathCodeLean` readiness
构建成功；Mathlib cache 下载失败时可以回退到本地构建。

若要复用系统安装：

```bash
MATHCODE_SETUP_USE_SYSTEM_LEAN=1 bash setup.sh --with-lean
```

Lean 和 Lake 都必须符合锁定版本。Setup 将 Elan proxy 解析为具体可执行文件，
校验后把路径保存到 `.env`；不符合要求时回退到包内工具链。选择锁定工具链时会
忽略外部 `ELAN_TOOLCHAIN` 覆盖。用户自己的项目仍使用自己的工具链配置。

## 常见问题

| 现象 | 处理方法 |
| --- | --- |
| Setup 后找不到 `mathcode` | 打开新 shell，或直接使用 `./run`。 |
| `exec format error` 或 `Bad CPU type in executable` | 重新执行 setup，或下载匹配系统和 CPU 的 archive。 |
| 缺少 Codex 认证 | 执行 `codex auth login`。 |
| Lean 状态为 deferred | 需要本地 Lean 时执行 `bash setup.sh --install-lean`。 |
| 升级后 WebUI 仍使用旧默认值 | 重启 daemon，并检查设置页的 **Follow application defaults**。 |

Setup 只替换自己创建的启动脚本。可用 `MATHCODE_INSTALL_BIN_DIR` 指定其他目录，
相对路径以安装包根目录为基准。写入启动脚本失败时仍可通过 `./run` 使用安装包。
