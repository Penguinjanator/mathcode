# 配置与扩展

[English](configuration.md) · [安装](installation.ZH.md) · [使用](usage.ZH.md)

## 后端与模型

默认路线使用 Codex OAuth，执行 `codex auth login` 即可，新安装无需修改 `.env`。
发行模板选择 GPT-6 Astra 与 medium 推理强度。若要显式更新旧配置：

```env
OPENAI_MODEL=gpt-6-astra
OPENAI_SMALL_MODEL=gpt-6-astra
OPENAI_REASONING_EFFORT=medium
MATHCODE_EFFORT_LEVEL=medium
```

Anthropic 兼容后端示例：

```env
MATHCODE_USE_OPENAI=0
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5
```

OpenRouter、Bedrock、Vertex 和 Foundry 的设置见包内 `.env.example`。
所需 SDK 已打包；Bedrock、Vertex、Foundry 使用各自的 provider 凭据。
`./run` 在启动 MathCode 前会加载 `.env`。

System prompt 根据实际请求模型选择：Fable 使用 MathCode/Fable prompt，其他
已识别 Claude 模型使用 Claude 模板，其余模型使用 Codex/Astra。
自定义 system 与 agent prompt 优先级不变；这种选择不改变模型或 effort 设置。

Codex Responses 请求使用流式传输。`stream` 不是 MathCode 设置项，
不要为解决 API 错误而把它写入 `settings.json`。

## WebUI 设置

WebUI 路由独立于 CLI `.env`。新设置默认启用 **Follow application defaults**，
启动时采用当前应用的 provider、model 和 effort。关闭该选项并保存可以固定选择。
已有设置会保留原选择，直到手动启用跟随默认值。

设置文件位于 `$XDG_CONFIG_HOME/mathcode/webui/ui-settings.json`，默认是
`~/.config/mathcode/webui/ui-settings.json`。`git pull` 不修改该文件；
更新应用后请重启 daemon。

Provider-key 行支持 Anthropic 和 OpenRouter。Codex/OpenAI 使用 Codex OAuth，
不使用 `OPENAI_API_KEY` 字段。WebUI 的 `minimal` effort 在 OpenAI/OpenRouter
路线保留，在 Anthropic 兼容路线映射为 `low`。

## 技能、工具与插件

| 扩展 | 位置与用法 |
| --- | --- |
| 项目技能 | `.mathcode/skills/<name>/SKILL.md`，每个技能一个目录；独立的 `skills/*.md` 不会被加载。 |
| Python 工具 | 带 YAML frontmatter 的 `tools/*.py`，启动时发现；需要 Python 3.12+。 |
| 插件 | 含 `.mathcode-plugin/plugin.json` 的目录，通过 `--plugin-dir` 加载，或用 `/plugin` 从 Git 安装。 |

内置 Python 工具包括 `axiom-checker`、`lib-search` 和 `proof-stats`。
从包目录之外启动时仍可使用；工作区中规范化后同名的工具会覆盖内置版本。
`lib-search` 需要激活 vault，见 [Lean 工作流](lean.ZH.md)。

自定义 Agent 的 description 与 prompt 不能为空，可选的空 initial prompt 会被忽略。
MCP XAA IdP 配置要求非空 HTTPS issuer：`mathcode mcp xaa setup --issuer ...`
会在写入设置前拒绝 HTTP URL，包括 loopback 地址。
