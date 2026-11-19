"""Haljastuse pakkumise tööriist – Streamlit rakendus.

Käivitamine arvutis:  streamlit run app.py
"""
from __future__ import annotations
import io
import os
import sys
import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
DB_PATH = os.path.join(HERE, "data", "taimed.xlsx")

from core.db import load_db, ROMAN
from core.export import run_all, build_zip, slug, VAT
from core.photo import build_prompt, generate_photo, DEFAULT_MODEL

st.set_page_config(page_title="Istutusplaani tööriist", page_icon="🌿", layout="wide")

DEFAULT_SELECTION = [
    ("Harilik nurmenukk", 5), ("Aasnelk", 7), ("Verev kurereha", 12), ("Kerakellukas", 8),
    ("Harilik härjasilm", 8), ("Faasseni kassinaeris", 10), ("Harilik raudrohi", 10), ("Värv-karikakar", 8),
    ("Purpur-siilkübar", 10), ("Must tulikas", 5), ("Harilik kuldvits", 7), ("Lamba-aruhein", 10),
]
MONTHS = {5: "mai", 6: "juuni", 7: "juuli", 8: "august", 9: "september"}


def secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


# --- parool (valikuline) ---
pw = secret("APP_PASSWORD")
if pw and not st.session_state.get("auth"):
    st.title("Istutusplaani tööriist")
    entered = st.text_input("Parool", type="password")
    if entered and entered == pw:
        st.session_state.auth = True
        st.rerun()
    elif entered:
        st.error("Vale parool.")
    st.stop()


@st.cache_data(show_spinner=False)
def _load(data: bytes | None):
    return load_db(io.BytesIO(data) if data else DB_PATH)


# --- külgriba: andmebaas ---
with st.sidebar:
    st.header("Taimede andmebaas")
    up = st.file_uploader("Lae üles oma taimed.xlsx", type=["xlsx"], help="Sama ülesehitusega fail nagu data/taimed.xlsx. Hinnad veerus 'Hind (€/tk)'.")
    try:
        db = _load(up.getvalue() if up else None)
    except Exception as e:
        st.error(f"Faili ei saanud lugeda: {e}")
        st.stop()
    priced = sum(1 for p in db.values() if p.price is not None)
    st.caption(f"{len(db)} taime, neist hinnaga {priced}.")
    with open(DB_PATH, "rb") as f:
        st.download_button("Lae alla andmebaasi põhi (xlsx)", f.read(), "taimed.xlsx")
    st.divider()
    st.header("Fotorealistlik pilt")
    api_key = secret("OPENAI_API_KEY") or st.text_input("OpenAI API-võti", type="password", help="Püsivalt: lisa rakenduse Secrets alla OPENAI_API_KEY.")
    model = secret("OPENAI_IMAGE_MODEL", DEFAULT_MODEL)
    quality = st.selectbox("Pildi kvaliteet", ["low", "medium", "high"], index=1, help="Kõrgem kvaliteet on aeglasem ja kallim.")
    st.caption(f"Mudel: {model}" + (" · võti olemas" if api_key else " · võti puudub"))

st.title("Istutusplaani tööriist")
st.caption("Sisesta peenra mõõdud ja taimed. Tööriist arvutab kogused ja hinna ning teeb plaani, DXF-joonise ja visuaali.")

# --- 1. projekt ---
c1, c2, c3, c4 = st.columns([3, 1, 1, 1.4])
name = c1.text_input("Projekti nimi", "Elurikas peenar 4 × 5 m")
L = c2.number_input("Pikkus (m) – esikülg", 0.5, 60.0, 5.0, 0.1)
W = c3.number_input("Laius (m) – sügavus", 0.5, 60.0, 4.0, 0.1)
view = c4.selectbox("Peenra tüüp", ["front", "island"], format_func=lambda v: "Vaadatakse eest" if v == "front" else "Saarpeenar (igast küljest)")
c5, c6 = st.columns([1, 3])
month = c5.selectbox("Visuaali kuu", list(MONTHS), index=2, format_func=lambda m: MONTHS[m])

# --- 2. taimed ---
st.subheader("Taimed")
f1, f2, f3 = st.columns(3)
types = sorted({p.type for p in db.values()})
ft = f1.multiselect("Näita tüüpe", types, default=[t for t in types if t in ("Püsik", "Kõrreline", "Pinnakate", "Lehtpõõsas", "Igihaljas põõsas")])
lights = sorted({p.light for p in db.values() if p.light})
fl = f2.multiselect("Valgus", lights)
only_native = f3.checkbox("Ainult pärismaised")
options = sorted(n for n, p in db.items()
                 if (not ft or p.type in ft) and (not fl or p.light in fl) and (not only_native or p.native == "Jah"))

if "sel" not in st.session_state:
    st.session_state.sel = pd.DataFrame([{"Taim": n, "Osakaal (%)": v} for n, v in DEFAULT_SELECTION if n in db])

sel_df = st.data_editor(
    st.session_state.sel, num_rows="dynamic", use_container_width=True, key="editor",
    column_config={
        "Taim": st.column_config.SelectboxColumn("Taim", options=sorted(set(options) | set(st.session_state.sel["Taim"].dropna())), required=True, width="large"),
        "Osakaal (%)": st.column_config.NumberColumn("Osakaal (%)", min_value=0, max_value=100, step=1, required=True),
    },
)
sel_df = sel_df.dropna()
share_sum = float(sel_df["Osakaal (%)"].sum()) if len(sel_df) else 0.0
if abs(share_sum - 100) > 0.01:
    st.warning(f"Osakaalud kokku {share_sum:g}%. Peaks olema 100%.")
