#!/usr/bin/env python3
# ---
# name: proof-stats
# description: Report statistics about a Lean 4 file including theorem count, tactics, and complexity
# input:
#   path:
#     type: string
#     description: Path to a .lean file to analyze
#     required: true
# output: json
# ---
"""Report structural statistics about a Lean 4 file.

Shows theorem count, proof length, tactics used, imports, and complexity
metrics. Useful for understanding a proof before golfing or reviewing.

Usage:
    python3 tools/proof_stats.py path/to/problem.lean
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from _lean_masking import (
    LEAN_IDENT_BOUNDARY,
    iter_lean_declaration_names,
    mask_lean_comments_and_strings,
    mask_lean_escaped_identifiers,
)


_ATTR_FRAGMENT = r"(?:@\[(?:[^\]\[]|\[[^\]]*\])*\]\s*)*"
_SCOPED_COMMAND_PREFIX_FRAGMENT = (
    r"(?:(?:open\b[^\n]*?\bin|set_option\b[^\n]*?\bin)\s*)*"
)
_SCOPED_COMMAND_KEYWORD_PAYLOAD_FRAGMENT = (
    r"(?:import|namespace|end|section|variable|variables|universe|universes|"
    r"attribute|export|include|omit)\b"
)
_PLACEHOLDER_RE = LEAN_IDENT_BOUNDARY
_THEOREM_START_RE = re.compile(
    rf"^\s*{_SCOPED_COMMAND_PREFIX_FRAGMENT}{_ATTR_FRAGMENT}"
    r"(?:(?:private|protected|noncomputable|local|unsafe|partial|nonrec)\s+)*"
    r"(?:theorem|lemma)\b",
    re.MULTILINE,
)
_DEF_START_RE = re.compile(
    rf"^\s*{_SCOPED_COMMAND_PREFIX_FRAGMENT}{_ATTR_FRAGMENT}"
    r"(?:(?:private|protected|noncomputable|local|unsafe|partial|nonrec)\s+)*"
    r"(?:def|instance)\b",
    re.MULTILINE,
)
_IMPORT_RE = re.compile(
    r"^\s*(?:public\s+)?(?:meta\s+)?import\s+(.+)$",
    re.MULTILINE,
)
_IMPORT_TAIL_MODIFIERS = {"all"}
_TACTIC_RE = re.compile(
    r"(?<![\w'?!\.«])(simp|rfl|ring|omega|linarith|nlinarith|norm_num|aesop|decide|"
    r"exact|apply|rw|intro|constructor|cases|rcases|obtain|have|let|"
    r"suffices|calc|induction|ext|funext|congr|convert|refine|use|"
    r"trivial|tauto|contradiction|exfalso|push_neg|by_contra|"
    r"field_simp|ring_nf|norm_cast|push_cast|simpa|rwa)(?![\w'?!\.»])",
    re.MULTILINE,
)
_TOP_LEVEL_COMMAND_RE = re.compile(
    rf"^[^\S\r\n]*(?:"
    rf"{_ATTR_FRAGMENT}(?:(?:private|protected|noncomputable|local|scoped|unsafe|partial|nonrec)\s+)*"
    r"(?:theorem|lemma|example|def|instance|abbrev|opaque|axiom|constant|postulate|"
    r"inductive|structure|class|macro|macro_rules|syntax|elab|elab_rules|notation|"
    r"infix|infixl|infixr|prefix|postfix|declare_syntax_cat|run_cmd|initialize|"
    r"builtin_initialize|simproc|builtin_simproc|dsimproc|builtin_dsimproc|"
    r"cbv_simproc|builtin_cbv_simproc)\b"
    r"|#\w+"
    r"|(?:import|open|namespace|end|section|variable|variables|universe|universes|"
    r"set_option|attribute|export|include|omit)\b"
    r")",
    re.MULTILINE,
)
_BY_LINE_RE = re.compile(r"^\s*by\b")
_SCOPED_BY_RE = re.compile(
    r"^\s*(?:(?:open\b[^\n]*?\bin|set_option\b[^\n]*?\bin)\s*)+by\b",
)
_SCOPED_COMMAND_PAYLOAD_RE = re.compile(
    rf"\bin\s*{_SCOPED_COMMAND_PREFIX_FRAGMENT}(?:"
    r"#\w+"
    rf"|{_SCOPED_COMMAND_KEYWORD_PAYLOAD_FRAGMENT}"
    rf"|{_ATTR_FRAGMENT}(?:(?:private|protected|noncomputable|local|scoped|unsafe|partial|nonrec)\s+)*"
    r"(?:theorem|lemma|example|def|instance|run_cmd|initialize|abbrev|opaque|"
    r"axiom|constant|postulate|inductive|structure|class|macro|macro_rules|"
    r"syntax|elab|elab_rules|notation|"
    r"infix|infixl|infixr|prefix|postfix|declare_syntax_cat|simproc|"
    r"builtin_initialize|builtin_simproc|dsimproc|builtin_dsimproc|"
    r"cbv_simproc|builtin_cbv_simproc)\b"
    r")"
)
_TERM_LOCAL_BINDING_RE = re.compile(r"(?<![\w'?!«])(?:let|have|suffices)(?![\w'?!»])")


def _line_indent_at(text: str, index: int) -> int:
    line_start = text.rfind("\n", 0, index) + 1
    indent = 0
    while line_start + indent < len(text) and text[line_start + indent] in " \t":
        indent += 1
    return indent


def _line_is_blank_at(text: str, index: int) -> bool:
    line_start = text.rfind("\n", 0, index) + 1
    line_end = text.find("\n", index)
    if line_end == -1:
        line_end = len(text)
    return not text[line_start:line_end].strip()


def _next_nonblank_line_indent(text: str, index: int) -> int | None:
    line_start = text.find("\n", index)
    while line_start != -1:
        line_start += 1
        line_end = text.find("\n", line_start)
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end]
        if line.strip():
            return len(line) - len(line.lstrip(" \t"))
        line_start = text.find("\n", line_end)
    return None


def _find_next_top_level_semicolon_on_line(text: str, start: int) -> int | None:
    depth = 0
    opener_to_closer = {"(": ")", "[": "]", "{": "}"}
    closers = set(opener_to_closer.values())

    for index in range(start, len(text)):
        char = text[index]
        if char == "\n":
            return None
        if char == ";" and depth == 0:
            return index
        if char in opener_to_closer:
            depth += 1
        elif char in closers and depth > 0:
            depth -= 1

    return None


def _line_has_code_after(text: str, index: int) -> bool:
    line_end = text.find("\n", index)
    if line_end == -1:
        line_end = len(text)
    return bool(text[index:line_end].strip())


def _is_scoped_in_command_line(
    text: str,
    index: int,
    declaration_indent: int,
    proof_body_start: int | None,
) -> bool:
    if _line_indent_at(text, index) <= declaration_indent:
        return False
    if proof_body_start is None or index <= proof_body_start:
        return False
    proof_line_end = text.find("\n", proof_body_start)
    if (
        proof_line_end != -1
        and index > proof_line_end
        and _line_has_code_after(text, proof_body_start)
    ):
        return False
    line_end = text.find("\n", index)
    if line_end == -1:
        line_end = len(text)
    line = text[index:line_end].lstrip()
    if not re.match(r"(?:open|set_option)\b", line):
        return False
    if re.search(r"\bin\b", line) is None:
        return False
    return not (
        _SCOPED_COMMAND_PAYLOAD_RE.search(line)
        and _declaration_body_has_prior_code(text, proof_body_start, index)
    )


def _declaration_body_has_prior_code(
    text: str,
    body_start: int | None,
    boundary_start: int,
) -> bool:
    if body_start is None:
        return False
    boundary_line_start = text.rfind("\n", 0, boundary_start) + 1
    if boundary_line_start <= body_start:
        return False
    return bool(text[body_start:boundary_line_start].strip())


def _is_scoped_expression_header_boundary(
    text: str,
    boundary_start: int,
) -> bool:
    line_end = text.find("\n", boundary_start)
    if line_end == -1:
        line_end = len(text)
    line = text[boundary_start:line_end].lstrip()
    if not re.match(r"(?:open|set_option)\b", line):
        return False
    if re.search(r"\bin\b", line) is None:
        return False
    return _SCOPED_COMMAND_PAYLOAD_RE.search(line) is None


def _match_tactic_proof_by_prefix(text: str) -> re.Match[str] | None:
    return _BY_LINE_RE.match(text) or _SCOPED_BY_RE.match(text)


def _find_declaration_body_start(text: str) -> int | None:
    depth = 0
    local_assignment_pending = False
    skip_until_index: int | None = None
    skip_min_indent: int | None = None
    skip_min_start_index: int | None = None
    opener_to_closer = {"(": ")", "[": "]", "{": "}"}
    closers = set(opener_to_closer.values())

    for index, char in enumerate(text):
        if skip_until_index is not None and index >= skip_until_index:
            skip_until_index = None
        skipping_by_indent = False
        if (
            skip_min_indent is not None
            and skip_min_start_index is not None
            and index >= skip_min_start_index
        ):
            if (
                not _line_is_blank_at(text, index)
                and _line_indent_at(text, index) < skip_min_indent
            ):
                skip_min_indent = None
                skip_min_start_index = None
            else:
                skipping_by_indent = True
        skipping_local_binding_body = skip_until_index is not None or skipping_by_indent

        if text.startswith(":=", index) and depth == 0:
            if skipping_local_binding_body:
                continue
            proof_candidate = text[index + 2 :]
            if local_assignment_pending:
                skip_until_index = _find_next_top_level_semicolon_on_line(
                    text,
                    index + 2,
                )
                by_match = _match_tactic_proof_by_prefix(proof_candidate)
                if by_match:
                    after_by_index = index + 2 + by_match.end()
                    if _line_has_code_after(text, after_by_index):
                        line_end = text.find("\n", after_by_index)
                        if line_end != -1 and skip_until_index is None:
                            skip_until_index = line_end
                    else:
                        skip_min_indent = _next_nonblank_line_indent(
                            text,
                            after_by_index,
                        )
                        next_line_index = text.find("\n", after_by_index)
                        skip_min_start_index = (
                            next_line_index + 1 if next_line_index != -1 else None
                        )
                local_assignment_pending = False
                continue

            return index + 2
        if (
            depth == 0
            and not skipping_local_binding_body
            and _TERM_LOCAL_BINDING_RE.match(text, index)
        ):
            local_assignment_pending = True
        if char in opener_to_closer:
            depth += 1
        elif char in closers and depth > 0:
            depth -= 1

    return None


def _is_scoped_proof_prefix_boundary(
    text: str,
    boundary_start: int,
    proof_body_start: int,
) -> bool:
    prefix = text[boundary_start:proof_body_start]
    match = _SCOPED_BY_RE.match(prefix)
    return match is not None and match.end() == len(prefix)


def _find_tactic_proof_start(text: str) -> int | None:
    depth = 0
    local_assignment_pending = False
    skip_until_index: int | None = None
    skip_min_indent: int | None = None
    skip_min_start_index: int | None = None
    opener_to_closer = {"(": ")", "[": "]", "{": "}"}
    closers = set(opener_to_closer.values())

    for index, char in enumerate(text):
        if skip_until_index is not None and index >= skip_until_index:
            skip_until_index = None
        skipping_by_indent = False
        if (
            skip_min_indent is not None
            and skip_min_start_index is not None
            and index >= skip_min_start_index
        ):
            if (
                not _line_is_blank_at(text, index)
                and _line_indent_at(text, index) < skip_min_indent
            ):
                skip_min_indent = None
                skip_min_start_index = None
            else:
                skipping_by_indent = True
        skipping_local_binding_body = skip_until_index is not None or skipping_by_indent

        if text.startswith(":=", index) and depth == 0:
            if skipping_local_binding_body:
                continue
            proof_candidate = text[index + 2 :]
            if local_assignment_pending:
                skip_until_index = _find_next_top_level_semicolon_on_line(
                    text,
                    index + 2,
                )
                by_match = _match_tactic_proof_by_prefix(proof_candidate)
                if by_match:
                    after_by_index = index + 2 + by_match.end()
                    if _line_has_code_after(text, after_by_index):
                        line_end = text.find("\n", after_by_index)
                        if line_end != -1 and skip_until_index is None:
                            skip_until_index = line_end
                    else:
                        skip_min_indent = _next_nonblank_line_indent(
                            text,
                            after_by_index,
                        )
                        next_line_index = text.find("\n", after_by_index)
                        skip_min_start_index = (
                            next_line_index + 1 if next_line_index != -1 else None
                        )
                local_assignment_pending = False
                continue

            by_match = _match_tactic_proof_by_prefix(proof_candidate)
            if by_match:
                return index + 2 + by_match.end()
            return None
        if (
            depth == 0
            and not skipping_local_binding_body
            and _TERM_LOCAL_BINDING_RE.match(text, index)
        ):
            local_assignment_pending = True
        if char in opener_to_closer:
            depth += 1
        elif char in closers and depth > 0:
            depth -= 1

    return None


def _extract_tactic_contexts(searchable_text: str, tactic_text: str) -> str:
    """Return theorem/lemma proof text that starts at `:= by`."""
    contexts: list[str] = []
    boundary_starts = [
        match.start()
        for match in _TOP_LEVEL_COMMAND_RE.finditer(searchable_text)
    ]

    for decl_start, _, name_end, _ in iter_lean_declaration_names(searchable_text, _THEOREM_START_RE):
        declaration_indent = _line_indent_at(searchable_text, decl_start)
        proof_probe = tactic_text[name_end:]
        proof_start = _find_tactic_proof_start(proof_probe)
        if proof_start is None:
            continue
        proof_body_start = name_end + proof_start
        if any(
            start < proof_body_start
            and not _is_scoped_expression_header_boundary(searchable_text, start)
            and not _is_scoped_proof_prefix_boundary(
                searchable_text,
                start,
                proof_body_start,
            )
            for start in boundary_starts
            if start > decl_start
        ):
            continue
        candidate_boundary_starts = [
            start
            for start in boundary_starts
            if start > proof_body_start
        ]
        end = next(
            (
                start
                for start in candidate_boundary_starts
                if not _is_scoped_in_command_line(
                    searchable_text,
                    start,
                    declaration_indent,
                    proof_body_start,
                )
            ),
            len(searchable_text),
        )
        declaration = tactic_text[name_end:end]

        proof_start = _find_tactic_proof_start(declaration)
        if proof_start is None:
            continue

        contexts.append(declaration[proof_start:])

    return "\n".join(contexts)


def _extract_imports(searchable_text: str) -> list[str]:
    imports: list[str] = []
    for match in _IMPORT_RE.finditer(searchable_text):
        modules = [module for module in match.group(1).split() if module]
        while modules and modules[0] in _IMPORT_TAIL_MODIFIERS:
            modules.pop(0)
        imports.extend(modules)
    return imports


def analyze_file(path: Path) -> dict:
    """Compute statistics for a Lean file."""
    text = path.read_text(encoding="utf-8")
    searchable_text = mask_lean_comments_and_strings(text)
    identifier_masked_text = mask_lean_escaped_identifiers(searchable_text)
    lines = text.splitlines()

    theorems = [
        name
        for _, _, _, name in iter_lean_declaration_names(searchable_text, _THEOREM_START_RE)
    ]
    defs = [
        name
        for _, _, _, name in iter_lean_declaration_names(searchable_text, _DEF_START_RE)
    ]
    imports = _extract_imports(searchable_text)

    # Tactic frequency
    tactic_counts: dict[str, int] = {}
    proof_text = _extract_tactic_contexts(searchable_text, identifier_masked_text)
    for match in _TACTIC_RE.finditer(proof_text):
        tac = match.group(1)
        tactic_counts[tac] = tactic_counts.get(tac, 0) + 1

    # Sort by frequency
    sorted_tactics = sorted(tactic_counts.items(), key=lambda x: -x[1])

    has_sorry = any(match.group(1) == "sorry" for match in re.finditer(_PLACEHOLDER_RE, identifier_masked_text))
    has_admit = any(match.group(1) == "admit" for match in re.finditer(_PLACEHOLDER_RE, identifier_masked_text))

    return {
        "file": str(path),
        "lines": len(lines),
        "non_blank_lines": len([l for l in lines if l.strip()]),
        "theorems": theorems,
        "theorem_count": len(theorems),
        "definitions": defs,
        "imports": imports,
        "has_sorry": has_sorry,
        "has_admit": has_admit,
        "status": (
            "unresolved_placeholders"
            if (has_sorry or has_admit)
            else "verification_required"
        ),
        "certified": False,
        "tactic_frequency": dict(sorted_tactics),
        "unique_tactics": len(tactic_counts),
        "total_tactic_calls": sum(tactic_counts.values()),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 tools/proof_stats.py <lean_file>", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        return 1
    if not path.is_file() or path.suffix.lower() != ".lean":
        print(f"Error: {path} is not a .lean file", file=sys.stderr)
        return 1

    try:
        result = analyze_file(path)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: failed to read {path}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
