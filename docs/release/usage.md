# Using MathCode

[中文](usage.ZH.md) · [Installation](installation.md) · [Lean workflows](lean.md)

## Terminal

```bash
mathcode                         # interactive session
mathcode -p "explain this code"  # one prompt
echo "hello" | mathcode -p
mathcode --help
```

Use `./run` instead of `mathcode` from the bundle directory until your shell
picks up the installed launcher. The agent works in the selected workspace.

Useful interactive commands include `/context`, `/config`, `/stats`, `/tasks`,
`/branch`, `/rename`, and `/copy [N]` to copy a selected answer. `--from-pr TERM`
opens the PR-linked session picker; a PR number or URL selects matching sessions.

`/plan` saves plans under `~/.mathcode/plans/` by default. `MATHCODE_CONFIG_DIR`
relocates the config home. To keep plans in the project, set `plansDirectory`
in project or local settings to a path relative to the project root.

## Browser interface

```bash
./run webui
./run webui --no-browser
```

Open the authenticated local URL printed in the terminal. The wrapper loads the
bundle `.env` and Lean defaults. Running `./mathcode-webui` directly uses the
same wrapper. Keep the token-bearing URL private.

Inside an interactive CLI session, `/webui` (also `/webUI`) manages the daemon:

```text
/webui --no-browser
/webui --port 18731
/webui --status
/webui --stop
```

The slash command's port and workspace take precedence over matching `.env`
values. Release bundles do not support the source-only `--rebuild` option.

Messages support Markdown and KaTeX math with `$...$`, `$$...$$`, `\(...\)` and
`\[...\]`. A fenced `svg` block can render a diagram; scripts, external
resources and unsafe SVG elements are rejected or removed.

Closed assistant `js` or `javascript` code blocks offer Run, Stop and Reset for
an opt-in browser-local preview. Each run is limited to two seconds and cannot
access the WebUI DOM, storage, network or child workers. Console output and
errors appear in the transcript. Other code blocks remain plain code.

## Goals

```text
/goal 100k prove the main theorem
/goal --budget 100k --max-continuations 10 prove the main theorem
/goal status
/goal pause
/goal resume
/goal clear
```

Goals continue the current session. Budgets accept positive integers,
integer-valued decimals and `k`/`m`/`b` suffixes. `--budget=<value>` and
`--max-continuations=<N>` also work. See `/goal help` for the command interface.

| Setting | Purpose | Default |
| --- | --- | --- |
| `MATHCODE_GOAL_MAX_TOKEN_BUDGET` | Maximum accepted goal budget | `1000000000` |
| `MATHCODE_MAX_CHAINED_COMMAND_INPUTS` | Maximum nested slash-command submissions | `25` |

## Effort and schedules

Use `--effort <level>` or `/effort <level>` with `low`, `medium`, `high`, `max`,
or a positive integer. `/effort auto` and `/effort unset` return to model defaults.
Provider-specific reasoning settings are in the [configuration guide](configuration.md).

```text
/loop 10m check the deploy
/loop 1h /standup 1
```

Use loops for short-lived reminders and monitoring. Create a durable schedule
in the interactive session when it must survive restarts.

## Diagnostics and saved results

Tool errors retain actionable reasons, including permission denials, validation
failures, Lean diagnostics and MCP error details. In `/config`, **Show tool-use
warnings** controls non-error runtime warning events; it does not hide tool
errors or actionable tool-call diagnostics from the agent.

Binary WebFetch and MCP results can be saved in the session's `tool-results`
directory. The tool result reports the saved path, or explains why persistence
failed. Recognized types keep their extension; unknown data remains `.bin`.

To overwrite an existing file, the agent must first read the complete file
without an explicit line limit. A partial or truncated read is insufficient.
Malformed text encodings must be repaired before Write or NotebookEdit can
replace the file. Concrete validation and recovery instructions appear in tool
results; preserve them when reporting a problem.
