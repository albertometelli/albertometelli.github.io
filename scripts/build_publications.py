#!/usr/bin/env python3
"""Build and validate the static publications page from canonical BibTeX files.

The default build is deterministic and offline. Pass ``--online`` to also sync
and enrich the bibliography from the external sources supported by the
canonical pipeline.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(label: str, *arguments: str) -> None:
    command = [sys.executable, *arguments]
    print(f"\n==> {label}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--online",
        action="store_true",
        help="sync DBLP and enrich data from Crossref, CORE/ICORE, SCImago and OpenAccept",
    )
    parser.add_argument(
        "--crossref-limit",
        type=int,
        default=35,
        metavar="N",
        help="maximum Crossref title checks during an online build (default: 35)",
    )
    args = parser.parse_args(argv)

    if args.crossref_limit < 0:
        parser.error("--crossref-limit must be zero or greater")

    pipeline = [str(SCRIPTS / "bib_pipeline.py")]
    if args.online:
        pipeline.extend(("--sync-dblp", "--enrich-online", "--crossref-limit", str(args.crossref_limit)))

    try:
        run("Canonical BibTeX pipeline", *pipeline)
        run("Static HTML rendering", str(SCRIPTS / "render_shared_layout.py"))
        run(
            "Regression tests",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_*.py",
            "-v",
        )
    except subprocess.CalledProcessError as exc:
        print(f"\nBuild stopped: {exc.cmd!r} returned exit status {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1

    mode = "online" if args.online else "offline"
    print(f"\nPublications build completed successfully ({mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
