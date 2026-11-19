"""Fotorealistlik pilt OpenAI pildimudeliga (images/edits): illustratsioon + automaatne kirjeldus."""
from __future__ import annotations
import base64
import requests

MONTH_EN = {4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October"}
DEFAULT_MODEL = "gpt-image-2.5-sunburst"


def build_prompt(lines, layout: dict, month: int = 7, extra: str = "") -> str:
    W = layout["W"]
    # liigi keskmine sügavus -> ees / keskel / taga
    ys = {}
    for p in layout["plants"]:
        ys.setdefault(p["s"], []).append(p["y"])
    rows = {"front": [], "middle": [], "back": []}
    for i, ln in enumerate(lines):
        if i not in ys:
            continue
        m = sum(ys[i]) / len(ys[i]) / W
        key = "front" if m < .34 else ("middle" if m < .67 else "back")
        rows[key].append(ln)

    def desc(ln):
        p = ln.plant
        h = (f"{p.height:.2f}".rstrip("0").rstrip(".")) + " m tall"
        if month in p.bloom:
            col = f"{p.flower_en} flowers" if p.flower_en else "in flower"
            state = f"in bloom, {col}"
        elif p.form in ("grass",):
            state = "foliage clumps"
        elif p.bloom and month < p.bloom[0]:
            state = "green foliage, not yet flowering"
        elif p.bloom:
            state = "finished flowering, green foliage"
        else:
            state = "foliage"
        return f"{p.latin} ({h}, {state})"

    parts = []
    for key, label in (("front", "Front"), ("middle", "Middle"), ("back", "Back")):
        if rows[key]:
            parts.append(f"{label}: " + "; ".join(desc(l) for l in rows[key]) + ".")
    view = "eye-level view from the front" if layout.get("view", "front") == "front" else "eye-level view, island bed seen from one side"
    txt = (
        "Turn this illustration into a realistic photograph of the same planted garden bed. "
        "Keep the exact layout: the bed shape, the position and size of every plant group, plant heights and colours must match the illustration. "
        f"Planting bed {layout['L']:.1f} × {layout['W']:.1f} m with dark bark mulch and thin steel edging, mown lawn around it, "
        f"Estonian garden in {MONTH_EN.get(month, 'July')}, mature plants two years after planting, soft natural daylight, {view}, 35 mm lens. "
        "Plants (use these exact species): " + " ".join(parts) + " "
        "Natural, slightly wild look with plants grown together, no bare soil between them. No people, no text, no labels."
    )
    if extra:
        txt += " " + extra.strip()
    return txt


def generate_photo(api_key: str, illustration_png: bytes, prompt: str, model: str = DEFAULT_MODEL,
                   size: str = "1536x1024", quality: str = "medium", timeout: int = 240) -> bytes:
    """Saadab illustratsiooni ja kirjelduse OpenAI images/edits otspunkti. Tagastab PNG baidid."""
    r = requests.post(
        "https://api.openai.com/v1/images/edits",
        headers={"Authorization": f"Bearer {api_key}"},
        files={"image": ("illustratsioon.png", illustration_png, "image/png")},
        data={"model": model, "prompt": prompt, "size": size, "quality": quality, "n": "1"},
        timeout=timeout,
    )
    if r.status_code != 200:
        try:
            msg = r.json().get("error", {}).get("message", r.text)
        except ValueError:
            msg = r.text
        raise RuntimeError(f"OpenAI vastas veaga {r.status_code}: {msg}")
    item = r.json()["data"][0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        return requests.get(item["url"], timeout=60).content
    raise RuntimeError("OpenAI vastuses polnud pilti.")
