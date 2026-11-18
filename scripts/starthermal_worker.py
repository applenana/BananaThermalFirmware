#!/usr/bin/env python3
"""Run private source operations without exposing their output in public logs."""
from pathlib import Path
import os
import re
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".work" / "starthermal-source"
OUTPUT = ROOT / ".work" / "starthermal-output"


def main():
    log_path = Path(os.environ["RUNNER_TEMP"]) / "starthermal-private.log"
    with log_path.open("ab") as log:
        try:
            def run(args, cwd=None, capture=False):
                result = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE if capture else log,
                                        stderr=log, check=True)
                return result.stdout.decode("ascii").strip() if capture else None
            if sys.argv[1] == "fetch":
                repository = os.environ["STARTHERMAL_SOURCE_REPOSITORY"]
                tag = os.environ["SOURCE_TAG"]
                if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or not re.fullmatch(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", tag):
                    raise ValueError("Invalid source input")
                SOURCE.mkdir(parents=True)
                run(["git", "init", "--quiet"], cwd=SOURCE)
                run(["git", "remote", "add", "origin", f"git@github.com:{repository}.git"], cwd=SOURCE)
                run(["git", "fetch", "--quiet", "--depth=1", "origin", f"refs/tags/{tag}:refs/tags/{tag}"], cwd=SOURCE)
                run(["git", "checkout", "--quiet", "--detach", f"refs/tags/{tag}"], cwd=SOURCE)
                commit = run(["git", "rev-parse", "HEAD"], cwd=SOURCE, capture=True)
                with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
                    out.write(f"commit={commit}\n")
                # Diagnostic keys live on a separate private branch, never a firmware tag.
                for path in SOURCE.rglob("*"):
                    if path.is_file() and path.suffix in (".pem", ".key") and ".git" not in path.parts:
                        if b"PRIVATE KEY" in path.read_bytes():
                            raise ValueError("Private keys must not be part of firmware source tags")
            elif sys.argv[1] == "build":
                run([sys.executable, "tools/build_release.py", "--output", str(OUTPUT)], cwd=SOURCE)
            else:
                raise ValueError("Invalid operation")
        except Exception:
            log.write(traceback.format_exc().encode("utf-8"))
            print("Private StarThermal operation failed; download encrypted diagnostics.", file=sys.stderr)
            raise SystemExit(1) from None
    print("StarThermal operation completed.")


if __name__ == "__main__":
    main()
