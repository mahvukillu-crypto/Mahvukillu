"""Värviline istutusplaan PNG-na (pealtvaade + legend)."""
from __future__ import annotations
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch

INK, MUTED, SOIL = "#1f2a22", "#5d6a60", "#7a6048"


def _f(v):
    return f"{v:.2f}".replace(".", ",")


def build_plan_png(project: dict, lines, layout: dict, dpi=160) -> bytes:
    L, W = layout["L"], layout["W"]
    fig = plt.figure(figsize=(16, 9), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.03, 0.08, 0.55, 0.82])
    k = max(L, W) / 5
    ax.add_patch(Polygon([(0, 0), (L, 0), (L, W), (0, W)], closed=True, fc=SOIL, ec="#444", lw=2, zorder=0))
    for dr in layout["drifts"]:
        p = lines[dr["s"]].plant
        if len(dr["poly"]) > 2:
            ax.add_patch(Polygon(dr["poly"], closed=True, fc=p.flower_hex, alpha=.3, ec="white", lw=1.2, zorder=1))
    for pl in layout["plants"]:
        p = lines[pl["s"]].plant
        ax.add_patch(Circle((pl["x"], pl["y"]), p.spacing * 0.4, fc=p.flower_hex, ec=(0, 0, 0, .4), lw=.5, zorder=2))
    for dr in layout["drifts"]:
        ln = lines[dr["s"]]
        ax.text(dr["cx"], dr["cy"], f" {ln.nr} · {dr['n']} tk ", ha="center", va="center", fontsize=8, color=INK, zorder=4,
                bbox=dict(boxstyle="round,pad=0.25,rounding_size=0.8", fc="white", ec=(0, 0, 0, .3), alpha=.92))
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
    lg = fig.add_axes([0.6, 0.08, 0.38, 0.82]); lg.axis("off")
    lg.set_xlim(0, 1); lg.set_ylim(0, 1)
    lg.text(0, 1.0, project.get("name", "Istutusplaan"), fontsize=15, fontweight="bold", color=INK, va="top")
    tot = sum(l.qty for l in lines)
    lg.text(0, 0.955, f"Pindala {_f(L * W)} m² · {tot} taime · {len(lines)} liiki", fontsize=10, color=MUTED, va="top")
    heads = [(0.0, "Nr"), (0.08, "Taim"), (0.62, "Tk"), (0.72, "Vahe, m"), (0.86, "Õitseb")]
    y = 0.89
    for x, t in heads:
        lg.text(x, y, t, fontsize=8.5, color=MUTED, va="center")
    lg.plot([0, 1], [y - 0.018, y - 0.018], color="#d9ddd4", lw=1)
    step = min(0.055, 0.8 / max(1, len(lines)))
    for ln in lines:
        y -= step
        p = ln.plant
        lg.add_patch(Circle((0.022, y), 0.016, fc=p.flower_hex, ec=(0, 0, 0, .35), lw=.6, transform=lg.transData))
        lg.text(0.022, y, str(ln.nr), fontsize=7, ha="center", va="center", color=INK, fontweight="bold")
        lg.text(0.08, y + 0.008, p.name, fontsize=9, color=INK, va="center")
        lg.text(0.08, y - 0.014, p.latin, fontsize=7.5, color=MUTED, va="center", style="italic")
        lg.text(0.62, y, str(ln.qty), fontsize=9, color=INK, va="center")
        lg.text(0.72, y, _f(p.spacing), fontsize=9, color=INK, va="center")
        lg.text(0.86, y, p.bloom_roman, fontsize=9, color=INK, va="center")
    lg.plot([0, 1], [y - 0.03, y - 0.03], color="#d9ddd4", lw=1)
    lg.text(0.08, y - 0.06, "Kokku", fontsize=9.5, fontweight="bold", color=INK, va="center")
    lg.text(0.62, y - 0.06, str(tot), fontsize=9.5, fontweight="bold", color=INK, va="center")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)
    return buf.getvalue()
