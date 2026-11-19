"""Kogusetabel Excelisse, ZIP-pakett ja kogu ahela käivitamine."""
from __future__ import annotations
import io
import json
import re
import zipfile
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from .calc import calculate, summary
from .layout import make_layout
from .dxf import build_dxf
from .plan_png import build_plan_png
from .illustration import build_illustration

VAT = 0.24


def build_xlsx(project: dict, lines) -> bytes:
    wb = Workbook(); ws = wb.active; ws.title = "Kogused"
    L, W = project["L"], project["W"]
    ws.append([project.get("name", "Istutusplaan")]); ws["A1"].font = Font(bold=True, size=14)
    ws.append([f"Peenar {L:g} × {W:g} m = {L * W:g} m²   ·   {date.today():%d.%m.%Y}"])
    ws.append([])
    head = ["Nr", "Taim", "Ladinakeelne nimi", "Müügivorm", "Osakaal", "Pind (m²)", "Istutusvahe (m)",
            "Tihedus (tk/m²)", "Kogus (tk)", "Hind (€/tk, km-ta)", "Summa (€, km-ta)", "Õitseb", "Pärismaine"]
    ws.append(head)
    for c in ws[4]:
        c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="EEF1EA"); c.alignment = Alignment(wrap_text=True)
    first = 5
    for ln in lines:
        r = ws.max_row + 1
        p = ln.plant
        ws.append([ln.nr, p.name, p.latin, p.sale_form, ln.share, round(ln.area, 2), p.spacing,
                   round(p.density, 2), ln.qty, p.price, f"=IF(J{r}=\"\",\"\",I{r}*J{r})", p.bloom_text, p.native])
        ws[f"E{r}"].number_format = "0%"; ws[f"J{r}"].number_format = "0.00"; ws[f"K{r}"].number_format = "0.00"
        ws[f"C{r}"].font = Font(italic=True)
    last = ws.max_row
    ws.append(["", "Kokku", "", "", f"=SUM(E{first}:E{last})", f"=SUM(F{first}:F{last})", "", "", f"=SUM(I{first}:I{last})", "", f"=SUM(K{first}:K{last})"])
    t = ws.max_row
    ws.append(["", f"Käibemaks {int(VAT * 100)}%", "", "", "", "", "", "", "", "", f"=K{t}*{VAT}"])
    ws.append(["", "Kokku km-ga", "", "", "", "", "", "", "", "", f"=K{t}+K{t + 1}"])
    for r in range(t, t + 3):
        ws[f"B{r}"].font = Font(bold=True); ws[f"K{r}"].font = Font(bold=True); ws[f"K{r}"].number_format = "0.00"
    ws[f"E{t}"].number_format = "0%"
    for col, wd in zip("ABCDEFGHIJKLM", [5, 30, 32, 20, 9, 9, 11, 11, 10, 12, 13, 13, 14]):
        ws.column_dimensions[col].width = wd
    ws.freeze_panes = "C5"
    buf = io.BytesIO(); wb.save(buf); return buf.getvalue()


def slug(s: str) -> str:
    s = s.lower()
    for a, b in (("õ", "o"), ("ä", "a"), ("ö", "o"), ("ü", "u"), ("š", "s"), ("ž", "z")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "istutusplaan"


def run_all(db: dict, selection, L: float, W: float, name: str, month: int = 7, view: str = "front", seed: int = 7) -> dict:
    project = {"name": name, "L": L, "W": W}
    lines = calculate(db, selection, L, W)
    layout = make_layout(lines, L, W, seed=seed, view=view)
    res = {
        "project": project, "lines": lines, "layout": layout, "summary": summary(lines),
        "xlsx": build_xlsx(project, lines),
        "dxf": build_dxf(project, lines, layout),
        "plan_png": build_plan_png(project, lines, layout),
    }
    res["illustration"], res["illustration_labeled"] = build_illustration(lines, layout, month=month, with_labels=True)
    return res


def build_zip(res: dict, photo: bytes | None = None) -> bytes:
    base = slug(res["project"]["name"])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{base}_kogused.xlsx", res["xlsx"])
        z.writestr(f"{base}_istutusplaan.dxf", res["dxf"])
        z.writestr(f"{base}_istutusplaan.png", res["plan_png"])
        z.writestr(f"{base}_illustratsioon.png", res["illustration"])
        z.writestr(f"{base}_illustratsioon_tahistega.png", res["illustration_labeled"])
        if photo:
            z.writestr(f"{base}_visuaal.png", photo)
        z.writestr(f"{base}_paigutus.json", json.dumps(res["layout"], ensure_ascii=False))
    return buf.getvalue()
