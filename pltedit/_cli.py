"""
CLI entry point for plt-edit.

Usage::

    plt-edit [path/to/file.plt] [streamlit options]
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Launch the Plt-Edit Streamlit application."""
    try:
        from streamlit.web import cli as stcli
    except ImportError as exc:
        print(
            "Streamlit is required to run the plt-edit GUI.\n"
            "Install it with:  pip install plt-edit[app]",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    app_module = Path(__file__).parent / "_app.py"

    # Build the argv that Streamlit expects:
    #   streamlit run <app_module> [-- <extra_args>]
    # We forward any extra args after "--" so the app can read them.
    user_args = sys.argv[1:]
    sys.argv = ["streamlit", "run", str(app_module)] + user_args

    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
