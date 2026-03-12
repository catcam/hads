#!/usr/bin/env python3
"""
HADS Validator — Human-AI Document Standard v1.0.0
Validates a Markdown file against the HADS specification.

Usage:
    python validate.py <file.md>
    python validate.py <file.md> --verbose

Exit codes:
    0 — valid HADS document
    1 — missing required element (title, version, manifest)
    2 — malformed block tag
    3 — [BUG] block missing required fields
"""

import re
import sys
from pathlib import Path


# ── Constants ──────────────────────────────────────────────────────────────────

VALID_TAGS = {"[SPEC]", "[NOTE]", "[BUG]", "[?]"}
BLOCK_TAG_PATTERN = re.compile(r"^\*\*(\[(?:SPEC|NOTE|BUG|\?)\])\*\*$")
LOOSE_TAG_PATTERN = re.compile(r"\[(?:SPEC|NOTE|BUG|\?)\]")
VERSION_PATTERN = re.compile(r"\*\*Version\s+\d+\.\d+\.\d+\*\*")
MANIFEST_KEYWORDS = ["[SPEC]", "[BUG]", "reading instruction", "ai reading"]


# ── Helpers ────────────────────────────────────────────────────────────────────

def load(path: str) -> list[str]:
    try:
        return Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"ERROR: File is not valid UTF-8: {path}")
        sys.exit(1)


def find_h1(lines: list[str]) -> int | None:
    """Return line index of first H1, or None."""
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            return i
    return None


def find_version(lines: list[str]) -> int | None:
    """Return line index of version declaration, or None."""
    for i, line in enumerate(lines[:20]):  # version should be near top
        if VERSION_PATTERN.search(line):
            return i
    return None


def find_manifest(lines: list[str]) -> int | None:
    """Return line index where AI manifest starts, or None."""
    for i, line in enumerate(lines):
        lower = line.lower()
        if any(kw in lower for kw in MANIFEST_KEYWORDS):
            return i
    return None


def find_first_content_section(lines: list[str]) -> int | None:
    """Return line index of first H2 that is NOT the manifest."""
    in_manifest = False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            lower = line.lower()
            if "ai reading" in lower or "reading instruction" in lower:
                in_manifest = True
                continue
            if in_manifest:
                in_manifest = False
            return i
    return None


def find_bug_blocks(lines: list[str]) -> list[dict]:
    """Return list of BUG blocks with their content."""
    bugs = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = BLOCK_TAG_PATTERN.match(line)
        if m and m.group(1) == "[BUG]":
            block = {"line": i + 1, "content": []}
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if BLOCK_TAG_PATTERN.match(next_line) or next_line.startswith("## ") or next_line.startswith("### "):
                    break
                block["content"].append(lines[j])
                j += 1
            bugs.append(block)
            i = j
        else:
            i += 1
    return bugs


def check_loose_tags(lines: list[str]) -> list[tuple[int, str]]:
    """Find tag-like patterns that are not properly formatted."""
    issues = []
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Track fenced code blocks
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Skip properly formatted tags
        if BLOCK_TAG_PATTERN.match(stripped):
            continue
        # Look for loose tag usage — only flag if tag appears to be used as a block marker
        # (at start of line, possibly with leading **)
        # Ignore tags used as references in prose
        stripped_check = stripped.lstrip("*").strip()
        matches = LOOSE_TAG_PATTERN.findall(stripped_check)
        for match in matches:
            # Allow tags in inline code (backtick wrapped)
            if "`" + match + "`" in line:
                continue
            # Only flag if tag is at the very start of the stripped line (likely meant as block tag)
            if not stripped_check.startswith(match):
                continue
            # Allow **[TAG] title text** — valid titled block tag
            if stripped.startswith("**" + match):
                continue
            # It starts with the tag but is not properly bolded
            issues.append((i + 1, f"Possible unformatted tag '{match}' — should be **{match}**"))
    return issues


def check_bug_content(bug: dict) -> list[str]:
    """Check that a [BUG] block contains required fields."""
    content = " ".join(bug["content"]).lower()
    missing = []
    if "symptom" not in content and "symptom:" not in content:
        missing.append("symptom")
    if "fix" not in content:
        missing.append("fix")
    return missing


# ── Main validation ────────────────────────────────────────────────────────────

def validate(path: str, verbose: bool = False) -> int:
    lines = load(path)
    errors = []
    warnings = []
    passed = []

    # ── Check 1: H1 title ─────────────────────────────────────────────────────
    h1_line = find_h1(lines)
    if h1_line is None:
        errors.append("MISSING H1 title — document must begin with a '# Title' heading")
    else:
        passed.append(f"H1 title found (line {h1_line + 1}): {lines[h1_line][:60]}")

    # ── Check 2: Version declaration ──────────────────────────────────────────
    ver_line = find_version(lines)
    if ver_line is None:
        errors.append("MISSING version — add '**Version X.Y.Z**' near the top of the document")
    else:
        passed.append(f"Version found (line {ver_line + 1}): {lines[ver_line].strip()[:60]}")

    # ── Check 3: AI manifest ──────────────────────────────────────────────────
    manifest_line = find_manifest(lines)
    if manifest_line is None:
        errors.append("MISSING AI manifest — add an 'AI READING INSTRUCTION' section before content")
    else:
        passed.append(f"AI manifest found (line {manifest_line + 1})")

        # Check manifest appears before first content section
        content_line = find_first_content_section(lines)
        if content_line is not None and manifest_line > content_line:
            errors.append(
                f"AI manifest (line {manifest_line + 1}) appears AFTER first content section "
                f"(line {content_line + 1}) — manifest must come first"
            )

    # ── Check 4: [BUG] block fields ───────────────────────────────────────────
    bugs = find_bug_blocks(lines)
    for bug in bugs:
        missing = check_bug_content(bug)
        if missing:
            errors.append(
                f"[BUG] block at line {bug['line']} is missing required field(s): "
                + ", ".join(missing)
            )
        else:
            passed.append(f"[BUG] block at line {bug['line']} — OK")

    # ── Check 5: Loose / unformatted tags (warnings only) ────────────────────
    loose = check_loose_tags(lines)
    for line_num, msg in loose:
        warnings.append(f"Line {line_num}: {msg}")

    # ── Check 6: Skip nesting check — consecutive blocks in same section are valid HADS ──

    # ── Report ────────────────────────────────────────────────────────────────
    print(f"\nHADS Validator — {path}")
    print("─" * 60)

    if verbose and passed:
        print("\n✓ Passed checks:")
        for p in passed:
            print(f"  {p}")

    if warnings:
        print(f"\n⚠ Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print(f"\n✗ Errors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        print(f"\nResult: INVALID ({len(errors)} error(s))\n")
    else:
        print(f"\nResult: VALID HADS document")
        if warnings:
            print(f"        {len(warnings)} warning(s) — review recommended")
        print()

    # ── Exit code ─────────────────────────────────────────────────────────────
    if not errors:
        return 0
    # Categorize first error for exit code
    first = errors[0]
    if "MISSING" in first:
        return 1
    if "unformatted tag" in first or "nesting" in first:
        return 2
    if "[BUG]" in first:
        return 3
    return 1


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    target = sys.argv[1]
    sys.exit(validate(target, verbose=verbose))
