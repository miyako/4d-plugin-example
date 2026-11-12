#!/usr/bin/env python3
"""Verify canonical gitlinks, then reproduce the generated pipeline from its pin."""

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, encoding="utf-8"
    ).strip()


def check(root=ROOT):
    root = Path(root).resolve()
    canonical = root / "plugin-template"
    for name in ("plugin-template", "4D-Plugin-SDK"):
        entries = git(root, "ls-files", "--stage", "--", name).splitlines()
        if len(entries) != 1:
            raise ValueError(f"Expected one staged gitlink for {name}")
        metadata, path = entries[0].split("\t", 1)
        mode, pin, stage = metadata.split()
        if mode != "160000" or stage != "0" or path != name:
            raise ValueError(f"Invalid gitlink for {name}")
        submodule = root / name
        if not (submodule / ".git").exists():
            raise ValueError(f"Initialize {name}: git submodule update --init --recursive")
        if git(submodule, "rev-parse", "HEAD") != pin:
            raise ValueError(f"{name} checkout does not match its gitlink")
        if git(submodule, "status", "--porcelain", "--untracked-files=all"):
            raise ValueError(f"{name} must be clean, including nested submodules")
    nested = git(canonical, "submodule", "status", "--recursive")
    if not nested or any(line[0] in "-+U" for line in nested.splitlines()):
        raise ValueError("Initialize canonical submodules recursively")
    subprocess.run(
        [sys.executable, str(canonical / "scripts/generate_plugin_pipeline.py"),
         "--config", str(root / "pipeline/example.json"),
         "--output", str(root), "--check"],
        cwd=root, check=True,
    )
    subprocess.run(
        [sys.executable, str(root / "scripts/check_pipeline.py")],
        cwd=root, check=True,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        check(args.root)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"tutorial-pipeline: {error}\n")
    print("Tutorial pipeline matches the clean canonical pin.")


if __name__ == "__main__":
    main()
