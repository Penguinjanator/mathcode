# MathCode

[English](./README.md) | [中文](./README.ZH.md)

MathCode is a coding assistant for the terminal and browser, with built-in Lean 4
support. It can inspect proof goals, search declarations, check candidates, and
verify completed proofs.

[Website](https://math-ai-org.github.io/mathcode/) ·
[Releases](https://github.com/math-ai-org/mathcode/releases) ·
[Issues](https://github.com/math-ai-org/mathcode/issues) ·
[Discord](https://discord.gg/f2AFP9W5)

![MathCode terminal demo](./Demo.png)

## What you can do

- Work on code and Lean proofs in your own workspace.
- Use the terminal or a local WebUI with math and diagram rendering.
- Store verified theorems and explicit assumptions, and explore dependencies in Obsidian.
- Add project skills, Python analysis tools, and MCP plugins.

Lean is the proof authority: a proof is complete only after strict verification
succeeds. Library storage and vault updates are explicit actions.

## Get started

Supports **macOS Apple Silicon (arm64)** and **Linux x86_64 with glibc and AVX2**.
The default backend requires the `codex` CLI and a Codex login.

```bash
git clone https://github.com/math-ai-org/mathcode.git
cd mathcode
bash setup.sh
codex auth login
./run
```

Setup asks whether to install Lean/Mathlib. Use `bash setup.sh --without-lean`
for the CLI and WebUI only, or `--with-lean` for a full installation. Lean support
needs about 10 GiB of additional disk space and can be added later with
`bash setup.sh --install-lean`. Non-interactive setup defaults to a full install.

Setup installs a `mathcode` command for new shells. Use `./run` immediately, or
open a new shell and run:

```bash
mathcode -p "prove that the square of an even number is even"
```

For the browser interface, run `./run webui` and open the local URL. To update an
existing checkout, run `git pull --ff-only` and rerun setup.

## Documentation

Read the [online documentation](https://math-ai-org.github.io/mathcode/docs/).

| Guide | Contents |
| --- | --- |
| [Installation](docs/release/installation.md) | Requirements, install modes, upgrades, toolchains, troubleshooting |
| [Usage](docs/release/usage.md) | CLI, WebUI, goals, sessions, schedules, diagnostics |
| [Lean workflows](docs/release/lean.md) | Proof tools, theorem and axiom libraries, Obsidian, optional feedback backends |
| [Configuration](docs/release/configuration.md) | Providers, model settings, skills, tools, plugins |

See [release notes](RELEASE_NOTES.md) for the current release.

## Citation

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
