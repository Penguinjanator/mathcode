from __future__ import annotations

import re


def _is_ident_continue(ch: str | None) -> bool:
    return ch is not None and (ch == "_" or ch == "'" or ch == "?" or ch == "!" or ch.isalnum())


LEAN_IDENT_BOUNDARY = r"(?<![\w'?!«\.])!*(sorry|admit)(?![\w'?!»\.])"
LEAN_RECOVERY_IDENT_BOUNDARY = r"(?<![\w'?!«\.])!*(sorry|admit)(?![\w'?!\.])"
LEAN_DECL_NAME_DELIMITERS = {":", "(", "{", "[", "⦃"}


def _find_same_line_escaped_identifier_close(text: str, start: int) -> int | None:
    end = text.find("»", start + 1)
    if end == -1:
        return None
    newline = text.find("\n", start + 1, end)
    carriage_return = text.find("\r", start + 1, end)
    return None if newline != -1 or carriage_return != -1 else end


def _lean_decl_name_component_end(text: str, start: int) -> int | None:
    if (
        start >= len(text)
        or text[start].isspace()
        or text[start] in LEAN_DECL_NAME_DELIMITERS
    ):
        return None
    if text[start] == "«":
        end = _find_same_line_escaped_identifier_close(text, start)
        return end + 1 if end is not None else None

    cursor = start
    while cursor < len(text):
        char = text[cursor]
        if char == "." or char.isspace() or char in LEAN_DECL_NAME_DELIMITERS:
            break
        cursor += 1
    return cursor if cursor > start else None


def lean_decl_name_end(text: str, start: int) -> int | None:
    """Return the end offset for a Lean declaration name starting at `start`."""
    cursor = _lean_decl_name_component_end(text, start)
    if cursor is None:
        return None

    while cursor < len(text) and text[cursor] == ".":
        next_cursor = _lean_decl_name_component_end(text, cursor + 1)
        if next_cursor is None:
            break
        cursor = next_cursor

    return cursor


def iter_lean_declaration_names(
    searchable_text: str,
    start_re: re.Pattern[str],
) -> list[tuple[int, int, int, str]]:
    """Return declaration start/name spans for matches of `start_re`."""
    declarations: list[tuple[int, int, int, str]] = []
    for match in start_re.finditer(searchable_text):
        keyword_start = match.end()
        while keyword_start > match.start() and searchable_text[keyword_start - 1].isalpha():
            keyword_start -= 1
        cursor = match.end()
        if cursor >= len(searchable_text) or not searchable_text[cursor].isspace():
            continue
        while cursor < len(searchable_text) and searchable_text[cursor].isspace():
            cursor += 1
        name_end = lean_decl_name_end(searchable_text, cursor)
        if name_end is not None:
            declarations.append((
                keyword_start,
                cursor,
                name_end,
                searchable_text[cursor:name_end],
            ))
    return declarations


def _is_literal_prefix_boundary(text: str, prefix_index: int) -> bool:
    before = text[prefix_index - 1] if prefix_index > 0 else None
    if before == "!":
        bang_index = prefix_index - 1
        while bang_index > 0 and text[bang_index - 1] == "!":
            bang_index -= 1
        before = text[bang_index - 1] if bang_index > 0 else None
    return before is None or (not _is_ident_continue(before) and before != ".")


def _mask_range(chars: list[str], start: int, end: int) -> None:
    for j in range(start, end + 1):
        if chars[j] != "\n":
            chars[j] = " "


