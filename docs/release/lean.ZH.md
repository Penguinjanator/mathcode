# Lean 工作流

[English](lean.md) · [安装](installation.ZH.md) · [使用](usage.ZH.md)

## 证明工具

MathCode 直接处理选定工作区中的 Lean 文件。Agent 按需选择工具，`/lean` 提供可选指导。

| 工具 | 用途 |
| --- | --- |
| `LeanGoal` | 查看明确源码位置的目标。 |
| `LeanCheck` | 编译文件或临时候选，获取反馈。 |
| `LeanSearch` | 通过选定的一个 provider 搜索声明。 |
| `LeanVerify` | 严格验证一个完整限定名的声明。 |

只有成功的 `LeanVerify` 结果中 `data.verified=true` 才能判定证明完成。
默认超时为 1200 秒，`timeout_s` 可设到 3600 秒。Goal/check 反馈本身不是完成证书。

Agent 可以使用辅助引理、子目标、分支和定理复用。原子证明工具不会隐式保存定理、
添加公理或更新 vault。

## 定理库

```text
/theorem-store store <file> <qualified-declaration>
/theorem-store sync
/theorem-store check
/theorem-store status
```

`store` 验证并存储一个显式指定的定理：重新检查源码与依赖，在 `Stored.lean`
中验证重命名后的声明，再构建可导入模块。发布失败会回滚库更新。
编译和发布分别有 300 秒构建预算。

`sync` 发现候选并询问要保存哪些声明；`check` 编译检查整库；`status` 显示存储
数量与 vault 信息。仅通过 `MATHCODE_OBSIDIAN_VAULT` 或 `/obsidian on` 激活
vault 后才会提供 `LibSearch`，否则可用 `LeanSearch`。

## 公理库

```text
/axiomatize "A 比 B 快"
/axiomatize list
/axiomatize check
/axiomatize remove <name>
```

声明按 vault 保存，经过 Lean 编译检查与一致性审查。需要把这些假设放入证明上下文
时，请显式导入或引用；原子 Lean 调用不会自动注入已保存的假设。

## Obsidian

```text
/obsidian on
/obsidian off
/obsidian generate
```

修改证明后执行 `generate`，再用 Obsidian Graph View 查看依赖。引理笔记包含
从 Mathlib 查询的定义。生成操作会更新 MathCode 管理的笔记及可识别的旧投影，
保留其他用户笔记，遇到冲突文件名则失败。

论文 catalog ID 不能冲突。如果根据标题与作者生成的 ID 已属于另一篇论文，
请使用不同 ID 或另一个 vault。依赖环错误会指出相关 claim 和 catalog 修复方法。

## 可选反馈后端

符合条件的通用编译调用可以通过 `MATHCODE_LEAN_REPL=1` 使用进程内 REPL。
原子证明工具不使用这份缓存。

macOS 上可配置外部 Kimina Lean Server，为 `LeanGoal` 与 `LeanCheck` 提供反馈：

```env
MATHCODE_KIMINA_SERVER=1
MATHCODE_KIMINA_CMD="/absolute/path/to/kimina-lean-server/.venv/bin/python -m server"
MATHCODE_KIMINA_CWD=/absolute/path/to/kimina-lean-server
MATHCODE_KIMINA_PROJECT_ROOT=/absolute/path/to/served-lean-project
```

声明的项目与 Lean 版本必须匹配当前项目。命令须直接启动 Python；使用 virtualenv
时，它必须位于 `MATHCODE_KIMINA_CWD` 下。MathCode 在仅绑定 loopback 的沙箱中
启动服务，移除 provider 凭据，只允许写入私有 scratch。启动、兼容性或传输失败时
回退到锁定工具链的子进程，并报告警告。

Kimina 反馈不是完成证书。`LeanVerify` 与隔离论文 Agent 始终使用新的隔离子进程。
Linux 和 Windows 在此反馈路径中使用锁定工具链的子进程；发行包本身仅支持
[安装指南](installation.ZH.md)列出的平台。
