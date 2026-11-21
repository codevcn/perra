#!/usr/bin/env python3
import asyncio
import platform
import sys

import perra


DOUBLE_CLICK_INTRO = """\
Perra (Persona Radar) runs from the command line. You can:

  - call it from cmd/PowerShell:  perra USERNAME [options]
  - or enter a username below for a default search.

Full options:    perra --help
Repository:      https://github.com/codevcn/perra
"""


def _force_utf8_output() -> None:
    """Keep unicode output alive when stdout is not a console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _launched_by_double_click() -> bool:
    # Only treat as double-click when running on Windows with no CLI arguments
    # and interactive TTY handles (so automated subprocess calls never hang).
    if platform.system() != "Windows":
        return False
    if len(sys.argv) > 1:
        return False
    try:
        import ctypes

        buf = (ctypes.c_uint * 4)()
        count = ctypes.windll.kernel32.GetConsoleProcessList(buf, 4)
        return count <= 1
    except Exception:
        return False


def _pause() -> None:
    try:
        input("\nPress Enter to exit...")
    except EOFError:
        pass


def _prompt_for_username() -> str:
    try:
        return input("Username to search: ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def main() -> None:
    _force_utf8_output()

    if not _launched_by_double_click():
        asyncio.run(perra.cli())
        return

    print(DOUBLE_CLICK_INTRO)
    username = _prompt_for_username()

    if not username:
        print(
            "\nNo username entered. Re-run with one, e.g.\n"
            "    perra alice"
        )
        _pause()
        return

    # Inject the username so perra's argparse sees it like a normal CLI run.
    sys.argv = [sys.argv[0], username]
    try:
        asyncio.run(perra.cli())
    finally:
        _pause()


if __name__ == "__main__":
    main()
