#!/usr/bin/env python3
"""Entrypoint for the make.fun "news-image-20261126" entry.

The grader runs `python3 -P -s /bot/main.py` in a fresh, READ-ONLY container
with no network. /bot is not on sys.path (because of -P), and only the output
directory is writable. This script therefore:

  * never writes into its own directory or the current working directory;
  * prefers copying the committed, already-validated entry.png;
  * catches every exception and always exits with a valid 1024x1024 PNG;
  * uses only the Python standard library.
"""

import os
import shutil
import sys

SOURCE_NAME = "entry.png"
OUTPUT_NAME = "entry.png"
MIN_BYTES = 1024


def repo_dir():
    return os.path.dirname(os.path.abspath(__file__))


def output_dir():
    return sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
        "MAKEFUN_OUTPUT_DIR", "/output")


def writable(path):
    try:
        probe = os.path.join(path, ".writetest")
        with open(probe, "wb") as handle:
            handle.write(b"ok")
        os.remove(probe)
        return True
    except OSError:
        return False


def validate(path):
    """Check the PNG signature and its 1024x1024 IHDR; return the byte size."""
    size = os.path.getsize(path)
    if size < MIN_BYTES:
        raise ValueError("output too small: %d bytes" % size)
    with open(path, "rb") as handle:
        data = handle.read(24)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("output is not a PNG")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1024, 1024):
        raise ValueError("wrong dimensions: %dx%d" % (width, height))
    return size


def main():
    dest_dir = output_dir()
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as exc:
        raise SystemExit("cannot create output directory %s: %s" % (dest_dir, exc))
    if not writable(dest_dir):
        raise SystemExit("output directory is not writable: %s" % dest_dir)
    dest = os.path.join(dest_dir, OUTPUT_NAME)
    src = os.path.join(repo_dir(), SOURCE_NAME)

    # Copy the committed poster. Any failure is reported plainly; the grader's
    # container always has the committed entry.png beside this script.
    try:
        if os.path.abspath(src) != os.path.abspath(dest):
            shutil.copyfile(src, dest)
    except Exception as exc:
        raise SystemExit("cannot copy committed entry.png: %s" % exc)

    try:
        size = validate(dest)
    except Exception as exc:
        raise SystemExit("invalid output poster: %s" % exc)

    print("ok: wrote %s (%d bytes) to %s" % (OUTPUT_NAME, size, dest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
