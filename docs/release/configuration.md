# Configuration and extensions

[中文](configuration.ZH.md) · [Installation](installation.md) · [Usage](usage.md)

## Backend and model

The default route uses Codex OAuth. Run `codex auth login`; no `.env` edits are
needed for a new installation. The release template selects GPT-6 Astra with
medium reasoning effort. To update an older configuration explicitly:

```env
OPENAI_MODEL=gpt-6-astra
OPENAI_SMALL_MODEL=gpt-6-astra
OPENAI_REASONING_EFFORT=medium
MATHCODE_EFFORT_LEVEL=medium
```

For an Anthropic-compatible backend:

```env
MATHCODE_USE_OPENAI=0
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5
```

OpenRouter, Bedrock, Vertex and Foundry settings are documented in the bundle's
`.env.example`. Their SDKs are bundled; Bedrock, Vertex and Foundry use their
own provider credentials. `./run` sources `.env` before starting MathCode.

System prompts are selected for the actual request model: Fable uses the
MathCode/Fable prompt, other recognized Claude models use the Claude template,
and remaining models use Codex/Astra. Custom system and agent prompts retain
precedence. This selection does not change the chosen model or effort level.

Codex Responses requests use streaming transport. `stream` is not a MathCode
setting; do not add it to `settings.json` to work around an API error.

## WebUI settings

WebUI routing is separate from the CLI `.env`. New settings enable **Follow
application defaults**, taking the installed application's provider, model and
effort at startup. Disable it and save to pin a selection. Existing settings
keep their choices until you opt into following defaults.

Settings live in `$XDG_CONFIG_HOME/mathcode/webui/ui-settings.json`, or
`~/.config/mathcode/webui/ui-settings.json` by default. `git pull` does not change
this file. Restart the daemon after updating the application.

Provider-key rows support Anthropic and OpenRouter. Codex/OpenAI uses Codex OAuth
rather than an `OPENAI_API_KEY` field. WebUI `minimal` effort is preserved on
OpenAI/OpenRouter and maps to `low` on Anthropic-compatible routes.

## Skills, tools and plugins

| Extension | Location and use |
| --- | --- |
| Project skills | `.mathcode/skills/<name>/SKILL.md`, one directory per skill. Standalone `skills/*.md` files are not loaded. |
| Python tools | `tools/*.py` with YAML frontmatter; discovered at startup. Python 3.12+ is required. |
| Plugins | Folders containing `.mathcode-plugin/plugin.json`; load with `--plugin-dir` or install from Git with `/plugin`. |

Bundled Python tools include `axiom-checker`, `lib-search` and `proof-stats`.
They remain available outside the bundle workspace; a workspace tool with the
same normalized name overrides the bundled one. `lib-search` requires an active
vault; see [Lean workflows](lean.md).

Custom agents require nonblank descriptions and prompts. Optional blank initial
prompts are ignored. MCP XAA IdP setup requires a nonblank HTTPS issuer:
`mathcode mcp xaa setup --issuer ...` rejects HTTP URLs, including loopback,
before saving settings.