_LEAN_RECOVERY_COMMAND_RE = re.compile(
    r"^\s*(?:"
    r"#\w+"
    r"|(?:import|namespace|section|end|open|variable|variables|universe|universes|"
    r"set_option|attribute|export|include|omit)\b"
    r"|(?:@[^\n]*\]\s*)*"
    r"(?:(?:private|protected|noncomputable|local|scoped|unsafe|partial|nonrec)\s+)*"
    r"(?:theorem|lemma|example|def|instance|abbrev|opaque|axiom|constant|postulate|"
    r"inductive|structure|class|macro|macro_rules|syntax|elab|elab_rules|notation|"
    r"infix|infixl|infixr|prefix|postfix|declare_syntax_cat|run_cmd|initialize|"
    r"builtin_initialize|simproc|builtin_simproc|dsimproc|builtin_dsimproc|"
    r"cbv_simproc|builtin_cbv_simproc)\b"
    r")",
    re.MULTILINE,
)
_PROOF_PLACEHOLDER_HINT_RE = re.compile(
    r"(?:^|[^\w'?!\.«])(?:by|exact|have|let|show|suffices)\b.*"
    + LEAN_RECOVERY_IDENT_BOUNDARY
)
_BARE_PLACEHOLDER_RE = re.compile(r"^\s*" + LEAN_RECOVERY_IDENT_BOUNDARY)


def _next_line_start(text: str, index: int) -> int | None:
    line_end = _line_break_or_end(text, index)
    if line_end >= len(text):
        return None
    if text[line_end : line_end + 2] == "\r\n":
        return line_end + 2
    return line_end + 1


def _escaped_identifier_open_is_maskable(text: str, index: int) -> bool:
    if text[index] != "«":
        return False
    return not (
        index > 0
        and index + 1 < len(text)
        and text[index - 1] == "'"
        and text[index + 1] == "'"
    )


def _line_is_proof_placeholder_recovery_line(text: str, start: int, end: int) -> bool:
    line = text[start:end]
    if line == "":
        return False
    if _PROOF_PLACEHOLDER_HINT_RE.search(line) is not None:
        return True
    return line[0].isspace() and _BARE_PLACEHOLDER_RE.search(line) is not None


def _lean_escaped_identifier_end(text: str, index: int) -> int | None:
    if not _escaped_identifier_open_is_maskable(text, index):
        return None

    same_line_end = _find_same_line_escaped_identifier_close(text, index)
    if same_line_end is not None:
        return same_line_end

    line_start = _next_line_start(text, index)
    while line_start is not None and line_start < len(text):
        line_end = _line_break_or_end(text, line_start)
        proof_placeholder_line = _line_is_proof_placeholder_recovery_line(
            text,
            line_start,
            line_end,
        )
        if proof_placeholder_line:
            return None
        close_index = text.find("»", line_start, line_end)
        if close_index != -1:
            return close_index
        if _LEAN_RECOVERY_COMMAND_RE.match(
            text,
            line_start,
            line_end,
        ):
            return None
        line_start = _next_line_start(text, line_end)

    return None


def _lean_escaped_identifier_proof_recovery_close(text: str, index: int) -> int | None:
    if (
        not _escaped_identifier_open_is_maskable(text, index)
        or _find_same_line_escaped_identifier_close(text, index) is not None
    ):
        return None

    line_start = _next_line_start(text, index)
    while line_start is not None and line_start < len(text):
        line_end = _line_break_or_end(text, line_start)
        if _line_is_proof_placeholder_recovery_line(text, line_start, line_end):
            close_index = text.find("»", line_start, line_end)
            return close_index if close_index != -1 else None
        if text.find("»", line_start, line_end) != -1 or _LEAN_RECOVERY_COMMAND_RE.match(
            text,
            line_start,
            line_end,
        ):
            return None
        line_start = _next_line_start(text, line_end)

    return None


def _line_break_or_end(text: str, start: int) -> int:
    line_feed = text.find("\n", start)
    carriage_return = text.find("\r", start)
    candidates = [index for index in (line_feed, carriage_return) if index != -1]
    return min(candidates) if candidates else len(text)


def _malformed_escaped_identifier_line_end(text: str, index: int) -> int | None:
    if text[index] != "«" or _lean_escaped_identifier_end(text, index) is not None:
        return None
    return _line_break_or_end(text, index + 1)


