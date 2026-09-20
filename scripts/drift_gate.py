#!/usr/bin/env python3
"""Drift gate: docs/spec.md <-> tests must agree 1:1. Exit 0 pass, 1 block."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "spec.md"

blocks: list[tuple[str, str]] = []
fail: list[str] = []

text = SPEC.read_text(encoding="utf-8")
current, buf = None, []
for line in text.splitlines():
    m = re.match(r"^(AC-\d+)\b", line)
    if m:
        if current:
            blocks.append((current, "\n".join(buf)))
        current, buf = m.group(1), [line]
    elif current:
        buf.append(line)
if current:
    blocks.append((current, "\n".join(buf)))

verify_refs: set[str] = set()
for ac, block in blocks:
    vs = re.findall(r"Verify:\s*(tests/[\w/]+\.py)::(\w+)", block)
    if not vs:
        fail.append(f"{ac} has no Verify: line")
    for f, fn in vs:
        verify_refs.add(f"{f}::{fn}")

for ref in sorted(verify_refs):
    f, fn = ref.split("::")
    path = ROOT / f
    if not path.exists():
        fail.append(f"Verify {ref} -> file missing")
    elif not re.search(rf"def {re.escape(fn)}\b", path.read_text(encoding="utf-8")):
        fail.append(f"Verify {ref} -> function {fn} not defined")

for tf in sorted((ROOT / "tests").rglob("test_*.py")):
    rel_path = tf.relative_to(ROOT).as_posix()
    for fn in re.findall(r"def (test_\w+)", tf.read_text(encoding="utf-8")):
        if f"{rel_path}::{fn}" not in verify_refs:
            fail.append(f"orphan test {rel_path}::{fn} (no AC references it)")

print(f"== ACs: {len(blocks)}, Verify refs: {len(verify_refs)}")
if fail:
    for f in fail:
        print(f"BLOCK: {f}")
    print("DRIFT GATE: BLOCK")
    sys.exit(1)
print("DRIFT GATE: PASS")
