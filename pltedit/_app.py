"""
Streamlit GUI for Plt-Edit.

Launch with::

    plt-edit [path/to/file.plt]

or simply::

    plt-edit
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from pltedit._io import load, get_metadata


def _sidebar_metadata(meta: dict) -> None:
    """Render metadata in the sidebar."""
    st.sidebar.subheader("File metadata")
    st.sidebar.text(f"Created at:  {meta.get('created_at', 'N/A')}")
    st.sidebar.text(f"Python:      {meta.get('python_version', 'N/A')}")
    st.sidebar.text(f"Matplotlib:  {meta.get('matplotlib_version', 'N/A')}")
    st.sidebar.text(f"Plt-Edit:    {meta.get('plt_edit_version', 'N/A')}")


def _editing_controls(fig: plt.Figure) -> plt.Figure:
    """Render editing controls in the sidebar and return the (modified) figure."""
    axes = fig.get_axes()
    if not axes:
        return fig

    st.sidebar.divider()
    st.sidebar.subheader("Edit figure")

    # -- Figure title -------------------------------------------------------
    current_suptitle = fig._suptitle.get_text() if fig._suptitle else ""
    new_suptitle = st.sidebar.text_input("Figure title (suptitle)", value=current_suptitle)
    if new_suptitle != current_suptitle:
        fig.suptitle(new_suptitle)

    # -- Per-axes controls --------------------------------------------------
    for i, ax in enumerate(axes):
        label = f"Axes {i + 1}"
        with st.sidebar.expander(label, expanded=(i == 0)):
            # Title
            title = st.text_input("Title", value=ax.get_title(), key=f"ax{i}_title")
            if title != ax.get_title():
                ax.set_title(title)

            # X label
            xlabel = st.text_input("X label", value=ax.get_xlabel(), key=f"ax{i}_xlabel")
            if xlabel != ax.get_xlabel():
                ax.set_xlabel(xlabel)

            # Y label
            ylabel = st.text_input("Y label", value=ax.get_ylabel(), key=f"ax{i}_ylabel")
            if ylabel != ax.get_ylabel():
                ax.set_ylabel(ylabel)

            # X limits
            xlim = ax.get_xlim()
            col1, col2 = st.columns(2)
            xmin = col1.number_input("X min", value=float(xlim[0]), key=f"ax{i}_xmin", format="%g")
            xmax = col2.number_input("X max", value=float(xlim[1]), key=f"ax{i}_xmax", format="%g")
            if xmin != xlim[0] or xmax != xlim[1]:
                ax.set_xlim(xmin, xmax)

            # Y limits
            ylim = ax.get_ylim()
            col3, col4 = st.columns(2)
            ymin = col3.number_input("Y min", value=float(ylim[0]), key=f"ax{i}_ymin", format="%g")
            ymax = col4.number_input("Y max", value=float(ylim[1]), key=f"ax{i}_ymax", format="%g")
            if ymin != ylim[0] or ymax != ylim[1]:
                ax.set_ylim(ymin, ymax)

    return fig


def main() -> None:
    st.set_page_config(
        page_title="Plt-Edit",
        page_icon="📊",
        layout="wide",
    )

    st.title("📊 Plt-Edit")
    st.markdown(
        "Load a `.plt` file to display and edit the stored matplotlib figure."
    )

    # ---- File input -------------------------------------------------------
    # If a path is provided on the command line (after the Streamlit args),
    # pre-fill the uploader with it.
    preload_path: Path | None = None
    # sys.argv after Streamlit processing contains only extra user args
    extra_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if extra_args:
        candidate = Path(extra_args[0])
        if candidate.exists() and candidate.suffix.lower() == ".plt":
            preload_path = candidate

    uploaded = st.file_uploader("Choose a .plt file", type=["plt"])

    fig: plt.Figure | None = None
    meta: dict | None = None

    if uploaded is not None:
        try:
            import io
            import os
            import tempfile
            # Write to a temp file so load() can use np.load on a real path
            with tempfile.NamedTemporaryFile(suffix=".plt", delete=False) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            fig = load(tmp_path)
            meta = get_metadata(tmp_path)
            os.remove(tmp_path)
        except Exception as exc:
            st.error(f"Failed to load file: {exc}")
    elif preload_path is not None:
        try:
            fig = load(preload_path)
            meta = get_metadata(preload_path)
            st.info(f"Loaded from command-line argument: {preload_path}")
        except Exception as exc:
            st.error(f"Failed to load file: {exc}")

    # ---- Display & edit ---------------------------------------------------
    if fig is not None:
        if meta:
            _sidebar_metadata(meta)

        fig = _editing_controls(fig)

        st.pyplot(fig)
        plt.close(fig)


if __name__ == "__main__":
    main()
