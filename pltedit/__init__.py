"""
Plt-Edit: Save and load matplotlib figures as .plt files.

The .plt file format is a NumPy archive (.npz) with a .plt extension
that stores the serialized figure along with metadata (creation date,
Python version, matplotlib version, and Plt-Edit version).

Basic usage::

    import matplotlib.pyplot as plt
    import plt_edit

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])

    # Save the figure
    plt_edit.save(fig, "my_figure.plt")

    # Load the figure later
    fig2 = plt_edit.load("my_figure.plt")
    plt.show()
"""

from pltedit._io import save, load
from pltedit._version import __version__

__all__ = ["save", "load", "__version__"]
