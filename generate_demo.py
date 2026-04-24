import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# Ensure we have the save function from PltEdit
try:
    from pltedit._io import save
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from pltedit._io import save

def generate_demo_figure():
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle("Plt-Edit Demo Figure", fontsize=18, fontweight='bold')

    # 1. Standard Plot with multiple lines and a text annotation
    ax1 = fig.add_subplot(2, 3, 1)
    x = np.linspace(0, 10, 100)
    ax1.plot(x, np.sin(x), label="Sine", color="blue", linewidth=2)
    ax1.plot(x, np.cos(x), label="Cosine", color="orange", linestyle="--")
    ax1.plot(x, np.sin(x)*np.exp(-x/3), label="Damped", color="green", marker="o", markevery=10)
    ax1.set_title("Standard Lines")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Amplitude")
    ax1.text(5, 0.5, "Annotation", fontsize=12, color="purple", rotation=15)
    ax1.legend()

    # 2. Scatter Plot with colormap and sizes (PathCollection)
    ax2 = fig.add_subplot(2, 3, 2)
    np.random.seed(42)
    x_scat = np.random.rand(50)
    y_scat = np.random.rand(50)
    colors = np.random.rand(50)
    sizes = 1000 * np.random.rand(50)
    sc = ax2.scatter(x_scat, y_scat, c=colors, s=sizes, alpha=0.6, cmap='viridis', edgecolors='black', label="Random points")
    ax2.set_title("Scatter / Collections")
    ax2.set_xlabel("X coordinate")
    ax2.set_ylabel("Y coordinate")
    ax2.legend()
    fig.colorbar(sc, ax=ax2, label="Color intensity")

    # 3. Bar Chart and Patches
    ax3 = fig.add_subplot(2, 3, 3)
    categories = ['A', 'B', 'C', 'D']
    values = [4, 7, 2, 8]
    bars = ax3.bar(categories, values, color="salmon", edgecolor="red", linewidth=1.5, label="Values")
    ax3.set_title("Bar chart (Patches)")
    # Add a custom patch
    rect = Rectangle((-0.4, 0), 0.8, 4, facecolor='none', edgecolor='black', hatch='//', label="Hatched region")
    ax3.add_patch(rect)
    ax3.legend()

    # 4. Imshow / 2D Image
    ax4 = fig.add_subplot(2, 3, 4)
    x_im, y_im = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
    z_im = np.sin(x_im**2 + y_im**2)
    im = ax4.imshow(z_im, extent=[-3, 3, -3, 3], origin='lower', cmap='plasma')
    ax4.set_title("Imshow (Image)")
    fig.colorbar(im, ax=ax4, shrink=0.8)

    # 5. Polar Plot
    ax5 = fig.add_subplot(2, 3, 5, projection='polar')
    theta = np.linspace(0, 2*np.pi, 200)
    r = np.abs(np.sin(2*theta) * np.cos(2*theta))
    ax5.plot(theta, r, color="crimson", linewidth=2, label="Flower")
    ax5.fill(theta, r, color="crimson", alpha=0.3)
    ax5.set_title("Polar Plot", va='bottom')
    ax5.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3))

    # 6. 3D Plot
    ax6 = fig.add_subplot(2, 3, 6, projection='3d')
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R)
    surf = ax6.plot_surface(X, Y, Z, cmap='coolwarm', linewidth=0, antialiased=False, alpha=0.8)
    ax6.set_title("3D Surface")
    fig.colorbar(surf, ax=ax6, shrink=0.5, aspect=5)

    plt.tight_layout()

    # Save to a .plt file supported by PltEdit
    output_filename = "demo.plt"
    save(fig, output_filename)
    print(f"Demo figure generated and saved as '{output_filename}'")
    
    # Also save as PNG for reference
    plt.savefig("demo.png", dpi=150)
    print("Demo figure additionally exported as 'demo.png'")

if __name__ == "__main__":
    generate_demo_figure()
