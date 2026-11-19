"""Peenra illustratsioon perspektiivis (eestvaade). Sama paigutus kui plaanil.

Pilt on ka sisend fotorealistliku pildi tegemiseks: mudel saab sellelt kompositsiooni, kõrgused ja värvid.
"""
from __future__ import annotations
import io
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _hex(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def build_illustration(lines, layout: dict, month: int = 7, seed: int = 3, size=(2000, 1070)) -> bytes:
    rng = np.random.default_rng(seed)
    L, Wd = layout["L"], layout["W"]
    SS = 2
    FW, FH = size[0], size[1] + 130
    W, H = FW * SS, FH * SS

    # kaamera: peenar täidab ~85% laiusest
    span = max(L, Wd * 0.8)
    C = np.array([L / 2, -1.08 * span - 0.0, min(4.5, max(1.5, 0.31 * span))])
    T = np.array([L / 2, Wd * 0.5, 0.11 * span])
    fw = T - C; fw /= np.linalg.norm(fw)
    rt = np.cross(fw, [0, 0, 1]); rt /= np.linalg.norm(rt)
    up = np.cross(rt, fw)
    F = 2150 * SS * 5.0 / span

    def proj(p):
        v = np.asarray(p, float) - C
        z = v @ fw
        return (W / 2 + F * (v @ rt) / z, H * 0.53 - F * (v @ up) / z, z)

    def sc_at(p):
        return F / ((np.asarray(p, float) - C) @ fw)

    def jit(c, a=14):
        return tuple(int(max(0, min(255, v + rng.integers(-a, a + 1)))) for v in c)

    img = Image.new("RGB", (W, H))
    dr = ImageDraw.Draw(img)
    horizon = proj([L / 2, Wd + 60 * span, 0])[1]
    sky_top, sky_bot = (176, 203, 222), (232, 238, 236)
    for y in range(H):
        dr.line([(0, y), (W, y)], fill=_mix(sky_top, sky_bot, min(1, max(0, y / max(1, horizon)))))
    bg = Image.new("RGBA", (W, H), (150, 170, 140, 0)); bd = ImageDraw.Draw(bg)
    for _ in range(260):
        x = rng.uniform(-200, W + 200); r = rng.uniform(80, 220) * SS / 2
        yb = horizon + rng.uniform(-10, 30); hgt = rng.uniform(250, 620) * SS / 2
        col = _mix(jit((80, 108, 72), 14), sky_bot, 0.5)
        for _ in range(6):
            ox = rng.uniform(-r * .8, r * .8); oy = rng.uniform(0, hgt); rr = r * rng.uniform(.6, 1.0)
            bd.ellipse([x + ox - rr, yb - oy - rr, x + ox + rr, yb - oy + rr], fill=_mix(col, (60, 88, 56), rng.uniform(0, .25)) + (255,))
    for _ in range(500):
        x = rng.uniform(-100, W + 100); r = rng.uniform(40, 90) * SS / 2; y = horizon - rng.uniform(0, 160) * SS / 2
        bd.ellipse([x - r, y - r, x + r, y + r], fill=_mix(jit((88, 118, 72), 16), sky_bot, .3) + (255,))
    bg = bg.filter(ImageFilter.GaussianBlur(9 * SS))
    img.paste(bg, (0, 0), bg)
    dr = ImageDraw.Draw(img)
    for y in range(int(horizon), H):
        t = max(0, (y - horizon) / (H - horizon))
        dr.line([(0, y), (W, y)], fill=_mix((150, 168, 118), (96, 132, 62), min(1, t ** .6)))
    for _ in range(26000):
        x = rng.uniform(0, W); y = rng.uniform(horizon, H); t = (y - horizon) / (H - horizon)
        ln = (3 + 22 * t) * SS / 2
        dr.line([(x, y), (x + rng.uniform(-ln * .3, ln * .3), y - ln)], fill=jit((int(92 + 30 * t), int(128 + 20 * t), 60), 18), width=max(1, int(1 + 2 * t)))
    img = img.filter(ImageFilter.GaussianBlur(0.6 * SS))
    band = img.crop((0, int(horizon - 40 * SS), W, int(horizon + 40 * SS))).filter(ImageFilter.GaussianBlur(14 * SS))
    img.paste(band, (0, int(horizon - 40 * SS)))
    dr = ImageDraw.Draw(img)

    corners3 = [(0, 0, 0), (L, 0, 0), (L, Wd, 0), (0, Wd, 0)]
    corners = [proj(p)[:2] for p in corners3]
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon(corners, fill=255)
    mul = Image.new("RGB", (W, H), (84, 64, 46)); md = ImageDraw.Draw(mul)
    for _ in range(int(30000 * max(1, L * Wd / 20) ** .5)):
        x = rng.uniform(0, L); y = rng.uniform(0, Wd)
        sx, sy, _ = proj([x, y, 0]); s = sc_at([x, y, 0]) * 0.012
        md.ellipse([sx - s, sy - s * .45, sx + s, sy + s * .45], fill=jit((92, 70, 50), 22))
    img.paste(mul, (0, 0), mask)
    dr = ImageDraw.Draw(img)
    for a in range(4):
        dr.line([corners[a], corners[(a + 1) % 4]], fill=(70, 70, 66), width=int(4 * SS))

    # --- joonistusabilised ---
    def leaf(cx, cy, ln, wd, ang, col):
        ca, sa = math.cos(ang), math.sin(ang)
        pts = []
        for t in np.linspace(0, math.pi * 2, 10, endpoint=False):
            u = ln / 2 * math.cos(t); v = wd / 2 * math.sin(t) * (1 - 0.3 * math.cos(t))
            pts.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
        dr.polygon(pts, fill=col)

    def dot(cx, cy, r, col):
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    def stem(p0, p1, col, wpx):
        a = proj(p0); b = proj(p1)
        dr.line([a[:2], b[:2]], fill=col, width=max(1, int(wpx)))

    def mound(x, y, w, h, col, n=60, lenf=0.11):
        pts = []
        for _ in range(n):
            a = rng.uniform(0, 2 * math.pi); r = math.sqrt(rng.uniform(0, 1)) * w / 2
            zz = h * math.sqrt(max(0, 1 - (r / (w / 2 + 1e-9)) ** 2)) * rng.uniform(.75, 1)
            pts.append((x + r * math.cos(a), y + r * math.sin(a), zz))
        pts.sort(key=lambda p: -(np.array(p) - C) @ fw)
        for p in pts:
            sx, sy, _ = proj(p); s = sc_at(p)
            shade = 0.75 + 0.35 * (p[2] / (h + 1e-9))
            c = tuple(int(min(255, v * shade)) for v in jit(col, 12))
            leaf(sx, sy, s * lenf * w * 2.2, s * lenf * w * 1.1, rng.uniform(0, math.pi), c)
        return pts

    def shadow(x, y, r):
        sx, sy, _ = proj([x + .03, y + .03, 0]); s = sc_at([x, y, 0])
        dr.ellipse([sx - r * s, sy - r * s * .38, sx + r * s, sy + r * s * .38], fill=(66, 50, 37))

    def daisy(sx, sy, r, petal, center, n=12, tilt=.55):
        for kk in range(n):
            a = 2 * math.pi * kk / n + rng.uniform(-.1, .1)
            leaf(sx + math.cos(a) * r * .55, sy + math.sin(a) * r * .55 * tilt, r * .95, r * .32, math.atan2(math.sin(a) * tilt, math.cos(a)), jit(petal, 8))
        dot(sx, sy, r * .32, jit(center, 10))

    def head(kind, sx, sy, sc, fl):
        if kind == "daisy":
            daisy(sx, sy, sc * .028, fl, (232, 176, 30))
        elif kind == "cone":
            for kk in range(13):
                a = 2 * math.pi * kk / 13
                leaf(sx + math.cos(a) * sc * .026, sy + sc * .012 + abs(math.sin(a)) * sc * .006, sc * .04, sc * .011, math.atan2(.9, math.cos(a) * 2.2), jit(fl, 10))
            dot(sx, sy - sc * .004, sc * .015, jit((150, 80, 30) if fl[0] > 200 and fl[1] > 150 else (176, 92, 34), 10))
        elif kind in ("umbel", "flat"):
            for kk in range(40):
                a = rng.uniform(0, 2 * math.pi); r = math.sqrt(rng.uniform()) * sc * .04
                dot(sx + math.cos(a) * r, sy + math.sin(a) * r * .4, sc * .005, jit(fl, 10))
        elif kind in ("spray",):
            for kk in range(18):
                dot(sx + rng.uniform(-1, 1) * sc * .012, sy - rng.uniform(0, 1) * sc * .05, sc * .007, jit(fl, 12))
        elif kind in ("iris", "lily", "big"):
            r = sc * (.03 if kind != "big" else .045)
            for kk in range(6 if kind != "big" else 14):
                a = 2 * math.pi * kk / (6 if kind != "big" else 14)
                leaf(sx + math.cos(a) * r * .5, sy + math.sin(a) * r * .35, r * 1.1, r * .45, a, jit(fl, 10))
            dot(sx, sy, r * .25, jit(_mix(fl, (240, 220, 120), .5), 8))
        elif kind in ("plume_color",):
            for kk in range(25):
                dot(sx + rng.uniform(-1, 1) * sc * .01, sy - rng.uniform(0, 1) * sc * .06, sc * .006, jit(fl, 12))
        else:   # cluster, ball, five, dots ...
            for kk in range(14):
                dot(sx + rng.uniform(-1, 1) * sc * .016, sy + rng.uniform(-1, .6) * sc * .014, sc * .009, jit(fl, 16))

    def draw_plant(pl):
        ln = lines[pl["s"]]; p = ln.plant; x, y = pl["x"], pl["y"]
        leafc = _hex(p.leaf_hex); fl = _hex(p.flower_hex); bloom = month in p.bloom
        k = rng.uniform(.88, 1.12)
        w = min(p.width, p.spacing * 1.2) * k
        h = p.height * k
        form = p.form
        if form in ("tree", "conifer"):
            h = min(h, 2.2 + 0.4 * span)
        shadow(x, y, w * .38)
        if form == "grass":
            sx, sy, _ = proj([x, y, 0]); sc = sc_at([x, y, 0])
            for _ in range(55):
                a = rng.uniform(-1.3, 1.3); lnp = h * rng.uniform(.6, 1.0) * sc
                ex = sx + math.sin(a) * lnp * .55; ey = sy - math.cos(a) * lnp
                dr.line([(sx + rng.uniform(-3, 3) * SS, sy), ((sx + ex) / 2 + a * 4, (sy + ey) / 2), (ex, ey)], fill=jit(leafc, 16), width=max(1, int(sc * .006)))
            if bloom or (p.bloom and month > p.bloom[0]):
                plume = (196, 180, 124) if p.flower_en in ("", "brown", "golden", "silvery") else fl
                for _ in range(9 if h < .6 else 16):
                    a = rng.uniform(-.6, .6); lnp = h * 1.3 * sc
                    ex, ey = sx + math.sin(a) * lnp * .5, sy - math.cos(a) * lnp
                    dr.line([(sx, sy), (ex, ey)], fill=(176, 162, 112), width=max(1, int(sc * .004)))
                    leaf(ex, ey, sc * .05 * max(1, h * 2), sc * .012 * max(1, h), -math.pi / 2 + a, jit(plume, 10))
            return
        if form == "spike":
            mound(x, y, w * 1.1, .14, leafc, n=26, lenf=.18)
            stem([x, y, .1], [x + .02, y, h], (86, 110, 62), sc_at([x, y, .5]) * .012)
            for _ in range(70):
                t = rng.uniform(.4, 1.0); zz = h * t
                sx, sy, _ = proj([x + .02 * t, y, zz]); sc = sc_at([x, y, zz])
                ox = rng.uniform(-1, 1) * sc * .035 * (1.2 - t)
                if bloom and rng.uniform() < .85:
                    dot(sx + ox, sy, sc * .012, jit(fl, 12))
                else:
                    dot(sx + ox, sy, sc * .008, jit((120, 140, 80), 10))
            return
        if form == "fern":
            sx, sy, _ = proj([x, y, 0]); sc = sc_at([x, y, 0])
            for _ in range(14):
                a = rng.uniform(-1.2, 1.2); lnp = h * rng.uniform(.7, 1.0) * sc
                ex = sx + math.sin(a) * lnp * .7; ey = sy - math.cos(a) * lnp * .9
                for t in np.linspace(.15, 1, 9):
                    px, py = sx + (ex - sx) * t, sy + (ey - sy) * t
                    leaf(px, py, sc * .08 * (1.1 - t), sc * .02, a + 1.4, jit(leafc, 10))
                    leaf(px, py, sc * .08 * (1.1 - t), sc * .02, a - 1.4 + math.pi, jit(leafc, 10))
            return
        if form in ("conifer", "conifer_shrub"):
            dark = _mix(leafc, (30, 50, 35), .2)
            n = int(60 + 120 * h)
            for _ in range(n):
                t = rng.uniform(0, 1); zz = h * t
                rr = (w / 2) * (1 - t) ** (0.9 if p.height > p.width else 0.4) * rng.uniform(.3, 1)
                a = rng.uniform(0, 2 * math.pi)
                sx, sy, _ = proj([x + rr * math.cos(a), y + rr * math.sin(a), zz]); sc = sc_at([x, y, zz])
                leaf(sx, sy, sc * .07 * max(.4, w), sc * .035 * max(.4, w), rng.uniform(0, math.pi), jit(dark, 14))
            return
        if form == "tree":
            stem([x, y, 0], [x, y, h * .45], (92, 74, 58), sc_at([x, y, h * .3]) * .05)
            cr = min(p.width, h * .7) / 2
            pts = []
            for _ in range(260):
                a = rng.uniform(0, 2 * math.pi); r = math.sqrt(rng.uniform()) * cr
                zz = h * .45 + cr + (rng.uniform(-1, 1) * cr * math.sqrt(max(0, 1 - (r / cr) ** 2)))
                pts.append((x + r * math.cos(a), y + r * math.sin(a), zz))
            pts.sort(key=lambda q: -(np.array(q) - C) @ fw)
            for q in pts:
                sx, sy, _ = proj(q); sc = sc_at(q)
                leaf(sx, sy, sc * .16, sc * .09, rng.uniform(0, math.pi), jit(leafc, 16))
                if bloom and rng.uniform() < .25:
                    dot(sx, sy, sc * .03, jit(fl, 10))
            return
        if form in ("shrub",):
            pts = mound(x, y, w, h, leafc, n=int(80 + 140 * w * max(h, .5)), lenf=.06)
            if bloom:
                for _ in range(int(25 + 30 * w)):
                    q = pts[rng.integers(len(pts))]; sx, sy, _ = proj([q[0], q[1], q[2] + .02]); sc = sc_at(q)
                    head("umbel" if p.head == "umbel" else "cluster", sx, sy, sc * 1.4, fl)
            return
        if form in ("mound", "ground"):
            hh = h * (.8 if form == "mound" else 1.0)
            pts = mound(x, y, w, hh, leafc, n=55 if form == "mound" else 40, lenf=.12)
            if bloom:
                if p.head == "spikelets":
                    for _ in range(40):
                        q = pts[rng.integers(len(pts))]
                        stem([q[0], q[1], q[2]], [q[0] + rng.uniform(-.03, .03), q[1], q[2] + .14], (120, 140, 120), sc_at(q) * .003)
                        for t in np.linspace(0, 1, 7):
                            zz = q[2] + .04 + .1 * t; sx, sy, _ = proj([q[0], q[1], zz]); sc = sc_at([q[0], q[1], zz])
                            dot(sx + rng.uniform(-1, 1) * sc * .006, sy, sc * .007, jit(fl, 14))
                else:
                    for _ in range(30 if p.head != "dots" else 45):
                        q = pts[rng.integers(len(pts))]; sx, sy, _ = proj([q[0], q[1], q[2] + .02]); sc = sc_at(q)
                        if p.head == "five":
                            for qq in range(5):
                                a = qq * 1.2566
                                dot(sx + math.cos(a) * sc * .009, sy + math.sin(a) * sc * .006, sc * .008, jit(fl, 10))
                            dot(sx, sy, sc * .004, _mix(fl, (255, 255, 255), .5))
                        elif p.head == "dots":
                            dot(sx, sy, sc * .008, jit(fl, 14)); dot(sx, sy, sc * .003, _mix(fl, (255, 255, 255), .7))
                        else:
                            head(p.head, sx, sy, sc * .8, fl)
            return
        # püstine püsik
        mound(x, y, w * .9, h * .45, leafc, n=40, lenf=.13)
        n = 6 + int(rng.integers(0, 4))
        heads = []
        for _ in range(n):
            a = rng.uniform(0, 2 * math.pi); r = rng.uniform(0, w * .28)
            heads.append((x + r * math.cos(a) * .4, y + r * math.sin(a) * .4, x + r * math.cos(a), y + r * math.sin(a), h * rng.uniform(.82, 1.05)))
        heads.sort(key=lambda q: -(np.array(q[2:]) - C) @ fw)
        for bx, by, tx, ty, tz in heads:
            sc = sc_at([tx, ty, tz])
            stem([bx, by, h * .25], [tx, ty, tz], (78, 112, 58), sc * .006)
            for q in range(3):
                zz = h * .35 + q * (tz - h * .35) / 3
                sx, sy, _ = proj([bx + (tx - bx) * zz / tz, by + (ty - by) * zz / tz, zz])
                leaf(sx, sy, sc * .06, sc * .016, (0.5 if q % 2 else 2.6), jit(leafc, 10))
            sx, sy, _ = proj([tx, ty, tz])
            if bloom:
                head(p.head, sx, sy, sc, fl)
            else:
                dot(sx, sy, sc * .012, jit((130, 150, 80), 10))

    for pl in sorted(layout["plants"], key=lambda q: -((np.array([q["x"], q["y"], 0]) - C) @ fw)):
        draw_plant(pl)

    arr = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    arr *= (1 - 0.08 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2))[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((FW, FH), Image.LANCZOS).crop((0, 20, FW, FH - 110))
    buf = io.BytesIO(); img.save(buf, format="PNG")
    return buf.getvalue()
