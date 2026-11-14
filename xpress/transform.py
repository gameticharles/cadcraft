#!/usr/bin/env python3
"""Make CAD Studio from a CADCraft source tree: Xpress Survey's colours (brand.toml), name (rename.toml) and fonts (fonts.toml).

    python3 xpress/transform.py SRC [--recipe DIR] [--check]

SRC is a checkout of storytold/cadcraft at a release tag. The tree is changed in place; nothing is
committed. Every rule must find what it changes, so a CADCraft release that moved something stops
the build with a list of what was not found instead of shipping half-branded. --check reports
without writing. A list of the files changed is written to SRC/XPRESS-MODIFICATIONS.txt.

Python 3.11 or newer (tomllib); no other packages.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
import tomllib
from pathlib import Path


class Failures(list):
    def need(self, ok: bool, what: str) -> bool:
        if not ok:
            self.append(what)
        return ok


class Tree:
    """The source files, read once and written back at the end when changed."""

    def __init__(self, root: Path):
        self.root = root
        self.text: dict[str, str] = {}
        self.original: dict[str, str] = {}
        self.counts: dict[str, int] = {}

    def get(self, rel: str) -> str | None:
        if rel not in self.text:
            p = self.root / rel
            if not p.is_file():
                return None
            self.text[rel] = self.original[rel] = p.read_text(encoding="utf-8")
        return self.text[rel]

    def set(self, rel: str, new: str, changes: int = 1) -> None:
        self.text[rel] = new
        self.counts[rel] = self.counts.get(rel, 0) + changes

    def changed(self) -> list[str]:
        return sorted(r for r, t in self.text.items() if t != self.original[r])

    def write(self) -> None:
        for rel in self.changed():
            (self.root / rel).write_text(self.text[rel], encoding="utf-8")


def replace_once(tree: Tree, fail: Failures, rel: str, old: str, new: str, why: str) -> None:
    text = tree.get(rel)
    if not fail.need(text is not None, f"{why}: {rel} is missing"):
        return
    n = text.count(old)
    if fail.need(n == 1, f"{why}: {rel} has {n} of {old!r} (expected 1)"):
        tree.set(rel, text.replace(old, new))


# ---------------------------------------------------------------------------------------------- brand


def const_block(text: str, name: str) -> tuple[int, int] | None:
    """The body of `pub const NAME: Tokens = Tokens { ... };` as (start, end) offsets."""
    m = re.search(rf"pub const {name}: Tokens = Tokens \{{\n", text)
    if not m:
        return None
    end = text.find("\n    };", m.end())
    return (m.end(), end) if end >= 0 else None


def brand(tree: Tree, recipe: dict, fail: Failures) -> None:
    rel = recipe["theme_file"]
    for const, fields in recipe.get("tokens", {}).items():
        text = tree.get(rel)
        if not fail.need(text is not None, f"brand: {rel} is missing"):
            return
        span = const_block(text, const)
        if not fail.need(span is not None, f"brand: no `pub const {const}: Tokens` block in {rel}"):
            continue
        body = text[span[0] : span[1]]
        for field, value in fields.items():
            # One field per line: `        name: <expr>,` (rustfmt's layout of this block).
            pat = re.compile(rf"^(\s+{re.escape(field)}: ).*,$", re.M)
            hits = pat.findall(body)
            if fail.need(len(hits) == 1, f"brand: {const}.{field} found {len(hits)} times in {rel} (expected 1)"):
                body = pat.sub(lambda m: f"{m.group(1)}{value},", body)
        tree.set(rel, text[: span[0]] + body + text[span[1] :], len(fields))

    for lit in recipe.get("literal", []):
        replace_once(tree, fail, lit["file"], lit["old"], lit["new"], "brand literal")

    for theme, block in recipe.get("visuals", {}).items():
        text = tree.get(rel)
        m = re.search(r"\nfn visuals\(theme: Theme\) -> Visuals \{\n(.*?)\n    v\n\}\n", text or "", re.S)
        if not fail.need(m is not None, f"brand: `fn visuals(theme: Theme) -> Visuals` ending in `v` not found in {rel}"):
            continue
        lines = "".join(f"        {s}\n" for s in block["statements"])
        insert = f"\n    // CAD Studio: Xpress Survey's colours for egui's own widgets.\n    if theme == Theme::{theme} {{\n{lines}    }}"
        at = m.end(1)
        tree.set(rel, text[:at] + insert + text[at:], len(block["statements"]))


# --------------------------------------------------------------------------------------------- rename


def rust_strings(src: str):
    """(start, end) of the contents of each string literal in Rust source: "…", b"…", c"…", r"…", r#"…"#.
    Comments, char literals and lifetimes are stepped over."""
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "/" and src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif c == "/" and src.startswith("/*", i):
            depth, i = 1, i + 2
            while i < n and depth:
                if src.startswith("/*", i):
                    depth, i = depth + 1, i + 2
                elif src.startswith("*/", i):
                    depth, i = depth - 1, i + 2
                else:
                    i += 1
        elif c == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            yield i + 1, j
            i = j + 1
        elif c == "'":
            # A char literal ('a', '\n', '\u{..}', '"') or a lifetime/label ('a, 'static).
            m = re.match(r"'(\\(u\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{2}|.)|[^\\'])'", src[i:], re.S)
            i += m.end() if m else 1
        elif c.isalnum() or c == "_":
            # A whole word; r"…", br"…", cr"…" and their r#"…"# forms are raw strings.
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            m = re.match(r'(#*)"', src[j : j + 256]) if src[i:j] in ("r", "br", "cr") else None
            if m:
                start = j + m.end()
                end = src.find('"' + m.group(1), start)
                end = n if end < 0 else end
                yield start, end
                i = end + 1 + len(m.group(1))
            else:
                i = j  # b"…", c"…" and b'…' go on to the string and char branches
        else:
            i += 1


def renamer(cfg: dict):
    frm, to, protect = cfg["from"], cfg["to"], sorted(cfg.get("protect", []), key=len, reverse=True)

    def rename(s: str) -> tuple[str, int]:
        held = []
        for k, p in enumerate(protect):
            if p in s:
                s = s.replace(p, f"\x00{k}\x00")
                held.append(k)
        n = s.count(frm)
        s = s.replace(frm, to)
        for k in held:
            s = s.replace(f"\x00{k}\x00", protect[k])
        return s, n

    return rename


def excluded(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(rel, g) for g in globs)


def rename(tree: Tree, cfg: dict, fail: Failures) -> int:
    frm = cfg["from"]
    if about := cfg.get("about"):
        rel = about["file"]
        text = tree.get(rel)
        start = text.find(about["old_start"]) if text else -1
        if fail.need(start >= 0, f"rename about: {about['old_start']!r} not found in {rel}"):
            line_start = text.rfind("\n", 0, start) + 1
            indent = text[line_start:start]
            end_at = text.find(about["old_end"], start)
            if fail.need(end_at >= 0, f"rename about: {about['old_end']!r} not found after the heading in {rel}"):
                line_end = text.find("\n", end_at)
                body = "\n".join(indent + l if l else l for l in about["new"].strip("\n").split("\n"))
                tree.set(rel, text[:line_start] + body + text[line_end:])

    for t in cfg.get("text", []):
        replace_once(tree, fail, t["file"], t["old"], t["new"], "rename text")

    rn = renamer(cfg)
    total = 0
    globs = cfg.get("exclude", [])
    for root in cfg["roots"]:
        for p in sorted((tree.root / root).rglob("*")):
            rel = p.relative_to(tree.root).as_posix()
            if p.suffix not in (".rs", ".tsv") or not p.is_file() or excluded(rel, globs):
                continue
            text = tree.get(rel)
            if frm not in text:
                continue
            count = 0
            if p.suffix == ".tsv":
                out = []
                for line in text.split("\n"):
                    if not line.startswith("#"):
                        line, k = rn(line)
                        count += k
                    out.append(line)
                new = "\n".join(out)
            else:
                parts, last = [], 0
                for a, b in rust_strings(text):
                    s, k = rn(text[a:b])
                    if k:
                        parts += [text[last:a], s]
                        last = b
                        count += k
                new = "".join(parts) + text[last:]
            if count:
                tree.set(rel, new, count)
                total += count

    for e in cfg.get("expect", []):
        text = tree.get(e["file"]) or ""
        fail.need(e["text"] in text, f"rename expect: {e['text']!r} not in {e['file']} after renaming")
    return total


# ----------------------------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src", type=Path)
    ap.add_argument("--recipe", type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument("--check", action="store_true", help="report only; change nothing")
    a = ap.parse_args()

    if not (a.src / "crates/ui-egui/src/theme.rs").is_file():
        print(f"error: {a.src} is not a CADCraft source tree", file=sys.stderr)
        return 2
    marker = a.src / "XPRESS-MODIFICATIONS.txt"
    if marker.exists():
        print(f"error: {a.src} was transformed already ({marker.name}); use a fresh checkout", file=sys.stderr)
        return 2

    tree, fail = Tree(a.src), Failures()
    brand(tree, tomllib.loads((a.recipe / "brand.toml").read_text(encoding="utf-8")), fail)
    names = rename(tree, tomllib.loads((a.recipe / "rename.toml").read_text(encoding="utf-8")), fail)
    for t in tomllib.loads((a.recipe / "fonts.toml").read_text(encoding="utf-8")).get("text", []):
        replace_once(tree, fail, t["file"], t["old"], t["new"], "fonts")

    changed = tree.changed()
    print(f"{len(changed)} files changed, {names} names in strings and catalogs")
    if fail:
        print(f"\n{len(fail)} rule(s) did not apply:", file=sys.stderr)
        for f in fail:
            print(f"  - {f}", file=sys.stderr)
        return 1
    if a.check:
        for rel in changed:
            print(f"  {rel} ({tree.counts.get(rel, 0)})")
        return 0
    tree.write()
    marker.write_text(
        "CAD Studio is CADCraft (https://github.com/storytold/cadcraft) with these files changed by\n"
        "xpress/transform.py (https://github.com/gameticharles/cadcraft, branch xpress): Xpress Survey's\n"
        'colours, the name "CAD Studio" in what the app shows, updates left to Xpress Survey, and fonts\n'
        "supplied by Xpress Survey (TrueType/OpenType files in the web build, CADCRAFT_BUNDLED_FONTS on the desktop).\n\n"
        + "".join(f"{rel}\n" for rel in changed),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
