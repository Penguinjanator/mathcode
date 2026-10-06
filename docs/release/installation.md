# Installation and troubleshooting

[中文](installation.ZH.md) · [Usage](usage.md) · [Configuration](configuration.md)

## Requirements

- macOS arm64, or glibc-based Linux x86_64 with AVX2. Linux releases are built on Ubuntu 22.04.
- `curl` and either `shasum` or `sha256sum`.
- The `codex` CLI for the default backend; see [other providers](configuration.md).
- About 10 GiB of additional disk space for Lean/Mathlib. Linux Lean support also requires `bwrap` (the `bubblewrap` package) and `socat`.
- Python 3.12+ only if you use the bundled Python analysis tools.

## Choose an install mode

From the release checkout or an extracted release bundle:

```bash
bash setup.sh               # CLI and WebUI only (default)
bash setup.sh --with-lean     # CLI, WebUI, Lean and Mathlib
bash setup.sh --without-lean  # CLI and WebUI only
bash setup.sh --install-lean  # add or repair Lean support later
```

`bash setup.sh` defaults to CLI and WebUI only, without a selection prompt, in
both interactive terminals and scripts. Lean/Mathlib installation requires
`--with-lean` or `--install-lean`. Existing Lean installations are kept.

After a core-only install, the first approved local Lean goal, check, verify, or
library operation can install the deferred toolchain. Progress and failures are
shown during installation. This applies only to the bundled `lean-workspace`;
remote `LeanSearch` and caller-owned Lean projects do not trigger installation.

Setup creates `.env` if needed and installs a managed `mathcode` launcher in
`~/.local/bin/`. Existing configuration is preserved. The bundle includes CLI,
WebUI, and ripgrep; a source checkout or `node_modules` is not required.

## Upgrade and repair

```bash
git pull --ff-only           # for a cloned release checkout
bash setup.sh --without-lean # or --with-lean, according to your needs
bash setup.sh --status
```

Setup checks runtime versions and hashes, repairing missing, stale or invalid
files from the matching GitHub Release. It verifies the downloaded checksum
before replacing an existing installation. `--status` reports CLI, WebUI,
ripgrep and Lean readiness. Restart a running WebUI daemon after upgrading.

`bash setup.sh --clean` removes installed runtime/toolchain artifacts while
preserving proofs in `LeanFormalizations/`, vault data, and the locked Lake
manifest. Rerun setup afterwards. See `bash setup.sh --help` for all flags.

## Use a downloaded archive

Download your platform's `.tar.gz` and `SHA256SUMS.txt` from
[Releases](https://github.com/math-ai-org/mathcode/releases). Check the archive
against its matching checksum entry, extract it, then run setup from that folder.
The archive is self-contained; setup downloads runtime files only when repair
is needed. Keep using the matching platform when updating manually.

## Lean toolchain selection

When Lean installation is requested, the default is a bundle-local toolchain
in `.local/elan`, pinned by
`lean-workspace/lean-toolchain`. Setup retains the bundled `lake-manifest.json`
and requires a successful `MathCodeLean` readiness build; failed Mathlib cache
fetches can fall back to building locally.

To reuse a system installation, run:

```bash
MATHCODE_SETUP_USE_SYSTEM_LEAN=1 bash setup.sh --with-lean
```

Both Lean and Lake must match the pinned version. Setup resolves Elan proxies
to concrete binaries and saves validated paths in `.env`; an invalid pair falls
back to bundle-local Lean. Ambient `ELAN_TOOLCHAIN` overrides are ignored when
selecting the pinned toolchain. Custom projects retain their own toolchain setup.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `mathcode` is not found after setup | Open a new shell, or use `./run` immediately. |
| `exec format error` or `Bad CPU type in executable` | Rerun setup or download the archive for your OS and CPU. |
| Codex authentication is missing | Run `codex auth login`. |
| Lean is reported as deferred | Run `bash setup.sh --install-lean` when you need local Lean support. |
| An upgrade still uses old WebUI defaults | Restart the daemon and check **Follow application defaults** in Settings. |

Setup replaces only launchers it previously created. Use `MATHCODE_INSTALL_BIN_DIR`
to select another launcher directory; relative paths are resolved from the bundle
root. If setup cannot write the launcher, the bundle remains usable through `./run`.