def mask_lean_escaped_identifiers(text: str) -> str:
    """Mask Lean guillemet-escaped identifier spans while preserving shape."""
    chars = list(text)
    i = 0
    while i < len(chars):
        end = _lean_escaped_identifier_end(text, i)
        if end is None:
            recovery_close = _lean_escaped_identifier_proof_recovery_close(text, i)
            if recovery_close is not None:
                chars[recovery_close] = " "
            i += 1
            continue
        _mask_range(chars, i, end)
        i = end + 1
    return "".join(chars)


def _lean_raw_string_end(text: str, index: int) -> int | None | bool:
    if text[index] != "r":
        return False
    quote_index = index + 1
    while quote_index < len(text) and text[quote_index] == "#":
        quote_index += 1
    if quote_index >= len(text) or text[quote_index] != '"':
        return False
    if not _is_literal_prefix_boundary(text, index):
        return None

    hashes = text[index + 1 : quote_index]
    close = '"' + hashes
    close_index = text.find(close, quote_index + 1)
    if close_index == -1:
        return None
    return close_index + len(close) - 1


def _lean_string_end(text: str, quote_index: int) -> int | None:
    i = quote_index + 1
    while i < len(text):
        if text[i] == "\\":
            if i + 1 >= len(text):
                return None
            i += 2
            continue
        if text[i] == '"':
            return i
        i += 1
    return None


def _lean_char_literal_end(text: str, index: int) -> int | None:
    if text[index] != "'":
        return None
    before = text[index - 1] if index > 0 else None
    if _is_ident_continue(before):
        return None
    if index + 1 >= len(text) or text[index + 1] in {"\n", "'"}:
        return None

    if text[index + 1] == "\\":
        cursor = index + 2
        if cursor >= len(text) or text[cursor] == "\n":
            return None
        if text[cursor] == "'":
            return cursor + 1 if cursor + 1 < len(text) and text[cursor + 1] == "'" else None
        max_cursor = min(len(text), index + 16)
        while cursor < max_cursor and text[cursor] != "\n":
            if text[cursor] == "'":
                return cursor if cursor > index + 2 else None
            cursor += 1
        return None

    return index + 2 if index + 2 < len(text) and text[index + 2] == "'" else None


def _lean_block_comment_end(text: str, index: int) -> int | None:
    depth = 1
    i = index + 2
    while i < len(text) - 1:
        pair = text[i : i + 2]
        if pair == "/-":
            depth += 1
            i += 2
            continue
        if pair == "-/":
            depth -= 1
            if depth == 0:
                return i + 1
            i += 2
            continue
        i += 1
    return None


def _is_interpolated_quote_start(text: str, quote_index: int) -> bool:
    if quote_index < 2 or text[quote_index] != '"' or text[quote_index - 1] != "!":
        return False
    prefix = text[quote_index - 2]
    return prefix in {"s", "m", "f"} and _is_literal_prefix_boundary(text, quote_index - 2)


