"""Taimede paigutus ristkülikukujulisele peenrale.

Iga liik saab 1–3 gruppi (triivi). Grupid paigutatakse kõrguse järgi: madalad ees (y = 0), kõrged taga.
Gruppide pindala tasakaalustatakse kaalutud Voronoi (power diagram) abil, taimed paigutatakse grupi sisse
Lloydi algoritmiga, et vahekaugus oleks ühtlane.
"""
from __future__ import annotations
import math
import numpy as np
import contourpy
from .calc import Line


def make_layout(lines: list[Line], L: float, W: float, seed: int = 7, view: str = "front") -> dict:
    rng = np.random.default_rng(seed)
    area_total = L * W
    res = max(0.02, math.sqrt(area_total / 60000))
    nx, ny = max(10, int(L / res)), max(10, int(W / res))
    xs = (np.arange(nx) + 0.5) * L / nx
    ys = (np.arange(ny) + 0.5) * W / ny
    GX, GY = np.meshgrid(xs, ys)
    P = np.stack([GX.ravel(), GY.ravel()], 1)
    cell_a = (L / nx) * (W / ny)

    # liigid kõrguse järgi; sihtsügavus = kumulatiivne pindala
    order = sorted(range(len(lines)), key=lambda i: lines[i].plant.height)
    ytar = {}
    cum = 0.0
    for i in order:
        a = lines[i].area
        if view == "island":
            # saarpeenar: kõrged keskel -> "sügavus" = kaugus servast
            ytar[i] = (cum + a / 2) / area_total
        else:
            ytar[i] = W * (cum + a / 2) / area_total
        cum += a

    drift_area = max(0.8, min(3.0, area_total / 16))
    drifts = []
    for i, ln in enumerate(lines):
        if ln.area <= 0 or ln.qty <= 0:
            continue
        n = max(1, min(4, round(ln.area / drift_area)))
        n = min(n, ln.qty)
        for _ in range(n):
            drifts.append([i, ln.area / n])
    D = len(drifts)
    if D == 0:
        return {"L": L, "W": W, "plants": [], "drifts": []}

    seeds = np.zeros((D, 2))
    anchors = np.zeros((D, 2))
    if view == "island":
        cx, cy = L / 2, W / 2
        rings = {}
        for d, (i, _) in enumerate(drifts):
            frac = 1 - ytar[i]          # 1 = serv, 0 = kese
            rings.setdefault(min(3, int(frac * 4)), []).append((d, frac))
        for ring, items in rings.items():
            items = [items[j] for j in rng.permutation(len(items))]
            off = rng.uniform(0, 2 * math.pi)
            for j, (d, frac) in enumerate(items):
                ang = off + 2 * math.pi * j / len(items)
                r = max(frac, 0.08 if len(items) > 1 else 0.0)
                seeds[d] = [cx + math.cos(ang) * r * L * 0.45, cy + math.sin(ang) * r * W * 0.45]
                anchors[d] = seeds[d]
    else:
        row_h = max(0.6, min(1.5, W / 4))
        rows = {}
        for d, (i, _) in enumerate(drifts):
            rows.setdefault(min(int(ytar[i] / row_h), int(W / row_h)), []).append(d)
        for key, ds in rows.items():
            ds = list(rng.permutation(ds))
            for _ in range(30):
                if all(drifts[ds[j]][0] != drifts[ds[j + 1]][0] for j in range(len(ds) - 1)):
                    break
                ds = list(rng.permutation(ds))
            for j, d in enumerate(ds):
                seeds[d] = [(j + 0.5) * L / len(ds) + rng.uniform(-.05, .05) * L / len(ds),
                            ytar[drifts[d][0]] + rng.uniform(-.1, .1)]
    seeds[:, 0] = np.clip(seeds[:, 0], 0.01, L - 0.01)
    seeds[:, 1] = np.clip(seeds[:, 1], 0.01, W - 0.01)

    targets = np.array([a for _, a in drifts])
    wts = np.zeros(D)
    NZ = np.zeros((len(P), D), dtype=np.float32)
    scale = min(L, W) / 4
    for d in range(D):
        for _ in range(3):
            fx, fy = rng.uniform(2, 5, 2) / max(scale, .5); px, py = rng.uniform(0, 6.3, 2)
            NZ[:, d] += 0.06 * scale ** 2 * np.sin(fx * P[:, 0] + px) * np.sin(fy * P[:, 1] + py)

    def anchor_y(d):
        i = drifts[d][0]
        return ytar[i]

    lab = None
    for it in range(240):
        d2 = ((P[:, None, :] - seeds[None, :, :]) ** 2).sum(-1) - wts[None, :] + NZ
        lab = d2.argmin(1)
        areas = np.bincount(lab, minlength=D) * cell_a
        wts += 0.5 * (targets - areas)
        if it % 4 == 3 and it < 190:
            for d in range(D):
                m = lab == d
                if m.any():
                    c = P[m].mean(0)
                    if view == "island":
                        seeds[d] = 0.5 * c + 0.5 * anchors[d]
                    else:
                        seeds[d] = [0.6 * c[0] + 0.4 * seeds[d][0], 0.7 * c[1] + 0.3 * anchor_y(d)]
                else:   # tühjaks jäänud grupp: nihuta juhuslikku kohta
                    seeds[d] = anchors[d] + rng.normal(0, .1, 2) if view == "island" else [rng.uniform(0, L), anchor_y(d)]
    areas = np.bincount(lab, minlength=D) * cell_a
    labels = lab.reshape(ny, nx)

    plants, drift_out = [], []
    xg = np.concatenate([[0], xs, [L]]); yg = np.concatenate([[0], ys, [W]])
    for i, ln in enumerate(lines):
        ds = [d for d in range(D) if drifts[d][0] == i and areas[d] > 0]
        if not ds:
            continue
        tot = sum(areas[d] for d in ds)
        raw = [ln.qty * areas[d] / tot for d in ds]
        cnt = [int(math.floor(x)) for x in raw]
        for j in np.argsort([-(x - math.floor(x)) for x in raw])[:ln.qty - sum(cnt)]:
            cnt[j] += 1
        for d, n in zip(ds, cnt):
            pts = P[lab == d]
            if n <= 0 or len(pts) == 0:
                continue
            n = min(n, len(pts))
            cen = pts[rng.choice(len(pts), n, replace=False)].copy()
            for _ in range(50):
                a = ((pts[:, None, :] - cen[None]) ** 2).sum(-1).argmin(1)
                for k in range(n):
                    m = a == k
                    if m.any():
                        cen[k] = pts[m].mean(0)
            for c in cen:
                plants.append({"s": i, "x": round(float(c[0]), 3), "y": round(float(c[1]), 3)})
            mask = np.zeros((ny + 2, nx + 2)); mask[1:-1, 1:-1] = labels == d
            lines_c = contourpy.contour_generator(xg, yg, mask).lines(0.5)
            poly = max(lines_c, key=len)[::3] if lines_c else []
            poly = np.clip(np.asarray(poly), 0, [L, W]) if len(poly) else []
            drift_out.append({"s": i, "n": int(n), "area": round(float(areas[d]), 2),
                              "cx": round(float(pts[:, 0].mean()), 3), "cy": round(float(pts[:, 1].mean()), 3),
                              "poly": [[round(float(p[0]), 3), round(float(p[1]), 3)] for p in poly]})
    return {"L": L, "W": W, "view": view, "plants": plants, "drifts": drift_out}
