try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
except Exception:
    plt = None
    patches = None

def draw_memory(blocks, total_size, title="Memoria"):
    if plt is None:
        print(title)
        print("Direccion:", 0, "->", total_size)
        for b in blocks:
            end = b.start + b.size
            if b.locked:
                label = "LOCK"
            elif b.pid is None:
                label = "FREE"
            else:
                label = f"PID {b.pid}"
            print(f"[{b.start}-{end}] {label} size={b.size}")
        return
    fig, ax = plt.subplots(figsize=(12, 2))
    y = 0.3
    h = 0.45

    for b in blocks:
        rect = patches.Rectangle((b.start, y), b.size, h,
                                 edgecolor="black", facecolor="none")
        ax.add_patch(rect)

        label = ""
        if b.locked:
            label = "LOCK"
        elif b.pid is None:
            label = f"FREE\n{b.size}"
        else:
            label = f"PID {b.pid}\n{b.size}"

        ax.text(
            b.start + b.size/2, y + h/2,
            label,
            ha="center", va="center", fontsize=8
        )

    ax.set_xlim(0, total_size)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_title(title)
    ax.set_xlabel("Dirección")
    plt.tight_layout()
    plt.show()
