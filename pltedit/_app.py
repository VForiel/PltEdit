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

import matplotlib
matplotlib.use("Agg")  # Prevent Tkinter thread crashes in Streamlit

import matplotlib.pyplot as plt
import streamlit as st

from pltedit._io import load, get_metadata, save
from pltedit._style import set_style


def _display_metadata(meta: dict) -> None:
    """Render metadata in an expander on the main page."""
    with st.expander("ℹ️ File metadata"):
        st.text(f"Created at:  {meta.get('created_at', 'N/A')}")
        st.text(f"Python:      {meta.get('python_version', 'N/A')}")
        st.text(f"Matplotlib:  {meta.get('matplotlib_version', 'N/A')}")
        st.text(f"Plt-Edit:    {meta.get('plt_edit_version', 'N/A')}")


def _editing_controls(fig: plt.Figure) -> plt.Figure:
    """Render editing controls in the sidebar and return the (modified) figure."""
    axes = fig.get_axes()
    if not axes:
        return fig

    st.sidebar.subheader("Edit figure")

    # -- Global Style -------------------------------------------------------
    current_style = "default"
    available_styles = ["default"] + plt.style.available
    selected_style = st.sidebar.selectbox("Matplotlib style", available_styles, index=0)
    if selected_style != "default":
        fig = set_style(fig, selected_style)
        # Update axes reference after regenerating the figure
        axes = fig.get_axes()
        if not axes:
            return fig

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


