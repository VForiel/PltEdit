# Plt-Edit
A simple tool to save matplotlib figures as a unique file and edit them afterward while keeping data integrity

## Overview

**Plt-Edit** is a Python package that lets you save a `matplotlib` figure (or axes) — including all its underlying data — to a single `.plt` file, and reload it in another Python session or in a Streamlit-based GUI.

Unlike `matplotlib`'s built-in `savefig()` (which exports to raster/vector image formats), a `.plt` file preserves the full figure object so it can be displayed, inspected, and edited programmatically.

## File format

A `.plt` file is a **NumPy archive** (`.npz`) with a custom `.plt` extension.  It contains two arrays:

| Key | Content |
|-----|---------|
| `figure` | `uint8` array — pickle-serialised `matplotlib.figure.Figure` |
| `metadata` | 0-D object array — JSON string with creation info |

The metadata JSON includes:

```json
{
  "created_at": "2024-01-15T12:00:00+00:00",
  "python_version": "3.12.3 (main, ...)",
  "matplotlib_version": "3.10.1",
  "pltedit_version": "0.1.0"
}
```

## Installation

```bash
# Core library only
pip install plt-edit

# With the Streamlit GUI
pip install plt-edit[app]
```

## Usage

### Python API

```python
import matplotlib.pyplot as plt
import pltedit as plte

# Create a figure
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6], label="my data")
ax.set_title("My plot")

# Save to .plt
plte.save(fig, "my_figure.plt")

# Load in another session
fig2 = plte.load("my_figure.plt")

# Change style
fig2 = plte.set_style(fig2, "seaborn-v0_8")

# Display
fig2.show()

# Inspect metadata
from pltedit._io import get_metadata
meta = get_metadata("my_figure.plt")
print(meta["created_at"])
```

You can also pass an `Axes` object directly to `save()`:

```python
plte.save(ax, "from_axes.plt")
```

### Streamlit GUI

```bash
pltedit                        # open the GUI (file upload)
pltedit path/to/figure.plt     # open the GUI with a pre-loaded file
```

The GUI lets you:

- Upload any `.plt` file
- View the stored figure metadata
- Edit the figure title, axis labels, and axis limits interactively

## Development

```bash
git clone https://github.com/VForiel/Plt-Edit.git
cd Plt-Edit
pip install -e ".[dev]"
pytest
```
