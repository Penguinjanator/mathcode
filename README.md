# MathCode

### MathCode: A Frontier Mathematical Coding Agent

```
███╗   ███╗ █████╗ ████████╗██╗  ██╗ ██████╗ ██████╗ ██████╗ ███████╗
████╗ ████║██╔══██╗╚══██╔══╝██║  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝
██╔████╔██║███████║   ██║   ███████║██║     ██║   ██║██║  ██║█████╗
██║╚██╔╝██║██╔══██║   ██║   ██╔══██║██║     ██║   ██║██║  ██║██╔══╝
██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║╚██████╗╚██████╔╝██████╔╝███████╗
╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
```

**Project Page:** [math-ai-org/mathcode](https://github.com/math-ai-org/mathcode)

<p align="right"><strong>English</strong> | <a href="./README.ZH.md">中文</a></p>

MathCode is a terminal AI coding assistant with built-in Lean capabilities. The
agent can inspect goals, check candidates, search declarations, and verify a
finished proof interactively.

![](./Demo.png)

## Quick Start

```bash
git clone https://github.com/math-ai-org/mathcode.git
cd mathcode
bash setup.sh
codex auth login
mathcode
```

`setup.sh` prepares the release checkout for daily use. It downloads or repairs
the bundled runtime, prepares local configuration, and installs a user-local
`mathcode` launcher for future shells. On Linux it also requires `bwrap`
(package `bubblewrap`) and `socat` when Lean support is installed.

If your current shell has not reloaded its profile yet, use `./run` as the
bundle-local fallback.

### Optional Lean Installation

Public release archives support macOS Apple Silicon (arm64) and Linux
x86_64 with glibc and AVX2. Download the matching archive and `SHA256SUMS.txt`
from [GitHub Releases](https://github.com/math-ai-org/mathcode/releases).
For an existing bootstrap checkout, run `git pull --ff-only` and rerun setup
to install the current release while preserving configuration.

MathCode now supports two explicit release install modes:

```bash
bash setup.sh --with-lean     # CLI/WebUI plus the pinned Lean/Mathlib runtime
bash setup.sh --without-lean  # lightweight CLI/WebUI install; defer Lean
```

At an interactive terminal, plain `bash setup.sh` asks which mode to use and
defaults to the full install. Non-interactive invocations keep the previous
full-install behavior. A core-only installation can add Lean later with:

```bash
bash setup.sh --install-lean
```

The first approved local Lean execution after a core-only install also runs
that same installer, shows its progress, and then retries the requested tool.
This applies to local Lean goal/check/verify and library operations; remote
`LeanSearch` does not trigger a Lean download. The automatic installer is
limited to the release's bundled `lean-workspace` and does not modify a
caller-owned Lean project. Installing Lean/Mathlib may require network access,
several minutes, and about 10 GiB of additional disk space.

### Setup Responsibilities

Runtime files:

- downloads the matching `mathcode-vX.Y.Z-<os>-<arch>.tar.gz` asset when
  bundled runtime files are missing, stale, unverified, or invalid for the
  current platform
- restores `./mathcode`, `./mathcode-webui`, and `vendor/ripgrep/` from that
  archive when repair is needed
- verifies the current-platform `SHA256SUMS.txt` entry with `shasum` or
  `sha256sum`
- validates downloaded runtime files before replacing an existing working
  install
- records release metadata for the CLI and WebUI helper so later `setup.sh` and
  `setup.sh --status` runs can detect stale or unverified binaries

Local configuration:

- creates `.env` from `.env.example` when needed
- installs a managed user-local `mathcode` launcher in `~/.local/bin/` by
  default
- creates `tools/` and `plugins/` extension directories plus the bundled
  `skills/` reference-doc directory; project skills load from
  `.mathcode/skills/<name>/SKILL.md`
- ships a bundled `rg` binary under `vendor/ripgrep/` for MathCode's internal
  search paths

Lean toolchain:

- can be installed during initial setup, deferred with `--without-lean`, or
  added later with `--install-lean` or the first approved local Lean execution
- ships the versioned `lean-workspace/lake-manifest.json` so setup and local
  runs use the dependency graph locked by the release
- setup materializes an empty managed `VaultLibs/UserVaultLibs/` skeleton when
  needed; source-host local vault mirrors, test fixtures, and scratch Lean files
  are not packaged
- materializes that locked graph during setup without running `lake update` or
  rewriting the manifest
- requires a local `MathCodeLean` readiness build after the optional Mathlib
  cache fetch; cache skips and download failures fall back to that build, and a
  build failure aborts setup
- uses a complete bundle-local `.local/elan` Lean/Lake pair by default and
  clears ambient `ELAN_TOOLCHAIN` whenever that local pair is selected
- accepts `lean.exe` / `lake.exe` pairs from Git Bash/MSYS
- repairs partial local elan tool-file installs before bootstrapping the Lean
  workspace
- uses system Lean/Lake only when `MATHCODE_SETUP_USE_SYSTEM_LEAN=1` and both
  tools resolve to concrete binaries whose Lean and Lake versions exactly
  match `lean-workspace/lean-toolchain`; ambient `ELAN_TOOLCHAIN` overrides are
  ignored during this check, and validation failure falls back to bundle-local
  Lean without persisting an Elan proxy; your existing `ELAN_HOME` is preserved

### Launcher And PATH Behavior

Setup only overwrites launcher files it previously created. This avoids
clobbering an unrelated existing `mathcode` command.

If `MATHCODE_INSTALL_BIN_DIR` is set, setup resolves relative paths against the
bundle root before writing the launcher, recorded state, or managed PATH block.
It also refreshes the managed profile block even when the chosen directory is
already on the current shell's `PATH`, so future shells keep resolving
`mathcode`.

If the selected launcher directory cannot be used, setup skips only the
launcher step and continues the rest of installation.

When `MATHCODE_SETUP_USE_SYSTEM_LEAN=1`, setup captures system `lean` and
`lake` before changing into the bundle root, resolves launchers such as Elan
proxies through the Lean-reported toolchain prefix, and records the validated
concrete executable paths in `.env`. Runtime resolution validates and uses that
pair even when a later process has a different `PATH`. These managed system
paths use strict `base64:` UTF-8 encoding so Bun dotenv parsing and `./run`
shell sourcing both preserve literal backslashes, quotes, and backticks.
Without that opt-in, setup removes any stale managed system-toolchain selection
and `--status` reports the default local `.local/elan` path instead of treating
system Lean as installed.

Generated `.env` path values are shell-quoted, so bundle paths containing
characters such as `$` or single quotes remain literal when `./run` sources the
file; the managed system Lean/Lake values use the dual-parser encoding above.

### Maintenance Commands

```bash
bash setup.sh --install-lean  # add or repair optional Lean/Mathlib support
bash setup.sh --status        # check binary, tooling, and deferred/ready state
bash setup.sh --clean         # remove install artifacts, keep proofs/vault data
bash setup.sh --help          # show all setup flags
```

`setup.sh --status` checks that:

- `./mathcode --version` and checksum match this release tag's metadata
- `./mathcode-webui` matches the recorded release metadata
- the current platform's bundled `rg` is executable and reports a ripgrep
  version banner
- optional Lean support is ready, deferred, incomplete, or not prepared

`setup.sh --clean` preserves user outputs in `LeanFormalizations/`, vault
data, and the release's locked Lake manifest. If setup previously recorded a managed launcher, later `--status` and
`--clean` runs keep tracking it even when `MATHCODE_INSTALL_BIN_DIR` is unset.

## Requirements

- macOS (arm64) or glibc-based Linux (x86_64 with AVX2, built on Ubuntu 22.04)
- `curl` for setup/bootstrap downloads
- `shasum` or `sha256sum` for release archive verification and metadata
- enough disk space for the core bundle; allow about 10 GiB more when enabling
  Lean/Mathlib
- `codex` CLI if you want the default backend and default math flow
- Python 3.12+ (optional, only needed for analysis tools in `tools/`)

## Common Commands

### CLI

```bash
mathcode -p "prove that the square of an even number is even"
echo "hello" | mathcode -p
mathcode --help
```

MCP XAA IdP setup requires a nonblank HTTPS issuer URL.
`mathcode mcp xaa setup --issuer ...` rejects `http://`, including loopback
URLs, before writing settings.

If you have not reloaded your shell yet, use the bundle-local fallback:

```bash
./run -p "prove that the square of an even number is even"
echo "hello" | ./run -p
./run --help
```

The agent edits Lean files in the selected workspace. The atomic Lean tools do
not create a separate run directory or write proof-library artifacts.

### Prompt editing and output handling

In Vim mode, character deletion, replacement, case toggling, and find/till commands respect the current line. Text-object counts, paste, and dot-repeat preserve the selected text, register kind, and cursor position, including empty lines and CRLF input.

Search fields preserve encoded spaces and uppercase characters, support Meta-letter editing shortcuts, and ignore unsupported function keys. Vim processes consecutive commands in one terminal input chunk; arrows do not become replacement text. Undo does not restore edits discarded before its history timer fires. Commands following undo in the same input chunk use the restored text and history. Vim dot-repeat includes newline and control-key edits, preserves append commands, and separates edits made after cursor movement. Selection dialogs apply navigation before confirmation when both keys arrive together, and submit the latest text when typing and Enter arrive together.

Full-file reads preserve a lone final carriage return. Edit asks for exact text when quote normalization finds multiple literal styles. Edit, Write, and NotebookEdit reject truncated UTF-16LE files instead of dropping the incomplete byte. Selected blank lines retain their line numbers, including at the end of a partial range, without a false end-of-file warning. Consecutive Edits recognize their own CRLF or BOM writes while retaining checks for external changes.

Custom shortcut chords keep literal `+` keys separate from neighboring steps, such as `ctrl++ ctrl+a`. Grep preserves glob escapes for literal wildcard characters; absolute Glob patterns match only the specified location unless they include `**`. Grep and Glob preserve trailing whitespace in returned filenames; Grep also preserves matched content whitespace.

Large paper dependency cycles report their actual members and the catalog repair instruction without overflowing the traversal stack. Claim, bibliography and concept IDs cannot share stub filenames when compared without case; extraction disambiguates IDs and keeps their references aligned. Saving a distinct paper whose title and authors generate an existing paper ID reports the collision before replacing the catalog or notes. Use a distinct ID or separate vault for that paper.

Obsidian dependency notes preserve the complete recognized Lean reference name, including apostrophes, Unicode continuation characters and `?`/`!` suffixes.

`/stats` clears its loading indicator when you return to all-time or already loaded statistics while another range is still loading. Day spans count inclusive UTC calendar dates; recent ranges exclude future dates. Speculation savings and optional shot counts are attributed once to the accepted session day. Existing historical cache totals are preserved.

The startup resume picker keeps the selected tag when older sessions load. Repeated scrolling cannot load the same page twice, and results from a previous project scope cannot leak into the current view. Local transcript search highlights the original text correctly when Unicode lowercasing changes its length. Session loading skips entire malformed JSONL rows. `/branch` flushes pending history and preserves the latest conversation, including equal timestamps; branch names avoid case-insensitive collisions. Generated `/rename` results cannot replace a newer name or affect a different session, and blank generated names are rejected.

Cancelling Ctrl+R restores the draft and its input mode; old reads cannot replace it after the search closes or changes. In Bash mode, Up followed by Down returns to the unsent draft. Returning to the draft with Down or resetting input prevents an older pending recall from replacing it.

Pasting with 7-bit or 8-bit terminal markers keeps pasted control sequences from acting as keystrokes and leaves following input available for normal editing. Markdown separates horizontal rules from following text, renders alternate list markers and escapes, and preserves LF, CRLF and CR paragraph boundaries in streaming and completed messages. `/copy [N]` copies the complete selected answer, including text delivered in separate streamed blocks.

`--from-pr TERM` opens the PR-linked session picker with `TERM` as its search text; PR numbers and URLs still select their matching sessions. A first page without sessions matching the PR filter continues to older pages. If reading another page fails, the picker shows the concrete error and accepts Enter to retry, preserving its search and already loaded sessions. Where space permits, the focused row remains visible when the error reduces the list height; oversized errors remain retryable on short terminals. While `/diff` is loading, navigation keeps the first arriving file selectable. Pasting words such as `escape` or `return` into a search field inserts those words.

In builds with workspace search enabled, completed searches show current files and line text, including at the 500-result limit. Temporary results from the previous query are discarded at completion.

File previews retain accurate line counts and truncation markers, and FileEdit refreshes cached text after timestamp-preserving replacements. Queued prompts remain queued when submission is deferred. Output limits account for UTF-8 bytes; truncation preserves Unicode pairs and reports omitted output.

A stalled tool or hook no longer blocks an early concurrent stream exit or hides another task's error during cleanup.

### Saved WebFetch and MCP Content

When WebFetch classifies a response as binary, or an MCP binary payload is
routed to sidecar storage, MathCode saves the exact persisted bytes in the
current session's `tool-results` directory and reports the full path in the
tool result. If saving fails — a full disk, a read-only or unwritable
`tool-results` directory — the fetch still succeeds and the tool result says so
explicitly, naming the reason instead of a path, so the summary is never
presented alongside a file that does not exist. Recognized declared MIME types keep their normal extension. When
persisted content has no recognized MIME-derived extension, for example
`application/octet-stream`, MathCode checks the content: valid UTF-8 text
without binary control patterns uses `.txt`, supported PDF/PNG/JPEG/GIF/WebP
signatures use their native extension, and other opaque bytes remain `.bin`.
This gives FileRead a readable sidecar when possible without discarding
unsupported binary data.

### Browser UI

```bash
./run webui
```

`./run webui` sources the bundle `.env`, starts the local daemon, and prints the
browser authentication URL.

If launched directly, the packaged `./mathcode-webui` helper re-enters the
sibling `./run webui` wrapper first. Direct and wrapper launches therefore use
the same `.env`, local Lean toolchain, and bundle defaults. A present but
broken wrapper is reported as a launch failure.

Inside an interactive `./run` session, `/webui` and `/webUI` launch or manage
the same local daemon. The slash command supports `--no-browser`,
`--port <port>`, `--status`, and `--stop`; source-only `--rebuild` is not
available in release bundles. The full authenticated URL is written only to the
local terminal, while command result/status text redacts it as
`token=<redacted>`. For slash-command launches, the selected port and workspace
override same-named WebUI keys from the bundle `.env`.

Transcript messages render GFM plus KaTeX for `$...$`, `$$...$$`, `\(...\)`,
and `\[...\]` math. To render an SVG diagram, put one `<svg>` document in a
fenced code block whose info string is `svg`. SVG previews use a bounded
allowlist: raw HTML remains escaped, and scripts, event handlers,
`foreignObject`, external resources, document declarations, all `use`
elements/expansion, and nested resource-definition references are removed or
rejected. Bracketed formulas remain independent from stray streaming `$`
characters; code, links, emphasis, and images between unrelated dollars remain
ordinary Markdown. Oversized inline/display formulas and GFM tables scroll
inside the transcript instead of widening the page. Safe SVG text includes
browser-parsed CDATA; inert color inheritance, clip/mask units, mask type, and
preserved XML text spacing remain available. Blank or zero-width-only SVG
titles/ARIA labels fall back to the default diagram name. An unfinished
streaming SVG fence stays a quiet code preview until its closing fence arrives.
Closed assistant code fences labelled `js` or `javascript` add Run, Stop, and
Reset controls for a browser-local console preview. Execution is opt-in and
isolated in a sandboxed iframe plus a dedicated worker: it cannot access the
WebUI DOM, parent window, storage, network, or child workers, and each run is
stopped after two seconds. Console output, returned async values, syntax/runtime
errors, and unhandled promise rejections raised during the active run remain
visible in the transcript; tracked timers keep that run active until they clear
or reach the same deadline.
User-message, thinking, non-JavaScript, and unfinished streaming fences remain
plain code.

### Goal And Command Limits

- `MATHCODE_GOAL_MAX_TOKEN_BUDGET` caps token budgets accepted by source
  `/goal`, `/goal` daemon commands, and `/api/v1/sessions/:id/goal`. It accepts
  the same positive integer, integer-valued decimal, and `k`/`m`/`b` compact
  formats as `/goal`; unset or invalid values fall back to `1000000000`.
- `MATHCODE_MAX_CHAINED_COMMAND_INPUTS` caps nested local slash-command
  next-input submissions before `QueryEngine` aborts. Unset or invalid values
  fall back to `25`.

### Goal Command Syntax

Interactive release sessions support:

- `/goal <token-budget> <objective>`
- `/goal --budget <token-budget>`
- `/goal --budget=<token-budget>`
- optional `--max-continuations N` or `--max-continuations=<N>`
- `/goal pause`, `/goal resume`, `/goal status`, and `/goal clear`
- bare `/goal`, `/goal help`, `/goal -h`, and `/goal --help`

The command continues the same session; it does not spawn a separate agent.
Objectives that begin with `/` are submitted as plain goal text, not parsed as
another slash command.

After a budget, `--help` can be the first objective token. Once objective
parsing has started, flag-looking tokens remain objective text unless a valid
later `--budget` is being used to supply the required explicit budget.

Invalid `--budget` values are rejected when `--budget` is parsed as the budget
option, including numeric-expression objectives like:

```text
1 + 1 ... --budget nope
```

### Model Effort

Use `--effort <level>` or interactive `/effort <level>` with `low`, `medium`,
`high`, `max`, or a positive integer; `/effort auto` and `/effort unset` return
the session to the model default.
For CLI model overrides, the reserved `default` value is matched
case-insensitively; custom model IDs keep their original casing.

### Custom Agents

Custom agent definitions trim `description`, JSON `prompt`, markdown prompt
bodies, `initialPrompt`, and JSON enum fields such as `effort`,
`permissionMode`, `memory`, and `isolation`; blank required
descriptions/prompts are rejected, and blank optional initial prompts are
ignored. JSON `skills` lists are normalized like markdown frontmatter.

### Session Diagnostics, Compaction, And Tasks

Interactive context displays keep diagnostic context intact:

- `/context` uses the same visible markdown transcript output in interactive and
  non-interactive sessions
- `/config` includes a default-on `Show tool-use warnings` toggle. Disabling it
  suppresses only non-error runtime warning transcript events that are not
  stream parser/drop diagnostics; tool errors, permission denials, validation
  failures, stream-json parser diagnostics, and actionable tool-call diagnostics
  remain visible to the agent.
- markdown table cells are escaped
- slash-command and deferred built-in tool details remain visible
- MCP loaded/available status is shown
- deferred categories are excluded from current-usage tables
- manual compact reserve is shown as reserved buffer
- free/reserved rows stay visible when current usage is empty
- malformed token rows and zero-token synthetic windows do not produce invalid
  suggestion percentages
- server-side and MCP tool blocks are counted in message breakdowns

Compact and autocompact paths:

- clamp malformed thresholds, token counts, legacy content shapes, and blank
  tool IDs
- preserve singleton tool-result pairs
- scope statusline, away summary, survey, and sticky-prompt UI to the active
  post-compact transcript
- suppress stale warnings after partial compact
- coalesce duplicate remote compacting statuses

Task handling:

- `/tasks`, `TaskStop`, and SDK `stop_task` do not count the selectable leader
  row as a running teammate
- pending remote agents and running in-process teammates can be stopped
- task tools and SDK `stop_task` trim task IDs
- deprecated `shell_id` and TaskOutput `agentId`/`bash_id` aliases can backfill
  blank `task_id` values
- legacy `wait_up_to` seconds are normalized
- legacy persisted task statuses are recovered across user-visible status shapes
- legacy `TaskUpdate` status aliases are accepted
- blank task text fields are rejected
- task metadata keys are trimmed, and blank or unsafe `__proto__` metadata keys
  are rejected
- TaskOutput timeouts must be integer-valued
- idle in-process teammate output is treated as ready instead of waiting for
  timeout
- mixed text/structured TaskOutput and TaskStop results replay correctly
- legacy TaskOutput output replay preserves tag-looking text such as `<error>`
- trimming command whitespace does not create false TaskStop truncation markers
- recently completed rows expire on schedule, while hidden summaries remain
  visible in very short terminals

Shell sleep auto-backgrounding and path validation recognize:

- decimal, suffixed, signed, exponent, and trailing-dot durations, such as
  `sleep 2s`, `sleep 2m`, `sleep +2`, and `sleep 2e0`
- wrapped shell forms such as `env ... sleep 2s`
- PowerShell quoted, commented, redirected, and module-qualified sleep commands,
  such as `& 'sleep' 2`, `Start-Sleep -Seconds:2 > $null`, and
  `Microsoft.PowerShell.Utility\Start-Sleep -Seconds 2`
- TimeSpan `-Duration` values, PowerShell parameter abbreviations and common
  parameters
- short, fractional, signed, and exponent `timeout` wrappers

Terminal sessions retain tool errors and hook blocking reasons in compact
summaries, including failures before any inner operation completes. Skill
arguments preserve literal glob patterns and Markdown frontmatter is recognized
only at the start of a file. Config recovery recommends valid local backup
files; future timestamps and corrupt generations cannot suppress normal backups.
Failed quarantine copies report their actual error. Stats labels fit the
available columns, screenshots handle ANSI hyperlinks, and release notes stop
at the installed version.
Recognized ANSI control-string contents stay out of screenshots even across
line breaks. SVG exports expand tabs to eight-column stops. Brace expansions that exceed
their depth or result budget return the complete original pattern.
YAML recovery preserves valid neighboring scalar values and their quote/comment
semantics. Recovered brace globs retain skill/instruction path scoping, and unmatched
character classes cannot consume patterns in later path segments. Transcript
mode shows failed or blocked hook commands even when verbose mode is off.
Git config lookups preserve significant whitespace before line continuations,
including a final backslash at EOF, so configured hook paths retain their value.

Write requires a complete prior read of an existing file, starting at the first
line without an explicit `limit` (even if a limited read reaches EOF). Unread, partial, and
truncated views are rejected before loading the target; subsequent reads are
bounded by the cached snapshot, including if the file grows during validation.

Full-file edits check the latest content even when an external save preserves or
backdates the modification time. Notebook reads retain complete JSON snapshots
for safe whole-file replacement. Text and notebook reads warn about invalid
UTF-8 and do not cache lossy snapshots, even when token validation fails.
Write and NotebookEdit refuse to replace malformed bytes regardless of file
size until the encoding is repaired. Merging read caches preserves the newer file
state even when the cache is full. Notebook edits reject lossy decoding, return
the stored cell ID, and remove text-cell attachments when converting to code.
Glob results are independent of personal ripgrep output settings; Grep preserves
delimiters inside character classes. Git diffs preserve special filenames,
select literal paths, count header-like content, and enforce UTF-8 byte limits.

Tool diagnostics retain failure reasons and warnings alongside verbose logs.
MCP errors retain embedded resource details and structured fields. If an MCP
content block cannot be processed, its diagnostic remains visible alongside
readable blocks and structured results. Agent hooks preserve nested exception
details, inherited timeout reasons, and provider errors. Invalid Lean results
preserve readable diagnostics, file/range/code fields, and warnings even when
other fields cannot be read.

Task output retains a bounded diagnostic tail after overflow and preserves
concrete read errors. Completion notices retain both ends of long output, and
successful asynchronous hooks still report stderr diagnostics. Quiet hooks
report cleanup failures, remove completed entries, and invalidate the session
environment after SessionStart. WebFetch keeps decoding warnings on cached and binary responses, including when summarization
fails without a saved file. New sessions refresh hook
environments instead of reusing a prior session's values.

Transcript export includes pre-compaction history and expanded tool details,
continues past invisible chunks, and validates chunk sizes. Early terminal input
preserves split UTF-8 during handoff and normalizes pasted CRLF once. Repeated
scalar CLI options use the last actual occurrence. Scheduled runs remain in the
future across fall-back transitions, and uneven cron steps retain their precise
expression instead of an inaccurate interval label. Activity accounting retains
eligible user time before and between CLI work, subtracting only actual overlap.

WebUI start retries preserve request identity after a lost acknowledgement.
On command/session conflicts, WebUI checks the original session and opens it
without replaying the prompt, preserving the draft when acceptance is uncertain.
If the session is confirmed missing, the next explicit retry uses a new command
ID with the same session ID; failed lookups retain both IDs and their diagnostics.
Late replies respect navigation and newer goal actions. Goal objectives accept
ordinary apostrophes and primed Lean names. Invalid SSE end frames trigger
recovery, and arXiv freshness labels describe the data actually returned.


## Features

### Persistent Lean feedback backends

Eligible generic compile callers can opt into the in-process Lean REPL:

```env
MATHCODE_LEAN_REPL=1
```

An external Kimina Lean Server can additionally serve atomic exploration:

```env
MATHCODE_KIMINA_SERVER=1
MATHCODE_KIMINA_CMD="/absolute/path/to/kimina-lean-server/.venv/bin/python -m server"
MATHCODE_KIMINA_CWD=/absolute/path/to/kimina-lean-server
MATHCODE_KIMINA_PROJECT_ROOT=/absolute/path/to/served-lean-project
```

On macOS, `LeanGoal` and `LeanCheck` reuse that server only when the declared project
matches the resolved project and a live guard confirms its Lean version.
Otherwise they fall back to the pinned subprocess and expose the reason as a
warning. Kimina feedback is not a completion certificate. `LeanVerify` and
isolated paper agents always use fresh isolated subprocesses. MathCode launches
Kimina loopback-only inside its fail-closed Lean sandbox, with a random bearer
key that never enters the Lean REPL environment, no provider credentials, and
scratch-only writes. A virtualenv, when used, must live below
`MATHCODE_KIMINA_CWD`, and `MATHCODE_KIMINA_CMD` must start directly with that
Python executable rather than a command wrapper. Manifest roots that contain the project or another
protected host scope are rejected, and remote-package storage stays inside the
project. A standard-library-only Python guardian lives in a separate read-only
support root and reuses the selected Kimina interpreter, so no MathCode source
tree or second runtime is exposed to the sandbox. Python site, `.pth`, and
`sitecustomize` loading are disabled before the handoff path enters that
interpreter. It mediates supported
`setsid` Lake launches, deletes the mode-0600 auth handoff and strips both
Kimina key names plus its private environment before Lean starts, and kills its
separately owned Lake group through an independent owner-pipe HUP observer, even
when Lake stops reading input. Parent exit and
`SIGINT`/`SIGTERM`/`SIGHUP`
also clean the complete owned tree. Current `/api/check` caller cancellation
preserves the shared service; legacy `/verify` cancellation or uncertain
backend/transport state cleans up the complete service tree before restart.
Linux and Windows use pinned subprocesses.

### Plan Files

`/plan` stores session plan markdown in the active user config-home `plans/`
slot by default (`~/.mathcode/plans/` unless `MATHCODE_CONFIG_DIR` relocates
the config home). To keep plan files under the project tree, set
`plansDirectory` in project or local settings to a custom directory relative to
the project root. Nested directories are created as needed, and symlink escapes
fall back to the user config-home `plans/` directory.

### Theorem Library

Manage an explicit library of proved theorems:

```bash
/theorem-store store <file> <qualified-declaration> # verify and store one theorem
/theorem-store sync   # inspect candidates and ask which declarations to store
/theorem-store check  # compile-check the assembled library
/theorem-store status # show stored count and vault info
```

`/theorem-store store` calls `LeanTheoremLibrary` for one explicit fully
qualified declaration. The tool performs fresh strict verification, rechecks
the source and dependency snapshot immediately before persistence, then
strictly verifies the exact renamed declaration in the assembled `Stored.lean`.
The elaborated proposition must remain identical, and success immediately
builds an importable workspace module. The library, workspace mirror, compiled
artifacts, and index update as one rollback-capable transaction.
Private theorem compilation and public Lake publication each have a separate
bounded 300-second build budget; a timeout still rolls the transaction back
without exposing incomplete artifacts.
`/theorem-store sync` is optional
agent guidance: it discovers candidates, asks which declarations to store, then
uses the same one-declaration tool call for each confirmed candidate. Atomic
Lean feedback tools never append to the theorem library as a hidden effect.

`LibSearch` is exposed to the agent only while a vault is active through
`MATHCODE_OBSIDIAN_VAULT` or `/obsidian on`. Without an active vault, the agent
skips stored-library search and can still use `LeanSearch` for Lean declarations.
After `/obsidian off`, a previously cached `LibSearch` tool is removed before
the next agent turn.

### Axiom Library

Store conversational assumptions as persistent, consistency-checked declarations:

```bash
/axiomatize "A is faster than B"     # formalize + store
/axiomatize list                     # show all active axioms
/axiomatize check                    # consistency review
/axiomatize remove <name>            # remove a declaration
```

Axioms are stored per vault with Lean formalization and compile checks. Atomic
Lean tool calls do not inject them implicitly; import or reference the stored
declarations explicitly when they are part of the intended proof context.

### Obsidian Theorem Graph

Generate an Obsidian vault that visualizes theorem dependencies as a knowledge graph:

```bash
/obsidian on       # enable + generate from existing formalizations
/obsidian off      # disable
/obsidian generate # regenerate now
```

Use `/obsidian generate` after changing proofs to refresh the vault explicitly.
Atomic Lean tool calls never update it as a hidden side effect. Open it in
Obsidian and use Graph View to see theorem-to-lemma relationships.
Refreshes overwrite MathCode-managed notes and exact legacy MathCode projections
from before the managed marker existed; those legacy notes gain the marker. If
a theorem, lemma, index, or blueprint filename is occupied by any other user
note, generation fails and preserves that note.

Each lemma stub includes the full Lean definition queried from Mathlib via
`#print`.

### Agentic Lean

For ordinary Lean work, the agent can choose among four atomic tools:

- `LeanGoal` inspects one explicit source position.
- `LeanCheck` compiles a file or ephemeral candidate and returns structured feedback.
- `LeanSearch` queries one explicit provider without hidden fan-out and safely
  folds provider-formatted multiline type signatures onto one line.
- `LeanVerify` performs the strict final check for one fully qualified declaration; only `data.verified=true` certifies completion.

`LeanVerify` uses a 1,200-second default timeout and accepts an explicit
`timeout_s` of up to 3,600 seconds.

The optional `/lean` skill offers guidance without imposing a fixed phase,
tactic order, retry budget, or planner. The former fixed controllers have been
removed and are not release entrypoints or model-visible tools.
The fixed scheme is retired, not the useful methods: the agent may still choose
subgoal decomposition, helper lemmas, branching, milestones, stuck detection,
diagnostic repair, and theorem reuse, then reorder or abandon them freely.
Axiom and theorem libraries are separate explicit actions, never hidden effects
of an atomic Lean call.
Strict verification resolves Lean/Lake executables outside the project tree,
preserves Lake's canonical source/module context, and obtains target axiom
usage plus direct module axioms through Lean's environment API rather than
source-controlled macros or output.

### Scheduled Agent Loops

The bundled CLI ships with recurring prompt scheduling enabled out of the box.

Inside interactive MathCode sessions you can use:

```bash
/loop 10m check the deploy
/loop 1h /standup 1
```

Use short-lived loops for reminders and monitoring. When you want a schedule to survive restarts, create a durable schedule from the interactive session.

## Extensibility

MathCode supports three extension mechanisms:

### Skills (`.mathcode/skills/`)

Add project-local skills at `.mathcode/skills/<name>/SKILL.md`. Each skill
uses its own directory; standalone `skills/*.md` files are not loaded.

### Tools (`tools/`)

Drop Python `.py` scripts with YAML frontmatter to add analysis tools. Auto-discovered at startup.

3 analysis tools are included: `axiom-checker`, `lib-search`, and
`proof-stats`. They remain available when MathCode is launched from another
workspace; a workspace-local tool with the same normalized name overrides the
bundled copy. Python 3.12+ is required only if you use these tools.

### Plugins (`plugins/`)

Drop plugin folders with `.mathcode-plugin/plugin.json` manifests to add commands, skills, agents, MCP servers, hooks, and more. Load via `--plugin-dir` or install from Git repos via `/plugin`.

## Backend Setup

The default system prompt combines Codex/Astra workflow guidance with MathCode's
coding, Lean, and EDA capabilities. Fable request models (such as `claude-fable-5`
and `claude-fable-5-1`) use a dedicated MathCode/Fable adaptation emphasizing
action on sufficient evidence and complete delivery. Other recognized Claude
models retain the original template; other models use Astra. This also applies
through OpenRouter. Both new templates favor authorized action, parallel
independent reads, and focused verification.
Custom system/agent prompts keep their existing precedence. Model and
reasoning-effort settings are unchanged; task latency must be measured separately.
When the independent-verification feature is enabled and Agent is available,
Astra/Fable retain its completion-time review requirement, as standard Claude does.
Both also retain the instruction to record important tool information in responses
before the original results may be cleared.

### Default Codex/OpenAI Path

No `.env` edits are required for the default path.

```bash
codex auth login
mathcode
```

If you are still in the same shell where setup just finished, `./run` is the immediate fallback until you reload your shell profile.

The packaged `.env` template now selects GPT-6 Astra at medium reasoning effort.
To apply the same values to an existing `.env` created by an older release and
also select medium for the CLI effort level, set:

```env
OPENAI_MODEL=gpt-6-astra
OPENAI_SMALL_MODEL=gpt-6-astra
OPENAI_REASONING_EFFORT=medium
MATHCODE_EFFORT_LEVEL=medium
```

Codex Responses requests always use the required streaming transport, including
internal retries that collect a complete response before returning it. `stream`
is not a MathCode setting; do not add it to `settings.json` to fix an API error.

Responses tool calls preserve optional arguments such as Read’s line limit; an entire-file read can omit that limit.

To use an Anthropic-compatible backend instead, set:

```env
MATHCODE_USE_OPENAI=0

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5
```

The release `./run` wrapper sources the bundle `.env` before launching
MathCode. For interactive `/webui` slash-command launches, the selected WebUI
port and workspace override same-named keys from that `.env`.

WebUI routing is separate from the CLI `.env`. New settings enable **Follow
application defaults**: provider, model, and reasoning effort follow the installed
application on startup (currently `openai` / `gpt-6-astra` / `medium`). Turn this
off in Settings and save to pin your selection. Older settings have no record
of whether their route was chosen manually, so they keep their selection until
you enable this option and save. Other settings and existing sessions are preserved.
Settings live outside Git at `$XDG_CONFIG_HOME/mathcode/webui/ui-settings.json`
(default `~/.config/mathcode/webui/ui-settings.json`); `git pull` does not edit
that file. Restart an updated daemon to load the new application defaults.

### WebUI Provider Keys

In the WebUI settings panel, provider-key rows are limited to secrets the
daemon can pass to real child sessions today: `anthropic` and `openrouter`.
Codex/OpenAI routes use Codex OAuth, not an `OPENAI_API_KEY` row.
WebUI `minimal` reasoning effort is preserved for OpenAI/OpenRouter routes and
maps to the CLI's lowest available `low` effort on Anthropic-compatible routes.

### Bundled Provider Dependencies

The release binary bundles the provider SDKs used by the Anthropic-compatible,
Bedrock, Vertex, and Foundry branches, plus the MCPB/DXT plugin package; these
routes do not require a source checkout's `node_modules`. Bedrock, Vertex, and
Foundry use their provider-specific credentials rather than
Anthropic-compatible `ANTHROPIC_AUTH_TOKEN` / `apiKeyHelper` bearer headers.

## FAQ

**Q: `mathcode` is not found right after setup**

Open a new shell, or run:

```bash
source ~/.zshrc
```

If you want to keep working immediately before reloading your shell, use:

```bash
./run
```

**Q: `./run` fails with `exec format error`, `Bad CPU type in executable`, or a similar startup error**

You probably downloaded the wrong binary for your platform. Re-run `bash setup.sh`, or download the correct release asset manually from GitHub Releases.

**Q: Startup says Codex auth is missing**

Run:

```bash
codex auth login
```

**Q: Can I skip cloning and just download a release asset**

Yes. You can download and extract the `.tar.gz` bundle from GitHub Releases
directly.

The archive is self-contained; `bash setup.sh` only downloads from GitHub when
bundled runtime files are missing, stale, or unverified. The bootstrap repo just
makes `bash setup.sh` the default path.

## Star History

Track the project's growth over time here:

[![Star History Chart](https://star-history.dera.page/svg?repos=math-ai-org/mathcode&type=Date)](https://star-history.dera.page/#math-ai-org/mathcode&Date)

## Citation

If you use MathCode in research, please cite it as:

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

## Community

When the build-provided feedback instruction is blank, MathCode's main agent
directs users to [open a GitHub issue](https://github.com/math-ai-org/mathcode/issues).

Join our Discord for help, feedback, and discussion: **[discord.gg/f2AFP9W5](https://discord.gg/f2AFP9W5)**

## Acknowledgments

MathCode preserves useful proof-search ideas as optional agent guidance while
Lean remains the proof authority.
