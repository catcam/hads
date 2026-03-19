#!/usr/bin/env python3
"""Parse Markdown documents that follow the HADS convention.

The parser focuses on the parts of HADS that matter for AI-friendly extraction:

* the document header (`# Title` and `**Version X.Y.Z**`)
* the AI manifest
* tagged blocks such as `[SPEC]`, `[NOTE]`, `[BUG]`, and `[?]`

`parse()` is the main entry point. It returns a `HADSDocument` with block
metadata, while helper functions make it easy to filter blocks, serialize the
result, or rebuild Markdown for a subset of block types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys


_VERSION_PATTERN = re.compile(r"\*\*Version\s+(\d+\.\d+\.\d+)\*\*")
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_BLOCK_TAG_PATTERN = re.compile(r"^\*\*(\[(?:SPEC|NOTE|BUG|\?)\])(?:\s+(.+?))?\*\*$")
_LOOSE_TAG_PATTERN = re.compile(r"^\s*(?:\*\*)?\[(?:SPEC|NOTE|BUG|\?)\]")
_THEMATIC_BREAK_PATTERN = re.compile(r"^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$")

_TAG_TO_TYPE = {
    "[SPEC]": "SPEC",
    "[NOTE]": "NOTE",
    "[BUG]": "BUG",
    "[?]": "QUESTION",
}
_TYPE_TO_TAG = {
    "SPEC": "**[SPEC]**",
    "NOTE": "**[NOTE]**",
    "BUG": "**[BUG]**",
    "QUESTION": "**[?]**",
}


class HADSParseError(ValueError):
    """Raised when a Markdown document does not satisfy HADS parsing rules."""

    def __init__(self, message: str, *, line: int | None = None) -> None:
        prefix = f"Line {line}: " if line is not None else ""
        super().__init__(prefix + message)
        self.line = line
        self.message = message


@dataclass(slots=True, frozen=True)
class _Heading:
    """Internal representation of a heading path segment."""

    level: int
    text: str
    raw: str


@dataclass(slots=True)
class HADSBlock:
    """A parsed HADS block or an implicit NOTE-style content block."""

    type: str
    content: str
    section: str
    line_start: int
    line_end: int
    _tag_line: str | None = field(default=None, repr=False, compare=False)
    _section_path: tuple[_Heading, ...] = field(default_factory=tuple, repr=False, compare=False)
    _implicit: bool = field(default=False, repr=False, compare=False)


@dataclass(slots=True)
class HADSDocument:
    """A parsed HADS document."""

    name: str
    description: str
    version: str
    manifest: str
    blocks: list[HADSBlock]
    _source_text: str = field(default="", repr=False, compare=False)
    _source_lines: tuple[str, ...] = field(default_factory=tuple, repr=False, compare=False)
    _title_line: str = field(default="", repr=False, compare=False)
    _version_line: str = field(default="", repr=False, compare=False)
    _manifest_heading: str = field(default="## AI READING INSTRUCTION", repr=False, compare=False)


def parse(text: str) -> HADSDocument:
    """Parse a HADS document from Markdown text.

    Raises:
        HADSParseError: If the document is missing required structure or
            contains malformed block markers.
    """

    lines = text.splitlines()
    if lines and lines[0].startswith("\ufeff"):
        lines[0] = lines[0].lstrip("\ufeff")

    title_index = _find_first_nonblank_index(lines)
    if title_index is None:
        raise HADSParseError("document is empty")

    title_heading = _match_heading(lines[title_index])
    if not title_heading or title_heading.level != 1:
        raise HADSParseError("missing H1 title at the start of the document", line=title_index + 1)

    version_index, version = _find_version(lines, start=title_index + 1)
    if version_index is None or version is None:
        raise HADSParseError("missing version declaration near the top of the document")

    manifest_index = _find_manifest_heading(lines)
    if manifest_index is None:
        raise HADSParseError("missing AI manifest heading")

    for idx in range(title_index + 1, manifest_index):
        heading = _match_heading(lines[idx])
        if heading and heading.level == 2:
            raise HADSParseError(
                "manifest must appear before the first content section",
                line=idx + 1,
            )

    next_h2_after_manifest = _find_next_h2(lines, manifest_index + 1)
    manifest_raw = lines[manifest_index + 1 : next_h2_after_manifest]
    manifest_lines = _trim_outer_spacing_and_breaks(manifest_raw)
    if not manifest_lines:
        raise HADSParseError("AI manifest is present but empty", line=manifest_index + 1)

    description_lines = _trim_outer_spacing_and_breaks(lines[version_index + 1 : manifest_index])
    blocks = _parse_blocks(lines, start=next_h2_after_manifest)

    return HADSDocument(
        name=title_heading.text,
        description="\n".join(description_lines),
        version=version,
        manifest="\n".join(manifest_lines),
        blocks=blocks,
        _source_text=text,
        _source_lines=tuple(lines),
        _title_line=lines[title_index],
        _version_line=lines[version_index],
        _manifest_heading=lines[manifest_index],
    )


def parse_file(path: str) -> HADSDocument:
    """Parse a HADS document from a file path."""

    text = Path(path).read_text(encoding="utf-8")
    return parse(text)


def filter_blocks(doc: HADSDocument, block_type: str) -> list[HADSBlock]:
    """Return blocks whose normalized type matches `block_type`."""

    wanted = _normalize_block_type(block_type)
    return [block for block in doc.blocks if block.type == wanted]


def get_manifest(doc: HADSDocument) -> str:
    """Return the manifest text stored in a parsed document."""

    return doc.manifest


def to_markdown(doc: HADSDocument, include_types: list[str] | tuple[str, ...] | set[str] | None = None) -> str:
    """Reconstruct Markdown from a parsed document.

    When `include_types` is omitted, the original source is returned. When a
    block-type filter is provided, only matching blocks are emitted, together
    with the headings that contain them.
    """

    if include_types is None:
        return doc._source_text or "\n".join(doc._source_lines)

    allowed = {_normalize_block_type(block_type) for block_type in include_types}
    selected = [block for block in doc.blocks if block.type in allowed]

    lines: list[str] = [doc._title_line or f"# {doc.name}", doc._version_line or f"**Version {doc.version}**"]

    if doc.description:
        lines.extend(["", *doc.description.splitlines()])

    lines.extend(["", "---", "", doc._manifest_heading or "## AI READING INSTRUCTION", ""])
    lines.extend(doc.manifest.splitlines())

    if not selected:
        return _join_lines(lines)

    previous_path: tuple[_Heading, ...] = ()
    for block in selected:
        path = block._section_path
        if previous_path and path and previous_path[0] != path[0]:
            lines.extend(["", "---"])

        common = _common_heading_prefix(previous_path, path)
        for heading in path[common:]:
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(heading.raw)
            lines.append("")

        if lines and lines[-1] != "":
            lines.append("")

        if block._implicit:
            lines.extend(block.content.splitlines())
        else:
            lines.append(block._tag_line or _TYPE_TO_TAG[block.type])
            lines.extend(block.content.splitlines())

        previous_path = path

    return _join_lines(lines)


def to_dict(doc: HADSDocument) -> dict:
    """Convert a parsed document into a JSON-serializable dictionary."""

    return {
        "name": doc.name,
        "description": doc.description,
        "version": doc.version,
        "manifest": doc.manifest,
        "blocks": [
            {
                "type": block.type,
                "content": block.content,
                "section": block.section,
                "line_start": block.line_start,
                "line_end": block.line_end,
            }
            for block in doc.blocks
        ],
    }


def _parse_blocks(lines: list[str], start: int) -> list[HADSBlock]:
    """Parse tagged and untagged content blocks after the manifest."""

    blocks: list[HADSBlock] = []
    section_path: tuple[_Heading, ...] = ()
    i = start

    while i < len(lines):
        line = lines[i]
        heading = _match_heading(line)

        if heading and heading.level >= 2:
            section_path = _update_section_path(section_path, heading)
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        if _is_thematic_break(line):
            i += 1
            continue

        tag_info = _parse_tag_line(line)
        if tag_info:
            if not section_path:
                raise HADSParseError("block appears before any section heading", line=i + 1)
            block, i = _consume_explicit_block(lines, i, section_path, tag_info)
            blocks.append(block)
            continue

        if _looks_like_malformed_tag(line):
            raise HADSParseError("malformed block marker", line=i + 1)

        if not section_path:
            raise HADSParseError(
                "content appears before the first section heading after the manifest",
                line=i + 1,
            )

        block, i = _consume_implicit_block(lines, i, section_path)
        if block is not None:
            blocks.append(block)

    return blocks


def _consume_explicit_block(
    lines: list[str],
    start: int,
    section_path: tuple[_Heading, ...],
    tag_info: tuple[str, str],
) -> tuple[HADSBlock, int]:
    """Consume a tagged block starting at `start`."""

    block_type, tag_line = tag_info
    next_index = start + 1

    if next_index >= len(lines) or not lines[next_index].strip():
        raise HADSParseError(
            "block tag must be immediately followed by content",
            line=start + 1,
        )

    content_lines: list[str] = []
    in_fence = False
    i = next_index
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not in_fence:
            heading = _match_heading(line)
            if heading and heading.level >= 2:
                break
            if _is_thematic_break(line):
                break
            if _parse_tag_line(line):
                break
            if _looks_like_malformed_tag(line):
                raise HADSParseError("malformed block marker inside block content", line=i + 1)

        content_lines.append(line)
        if stripped.startswith("```"):
            in_fence = not in_fence
        i += 1

    if in_fence:
        raise HADSParseError("unterminated fenced code block inside block content", line=start + 1)

    trimmed_lines, line_end = _trim_block_content(content_lines, start_line=next_index + 1)
    if not trimmed_lines:
        raise HADSParseError("block content is empty", line=start + 1)

    block = HADSBlock(
        type=block_type,
        content="\n".join(trimmed_lines),
        section=_section_name(section_path),
        line_start=start + 1,
        line_end=line_end,
        _tag_line=tag_line,
        _section_path=section_path,
        _implicit=False,
    )

    if block_type == "BUG":
        _validate_bug_block(block)

    return block, i


def _consume_implicit_block(
    lines: list[str],
    start: int,
    section_path: tuple[_Heading, ...],
) -> tuple[HADSBlock | None, int]:
    """Consume untagged content and treat it as an implicit NOTE block."""

    content_lines: list[str] = []
    in_fence = False
    i = start

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not in_fence:
            heading = _match_heading(line)
            if heading and heading.level >= 2:
                break
            if _is_thematic_break(line):
                break
            if _parse_tag_line(line):
                break
            if _looks_like_malformed_tag(line):
                raise HADSParseError("malformed block marker", line=i + 1)

        content_lines.append(line)
        if stripped.startswith("```"):
            in_fence = not in_fence
        i += 1

    if in_fence:
        raise HADSParseError("unterminated fenced code block inside section content", line=start + 1)

    trimmed_lines, line_end = _trim_block_content(content_lines, start_line=start + 1)
    if not trimmed_lines:
        return None, i

    return (
        HADSBlock(
            type="NOTE",
            content="\n".join(trimmed_lines),
            section=_section_name(section_path),
            line_start=start + 1 + _leading_blank_count(content_lines),
            line_end=line_end,
            _section_path=section_path,
            _implicit=True,
        ),
        i,
    )


def _validate_bug_block(block: HADSBlock) -> None:
    """Validate the minimum required fields for a BUG block."""

    lowered = block.content.lower()
    missing: list[str] = []
    if "symptom:" not in lowered:
        missing.append("symptom")
    if "fix:" not in lowered:
        missing.append("fix")
    if missing:
        raise HADSParseError(
            f"[BUG] block missing required field(s): {', '.join(missing)}",
            line=block.line_start,
        )


def _normalize_block_type(block_type: str) -> str:
    """Normalize a block type name or tag into canonical uppercase form."""

    value = block_type.strip().upper()
    if value in _TYPE_TO_TAG:
        return value
    tag_to_type = {
        "[SPEC]": "SPEC",
        "[NOTE]": "NOTE",
        "[BUG]": "BUG",
        "[?]": "QUESTION",
        "?": "QUESTION",
    }
    if value in tag_to_type:
        return tag_to_type[value]
    raise ValueError(f"unknown HADS block type: {block_type}")


def _find_first_nonblank_index(lines: list[str]) -> int | None:
    """Return the first non-blank line index."""

    for index, line in enumerate(lines):
        if line.strip():
            return index
    return None


def _find_version(lines: list[str], start: int) -> tuple[int | None, str | None]:
    """Find the version line before the manifest heading."""

    for index in range(start, min(len(lines), start + 20)):
        match = _VERSION_PATTERN.search(lines[index])
        if match:
            return index, match.group(1)
    return None, None


def _find_manifest_heading(lines: list[str]) -> int | None:
    """Find the H2 heading that introduces the AI manifest."""

    for index, line in enumerate(lines):
        heading = _match_heading(line)
        if not heading or heading.level != 2:
            continue
        lowered = heading.text.lower()
        if "ai reading" in lowered or "reading instruction" in lowered:
            return index
    return None


def _find_next_h2(lines: list[str], start: int) -> int:
    """Find the next H2 heading, returning EOF when none exists."""

    for index in range(start, len(lines)):
        heading = _match_heading(lines[index])
        if heading and heading.level == 2:
            return index
    return len(lines)


def _match_heading(line: str) -> _Heading | None:
    """Parse a Markdown heading line."""

    match = _HEADING_PATTERN.match(line.strip())
    if not match:
        return None
    hashes, text = match.groups()
    return _Heading(level=len(hashes), text=text, raw=line.strip())


def _parse_tag_line(line: str) -> tuple[str, str] | None:
    """Return the normalized type and raw tag line if `line` is a HADS tag."""

    stripped = line.strip()
    match = _BLOCK_TAG_PATTERN.match(stripped)
    if match:
        return _TAG_TO_TYPE[match.group(1)], stripped

    return None


def _looks_like_malformed_tag(line: str) -> bool:
    """Return True when a line appears to start a tag but is malformed."""

    stripped = line.strip()
    if not stripped:
        return False
    if _parse_tag_line(line):
        return False
    return bool(_LOOSE_TAG_PATTERN.match(stripped))


def _trim_outer_spacing_and_breaks(lines: list[str]) -> list[str]:
    """Trim blank lines and thematic breaks around a region."""

    start = 0
    end = len(lines)
    while start < end and (not lines[start].strip() or _is_thematic_break(lines[start])):
        start += 1
    while end > start and (not lines[end - 1].strip() or _is_thematic_break(lines[end - 1])):
        end -= 1
    return lines[start:end]


def _trim_block_content(lines: list[str], start_line: int) -> tuple[list[str], int]:
    """Trim blank lines from block boundaries and return the last content line."""

    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1

    if start == end:
        return [], start_line - 1

    trimmed = lines[start:end]
    line_end = start_line + end - 1
    return trimmed, line_end


def _leading_blank_count(lines: list[str]) -> int:
    """Count blank lines at the beginning of a content region."""

    count = 0
    for line in lines:
        if line.strip():
            break
        count += 1
    return count


def _update_section_path(path: tuple[_Heading, ...], heading: _Heading) -> tuple[_Heading, ...]:
    """Update the current heading stack with a new heading."""

    keep = 0
    for existing in path:
        if existing.level < heading.level:
            keep += 1
            continue
        break
    return path[:keep] + (heading,)


def _section_name(section_path: tuple[_Heading, ...]) -> str:
    """Convert a heading path into a user-facing section label."""

    return " > ".join(heading.text for heading in section_path)


def _common_heading_prefix(left: tuple[_Heading, ...], right: tuple[_Heading, ...]) -> int:
    """Return the number of shared heading path elements."""

    length = min(len(left), len(right))
    common = 0
    for index in range(length):
        if left[index] != right[index]:
            break
        common += 1
    return common


def _is_thematic_break(line: str) -> bool:
    """Return True when the line is a Markdown thematic break."""

    return bool(_THEMATIC_BREAK_PATTERN.match(line))


def _join_lines(lines: list[str]) -> str:
    """Join output lines while trimming trailing blank lines."""

    trimmed = list(lines)
    while trimmed and trimmed[-1] == "":
        trimmed.pop()
    return "\n".join(trimmed)


def _main(argv: list[str]) -> int:
    """CLI entry point used by the module's `__main__` block."""

    if len(argv) < 2:
        print(f"Usage: python {Path(argv[0]).name} <path>", file=sys.stderr)
        return 1

    try:
        document = parse_file(argv[1])
    except (OSError, HADSParseError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(to_dict(document), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
