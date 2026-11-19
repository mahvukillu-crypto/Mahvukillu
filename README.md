# Istutusplaani tööriist (versioon 0.1)

Veebirakendus haljastuse hinnapäringute jaoks. Sisestad peenra mõõdud ja valid taimed, rakendus teeb:

- **kogusetabeli** koos hindade ja käibemaksuga (Excel),
- **istutusplaani** pealtvaates koos legendiga (PNG),
- **DXF-joonise** AutoCADi jaoks (iga liik eraldi kihil, legend, kirjanurk),
- **illustratsiooni** peenrast eest vaadates,
- **fotorealistliku visuaali** OpenAI pildimudeliga (illustratsioon + automaatne kirjeldus).

Kõik failid saab alla laadida eraldi või ühe ZIP-failina.

---

## Paigaldamine veebi (Streamlit Community Cloud, tasuta)

### 1. GitHub
1. Tee konto: <https://github.com/signup>
2. Paremal üleval **+** → **New repository**. Nimi näiteks `istutusplaan`. Vali **Private**. Vajuta **Create repository**.
3. Vajuta lingil **uploading an existing file** ja lohista sinna **kõik selle kausta failid ja kaustad** (`app.py`, `requirements.txt`, `core`, `data`, `.streamlit`, `tools`, `README.md`). Vajuta **Commit changes**.
   - Mac peidab punktiga algavaid kaustu (`.streamlit`). Kui see üles ei läinud, pole hullu: see on ainult värviteema.

### 2. Streamlit Cloud
1. Mine <https://share.streamlit.io> ja logi sisse GitHubi kontoga.
2. **Create app** → **Deploy a public app from GitHub** (rakendus jääb sellegipoolest privaatseks, kui repo on privaatne).
3. Vali oma repo `istutusplaan`, haru `main`, fail `app.py`.
4. **Advanced settings** → Python **3.12**.
5. Samas aknas **Secrets** lahtrisse kleebi:
   ```
   OPENAI_API_KEY = "sk-...sinu võti..."
   APP_PASSWORD = "vali-oma-parool"
   ```
6. **Deploy**. Esimene käivitus võtab paar minutit. Saad lingi, näiteks `https://istutusplaan.streamlit.app`.

### 3. OpenAI API-võti
1. Mine <https://platform.openai.com>, tee konto ja lisa maksekaart (**Settings → Billing**). API makstakse kasutuse järgi ja see on ChatGPT tellimusest eraldi.
2. **API keys → Create new secret key**. Kopeeri võti (algab `sk-`) ja pane see Streamliti Secrets alla (punkt 2.5).
3. Kui OpenAI nõuab pildimudelite jaoks organisatsiooni kinnitamist (**Settings → Organization → Verify**), tee see ära.
4. Soovi korral sea **Billing → Limits** alla kuulimiit, nt 10 $.

---

## Kasutamine

1. **Taimede andmebaas**: rakendus kasutab faili `data/taimed.xlsx`. Lae see külgribalt alla, lisa **kollasesse veergu oma hinnad (km-ta)** ja lae külgribal üles.
   Püsivalt: asenda GitHubis fail `data/taimed.xlsx` oma hindadega failiga.
2. Sisesta **projekti nimi**, **pikkus** (esikülg) ja **laius** (sügavus).
3. Vali **taimed ja osakaalud** (kokku 100%). Filtrid aitavad valikut kitsendada (tüüp, valgus, pärismaine).
4. **Arvuta ja koosta plaan**.
5. Vahelehel **Fotorealistlik visuaal** vaata kirjeldus üle (võid seda muuta) ja vajuta **Tee fotorealistlik visuaal**. Üks pilt maksab orienteeruvalt mõned sendid ja võtab 30–90 sekundit.
6. **Lae alla kõik ühe ZIP-failina**.

### Uue taime lisamine
Lisa rida faili `taimed.xlsx` lehele „Taimed“. Kohustuslikud veerud: Taim, Ladinakeelne nimi, Tüüp, Istutusvahe, Kõrgus, Laius.
- **Õitseb**: kujul `juuni–aug` või `mai`.
- **Õis / dekoratiivsus**: värvisõnad (valge, kollane, roosa, lilla, sinine, punane, oranž …) – nendest tuleb värv plaanil ja visuaalil.
- **Kuju** ja **Õievärv hex**: valikulised, kui automaatne tulemus illustratsioonil ei sobi.

---

## Arvutis käivitamine (valikuline)

```
pip install -r requirements.txt
streamlit run app.py
```
API-võti: kopeeri `.streamlit/secrets.toml.naide` → `.streamlit/secrets.toml` ja täida.

## Teadaolevad piirangud (v0.1)

- Ala on üks ristkülik. Vabakujulised alad (polügoon või DXF-ist imporditud kontuur) ja hekid jooksvas meetris tulevad järgmises versioonis.
- Paigutus: madalad ees, kõrged taga (või saarpeenra korral kõrged keskel), liigid triividena. Naabertaimede vahe võib kohati olla 10–20% väiksem kui nominaalne istutusvahe.
- Fotorealistlik visuaal on illustratiivne: pildimudel võib harvemaid liike valesti joonistada.
- Puud joonistatakse illustratsioonil noorte puudena (kõrgus piiratud).

## Failid

| Fail | Mis see on |
|---|---|
| `app.py` | Rakenduse kasutajaliides |
| `core/db.py` | Taimede andmebaasi lugemine, õitsemise ja värvide tuletamine |
| `core/calc.py` | Kogused ja maksumus |
| `core/layout.py` | Taimede paigutus peenral |
| `core/dxf.py` | DXF-joonis |
| `core/plan_png.py` | Värviline plaan |
| `core/illustration.py` | Illustratsioon |
| `core/photo.py` | Pildi kirjeldus ja OpenAI päring |
| `core/export.py` | Excel, ZIP, kogu ahel |
| `data/taimed.xlsx` | Taimede andmebaas (105 taime) |