def file_explorer():
    """Render a simple file explorer for .plt files."""
    st.subheader("📁 Local File Explorer")
    
    if "current_dir" not in st.session_state:
        st.session_state.current_dir = Path.cwd()
        
    current_dir = Path(st.session_state.current_dir)
    
    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        new_path = st.text_input("Current Directory", str(current_dir))
        if new_path != str(current_dir):
            candidate = Path(new_path)
            if candidate.exists() and candidate.is_dir():
                st.session_state.current_dir = candidate
                st.rerun()

    with col2:
        if st.button("⬆️ Up to parent"):
            st.session_state.current_dir = current_dir.parent
            st.rerun()
            
    # List subdirectories
    subdirs = sorted([d for d in current_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    if subdirs:
        dir_names = ["(Select a folder)"] + [d.name for d in subdirs]
        sel_dir = st.selectbox("Navigate to subfolder", dir_names)
        if sel_dir != "(Select a folder)":
            st.session_state.current_dir = current_dir / sel_dir
            st.rerun()
            
    st.divider()
    
    # List .plt files
    plt_files = sorted(list(current_dir.glob("*.plt")))
    if not plt_files:
        st.info("No `.plt` files found in this directory.")
        return None
        
    st.write(f"Found {len(plt_files)} `.plt` files:")
    
    # Display previews in a grid
    cols = st.columns(3)
    selected_file = None
    
    for i, file_path in enumerate(plt_files):
        with cols[i % 3]:
            st.markdown(f"**{file_path.name}**")
            try:
                # Load and show preview
                fig_preview = load(file_path)
                st.pyplot(fig_preview)
                plt.close(fig_preview)
                
                if st.button(f"Editor ➡️", key=f"edit_{file_path.name}"):
                    st.session_state.active_file = file_path
                    st.session_state.current_tab = "🖌️ Editor"
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading preview: {e}")
                
    return selected_file

def main() -> None:
    st.set_page_config(
        page_title="Plt-Edit",
        page_icon="📊",
        layout="wide",
    )

    st.title("📊 Plt-Edit")

    tabs = ["📁 File Explorer", "🖌️ Editor"]
    
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = tabs[0]

    # Tab navigation via radio buttons
    selected_tab = st.radio(
        "Select Tab",
        tabs,
        index=tabs.index(st.session_state.current_tab),
        horizontal=True,
        label_visibility="collapsed"
    )

    # If the user clicks a specific radio button, update session state
    if selected_tab != st.session_state.current_tab:
        st.session_state.current_tab = selected_tab
        st.rerun()

    preload_path: Path | None = None
    extra_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if extra_args:
        candidate = Path(extra_args[0])
        if candidate.exists() and candidate.suffix.lower() == ".plt":
            preload_path = candidate

    fig: plt.Figure | None = None
    meta: dict | None = None
    uploaded = None

    if st.session_state.current_tab == "📁 File Explorer":
        st.markdown("Drag and drop a `.plt` file here, or select one from your local directories.")
        uploaded = st.file_uploader("Choose a .plt file", type=["plt"])
        if uploaded is not None:
            st.session_state.uploaded_file = uploaded
            st.session_state.current_tab = "🖌️ Editor"
            st.rerun()

        st.divider()
        explorer_selection = file_explorer()
        if explorer_selection is not None:
            st.session_state.active_file = explorer_selection
            st.session_state.uploaded_file = None  # Clear temp upload
            st.session_state.current_tab = "🖌️ Editor"
            st.rerun()

    elif st.session_state.current_tab == "🖌️ Editor":
        # Check source: uploaded via button vs selected from active file vs preload
        uploaded_file = st.session_state.get("uploaded_file", None)
        
        if uploaded_file is not None:
            uploaded_file.seek(0)
            try:
                import io, os, tempfile
                with tempfile.NamedTemporaryFile(suffix=".plt", delete=False) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                fig = load(tmp_path)
                meta = get_metadata(tmp_path)
                os.remove(tmp_path)
            except Exception as exc:
                st.error(f"Failed to load file: {exc}")
                
        elif "active_file" in st.session_state:
            preload_path = st.session_state.active_file
            try:
                fig = load(preload_path)
                meta = get_metadata(preload_path)
                st.success(f"Editing: {preload_path.name}")
            except Exception as exc:
                st.error(f"Failed to load file: {exc}")
                
        elif preload_path is not None:
            try:
                fig = load(preload_path)
                meta = get_metadata(preload_path)
                st.success(f"Editing: {preload_path.name}")
            except Exception as exc:
                st.error(f"Failed to load file: {exc}")

        # ---- Display & edit ---------------------------------------------------
        if fig is not None:
            fig = _editing_controls(fig)
            st.pyplot(fig)
            
            if meta:
                _display_metadata(meta)
                
            st.divider()
            col1, col2, col3 = st.columns([1, 1, 1])
            
            # Identify the target filename
            save_target = "figure.plt"
            if "active_file" in st.session_state and st.session_state.active_file:
                save_target = str(st.session_state.active_file)
            elif uploaded_file:
                save_target = uploaded_file.name
            elif preload_path:
                save_target = str(preload_path)

            with col1:
                # Save overwrites exactly where it was
                if st.button("💾 Save", use_container_width=True):
                    try:
                        save(fig, save_target)
                        st.success(f"Saved successfully to `{save_target}`!")
                    except Exception as e:
                        st.error(f"Error saving: {e}")

            with col2:
                # Save as simply downloads the new modified plt
                import tempfile, os
                with tempfile.NamedTemporaryFile(suffix=".plt", delete=False) as tmp:
                    tmp_save_path = tmp.name
                try:
                    save(fig, tmp_save_path)
                    with open(tmp_save_path, "rb") as f:
                        plt_data = f.read()
                        
                    dl_name = Path(save_target).name if save_target else "figure.plt"
                    
                    st.download_button(
                        label="📤 Export",
                        data=plt_data,
                        file_name=dl_name,
                        mime="application/octet-stream",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error caching file: {e}")
                finally:
                    if os.path.exists(tmp_save_path):
                        os.remove(tmp_save_path)

            with col3:
                # Export to PNG 
                import io
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches='tight')
                img_data = buf.getvalue()
                
                dl_name = "figure.png"
                if "active_file" in st.session_state and st.session_state.active_file:
                    dl_name = f"{st.session_state.active_file.stem}.png"
                elif preload_path:
                    dl_name = f"{preload_path.stem}.png"
                elif uploaded_file:
                    dl_name = f"{uploaded_file.name.replace('.plt', '')}.png"
                    
                st.download_button(
                    label="🖼️ Export as PNG",
                    data=img_data,
                    file_name=dl_name,
                    mime="image/png",
                    use_container_width=True
                )

            plt.close(fig)
        else:
            st.info("Upload a `.plt` file or select one from the File Explorer tab to begin editing.")

if __name__ == "__main__":
    main()
