"""Värviline istutusplaan PNG-na (pealtvaade + legend). Iga liik saab eristuva tähisevärvi."""
from __future__ import annotations
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle

INK, MUTED, SOIL, LINE = "#1f2a22", "#5d6a60", "#d9cbb6", "#d9ddd4"


def _f(v):
    return f"{v:.2f}".replace(".", ",")


def _txt_color(hex_):
    h = hex_.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#ffffff" if (0.299 * r + 0.587 * g + 0.114 * b) < 140 else INK


def build_plan_png(project: dict, lines, layout: dict, dpi=160) -> bytes:
    L, W = layout["L"], layout["W"]
    fig = plt.figure(figsize=(16, 9), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.03, 0.08, 0.52, 0.84])
    k = max(L, W) / 5
    ax.add_patch(Polygon([(0, 0), (L, 0), (L, W), (0, W)], closed=True, fc=SOIL, ec="#444", lw=2, zorder=0))
    for dr in layout["drifts"]:
        ln = lines[dr["s"]]
        if len(dr["poly"]) > 2:
            ax.add_patch(Polygon(dr["poly"], closed=True, fc=ln.color, alpha=.16, ec="#333", lw=1.0, zorder=1))
    for pl in layout["plants"]:
        ln = lines[pl["s"]]
        ax.add_patch(Circle((pl["x"], pl["y"]), ln.plant.spacing * 0.4, fc=ln.color, alpha=.85, ec=(0, 0, 0, .55), lw=.5, zorder=2))
    # grupi silt: number + nimi + kogus
    fs = max(6, min(8.5, 8.5 * 5 / max(L, W, 5) * 1.3))
    for dr in layout["drifts"]:
        ln = lines[dr["s"]]
        name = ln.plant.name if len(ln.plant.name) <= 22 else ln.plant.name[:21] + "…"
        ax.text(dr["cx"], dr["cy"], f"{ln.nr}. {name}\n{dr['n']} tk", ha="center", va="center", fontsize=fs, color=INK,
                zorder=4, linespacing=1.15,
                bbox=dict(boxstyle="round,pad=0.3,rounding_size=0.6", fc="white", ec=ln.color, lw=1.4, alpha=.95))
    o = 0.3 * k
    ax.annotate("", (0, -o), (L, -o), arrowprops=dict(arrowstyle="|-|", color=MUTED, lw=1, shrinkA=0, shrinkB=0))
    ax.text(L / 2, -o - 0.05 * k, f"{_f(L)} m", ha="center", va="top", fontsize=10, color=INK)
    ax.annotate("", (-o, 0), (-o, W), arrowprops=dict(arrowstyle="|-|", color=MUTED, lw=1, shrinkA=0, shrinkB=0))
    ax.text(-o - 0.06 * k, W / 2, f"{_f(W)} m", ha="right", va="center", fontsize=10, color=INK, rotation=90)
    if layout.get("view", "front") == "front":
        ax.text(L / 2, -o - 0.35 * k, "▲ ESIKÜLG · VAATESUUND", ha="center", va="top", fontsize=9, color=MUTED)
    ax.set_xlim(-0.8 * k, L + 0.2 * k); ax.set_ylim(-1.0 * k, W + 0.2 * k)
    ax.set_aspect("equal"); ax.axis("off")

    # legend
    lg = fig.add_axes([0.57, 0.05, 0.42, 0.88]); lg.axis("off")
    lg.set_xlim(0, 1); lg.set_ylim(0, 1)
    lg.text(0, 1.0, project.get("name", "Istutusplaan"), fontsize=15, fontweight="bold", color=INK, va="top")
    tot = sum(l.qty for l in lines)
    lg.text(0, 0.955, f"Pindala {_f(L * W)} m² · {tot} taime · {len(lines)} liiki", fontsize=10, color=MUTED, va="top")
    heads = [(0.0, "Tähis"), (0.085, "Taim"), (0.55, "Õis"), (0.75, "Kõrgus"), (0.86, "Vahe"), (0.95, "Tk")]
    y = 0.895
    for x, t in heads:
        lg.text(x, y, t, fontsize=8.5, color=MUTED, va="center")
    lg.plot([0, 1], [y - 0.02, y - 0.02], color=LINE, lw=1)
    step = min(0.062, 0.78 / max(1, len(lines)))
    for ln in lines:
        y -= step
        p = ln.plant
        lg.add_patch(Rectangle((0.0, y - 0.018), 0.06, 0.036, fc=ln.color, ec=(0, 0, 0, .5), lw=.6))
        lg.text(0.03, y, str(ln.nr), fontsize=9, ha="center", va="center", color=_txt_color(ln.color), fontweight="bold")
        lg.text(0.085, y + 0.010, p.name, fontsize=9.5, color=INK, va="center", fontweight="bold")
        lg.text(0.085, y - 0.014, p.latin, fontsize=8, color=MUTED, va="center", style="italic")
        bloom = p.flower_et or (p.flower_text.split(";")[0][:18] if p.flower_text else "–")
        lg.add_patch(Circle((0.558, y + 0.010), 0.008, fc=p.flower_hex, ec=(0, 0, 0, .4), lw=.5))
        lg.text(0.575, y + 0.010, bloom, fontsize=8.5, color=INK, va="center")
        lg.text(0.55, y - 0.014, p.bloom_text or "–", fontsize=8, color=MUTED, va="center")
        lg.text(0.75, y, f"{_f(p.height)} m", fontsize=9, color=INK, va="center")
        lg.text(0.86, y, f"{_f(p.spacing)} m", fontsize=9, color=INK, va="center")
        lg.text(0.95, y, str(ln.qty), fontsize=9.5, color=INK, va="center", fontweight="bold")
        lg.plot([0, 1], [y - step / 2, y - step / 2], color=LINE, lw=.5)
    lg.text(0.085, y - step * 0.9, "Kokku", fontsize=10, fontweight="bold", color=INK, va="center")
    lg.text(0.95, y - step * 0.9, str(tot), fontsize=10, fontweight="bold", color=INK, va="center")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)
    return buf.getvalue()
