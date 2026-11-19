"""Koguste ja maksumuse arvutus."""
from __future__ import annotations
import math
from dataclasses import dataclass
from .db import Plant


# selgelt eristuvad tähisevärvid plaanile (järjekorras)
PALETTE = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#46c0c0", "#f032e6", "#9a6324",
           "#bcbd22", "#000075", "#fabed4", "#808000", "#ffd8b1", "#aaffc3", "#dcbeff", "#800000",
           "#a9a9a9", "#ffe119", "#469990", "#e6beff"]


@dataclass
class Line:
    nr: int
    plant: Plant
    share: float      # 0..1
    area: float       # m²
    qty: int

    @property
    def color(self):
        return PALETTE[(self.nr - 1) % len(PALETTE)]

    @property
    def total(self):
        return None if self.plant.price is None else self.qty * self.plant.price


def calculate(db: dict, selection: list[tuple[str, float]], length: float, width: float) -> list[Line]:
    """selection: [(taime nimi, osakaal protsentides)]. Kogus = pind × osakaal × 1/vahe², ümardatud üles."""
    total_pct = sum(p for _, p in selection)
    if total_pct <= 0:
        raise ValueError("Osakaalud on nullid.")
    area = length * width
    lines = []
    for i, (name, pct) in enumerate(selection, 1):
        if name not in db:
            raise ValueError(f"Taime '{name}' ei leitud andmebaasist.")
        p = db[name]
        share = pct / 100.0
        a = area * share
        qty = math.ceil(round(a * p.density, 6))
        lines.append(Line(i, p, share, a, qty))
    return lines


def summary(lines: list[Line]) -> dict:
    priced = [l for l in lines if l.total is not None]
    return {
        "qty": sum(l.qty for l in lines),
        "total": sum(l.total for l in priced),
        "missing_prices": [l.plant.name for l in lines if l.plant.price is None],
        "share_sum": sum(l.share for l in lines),
    }
