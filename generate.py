#!/usr/bin/env python3
"""Root dispatcher: `python generate.py <name> [args...]` -> runs
`markslidego.generate_<name>` as a module.

Examples:
  python generate.py course --some-option
  python generate.py moodle
"""
from __future__ import annotations
import sys
import os
import importlib
import runpy


def available_targets() -> list[str]:
    pkg_dir = os.path.join(os.path.dirname(__file__), "markslidego")
    try:
        names = []
        for fn in os.listdir(pkg_dir):
            if fn.startswith("generate_") and fn.endswith(".py"):
                names.append(fn[len("generate_"):-3])
        names.sort()
        return names
    except Exception:
        return []


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv) if argv is None else list(argv)
    if len(argv) < 2:
        print("Usage: python generate.py <name> [args...]")
        targets = available_targets()
        if targets:
            print("Available targets:", ", ".join(targets))
        return 2

    name = argv[1]
    module_name = f"markslidego.generate_{name}"

#    # Check module availability
#    try:
#        importlib.import_module(module_name)
#    except Exception as exc:  # avoid failing on import-time errors in target module
#        # If module file doesn't exist, show available targets.
#        targets = available_targets()
#        if targets and f"{name}" not in targets:
#            print(f"Module for '{name}' not found.")
#            print("Available targets:", ", ".join(targets))
#            return 1
#        # If module exists but import raised, surface the error
#        print(f"Error importing {module_name}: {exc}", file=sys.stderr)
#        return 1

    # Set argv for the target module: argv[0] will be module name for clarity
    sys.argv = [module_name] + argv[2:]
    runpy.run_module(module_name, run_name="__main__", alter_sys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
