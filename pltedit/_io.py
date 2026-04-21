"""
Save and load matplotlib figures as .plt files.

A .plt file is a NumPy archive (.npz) renamed to .plt.  It contains:

- ``figure``: a 1-D uint8 array holding the pickle-serialised
  :class:`matplotlib.figure.Figure` object.
- ``metadata``: a 0-D object array whose single element is a JSON string
  with the following keys:

  ``created_at``
      ISO-8601 timestamp of when the file was saved.
  ``python_version``
      Full Python version string (e.g. ``"3.12.3"``).
  ``matplotlib_version``
      Matplotlib version string (e.g. ``"3.10.1"``).
  ``pltedit_version``
      Plt-Edit version string (e.g. ``"0.1.0"``).
"""

from __future__ import annotations

import io
import json
import os
import pickle
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

import matplotlib
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from pltedit._version import __version__


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def save(fig: Union[Figure, Axes], path: Union[str, os.PathLike]) -> None:
    """Serialise *fig* to a ``.plt`` file at *path*.

    Parameters
    ----------
    fig:
        A :class:`~matplotlib.figure.Figure` or
        :class:`~matplotlib.axes.Axes` instance.  When an
        :class:`~matplotlib.axes.Axes` is supplied the parent figure is saved.
    path:
        Destination file path.  The ``.plt`` extension is appended
        automatically if it is missing.

    Raises
    ------
    TypeError
        If *fig* is neither a :class:`~matplotlib.figure.Figure` nor an
        :class:`~matplotlib.axes.Axes`.
    """
    if isinstance(fig, Axes):
        fig = fig.get_figure()
    if not isinstance(fig, Figure):
        raise TypeError(
            f"Expected a matplotlib Figure or Axes, got {type(fig)!r}."
        )

    path = Path(path)
    if path.suffix.lower() != ".plt":
        path = path.with_suffix(".plt")

    # ---- serialise the figure -------------------------------------------
    buf = io.BytesIO()
    pickle.dump(fig, buf)
    figure_bytes = np.frombuffer(buf.getvalue(), dtype=np.uint8)

    # ---- build metadata -------------------------------------------------
    metadata_dict = {
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "python_version": sys.version,
        "matplotlib_version": matplotlib.__version__,
        "pltedit_version": __version__,
    }
    metadata_array = np.array(json.dumps(metadata_dict))

    # ---- write as npz with .plt extension --------------------------------
    # np.savez writes a .npz file; we write to a temporary file and rename.
    with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        np.savez(tmp_path, figure=figure_bytes, metadata=metadata_array)
        shutil.move(tmp_path, path)
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def load(path: Union[str, os.PathLike]) -> Figure:
    """Deserialise a ``.plt`` file and return the stored figure.

    .. warning::

        ``.plt`` files are deserialised with :mod:`pickle`.  Only load files
        from sources you trust.  A maliciously crafted ``.plt`` file could
        execute arbitrary code when loaded.

    Parameters
    ----------
    path:
        Path to a ``.plt`` file.

    Returns
    -------
    matplotlib.figure.Figure
        The reconstructed figure.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If *path* is not a valid ``.plt`` file.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path!r}")

    try:
        archive = np.load(path, allow_pickle=False)
    except Exception as exc:
        raise ValueError(f"{path!r} is not a valid .plt file: {exc}") from exc

    if "figure" not in archive:
        raise ValueError(
            f"{path!r} is missing the 'figure' array — not a valid .plt file."
        )

    figure_bytes = bytes(archive["figure"].tobytes())
    fig = pickle.loads(figure_bytes)  # noqa: S301 — trusted .plt files only

    if not isinstance(fig, Figure):
        raise ValueError(
            "The deserialized object is not a matplotlib Figure."
        )

    import matplotlib.pyplot as plt
    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)

    return fig


def get_metadata(path: Union[str, os.PathLike]) -> dict:
    """Return the metadata stored inside a ``.plt`` file.

    Parameters
    ----------
    path:
        Path to a ``.plt`` file.

    Returns
    -------
    dict
        Dictionary with keys ``created_at``, ``python_version``,
        ``matplotlib_version``, and ``pltedit_version``.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If *path* is not a valid ``.plt`` file or has no metadata.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path!r}")

    try:
        archive = np.load(path, allow_pickle=False)
    except Exception as exc:
        raise ValueError(f"{path!r} is not a valid .plt file: {exc}") from exc

    if "metadata" not in archive:
        raise ValueError(
            f"{path!r} is missing the 'metadata' array — not a valid .plt file."
        )

    return json.loads(str(archive["metadata"]))
