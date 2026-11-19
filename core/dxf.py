"""Istutusplaani eksport DXF R12 (AC1009) kujul. Ühikud meetrites."""
from __future__ import annotations
from datetime import date

ACI_CYCLE = [51, 230, 132, 212, 171, 182, 30, 241, 50, 221, 40, 42, 92, 150, 10, 200, 62, 112, 190, 20]


def _f(v):
    return f"{v:.2f}".replace(".", ",")


def build_dxf(project: dict, lines, layout: dict) -> bytes:
    L, W = layout["L"], layout["W"]
    k = max(L, W) / 5.0                     # tekstide ja legendi mõõtkava
    out = []
    g = lambda c, v: out.append(f"{c}\n{v}")
    lname = lambda ln: f"TAIM_{ln.nr:02d}"
    layers = [("PEENAR", 7), ("MOOTMED", 8), ("TRIIVID", 8), ("TRIIVI_TEKST", 7), ("LEGEND", 7), ("KIRJANURK", 7)]
    layers += [(lname(ln), ACI_CYCLE[(ln.nr - 1) % len(ACI_CYCLE)]) for ln in lines]

    g(0, "SECTION"); g(2, "HEADER")
    g(9, "$ACADVER"); g(1, "AC1009"); g(9, "$DWGCODEPAGE"); g(3, "ANSI_1257")
    g(9, "$INSBASE"); g(10, 0.0); g(20, 0.0); g(30, 0.0)
    g(9, "$EXTMIN"); g(10, -1.0 * k); g(20, -2.6 * k); g(30, 0.0)
    g(9, "$EXTMAX"); g(10, L + 9 * k); g(20, W + 0.5 * k); g(30, 0.0)
    g(0, "ENDSEC")
    g(0, "SECTION"); g(2, "TABLES")
    g(0, "TABLE"); g(2, "LTYPE"); g(70, 1)
    g(0, "LTYPE"); g(2, "CONTINUOUS"); g(70, 0); g(3, "Solid line"); g(72, 65); g(73, 0); g(40, 0.0)
    g(0, "ENDTAB")
    g(0, "TABLE"); g(2, "LAYER"); g(70, len(layers))
    for n, c in layers:
        g(0, "LAYER"); g(2, n); g(70, 0); g(62, c); g(6, "CONTINUOUS")
    g(0, "ENDTAB")
    g(0, "TABLE"); g(2, "STYLE"); g(70, 1)
    g(0, "STYLE"); g(2, "STANDARD"); g(70, 0); g(40, 0.0); g(41, 1.0); g(50, 0.0); g(71, 0); g(42, 0.1); g(3, "arial.ttf"); g(4, "")
    g(0, "ENDTAB"); g(0, "ENDSEC")
    g(0, "SECTION"); g(2, "ENTITIES")

    def line(x1, y1, x2, y2, lay):
        g(0, "LINE"); g(8, lay); g(10, f"{x1:.4f}"); g(20, f"{y1:.4f}"); g(30, 0.0); g(11, f"{x2:.4f}"); g(21, f"{y2:.4f}"); g(31, 0.0)

    def poly(pts, lay):
        g(0, "POLYLINE"); g(8, lay); g(66, 1); g(10, 0.0); g(20, 0.0); g(30, 0.0); g(70, 1)
        for x, y in pts:
            g(0, "VERTEX"); g(8, lay); g(10, f"{x:.4f}"); g(20, f"{y:.4f}"); g(30, 0.0)
        g(0, "SEQEND"); g(8, lay)

    def circle(x, y, r, lay):
        g(0, "CIRCLE"); g(8, lay); g(10, f"{x:.4f}"); g(20, f"{y:.4f}"); g(30, 0.0); g(40, f"{r:.4f}")

    def text(x, y, h, s, lay, align=None):
        g(0, "TEXT"); g(8, lay); g(10, f"{x:.4f}"); g(20, f"{y:.4f}"); g(30, 0.0); g(40, f"{h:.3f}"); g(1, s)
        if align:
            g(72, {"center": 1, "right": 2, "middle": 4}[align]); g(11, f"{x:.4f}"); g(21, f"{y:.4f}"); g(31, 0.0)

    poly([(0, 0), (L, 0), (L, W), (0, W)], "PEENAR")
    for dr in layout["drifts"]:
        ln = lines[dr["s"]]
        if len(dr["poly"]) > 2:
            poly(dr["poly"], "TRIIVID")
        text(dr["cx"], dr["cy"], 0.09 * k, f"{ln.nr} - {dr['n']} tk", "TRIIVI_TEKST", "middle")
    for p in layout["plants"]:
        ln = lines[p["s"]]
        circle(p["x"], p["y"], ln.plant.spacing * 0.4, lname(ln))
        circle(p["x"], p["y"], 0.01 * k, lname(ln))

    # mõõtmed
    o = 0.35 * k
    line(0, -o, L, -o, "MOOTMED"); line(-o, 0, -o, W, "MOOTMED")
    for x in (0, L):
        line(x, -0.02 * k, x, -o - 0.06 * k, "MOOTMED"); line(x - .04 * k, -o - .04 * k, x + .04 * k, -o + .04 * k, "MOOTMED")
    for y in (0, W):
        line(-0.02 * k, y, -o - 0.06 * k, y, "MOOTMED"); line(-o - .04 * k, y - .04 * k, -o + .04 * k, y + .04 * k, "MOOTMED")
    text(L / 2, -o + 0.06 * k, 0.1 * k, _f(L), "MOOTMED", "center")
    text(-o - 0.08 * k, W / 2, 0.1 * k, _f(W), "MOOTMED", "right")
    if layout.get("view", "front") == "front":
        text(L / 2, -0.75 * k, 0.1 * k, "ESIKÜLG (vaatesuund)", "MOOTMED", "center")

    # legend
    lx, ly = L + 0.8 * k, W
    text(lx, ly, 0.16 * k, "TAIMEDE LEGEND", "LEGEND")
    cols = [(0, "Tähis"), (0.45, "Nr"), (0.7, "Taim"), (2.6, "Ladinakeelne nimi"), (4.7, "Vahe, m"),
            (5.4, "Kogus, tk"), (6.15, "Kõrgus, m"), (6.95, "Õitseb")]
    y = ly - 0.35 * k
    for dx, t in cols:
        text(lx + dx * k, y, 0.08 * k, t, "LEGEND")
    line(lx, y - 0.07 * k, lx + 7.6 * k, y - 0.07 * k, "LEGEND")
    for ln in lines:
        y -= 0.27 * k
        circle(lx + 0.15 * k, y + 0.04 * k, 0.09 * k, lname(ln))
        vals = [str(ln.nr), ln.plant.name, ln.plant.latin, _f(ln.plant.spacing), str(ln.qty), _f(ln.plant.height), ln.plant.bloom_roman]
        for (dx, _), v in zip(cols[1:], vals):
            text(lx + dx * k, y, 0.08 * k, v, "LEGEND")
    line(lx, y - 0.1 * k, lx + 7.6 * k, y - 0.1 * k, "LEGEND")
    y -= 0.3 * k
    total = sum(ln.qty for ln in lines)
    text(lx + 0.7 * k, y, 0.09 * k, "KOKKU", "LEGEND"); text(lx + 5.4 * k, y, 0.09 * k, str(total), "LEGEND")

    # kirjanurk
    bx, by, bw, bh = L + 0.8 * k, -2.2 * k, 7.6 * k, 1.3 * k
    poly([(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh)], "KIRJANURK")
    line(bx, by + 0.85 * k, bx + bw, by + 0.85 * k, "KIRJANURK")
    line(bx + 4.6 * k, by, bx + 4.6 * k, by + 0.85 * k, "KIRJANURK")
    text(bx + 0.15 * k, by + 1.0 * k, 0.16 * k, f"ISTUTUSPLAAN - {project.get('name', '').upper()}"[:60], "KIRJANURK")
    text(bx + 0.15 * k, by + 0.6 * k, 0.09 * k, f"Pindala {_f(L * W)} m2 | Taimi kokku {total} tk | {len(lines)} liiki", "KIRJANURK")
    text(bx + 0.15 * k, by + 0.4 * k, 0.09 * k, f"Peenar {_f(L)} x {_f(W)} m. Mõõdud meetrites.", "KIRJANURK")
    text(bx + 0.15 * k, by + 0.2 * k, 0.09 * k, "Taime tähise läbimõõt = 0,8 x istutusvahe", "KIRJANURK")
    scale = 50 if max(L, W) <= 8 else (100 if max(L, W) <= 16 else 200)
    text(bx + 4.75 * k, by + 0.6 * k, 0.09 * k, f"Mõõtkava 1:{scale} (A3)", "KIRJANURK")
    text(bx + 4.75 * k, by + 0.4 * k, 0.09 * k, f"Kuupäev {date.today():%d.%m.%Y}", "KIRJANURK")
    text(bx + 4.75 * k, by + 0.2 * k, 0.09 * k, project.get("stage", "Staadium: hinnapäring"), "KIRJANURK")
    g(0, "ENDSEC"); g(0, "EOF")
    return ("\r\n".join(out) + "\r\n").encode("cp1257", errors="replace")
