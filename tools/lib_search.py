#!/usr/bin/env python3
# ---
# name: lib-search
# description: Search the theorem library for stored theorems matching a keyword query
# input:
#   query:
#     type: string
#     description: Space-separated keywords to search for in theorem names and signatures
#     required: true
#   vault:
#     type: string
#     description: Optional Obsidian vault path to search instead of MATHCODE_OBSIDIAN_VAULT
#     required: false
# output: json
# ---
"""Search the user theorem library for relevant stored theorems.

Searches Stored.lean and INDEX.md for theorems matching a keyword query.
Useful for the agent to check what's already proved before attempting
a new proof.

Usage:
    python3 tools/lib_search.py "cyclic"
    python3 tools/lib_search.py "prime order"
    python3 tools/lib_search.py "even odd parity"
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any


STORED_THEOREM_BLOCK_RE = re.compile(
    r"-- @stored-theorem\s+(?P<stored_name>[A-Za-z0-9_]+)\b.*?\n"
    r"-- Original:\s*(?P<original>.+?)\n"
    r"-- Source:\s*(?P<source>.*?)\n"
    r"-- Proved:\s*(?P<proved>.*?)\n"
    r"theorem\s+(?P=stored_name)\s+(?P<type_and_body>.+?)\n"
    r"-- @end-stored-theorem",
    re.DOTALL,
)
STORED_THEOREM_START_MARKER_RE = re.compile(r"^-- @stored-theorem(?:\s|$)")
STORED_THEOREM_PLAUSIBLE_BLOCK_START_RE = re.compile(
    r"^-- @stored-theorem\s+(?P<stored_name>[A-Za-z0-9_]+)\b.*?\n"
    r"-- Original:\s*.+?\n"
    r"-- Source:\s*.*?\n"
    r"-- Proved:\s*.*?\n"
    r"theorem\s+(?P=stored_name)\b",
    re.DOTALL,
)


def validate_lean_identifier(name: str) -> str | None:
    """Return the name if it is a legal Lean identifier, else None."""
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) else None


def derive_vault_basename(vault_path: Path) -> str:
    """Mirror the TypeScript vault-name derivation used by theoremLib.ts."""
    raw = vault_path.name
    segments = [segment for segment in re.split(r"[-_\s]+", raw) if segment]
    pascal = "".join(segment[:1].upper() + segment[1:] for segment in segments)
    pascal = re.sub(r"[^A-Za-z0-9]", "", pascal)
    if pascal and pascal[0].isdigit():
        pascal = f"V{pascal}"
    if not pascal:
        pascal = "Default"
    return pascal[:32]


def derive_vault_namespace(vault_path: Path) -> str:
    """Return the theorem-library namespace for the active vault."""
    override = os.environ.get("MATHCODE_VAULT_NAME", "").strip()
    if override:
        validated = validate_lean_identifier(override)
        if validated is not None:
            return f"{validated}TheoremLib"
        raise ValueError(
            f"MATHCODE_VAULT_NAME={override} is not a legal Lean identifier "
            "(must start with a letter or underscore and contain only [A-Za-z0-9_])"
        )
    return f"{derive_vault_basename(vault_path)}TheoremLib"


def split_header_and_body(type_and_body: str) -> tuple[str, str]:
    """Mirror theoremLib.ts splitHeaderAndBody for Stored.lean blocks."""
    depth = 0
    for idx, ch in enumerate(type_and_body):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(depth - 1, 0)
        elif ch == ":" and depth == 0 and idx + 1 < len(type_and_body) and type_and_body[idx + 1] == "=":
            body_start = idx + 2
            while body_start < len(type_and_body) and type_and_body[body_start].isspace():
                body_start += 1
            header = type_and_body[:idx].rstrip()
            if type_and_body.startswith("by", body_start):
                body = type_and_body[body_start + 2 :].lstrip("\n").rstrip()
                return header, body
            term = type_and_body[idx + 2 :].strip()
            if term:
                return header, f"  exact ({term})"
    return type_and_body.strip(), ""


def parse_stored_lean(text: str) -> list[dict[str, str]]:
    """Parse Stored.lean blocks without depending on a controller runtime."""
    records: list[dict[str, str]] = []
    matches = list(STORED_THEOREM_BLOCK_RE.finditer(text))
    for match in matches:
        groups = match.groupdict()
        header, body = split_header_and_body(groups["type_and_body"])
        records.append(
            {
                "stored_name": groups["stored_name"].strip(),
                "original_name": groups["original"].strip(),
                "source": groups["source"].strip(),
                "proved_at": groups["proved"].strip(),
                "signature": f"theorem {groups['stored_name'].strip()} {header}".strip(),
                "proof_body": body,
            }
        )
    parsed_starts = {match.start() for match in matches}
    parsed_spans = [match.span() for match in matches]
    sentinel_count = 0
    offset = 0
    for line in text.splitlines(keepends=True):
        content_line = line.removesuffix("\n").removesuffix("\r")
        if STORED_THEOREM_START_MARKER_RE.match(content_line):
            inside_parsed_block = any(start < offset < end for start, end in parsed_spans)
            plausible_start = STORED_THEOREM_PLAUSIBLE_BLOCK_START_RE.match(
                text[offset:]
            )
            if (
                offset in parsed_starts
                or not inside_parsed_block
                or plausible_start is not None
            ):
                sentinel_count += 1
        offset += len(line)
    if sentinel_count > len(records):
        raise ValueError("Stored.lean contains malformed stored-theorem blocks")
    return records


def expand_home_vault_path(raw: str) -> Path:
    """Expand only the current user's home alias, not arbitrary ~user names."""
    if raw == "~" or raw.startswith("~/") or raw.startswith("~\\"):
        return Path(raw).expanduser()
    return Path(raw)


