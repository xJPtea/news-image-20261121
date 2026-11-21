#!/usr/bin/env python3
"""Local test for the news-image-20261121 entry.

Runs main.py twice into two fresh directories and checks:
- both runs exit 0 and write entry.png
- the two files are byte-identical (determinism)
- PNG signature + IHDR say 1024x1024, 8-bit, colour type 2
- file size is at most 1 MiB
- main.py imports no network modules (stdlib-only rule)
"""
import hashlib
import os
import struct
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(ROOT, "main.py")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def main():
    failures = []

    src = open(MAIN, encoding="utf-8").read()
    for banned in ("socket", "urllib", "requests", "http.client", "ssl"):
        if banned in src:
            failures.append(f"main.py mentions network module: {banned}")

    with tempfile.TemporaryDirectory() as tmp:
        hashes = []
        sizes = []
        for run in (1, 2):
            out = os.path.join(tmp, f"run{run}")
            env = dict(os.environ, MAKEFUN_OUTPUT_DIR=out)
            proc = subprocess.run(
                [sys.executable, MAIN], env=env,
                capture_output=True, text=True, timeout=120)
            if proc.returncode != 0:
                failures.append(f"run {run} exit {proc.returncode}: {proc.stderr[-400:]}")
                continue
            path = os.path.join(out, "entry.png")
            if not os.path.exists(path):
                failures.append(f"run {run} wrote no entry.png")
                continue
            data = open(path, "rb").read()
            sizes.append(len(data))
            hashes.append(sha256(path))
            if data[:8] != b"\x89PNG\r\n\x1a\n":
                failures.append(f"run {run}: bad PNG signature")
            w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
            if (w, h) != (1024, 1024):
                failures.append(f"run {run}: size {w}x{h}, expected 1024x1024")
            if depth != 8 or ctype != 2:
                failures.append(f"run {run}: bit depth {depth}, colour type {ctype}")
            if len(data) > 1048576:
                failures.append(f"run {run}: {len(data)} bytes exceeds 1 MiB")
        if len(hashes) == 2 and hashes[0] != hashes[1]:
            failures.append("runs differ: output is not deterministic")
        print(f"run sizes: {sizes}")
        print(f"sha256: {hashes[0] if hashes else 'n/a'}")
        print(f"deterministic: {len(hashes) == 2 and hashes[0] == hashes[1]}")

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