def _lean_interpolation_hole_end(text: str, open_index: int) -> int | None:
    depth = 1
    i = open_index + 1
    while i < len(text):
        escaped_ident_end = _lean_escaped_identifier_end(text, i)
        if escaped_ident_end is not None:
            i = escaped_ident_end + 1
            continue
        malformed_ident_line_end = _malformed_escaped_identifier_line_end(text, i)
        if malformed_ident_line_end is not None:
            i = malformed_ident_line_end
            continue
        pair = text[i : i + 2]
        if pair == "--":
            newline_index = text.find("\n", i + 2)
            if newline_index == -1:
                return None
            i = newline_index + 1
            continue
        if pair == "/-":
            comment_end = _lean_block_comment_end(text, i)
            if comment_end is None:
                return None
            i = comment_end + 1
            continue
        raw_end = _lean_raw_string_end(text, i)
        if raw_end is not False:
            if raw_end is None:
                return None
            i = raw_end + 1
            continue
        if text[i] == '"':
            string_end = _lean_string_end(text, i)
            if string_end is None:
                return None
            i = string_end + 1
            continue
        char_end = _lean_char_literal_end(text, i)
        if char_end is not None:
            i = char_end + 1
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def _mask_interpolated_string(text: str, chars: list[str], quote_index: int) -> int | None | bool:
    if not _is_interpolated_quote_start(text, quote_index):
        return False

    chars[quote_index] = " "
    i = quote_index + 1
    while i < len(chars):
        if text[i] == "\\":
            if i + 1 >= len(chars):
                return None
            chars[i] = " "
            if chars[i + 1] != "\n":
                chars[i + 1] = " "
            i += 2
            continue
        if text[i] == '"':
            chars[i] = " "
            return i
        if text[i] == "{":
            hole_end = _lean_interpolation_hole_end(text, i)
            if hole_end is None:
                return None
            chars[i] = " "
            masked_hole = mask_lean_comments_and_strings(text[i + 1 : hole_end])
            for offset, ch in enumerate(masked_hole):
                chars[i + 1 + offset] = ch
            chars[hole_end] = " "
            i = hole_end + 1
            continue
        if chars[i] != "\n":
            chars[i] = " "
        i += 1
    return None


def mask_lean_comments_and_strings(
    text: str,
    *,
    mask_strings: bool = True,
) -> str:
    """Mask Lean comments/strings with spaces while preserving line structure."""
    chars = list(text)
    i = 0
    n = len(chars)
    block_depth = 0
    in_string = False

    while i < n:
      if in_string:
        if chars[i] == "\\" and i + 1 < n:
          if chars[i] != "\n":
            chars[i] = " "
          if chars[i + 1] != "\n":
            chars[i + 1] = " "
          i += 2
          continue
        if chars[i] == '"':
          chars[i] = " "
          in_string = False
        elif chars[i] != "\n":
          chars[i] = " "
        i += 1
        continue

      if block_depth > 0:
        if i + 1 < n and text[i : i + 2] == "/-":
          chars[i] = " "
          chars[i + 1] = " "
          block_depth += 1
          i += 2
          continue
        if i + 1 < n and text[i : i + 2] == "-/":
          chars[i] = " "
          chars[i + 1] = " "
          block_depth -= 1
          i += 2
          continue
        if chars[i] != "\n":
          chars[i] = " "
          i += 1
          continue

      escaped_ident_end = _lean_escaped_identifier_end(text, i)
      if escaped_ident_end is not None:
        i = escaped_ident_end + 1
        continue
      malformed_ident_line_end = _malformed_escaped_identifier_line_end(text, i)
      if malformed_ident_line_end is not None:
        i = malformed_ident_line_end
        continue

      raw_string_end = _lean_raw_string_end(text, i)
      if raw_string_end is not False:
        if raw_string_end is None:
          i += 1
        else:
          if mask_strings:
            _mask_range(chars, i, raw_string_end)
          i = raw_string_end + 1
        continue

      char_literal_end = _lean_char_literal_end(text, i)
      if char_literal_end is not None:
        if mask_strings:
          _mask_range(chars, i, char_literal_end)
        i = char_literal_end + 1
        continue

      if i + 1 < n and text[i : i + 2] == "--":
        chars[i] = " "
        chars[i + 1] = " "
        i += 2
        while i < n and chars[i] != "\n":
          chars[i] = " "
          i += 1
        continue

      if i + 1 < n and text[i : i + 2] == "/-":
        chars[i] = " "
        chars[i + 1] = " "
        block_depth = 1
        i += 2
        continue

      if mask_strings and chars[i] == '"':
        interpolated_end = _mask_interpolated_string(text, chars, i)
        if interpolated_end is not False:
          if interpolated_end is None:
            chars[i] = " "
            i += 1
          else:
            i = interpolated_end + 1
          continue
        chars[i] = " "
        in_string = True
        i += 1
        continue

      i += 1

    return "".join(chars)
