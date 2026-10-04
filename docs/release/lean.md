# Lean workflows

[中文](lean.ZH.md) · [Installation](installation.md) · [Usage](usage.md)

## Proof tools

MathCode works directly on Lean files in the selected workspace. The agent
chooses tools as needed; `/lean` provides optional guidance.

| Tool | Use |
| --- | --- |
| `LeanGoal` | Inspect a goal at an explicit source position. |
| `LeanCheck` | Compile a file or temporary candidate for feedback. |
| `LeanSearch` | Search declarations through one selected provider. |
| `LeanVerify` | Strictly verify one fully qualified declaration. |

Only a successful `LeanVerify` result with `data.verified=true` certifies
completion. Its default timeout is 1,200 seconds; `timeout_s` can be set up to
3,600 seconds. Goal/check feedback alone is not a certificate.

The agent may use helper lemmas, subgoals, branching and theorem reuse. Atomic
proof tools do not silently store theorems, add axioms, or update a vault.

## Theorem library

```text
/theorem-store store <file> <qualified-declaration>
/theorem-store sync
/theorem-store check
/theorem-store status
```

`store` verifies and stores one explicit theorem. It rechecks the source and
dependencies, verifies the renamed declaration in `Stored.lean`, and builds an
importable module. Failed publication rolls back the library update. Compilation
and publication each have a 300-second build budget.

`sync` discovers candidates and asks which declarations to store. `check`
compile-checks the assembled library; `status` reports stored count and vault
information. `LibSearch` is available only with an active vault through
`MATHCODE_OBSIDIAN_VAULT` or `/obsidian on`. Without one, use `LeanSearch`.

## Axiom library

```text
/axiomatize "A is faster than B"
/axiomatize list
/axiomatize check
/axiomatize remove <name>
```

Declarations are stored per vault with Lean compile checks and a consistency
review. Import or reference them explicitly when they belong in the proof
context. Atomic Lean calls do not inject stored assumptions automatically.

## Obsidian

```text
/obsidian on
/obsidian off
/obsidian generate
```

Use `generate` after changing proofs, then open the vault in Obsidian Graph View
to inspect dependencies. Lemma notes include definitions queried from Mathlib.
Generation updates MathCode-managed notes and recognized legacy projections;
it preserves unrelated user notes and fails on conflicting filenames.

Paper catalog IDs must not collide. If another paper already has the ID derived
from a title and authors, choose a distinct ID or another vault. Dependency-cycle
errors identify the involved claims and how to repair the catalog.

## Optional feedback backends

Eligible generic compile callers can use the in-process REPL with
`MATHCODE_LEAN_REPL=1`. Atomic proof tools do not use that cache.

On macOS, an external Kimina Lean Server can provide `LeanGoal` and `LeanCheck`
feedback:

```env
MATHCODE_KIMINA_SERVER=1
MATHCODE_KIMINA_CMD="/absolute/path/to/kimina-lean-server/.venv/bin/python -m server"
MATHCODE_KIMINA_CWD=/absolute/path/to/kimina-lean-server
MATHCODE_KIMINA_PROJECT_ROOT=/absolute/path/to/served-lean-project
```

The declared project and Lean version must match the current project. Start
Kimina directly with Python; any virtualenv must be below `MATHCODE_KIMINA_CWD`.
MathCode launches it in a loopback-only sandbox without provider credentials,
with writes limited to private scratch space. Setup, compatibility or transport
failures fall back to the pinned subprocess and report a warning.

Kimina feedback is not a completion certificate. `LeanVerify` and isolated paper
agents always use fresh isolated subprocesses. Linux and Windows use pinned
subprocesses for this feedback path; the release archives themselves support
only the platforms listed in the [installation guide](installation.md).
