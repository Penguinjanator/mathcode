# 使用 MathCode

[English](usage.md) · [安装](installation.ZH.md) · [Lean 工作流](lean.ZH.md)

## 终端

```bash
mathcode                        # 交互式会话
mathcode -p "解释这段代码"       # 单次提问
echo "hello" | mathcode -p
mathcode --help
```

Shell 尚未加载安装的启动脚本时，可在包目录用 `./run` 代替 `mathcode`。
Agent 在选定的工作区执行任务。

常用交互命令包括 `/context`、`/config`、`/stats`、`/tasks`、`/branch`、`/rename`，
以及复制指定回复的 `/copy [N]`。`--from-pr TERM` 打开关联 PR 的会话选择器；
也可以传 PR 编号或 URL 来选择匹配会话。

`/plan` 默认把计划保存在 `~/.mathcode/plans/`，可用 `MATHCODE_CONFIG_DIR`
更改配置根目录。若要把计划放在项目中，在 project 或 local settings 设置
`plansDirectory`，路径相对于项目根目录。

## 浏览器界面

```bash
./run webui
./run webui --no-browser
```

打开终端打印的本地认证 URL。Wrapper 会加载包内 `.env` 与 Lean 默认配置，
直接运行 `./mathcode-webui` 也会使用同一 wrapper。请勿分享带 token 的 URL。

交互式 CLI 会话中可用 `/webui`（或 `/webUI`）管理 daemon：

```text
/webui --no-browser
/webui --port 18731
/webui --status
/webui --stop
```

Slash command 指定的 port 和 workspace 优先于 `.env` 同名设置。
发行包不支持仅供源码模式使用的 `--rebuild`。

消息支持 Markdown 与 KaTeX 数学公式，包括 `$...$`、`$$...$$`、`\(...\)` 和
`\[...\]`。标为 `svg` 的 fenced code block 可显示图表；脚本、外部资源和
不安全 SVG 元素会被拒绝或移除。

Assistant 回复中已闭合的 `js` 或 `javascript` 代码块提供 Run、Stop、Reset，
供用户主动运行浏览器本地预览。单次限制为两秒，不能访问 WebUI DOM、存储、网络
或子 worker；控制台输出与错误显示在会话中。其他代码块保持纯文本。

## 目标

```text
/goal 100k 证明主定理
/goal --budget 100k --max-continuations 10 证明主定理
/goal status
/goal pause
/goal resume
/goal clear
```

Goal 延续当前会话。预算支持正整数、整数值小数和 `k`/`m`/`b` 后缀，
也支持 `--budget=<value>` 与 `--max-continuations=<N>` 写法。
命令帮助见 `/goal help`。

| 设置 | 用途 | 默认值 |
| --- | --- | --- |
| `MATHCODE_GOAL_MAX_TOKEN_BUDGET` | 可接受的最大目标预算 | `1000000000` |
| `MATHCODE_MAX_CHAINED_COMMAND_INPUTS` | 嵌套 slash-command 提交次数上限 | `25` |

## Effort 与定时任务

`--effort <level>` 或 `/effort <level>` 支持 `low`、`medium`、`high`、`max`
或正整数。`/effort auto` 和 `/effort unset` 恢复模型默认值。
各后端的推理设置见[配置指南](configuration.ZH.md)。

```text
/loop 10m 检查部署
/loop 1h /standup 1
```

短期提醒和监控可用 loop；需要重启后继续保留时，在交互会话中创建持久化定时任务。

## 诊断与保存的结果

工具错误保留可操作的原因，包括权限拒绝、参数校验失败、Lean 诊断与 MCP 错误。
`/config` 中的 **Show tool-use warnings** 控制非错误运行时警告事件，
不会对 Agent 隐藏工具错误或需要处理的工具调用诊断。

WebFetch 与 MCP 的二进制结果可以保存在会话的 `tool-results` 目录中。
工具结果会给出已保存的路径，或说明保存失败的原因。已识别的类型保留对应扩展名，
未知二进制数据保留为 `.bin`。

覆盖已有文件前，Agent 必须先完整读取文件且不显式限制行数；部分或截断读取不够。
文本编码损坏时，需要先修复编码，再由 Write 或 NotebookEdit 替换文件。
工具结果会提供具体校验和恢复说明，反馈问题时请保留这些内容。
