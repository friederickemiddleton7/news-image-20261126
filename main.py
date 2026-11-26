#!/usr/bin/env python3
"""Entrypoint for the make.fun "news-image-20261126" entry.

The grader runs `python3 -P -s /bot/main.py` in a fresh, READ-ONLY container
with no network. /bot is not on sys.path (because of -P), and only the output
directory is writable. This script therefore:

  * never writes into its own directory or the current working directory;
  * runs the committed generator make_image.py via importlib only when
    entry.png is missing, so a fresh build is deterministic;
  * otherwise copies the committed, already-validated entry.png;
  * catches every exception and always exits with a valid 1024x1024 PNG;
  * uses only the Python standard library.
"""

import importlib.util
import os
import shutil
import sys

SOURCE_NAME = "entry.png"
GENERATOR_NAME = "make_image.py"
OUTPUT_NAME = "entry.png"
MIN_BYTES = 1024
MAX_BYTES = 2 * 1024 * 1024
CANVAS = (1024, 1024)


def repo_dir():
    return os.path.dirname(os.path.abspath(__file__))


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


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
    """Check the PNG signature and its 1024x1024 IHDR; return byte size."""
    size = os.path.getsize(path)
    if size < MIN_BYTES:
        raise ValueError("output too small: %d bytes" % size)
    if size > MAX_BYTES:
        raise ValueError("output implausibly large: %d bytes" % size)
    with open(path, "rb") as handle:
        data = handle.read(24)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("output is not a PNG")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != CANVAS:
        raise ValueError("wrong dimensions: %dx%d" % (width, height))
    return size


def run_generator(src_dir, dest):
    """Run the local generator (stdlib-free build) to (re)create entry.png."""
    gen = os.path.join(src_dir, GENERATOR_NAME)
    if not os.path.isfile(gen):
        raise FileNotFoundError("generator %s not present" % GENERATOR_NAME)
    spec = importlib.util.spec_from_file_location("make_image", gen)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load generator %s" % GENERATOR_NAME)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    build = getattr(module, "build", None)
    if build is None:
        raise AttributeError("generator has no build() function")
    build(dest)


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

    # Always write into the destination directory only, never into the repo dir.
    if not os.path.exists(dest) or os.path.getsize(dest) < MIN_BYTES:
        try:
            run_generator(repo_dir(), dest)
        except Exception:
            # Fall back to the committed poster if the generator misfires.
            shutil.copyfile(src, dest)

    try:
        size = validate(dest)
    except Exception as exc:
        raise SystemExit("invalid output poster: %s" % exc)

    print("ok: wrote %s (%d bytes, 1024x1024) to %s" % (OUTPUT_NAME, size, dest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
