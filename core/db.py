"""Taimede andmebaasi lugemine Excelist ja illustratsiooni parameetrite tuletamine."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
import pandas as pd

MONTHS = {"jaan": 1, "veeb": 2, "märts": 3, "marts": 3, "apr": 4, "aprill": 4, "mai": 5, "juuni": 6, "juuli": 7,
          "aug": 8, "sept": 9, "sep": 9, "okt": 10, "nov": 11, "dets": 12}
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"}

# eestikeelne värvisõna -> (hex, inglise keeles)
COLORS = [
    ("purpurroosa", "#b5317c", "magenta"), ("sinililla", "#8a86dc", "lavender-blue"),
    ("rohekaskollane", "#c9cf6a", "lime-yellow"), ("kollakasvalge", "#f3eec8", "creamy white"),
    ("valkjasroosa", "#f2d4dc", "pale pink"), ("roosakas", "#efc2cf", "pale pink"),
    ("roosa", "#d8609a", "pink"), ("lilla", "#7a52c6", "purple"), ("sinine", "#4f6fd0", "blue"),
    ("punane", "#c8323c", "red"), ("oranž", "#e8822a", "orange"), ("kollane", "#eabf1c", "yellow"),
    ("valge", "#f6f5ee", "white"), ("pruun", "#a07a4a", "brown"), ("kuld", "#d4a536", "golden"),
    ("hõbe", "#d7dacb", "silvery"),
]
LEAF = {"Okaspuu": "#3f6b4a", "Igihaljas põõsas": "#4a7350", "Kõrreline": "#8aa08a"}

# kujud illustratsioonil
FORMS = {"püsik-padi": "mound", "püsik-püstine": "upright", "tõlvik": "spike", "kõrreline": "grass",
         "põõsas": "shrub", "okaspõõsas": "conifer_shrub", "puu": "tree", "okaspuu": "conifer", "pinnakate": "ground"}

# õie tüüp perekonna järgi
HEAD_BY_GENUS = {
    "Leucanthemum": "daisy", "Anthemis": "daisy", "Rudbeckia": "cone", "Echinacea": "cone",
    "Achillea": "umbel", "Filipendula": "umbel", "Hydrangea": "umbel", "Sambucus": "umbel",
    "Verbascum": "spike", "Lythrum": "spike", "Lupinus": "spike", "Digitalis": "spike",
    "Nepeta": "spikelets", "Salvia": "spikelets", "Lavandula": "spikelets", "Veronica": "spikelets",
    "Geranium": "five", "Dianthus": "dots", "Armeria": "ball", "Campanula": "cluster",
    "Iris": "iris", "Hemerocallis": "lily", "Paeonia": "big", "Rosa": "five", "Calamagrostis": "plume",
    "Miscanthus": "plume", "Deschampsia": "plume", "Molinia": "plume", "Festuca": "plume",
    "Phlox": "cluster", "Astilbe": "plume_color", "Solidago": "spray", "Hylotelephium": "flat",
    "Sedum": "dots", "Phedimus": "dots", "Thymus": "dots", "Primula": "cluster",
}


@dataclass
class Plant:
    name: str
    latin: str
    type: str
    spacing: float
    height: float
    width: float
    price: float | None = None
    hedge: float | None = None
    sale_form: str = ""
    light: str = ""
    bloom_text: str = ""
    flower_text: str = ""
    notes: str = ""
    native: str = ""
    bloom: list = field(default_factory=list)
    flower_hex: str = "#dddddd"
    flower_en: str = ""
    leaf_hex: str = "#5d8a48"
    form: str = "mound"
    head: str = "cluster"

    @property
    def density(self) -> float:
        return 1.0 / self.spacing ** 2

    @property
    def bloom_roman(self) -> str:
        if not self.bloom:
            return "–"
        return ROMAN[self.bloom[0]] if len(self.bloom) == 1 else f"{ROMAN[self.bloom[0]]}–{ROMAN[self.bloom[-1]]}"


def parse_bloom(text) -> list:
    if not isinstance(text, str) or not text.strip():
        return []
    t = text.lower().replace("-", "–")
    found = []
    for part in re.split(r"[–,/ ]+", t):
        part = part.strip(". ")
        for k, v in MONTHS.items():
            if part.startswith(k):
                found.append(v); break
    if not found:
        return []
    if len(found) >= 2 and "–" in t:
        a, b = found[0], found[-1]
        return list(range(a, b + 1)) if b >= a else list(range(a, 13)) + list(range(1, b + 1))
    return sorted(set(found))


def parse_color(text):
    if not isinstance(text, str):
        return None, ""
    t = text.lower()
    best = None
    for word, hx, en in COLORS:
        i = t.find(word)
        if i >= 0 and (best is None or i < best[0]):
            best = (i, hx, en)
    return (best[1], best[2]) if best else (None, "")


def _num(v):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)) or v == "":
            return None
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def _str(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()


def _col(df, *names):
    low = {c.lower().strip(): c for c in df.columns}
    for n in names:
        for lc, c in low.items():
            if lc.startswith(n.lower()):
                return c
    return None


def derive_visual(p: Plant, form_override: str = "", color_override: str = ""):
    p.bloom = parse_bloom(p.bloom_text)
    hx, en = parse_color(p.flower_text)
    p.flower_hex = color_override if re.fullmatch(r"#[0-9a-fA-F]{6}", color_override or "") else (hx or "#eeeeee")
    p.flower_en = en
    p.leaf_hex = LEAF.get(p.type, "#5d8a48")
    genus = p.latin.split()[0] if p.latin else ""
    if form_override and form_override in FORMS:
        p.form = FORMS[form_override]
    elif p.type == "Kõrreline":
        p.form = "grass"
    elif p.type == "Pinnakate":
        p.form = "ground"
    elif p.type == "Lehtpõõsas":
        p.form = "shrub"
    elif p.type == "Igihaljas põõsas":
        p.form = "shrub" if genus in ("Rhododendron", "Calluna") else "conifer_shrub"
    elif p.type == "Lehtpuu":
        p.form = "tree"
    elif p.type == "Okaspuu":
        p.form = "conifer"
    elif genus in ("Verbascum", "Lythrum"):
        p.form = "spike"
    elif p.height >= 0.45:
        p.form = "upright"
    else:
        p.form = "mound"
    p.head = HEAD_BY_GENUS.get(genus, "cluster")
    if genus in ("Matteuccia", "Dryopteris"):
        p.form, p.head = "fern", "none"
    if genus == "Hosta":
        p.head = "spikelets"
    return p


def load_db(src) -> dict[str, Plant]:
    """src = failitee või üleslaaditud fail. Tagastab {nimi: Plant}."""
    xl = pd.ExcelFile(src)
    sheet = "Taimed" if "Taimed" in xl.sheet_names else xl.sheet_names[0]
    df = xl.parse(sheet)
    c = {k: _col(df, *v) for k, v in {
        "name": ["taim"], "latin": ["ladina"], "type": ["tüüp", "tyyp"], "spacing": ["istutusvahe"],
        "hedge": ["hekis"], "sale": ["müügivorm"], "price": ["hind"], "h": ["kõrgus"], "w": ["laius"],
        "light": ["valgus"], "bloom": ["õitseb"], "flower": ["õis"], "notes": ["märkus"], "native": ["pärismaine"],
        "form": ["kuju"], "color": ["õievärv"]}.items()}
    missing = [k for k in ("name", "latin", "type", "spacing", "h", "w") if c[k] is None]
    if missing:
        raise ValueError("Exceli failis puuduvad veerud: " + ", ".join(missing))
    out = {}
    for _, r in df.iterrows():
        name = _str(r[c["name"]])
        sp, h, w = _num(r[c["spacing"]]), _num(r[c["h"]]), _num(r[c["w"]])
        if not name or not sp or sp <= 0 or h is None or w is None:
            continue
        g = lambda k: r[c[k]] if c[k] is not None else None
        p = Plant(name=name, latin=_str(g("latin")), type=_str(g("type")), spacing=sp, height=h, width=w,
                  price=_num(g("price")), hedge=_num(g("hedge")), sale_form=_str(g("sale")), light=_str(g("light")),
                  bloom_text=_str(g("bloom")), flower_text=_str(g("flower")), notes=_str(g("notes")),
                  native=_str(g("native")))
        out[name] = derive_visual(p, _str(g("form")), _str(g("color")))
    return out
