# MathCode v0.4.0

MathCode v0.4.0 ships the terminal assistant and browser WebUI for macOS
Apple Silicon (arm64) and Linux x86_64. Linux requires an AVX2-capable CPU.
Download the matching archive and verify it against `SHA256SUMS.txt` from
[GitHub Releases](https://github.com/math-ai-org/mathcode/releases/tag/v0.4.0).

## Highlights

- Install the CLI and WebUI without Lean/Mathlib, then add the pinned Lean
  runtime when needed. Approved local Lean operations can install deferred
  support on first use; remote search and caller-owned projects do not trigger
  this installation.
- System-Lean setup resolves Elan launchers to concrete Lean and Lake binaries,
  verifies both against the workspace pin, and falls back to bundle-local Lean
  when validation fails.
- Tool validation errors, warnings, and structured result diagnostics preserve
  actionable details consistently, including Unicode text at output limits.

## Install or upgrade

```bash
git clone https://github.com/math-ai-org/mathcode.git
cd mathcode
bash setup.sh --without-lean
codex auth login
./run
```

For an existing checkout, run `git pull --ff-only` and rerun setup. Use
`bash setup.sh --with-lean` for a complete installation or
`bash setup.sh --install-lean` to add Lean/Mathlib later. Allow about 10 GiB
of additional disk space for Lean support. Interactive `bash setup.sh` asks
which mode to use; non-interactive setup defaults to the complete installation.

Start the browser interface with `./run webui --no-browser` and open the local
URL printed in the terminal. Setup also installs the `mathcode` command for
new shells. Existing configuration is preserved.

---

# MathCode v0.4.0 中文说明

本版本提供终端助手与浏览器 WebUI，支持 macOS Apple Silicon（arm64）和
Linux x86_64；Linux 需要支持 AVX2 的 CPU。请从
[GitHub Releases](https://github.com/math-ai-org/mathcode/releases/tag/v0.4.0)
下载对应平台的安装包，并用同页的 `SHA256SUMS.txt` 校验。

## 主要变化

- 可以先安装 CLI 与 WebUI，之后再补装锁定版本的 Lean/Mathlib。第一次获准
  执行本地 Lean 操作时可自动补装；远程搜索和用户自己的 Lean 项目不会触发安装。
- 选择系统 Lean 时，将 Elan launcher 解析为具体 Lean/Lake 可执行文件并校验
  两者版本；不符合 workspace 锁定版本时回退到安装包内的 Lean。
- 工具参数校验错误、警告及结构化结果保留可操作的诊断细节，并正确处理输出
  截断处的 Unicode 文本。

## 安装或升级

首次安装执行上方命令。已有 checkout 执行 `git pull --ff-only` 后重新运行 setup；
原有配置会保留。

```bash
bash setup.sh --without-lean  # 先安装 CLI 与 WebUI
bash setup.sh --with-lean     # 完整安装
bash setup.sh --install-lean  # 之后补装或修复 Lean/Mathlib
./run webui --no-browser     # 启动浏览器界面
```

Lean 支持需要额外约 10 GiB 磁盘空间。交互式 `bash setup.sh` 会询问安装方式，
非交互式调用默认完整安装。WebUI 启动后打开终端打印的本地 URL；setup 安装的
`mathcode` 命令可在新 shell 中使用。