if len(sel_df) and sel_df["Taim"].duplicated().any():
    st.warning("Sama taim on valikus mitu korda.")

# valitud taimede kiirülevaade
if len(sel_df):
    info = [{"Taim": n, "Tüüp": db[n].type, "Valgus": db[n].light, "Kõrgus (m)": db[n].height, "Vahe (m)": db[n].spacing,
             "Õitseb": db[n].bloom_text, "Hind (€/tk)": db[n].price, "Pärismaine": db[n].native}
            for n in sel_df["Taim"] if n in db]
    with st.expander("Valitud taimede andmed"):
        st.dataframe(pd.DataFrame(info), hide_index=True, use_container_width=True)

go = st.button("Arvuta ja koosta plaan", type="primary", disabled=not len(sel_df) or abs(share_sum - 100) > 0.01)
if go:
    selection = [(r["Taim"], float(r["Osakaal (%)"])) for _, r in sel_df.iterrows() if float(r["Osakaal (%)"]) > 0]
    with st.spinner("Arvutan koguseid, paigutan taimi ja joonistan … (10–40 s)"):
        try:
            st.session_state.res = run_all(db, selection, float(L), float(W), name, month=month, view=view)
            st.session_state.photo = None
            st.session_state.sel = sel_df.reset_index(drop=True)
        except Exception as e:
            st.error(f"Midagi läks valesti: {e}")

res = st.session_state.get("res")
if not res:
    st.stop()

# --- 3. tulemused ---
st.divider()
summ = res["summary"]
lines = res["lines"]
base = slug(res["project"]["name"])
m1, m2, m3, m4 = st.columns(4)
m1.metric("Pindala", f"{res['project']['L'] * res['project']['W']:.1f} m²".replace(".", ","))
m2.metric("Taimi kokku", f"{summ['qty']} tk")
m3.metric("Taimed km-ta", f"{summ['total']:.2f} €".replace(".", ","))
m4.metric(f"Km-ga ({int(VAT * 100)}%)", f"{summ['total'] * (1 + VAT):.2f} €".replace(".", ","))
if summ["missing_prices"]:
    st.info("Hind puudub: " + ", ".join(summ["missing_prices"]) + ". Lisa hinnad andmebaasi faili ja lae see üles.")

t1, t2, t3, t4 = st.tabs(["Kogused", "Istutusplaan", "Illustratsioon", "Fotorealistlik visuaal"])
with t1:
    df = pd.DataFrame([{
        "Nr": l.nr, "Taim": l.plant.name, "Ladinakeelne nimi": l.plant.latin, "Müügivorm": l.plant.sale_form,
        "Osakaal": f"{l.share * 100:g}%", "Pind (m²)": round(l.area, 2), "Vahe (m)": l.plant.spacing,
        "Kogus (tk)": l.qty, "Hind (€/tk)": l.plant.price, "Summa (€)": None if l.total is None else round(l.total, 2),
    } for l in lines])
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.download_button("Lae alla kogusetabel (xlsx)", res["xlsx"], f"{base}_kogused.xlsx")
with t2:
    st.image(res["plan_png"], use_container_width=True)
    a, b = st.columns(2)
    a.download_button("Lae alla plaan (PNG)", res["plan_png"], f"{base}_istutusplaan.png")
    b.download_button("Lae alla joonis (DXF, AutoCAD)", res["dxf"], f"{base}_istutusplaan.dxf")
    st.caption("DXF: mõõdud meetrites, iga liik eraldi kihil. AutoCADis „Salvesta kui“ → DWG.")
with t3:
    show_labels = st.toggle("Näita taimede tähiseid", value=True, help="Tähistega pilt aitab kontrollida, kus mis taim on. Fotorealistliku pildi jaoks kasutatakse tähisteta pilti.")
    st.image(res["illustration_labeled"] if show_labels else res["illustration"], use_container_width=True)
    a, b = st.columns(2)
    a.download_button("Lae alla tähistega (PNG)", res["illustration_labeled"], f"{base}_illustratsioon_tahistega.png")
    b.download_button("Lae alla tähisteta (PNG)", res["illustration"], f"{base}_illustratsioon.png")
with t4:
    prompt = st.text_area("Pildi kirjeldus (koostatud automaatselt, võid muuta)", build_prompt(lines, res["layout"], month), height=220)
    if not api_key:
        st.warning("OpenAI API-võti puudub. Lisa see külgribal või rakenduse seadetes (Secrets).")
    if st.button("Tee fotorealistlik visuaal", disabled=not api_key):
        with st.spinner("Pildimudel töötab … (tavaliselt 30–90 s)"):
            try:
                st.session_state.photo = generate_photo(api_key, res["illustration"], prompt, model=model, quality=quality)
            except Exception as e:
                st.error(str(e))
    if st.session_state.get("photo"):
        st.image(st.session_state.photo, use_container_width=True)
        with st.expander("Võrdle: millised taimed peaksid pildil olema"):
            st.image(res["illustration_labeled"], use_container_width=True)
        st.caption("Illustratiivne visuaal. Kontrolli enne kliendile saatmist, et taimed näeksid õiged välja.")
        st.download_button("Lae alla visuaal (PNG)", st.session_state.photo, f"{base}_visuaal.png")

st.divider()
st.download_button("Lae alla kõik ühe ZIP-failina", build_zip(res, st.session_state.get("photo")), f"{base}.zip", type="primary")