def parse_args(argv: list[str]) -> tuple[str, Path]:
    """Parse the command line. Supports `--vault <path>` as the help text claims."""
    args = argv[1:]
    vault_path: Path | None = None
    query_parts: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--vault":
            if i + 1 >= len(args):
                raise ValueError("--vault requires a path")
            vault_path = expand_home_vault_path(args[i + 1])
            i += 2
            continue
        query_parts.append(arg)
        i += 1

    if not query_parts:
        raise ValueError("missing query")

    if vault_path is None:
        vault_path_str = os.environ.get("MATHCODE_OBSIDIAN_VAULT", "").strip()
        if not vault_path_str:
            raise ValueError(
                "MATHCODE_OBSIDIAN_VAULT not set. Set the env var or pass --vault <path>."
            )
        vault_path = expand_home_vault_path(vault_path_str)

    return " ".join(query_parts), vault_path


def search_stored(query: str, vault_path: Path) -> list[dict[str, Any]]:
    """Search the theorem library for matching entries."""
    stored_path = vault_path / "TheoremLib" / "Stored.lean"
    if not stored_path.exists():
        return []

    text = stored_path.read_text(encoding="utf-8")
    records = parse_stored_lean(text)

    namespace = derive_vault_namespace(vault_path)
    keywords = query.lower().split()
    results: list[dict[str, Any]] = []

    for rec in records:
        searchable = (
            f"{rec['stored_name']} {rec['original_name']} "
            f"{rec['signature']} {rec['proof_body']}"
        ).lower()
        if any(kw in searchable for kw in keywords):
            results.append(
                {
                    "stored_name": rec["stored_name"],
                    "original_name": rec["original_name"],
                    "signature": rec["signature"],
                    "source": rec["source"],
                    "proved_at": rec["proved_at"],
                    "usage": f"exact {namespace}.{rec['stored_name']} <args>",
                }
            )

    return results


def main() -> int:
    try:
        query, vault_path = parse_args(sys.argv)
        results = search_stored(query, vault_path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print("Usage: python3 tools/lib_search.py [--vault <path>] <query>", file=sys.stderr)
        return 1

    if not results:
        print(json.dumps({"query": query, "matches": 0, "results": []}))
    else:
        print(json.dumps({"query": query, "matches": len(results), "results": results}, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
